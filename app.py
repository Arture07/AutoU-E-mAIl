import os
import re
import json
import logging
from time import sleep
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import google.generativeai as genai
import fitz 

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        logger.info("Gemini API configurada.")
    except Exception as e:
        logger.exception("Erro ao configurar Gemini SDK: %s", e)
else:
    logger.warning("GEMINI_API_KEY não encontrada.")

# ---------- UTILITÁRIOS ----------
def allowed_file(filename: str) -> bool:
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_json_load(s: str):
    """Tenta carregar um JSON de forma segura, removendo comentários e vírgulas finais."""
    s = re.sub(r'//.*?\n|/\*.*?\*/', '', s, flags=re.S)  # remove comentários
    s = re.sub(r',\s*([}\]])', r'\1', s)                # remove vírgulas finais
    return json.loads(s)

def find_first_json_object(text: str):
    """Encontra e retorna o primeiro objeto JSON balanceado no texto usando um parser por pilha."""
    if not text:
        raise ValueError("Texto vazio")
    start = None
    depth = 0
    in_string = False
    escape = False
    for i, ch in enumerate(text):
        if ch == '"' and not escape:
            in_string = not in_string
        if ch == '\\' and in_string:
            escape = not escape
            continue
        else:
            escape = False
        if not in_string:
            if ch == '{':
                if start is None:
                    start = i
                depth += 1
            elif ch == '}':
                if depth > 0:
                    depth -= 1
                if start is not None and depth == 0:
                    return text[start:i+1]
    raise ValueError("Nenhum objeto JSON balanceado foi encontrado")

def extract_json_from_text(text: str):
    """
    Extrai um objeto JSON da resposta da IA. Retorna None se o parsing falhar.
    """
    if not text:
        return None

    candidate = ""
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.S)
    if match:
        candidate = match.group(1)
    else:
        try:
            candidate = find_first_json_object(text)
        except ValueError:
            logger.warning("Nenhum objeto JSON balanceado foi encontrado no texto da IA.")
            return None

    try:
        return safe_json_load(candidate)
    except json.JSONDecodeError:
        logger.warning("Parsing do JSON falhou, tentando corrigir aspas.")
        try:
            corrected_candidate = candidate.replace("'", '"')
            return safe_json_load(corrected_candidate)
        except Exception as e:
            logger.error("Não foi possível parsear o JSON mesmo após correções: %s", e)
            return None

def preprocess_text(text: str) -> str:
    """Limpa o texto, preservando pontuação essencial e normalizando espaços."""
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def simple_rule_classifier(text: str):
    """Fallback local baseado em palavras-chave se a API falhar."""
    text_lower = text.lower()
    productive_keywords = [
        'urgente', 'precisa', 'necessita', 'requer', 'solicita', 'solicitação',
        'favor enviar', 'pode enviar', 'status', 'anexo', 'erro', 'ajuda', 'reunião',
        'confirmar', 'deadline', 'prazo', 'alteração', 'atualização', 'dúvida'
    ]
    if any(k in text_lower for k in productive_keywords):
        return {
            "classification": "Produtivo (Fallback)",
            "suggestion": "Obrigado pelo envio. Vamos analisar e retornar em breve."
        }
    return {
        "classification": "Improdutivo (Fallback)",
        "suggestion": "Obrigado pela mensagem!"
    }

def extract_text_from_file(file_storage):
    """Extrai texto de um arquivo .pdf ou .txt de forma segura."""
    filename = secure_filename(file_storage.filename or "")
    if not allowed_file(filename):
        logger.warning("Extensão de arquivo não permitida: %s", filename)
        return None

    try:
        file_storage.seek(0)
    except Exception:
        pass

    ext = filename.rsplit('.', 1)[1].lower()
    try:
        if ext == 'pdf':
            data = file_storage.read()
            pdf = fitz.open(stream=data, filetype="pdf")
            return "\n".join(page.get_text() for page in pdf)
        elif ext == 'txt':
            raw = file_storage.read()
            if isinstance(raw, bytes):
                try:
                    return raw.decode('utf-8')
                except UnicodeDecodeError:
                    return raw.decode('latin-1', errors='ignore')
            return str(raw)
    except Exception as e:
        logger.exception("Falha ao ler o arquivo %s: %s", filename, e)
        return None
    return None

# ---------- INTEGRAÇÃO COM GEMINI ----------
def call_gemini_api(text: str):
    """Chama a API Gemini com lógica de retentativa e retorna a resposta JSON, ou um erro."""
    if not api_key:
        logger.warning("GEMINI_API_KEY ausente, usando fallback.")
        return {"error": "API key ausente"}

    prompt = f"""
Você é um assistente corporativo altamente eficiente, especialista em triagem de e-mails. Sua tarefa é analisar o e-mail abaixo e retornar um objeto JSON.

**DEFINIÇÕES DAS CATEGORIAS:**
- **Produtivo:** E-mails que exigem uma ação ou resposta específica. Exemplos: solicitações de suporte, pedidos de atualização sobre projetos, dúvidas técnicas, agendamento de reuniões, envio de arquivos importantes para revisão.
- **Improdutivo:** E-mails que não necessitam de uma ação imediata ou são de natureza social. Exemplos: mensagens de "Feliz Natal", agradecimentos simples, SPAM, newsletters informativas que não pedem resposta.

**TAREFA:**
Analise o texto do e-mail abaixo e retorne **UNICAMENTE** um objeto JSON com duas chaves:
1.  `"classification"`: Deve ser `"Produtivo"` ou `"Improdutivo"`, com base nas definições acima.
2.  `"suggestion"`: Deve ser uma sugestão de resposta curta e profissional em português.
    - Se for **Produtivo**, a resposta deve acusar o recebimento e indicar que uma ação será tomada (ex: "Recebido, estamos verificando e retornaremos em breve.").
    - Se for **Improdutivo**, a resposta deve ser breve e cordial (ex: "Obrigado pela mensagem!").

**IMPORTANTE:** Sua resposta deve ser apenas o objeto JSON, sem nenhuma outra palavra, explicação ou formatação como markdown.

**Texto do E-mail:**
---
{text}
---
"""
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    for attempt in range(2):
        try:
            logger.info(f"Enviando prompt para Gemini (tentativa {attempt + 1}/2)...")
            response = model.generate_content(prompt)
            raw_text = getattr(response, "text", str(response)).strip()
            logger.debug("Resposta bruta da IA: %s", raw_text[:500])

            ai_json = extract_json_from_text(raw_text)
            if ai_json and 'classification' in ai_json and 'suggestion' in ai_json:
                return ai_json
            else:
                raise ValueError("JSON parseado é inválido ou não contém chaves esperadas.")
        except Exception as e:
            logger.warning(f"Tentativa {attempt + 1}/2 de chamar Gemini falhou: {e}")
            if attempt < 1:
                sleep(0.5)

    logger.error("Todas as tentativas de chamar a API Gemini falharam.")
    return {"error": "Falha na IA após múltiplas tentativas."}


# ---------- ROTAS ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Endpoint principal que recebe texto ou arquivo e retorna a análise."""
    try:
        email_text = None
        if request.is_json:
            data = request.get_json(silent=True) or {}
            email_text = data.get('text')
        elif 'file' in request.files:
            file = request.files['file']
            if not file or not file.filename:
                return jsonify({'error': 'Nenhum arquivo selecionado.'}), 400
            if not allowed_file(file.filename):
                return jsonify({'error': 'Extensão não permitida. Use .txt ou .pdf.'}), 400
            email_text = extract_text_from_file(file)
            if email_text is None:
                return jsonify({'error': 'Não foi possível extrair texto do arquivo.'}), 400
        else:
            return jsonify({'error': 'Formato de requisição inválido.'}), 400

        if not email_text or not email_text.strip():
            return jsonify({'error': 'Nenhum texto de e-mail fornecido.'}), 400

        processed_text = preprocess_text(email_text)
        ai_response = call_gemini_api(processed_text)

        if "error" in ai_response:
            logger.warning("IA falhou (%s). Aplicando fallback.", ai_response.get('error'))
            result = simple_rule_classifier(processed_text)
            result['note'] = 'fallback_local'
            return jsonify(result), 200

        return jsonify(ai_response), 200
    except Exception as e:
        logger.exception("Erro interno em /analyze: %s", e)
        return jsonify({'error': 'Erro interno ao processar a requisição.'}), 500

@app.route('/healthz')
def healthz():
    """Endpoint de health check."""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
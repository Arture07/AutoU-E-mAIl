from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
import json
from dotenv import load_dotenv
import fitz  # PyMuPDF

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configura a API do Google Gemini com a chave do ambiente
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A chave da API GEMINI_API_KEY não foi encontrada no ambiente.")
    genai.configure(api_key=api_key)
except ValueError as e:
    print(f"Erro de configuração: {e}")

# Função para chamar a API do Gemini (sem alterações)
def call_gemini_api(text):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = f"""
        Analise o seguinte texto de um e-mail e retorne um objeto JSON com duas chaves: "classification" e "suggestion".
        - A chave "classification" deve ter um dos seguintes valores: "Produtivo" ou "Improdutivo".
        - A chave "suggestion" deve conter uma sugestão de resposta curta, profissional e em português, adequada à classificação.
        - Se o e-mail for "Produtivo", a resposta deve ser informativa e neutra.
        - Se o e-mail for "Improdutivo", a resposta deve ser amigável e breve, como um agradecimento.
        - Responda apenas com o objeto JSON, sem nenhum texto ou formatação adicional como markdown.

        Texto do E-mail:
        ---
        {text}
        ---
        """
        response = model.generate_content(prompt)
        cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_response_text)
    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return {"error": "Falha ao processar a solicitação com a IA."}

# Função para extrair texto de arquivos
def extract_text_from_file(file_storage):
    if file_storage.filename.endswith('.pdf'):
        try:
            pdf_document = fitz.open(stream=file_storage.read(), filetype="pdf")
            text = ""
            for page in pdf_document:
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Erro ao ler PDF: {e}")
            return None
    elif file_storage.filename.endswith('.txt'):
        try:
            return file_storage.read().decode('utf-8')
        except Exception as e:
            print(f"Erro ao ler TXT: {e}")
            return None
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    # Adicionando logs para depuração
    print("\n--- Nova Requisição /analyze ---")
    print(f"Content-Type: {request.content_type}")
    print(f"É JSON? {request.is_json}")
    print(f"Arquivos na requisição: {list(request.files.keys())}")

    email_text = ""
    # Verifica se a requisição é JSON (para a aba de texto)
    if request.is_json:
        print("-> Rota: Requisição identificada como JSON.")
        data = request.get_json()
        email_text = data.get('text', '')
    # Verifica se a requisição contém um arquivo (para a aba de anexo)
    elif 'file' in request.files:
        print("-> Rota: Requisição identificada com um arquivo.")
        file = request.files['file']
        if file.filename == '':
            print("-> Erro: Nenhum arquivo selecionado (nome do arquivo vazio).")
            return jsonify({'error': 'Nenhum arquivo selecionado.'}), 400
        
        print(f"-> Info: Processando arquivo '{file.filename}'")
        email_text = extract_text_from_file(file)
        if email_text is None:
            print("-> Erro: Não foi possível extrair texto do arquivo.")
            return jsonify({'error': 'Não foi possível ler o arquivo. Verifique o formato.'}), 400
    else:
        print("-> Erro: Formato de requisição inválido (nem JSON, nem arquivo).")
        return jsonify({'error': 'Formato de requisição inválido.'}), 400

    if not email_text.strip():
        print("-> Erro: Texto do e-mail está vazio após o processamento.")
        return jsonify({'error': 'Nenhum texto de e-mail fornecido.'}), 400

    print(f"-> Sucesso: Enviando texto para a IA: '{email_text[:100]}...'")
    ai_response = call_gemini_api(email_text)

    if "error" in ai_response:
        return jsonify(ai_response), 500
    
    print("-> Sucesso: Análise concluída.")
    print("---------------------------------\n")
    return jsonify(ai_response)
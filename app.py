from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
import json
from dotenv import load_dotenv
import fitz
import re

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

def preprocess_text(text):
    """Realiza uma limpeza básica no texto antes de enviá-lo para a IA."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

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
    email_text = ""
    if request.is_json:
        data = request.get_json()
        email_text = data.get('text', '')
    elif 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado.'}), 400
        email_text = extract_text_from_file(file)
        if email_text is None:
            return jsonify({'error': 'Não foi possível ler o arquivo. Verifique o formato.'}), 400
    else:
        return jsonify({'error': 'Formato de requisição inválido.'}), 400

    if not email_text:
        return jsonify({'error': 'Nenhum texto de e-mail fornecido.'}), 400

    processed_text = preprocess_text(email_text)
    print(f"Texto pré-processado enviado para a IA: '{processed_text[:100]}...'")

    ai_response = call_gemini_api(processed_text)

    if "error" in ai_response:
        return jsonify(ai_response), 500
    
    return jsonify(ai_response)
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Pega os dados JSON enviados pelo frontend
    data = request.get_json()
    email_text = data.get('text', '')

    # Validação simples para garantir que o texto não está vazio
    if not email_text:
        return jsonify({'error': 'Nenhum texto de e-mail fornecido.'}), 400

    # Imprime no console do servidor para sabermos que a requisição chegou
    print(f"Texto recebido para análise: '{email_text[:100]}...'")

    # Resposta simulada (mock) para testar a conexão
    # Na próxima versão, a chamada à IA real entrará aqui.
    mock_response = {
        'classification': 'Produtivo (Resposta do Backend)',
        'suggestion': 'Olá,\n\nRecebemos sua mensagem e já estamos cuidando da sua solicitação. Entraremos em contato em breve com uma atualização.\n\nAtenciosamente,\nEquipe AutoU'
    }
    
    return jsonify(mock_response)
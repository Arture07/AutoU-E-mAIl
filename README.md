# InboxFlox - Analisador Inteligente de E-mails  

## 📄 Sobre o Projeto  

O **InboxFlox** é uma ferramenta demonstrativa de portfólio para triagem rápida de e-mails.  
O objetivo é otimizar a gestão de e-mails corporativos de alto volume, utilizando um modelo generativo para automatizar a classificação e sugerir respostas iniciais.  

A aplicação classifica os e-mails em duas categorias principais:  
- **Produtivo**: E-mails que demandam uma ação ou resposta direta.  
- **Improdutivo**: Mensagens que não necessitam de uma ação imediata, como agradecimentos ou felicitações.  

---

## ✨ Funcionalidades Principais  

- 📑 **Análise por Texto**: Cole o conteúdo de um e-mail diretamente na interface para uma análise instantânea.  
- 📂 **Análise por Arquivo**: Upload de e-mails salvos nos formatos `.txt` ou `.pdf`.  
- 🤖 **Classificação com IA**: Utiliza a API do Google Gemini para determinar se o e-mail é produtivo ou improdutivo.  
- ✉️ **Sugestão de Resposta**: A IA gera uma resposta automática apropriada.  
- 📱 **Interface Responsiva**: Design limpo e moderno, funcional em desktop e mobile.  

---

## 🛠️ Tecnologias Utilizadas  

**Frontend:**  
- HTML5  
- Tailwind CSS  
- JavaScript  

**Backend:**  
- Python 3  
- Flask  

**Inteligência Artificial:**  
- Google Gemini API  

**Bibliotecas Python:**  
- `google-generativeai`  
- `python-dotenv`  
- `PyMuPDF (fitz)`  

---

## 🚀 Como Executar Localmente  

### 🔹 Pré-requisitos  
- Python 3.8+  
- pip (gerenciador de pacotes do Python)  

### 🔹 1. Clone o Repositório  
```bash
git clone https://github.com/Arture07/AutoU-E-mAIl
cd AutoU-E-mAIl
```
### 🔹 2. Instale as Dependências
Crie um ambiente virtual (recomendado) e instale as bibliotecas necessárias.
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### 🔹 3. Configure a Chave da API
Acesse o Google AI Studio para gerar sua chave gratuita.

Abra o arquivo .env e cole sua chave de API:
```bash
GEMINI_API_KEY="SUA_CHAVE_DE_API_AQUI"
# Opcional: escolha do modelo (padrão: gemini-2.5-flash)
# Dicas:
# - Para melhor qualidade, use: gemini-2.5-pro
# - Para menor latência/custo, use: gemini-2.5-flash
# - Evite o sufixo "-latest" pois pode não estar disponível em algumas versões da API
GEMINI_MODEL="gemini-2.5-flash"
```
### 🔹 4. Rode a Aplicação
```bash
flask run
```
<br> 

*Projeto de portfólio desenvolvido por Artur Kuzma Marques (InboxFlox).* 

---

## 🔧 Respostas Estruturadas em JSON (opcional)

A API foi configurada para solicitar respostas diretamente em JSON, usando um schema que contém:
- classification: "Produtivo" | "Improdutivo"
- suggestion: string

Benefícios:
- Reduz erros de parsing e elimina formatações Markdown acidentais.
- Garante chaves obrigatórias.

Para desativar ou alterar, edite `app.py` em `generation_config` dentro de `call_gemini_api`.

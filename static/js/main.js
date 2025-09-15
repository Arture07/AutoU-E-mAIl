document.addEventListener('DOMContentLoaded', () => {
    // Elementos das Abas
    const tabText = document.getElementById('tab-text');
    const tabFile = document.getElementById('tab-file');
    const contentText = document.getElementById('content-text');
    const contentFile = document.getElementById('content-file');

    // Elementos do Upload
    const dragArea = document.getElementById('drag-area');
    const fileUpload = document.getElementById('file-upload');
    const fileNameDisplay = document.getElementById('file-name');
    let currentFile = null;

    // Elementos de Ação e Resultado
    const analyzeButton = document.getElementById('analyze-button');
    const resultSection = document.getElementById('result-section');
    const classificationResult = document.getElementById('classification-result');
    const suggestionResult = document.getElementById('suggestion-result');
    const copyButton = document.getElementById('copy-button');
    const copyIcon = document.getElementById('copy-icon');
    const checkIcon = document.getElementById('check-icon');
    const emailTextArea = document.getElementById('email-text');

    // --- Lógica de Troca de Abas ---
    const setActiveTab = (activeTab, inactiveTab) => {
        // Estilos da aba ativa
        activeTab.classList.add('text-violet-600', 'border-violet-600', 'border-b-2', 'font-semibold');
        activeTab.classList.remove('text-gray-500', 'font-medium');

        // Estilos da aba inativa
        inactiveTab.classList.add('text-gray-500', 'font-medium');
        inactiveTab.classList.remove('text-violet-600', 'border-violet-600', 'border-b-2', 'font-semibold');
    };

    tabText.addEventListener('click', () => {
        contentText.classList.remove('hidden');
        contentFile.classList.add('hidden');
        setActiveTab(tabText, tabFile);
        currentFile = null; // Limpa o arquivo se voltar para a aba de texto
        fileNameDisplay.textContent = '';
    });

    tabFile.addEventListener('click', () => {
        contentFile.classList.remove('hidden');
        contentText.classList.add('hidden');
        setActiveTab(tabFile, tabText);
    });

    // --- Lógica de Upload de Arquivo ---
    const handleFile = (file) => {
        if (file && (file.type === 'text/plain' || file.type === 'application/pdf')) {
            currentFile = file;
            fileNameDisplay.textContent = file.name;
        } else {
            fileNameDisplay.textContent = 'Formato inválido. Use .txt ou .pdf';
            currentFile = null;
        }
    };

    dragArea.addEventListener('click', () => fileUpload.click());
    fileUpload.addEventListener('change', () => handleFile(fileUpload.files[0]));

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dragArea.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dragArea.addEventListener(eventName, () => dragArea.classList.add('drag-area-border-active'));
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dragArea.addEventListener(eventName, () => dragArea.classList.remove('drag-area-border-active'));
    });

    dragArea.addEventListener('drop', e => handleFile(e.dataTransfer.files[0]));

    // --- Lógica de Análise ---
    analyzeButton.addEventListener('click', async () => {
        resultSection.classList.add('hidden');
        analyzeButton.textContent = 'Analisando...';
        analyzeButton.disabled = true;

        let body;
        let headers = {};

        if (!contentFile.classList.contains('hidden')) { // Aba de arquivo
            if (!currentFile) {
                alert('Por favor, selecione um arquivo.');
                analyzeButton.textContent = 'Analisar E-mail';
                analyzeButton.disabled = false;
                return;
            }
            body = new FormData();
            body.append('file', currentFile);
        } else { // Aba de texto
            const text = emailTextArea.value;
            if (!text.trim()) {
                alert('Por favor, insira o texto do e-mail.');
                analyzeButton.textContent = 'Analisar E-mail';
                analyzeButton.disabled = false;
                return;
            }
            body = JSON.stringify({ text });
            headers['Content-Type'] = 'application/json';
        }

        try {
            const response = await fetch('/analyze', { method: 'POST', headers, body });
            const data = await response.json();

            if (response.ok) {
                classificationResult.textContent = data.classification || 'N/A';
                suggestionResult.textContent = data.suggestion || 'Nenhuma sugestão disponível.';
                resultSection.classList.remove('hidden');
                resultSection.classList.add('fade-in');
            } else {
                throw new Error(data.error || 'Ocorreu um erro no servidor.');
            }
        } catch (error) {
            suggestionResult.textContent = `Erro: ${error.message}`;
            resultSection.classList.remove('hidden');
        } finally {
            analyzeButton.textContent = 'Analisar E-mail';
            analyzeButton.disabled = false;
        }
    });

    // --- Lógica de Copiar ---
    copyButton.addEventListener('click', () => {
        navigator.clipboard.writeText(suggestionResult.textContent).then(() => {
            copyIcon.classList.add('hidden');
            checkIcon.classList.remove('hidden');
            setTimeout(() => {
                copyIcon.classList.remove('hidden');
                checkIcon.classList.add('hidden');
            }, 1500);
        });
    });
});
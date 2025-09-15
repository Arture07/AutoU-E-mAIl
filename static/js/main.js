document.addEventListener('DOMContentLoaded', () => {
    // Elementos das abas
    const tabText = document.getElementById('tab-text');
    const tabFile = document.getElementById('tab-file');
    const contentText = document.getElementById('content-text');
    const contentFile = document.getElementById('content-file');

    // Elementos de input
    const emailTextarea = document.getElementById('email-text');
    const dragArea = document.getElementById('drag-area');
    const fileInput = document.getElementById('file-upload');
    const fileNameDisplay = document.getElementById('file-name');
    let uploadedFile = null;

    // Elementos de ação e resultado
    const analyzeButton = document.getElementById('analyze-button');
    const resultSection = document.getElementById('result-section');
    const classificationResult = document.getElementById('classification-result');
    const suggestionResult = document.getElementById('suggestion-result');
    const copyButton = document.getElementById('copy-button');

    // Lógica para trocar de abas
    tabText.addEventListener('click', () => {
        tabText.classList.add('text-white', 'border-blue-500', 'font-semibold');
        tabText.classList.remove('text-gray-400', 'font-medium');
        tabFile.classList.remove('text-white', 'border-blue-500', 'font-semibold');
        tabFile.classList.add('text-gray-400', 'font-medium');
        contentText.classList.remove('hidden');
        contentFile.classList.add('hidden');
    });

    tabFile.addEventListener('click', () => {
        tabFile.classList.add('text-white', 'border-blue-500', 'font-semibold');
        tabFile.classList.remove('text-gray-400', 'font-medium');
        tabText.classList.remove('text-white', 'border-blue-500', 'font-semibold');
        tabText.classList.add('text-gray-400', 'font-medium');
        contentFile.classList.remove('hidden');
        contentText.classList.add('hidden');
    });

    // Lógica para upload de arquivo (arrastar e soltar)
    dragArea.addEventListener('click', () => fileInput.click());
    
    dragArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dragArea.classList.add('drag-area-border-hover');
    });

    dragArea.addEventListener('dragleave', () => {
        dragArea.classList.remove('drag-area-border-hover');
    });
    
    dragArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dragArea.classList.remove('drag-area-border-hover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        if (file.type === 'text/plain' || file.type === 'application/pdf') {
            uploadedFile = file;
            fileNameDisplay.textContent = file.name;
        } else {
            alert('Por favor, selecione um arquivo .txt ou .pdf');
            uploadedFile = null;
            fileNameDisplay.textContent = '';
        }
    }

    // Lógica do botão "Analisar" com chamada ao backend
    analyzeButton.addEventListener('click', async () => {
        const isTextTabActive = !contentText.classList.contains('hidden');
        let requestBody;
        let requestHeaders = {};

        if (isTextTabActive) {
            const emailContent = emailTextarea.value;
            if (!emailContent.trim()) {
                alert('Por favor, cole o conteúdo do e-mail.');
                return;
            }
            requestHeaders['Content-Type'] = 'application/json';
            requestBody = JSON.stringify({ text: emailContent.trim() });
        } else {
            if (!uploadedFile) {
                alert('Por favor, selecione um arquivo.');
                return;
            }
            // Para upload de arquivo, usamos FormData
            const formData = new FormData();
            formData.append('file', uploadedFile);
            requestBody = formData;
            // NÃO definimos Content-Type aqui, o navegador faz isso
        }

        // Ativa o estado de carregamento
        analyzeButton.disabled = true;
        analyzeButton.textContent = 'Analisando...';
        resultSection.classList.add('hidden');
        
        try {
            // Faz a chamada (fetch) para o endpoint /analyze no backend
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: requestHeaders,
                body: requestBody,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Ocorreu um erro no servidor.');
            }

            const result = await response.json();
            
            // Atualiza a interface com os dados recebidos do backend
            classificationResult.textContent = result.classification;
            suggestionResult.textContent = result.suggestion;
            resultSection.classList.remove('hidden');

        } catch (error) {
            console.error('Erro ao analisar e-mail:', error);
            alert(`Não foi possível concluir a análise: ${error.message}`);
        } finally {
            // Restaura o botão, ocorrendo sucesso ou falha
            analyzeButton.disabled = false;
            analyzeButton.textContent = 'Analisar E-mail';
        }
    });

    // Lógica do botão "Copiar"
    copyButton.addEventListener('click', () => {
        const textToCopy = suggestionResult.textContent;
        const tempTextarea = document.createElement('textarea');
        tempTextarea.value = textToCopy;
        document.body.appendChild(tempTextarea);
        tempTextarea.select();
        try {
            document.execCommand('copy');
            alert('Resposta copiada para a área de transferência!');
        } catch (err) {
            console.error('Falha ao copiar texto: ', err);
        }
        document.body.removeChild(tempTextarea);
    });
});

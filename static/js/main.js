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

    // Lógica do botão "Analisar" (com dados mock)
    analyzeButton.addEventListener('click', () => {
        const emailContent = emailTextarea.value;
        const isTextTabActive = !contentText.classList.contains('hidden');

        if (isTextTabActive && !emailContent.trim()) {
            alert('Por favor, cole o conteúdo do e-mail.');
            return;
        }
        if (!isTextTabActive && !uploadedFile) {
            alert('Por favor, selecione um arquivo.');
            return;
        }

        // Simula estado de carregamento
        analyzeButton.disabled = true;
        analyzeButton.textContent = 'Analisando...';
        resultSection.classList.add('hidden');
        
        // Simula uma chamada de API
        setTimeout(() => {
            // Exibe resultados mock
            classificationResult.textContent = 'Produtivo';
            suggestionResult.textContent = 'Olá!\n\nRecebemos sua solicitação e já estamos trabalhando nela. Você receberá uma atualização sobre o status em breve.\n\nAtenciosamente,\nA Equipe AutoU';
            resultSection.classList.remove('hidden');

            // Restaura o botão
            analyzeButton.disabled = false;
            analyzeButton.textContent = 'Analisar E-mail';
        }, 1500); // 1.5 segundos de simulação
    });

    // Lógica do botão "Copiar"
    copyButton.addEventListener('click', () => {
        const textToCopy = suggestionResult.textContent;
        // Usa um textarea temporário para copiar o texto
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

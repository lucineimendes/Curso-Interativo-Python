let editor;

function initializeEditor(config) {
    // Inicializa o editor CodeMirror
    const editorElement = document.getElementById(config.editorId);
    if (!editorElement) {
        console.error('Elemento do editor não encontrado:', config.editorId);
        return;
    }

    editor = CodeMirror.fromTextArea(editorElement, {
        mode: "python",
        lineNumbers: true,
        theme: "monokai",
        indentUnit: 4,
        matchBrackets: true,
        autoCloseBrackets: true,
        lineWrapping: true
    });

    // Configura botão de executar código
    const runButton = document.getElementById(config.runButtonId);
    if (runButton) {
        runButton.addEventListener('click', () => executeCode(config));
    }

    // Configura botão de verificar exercício
    const checkButton = document.getElementById(config.checkButtonId);
    if (checkButton && config.courseId && config.exerciseId) {
        checkButton.addEventListener('click', () => checkExercise(config));
    }
}

async function executeCode(config) {
    const code = editor.getValue();
    const outputArea = document.getElementById(config.outputAreaId);
    const outputPre = document.getElementById(config.outputPreId);

    if (!code.trim()) {
        showOutput(outputArea, outputPre, "Por favor, escreva algum código antes de executar.", "error");
        return;
    }

    showOutput(outputArea, outputPre, "Executando código...", "info");

    try {
        const response = await fetch('/api/execute-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: code })
        });

        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.success) {
            const output = result.output || "(Nenhuma saída)";
            showOutput(outputArea, outputPre, output, "success");
        } else {
            const errorMsg = result.details || "Erro desconhecido";
            showOutput(outputArea, outputPre, errorMsg, "error");
        }

    } catch (error) {
        console.error('Erro ao executar código:', error);
        showOutput(outputArea, outputPre, `Erro de conexão: ${error.message}`, "error");
    }
}

async function checkExercise(config) {
    const code = editor.getValue();
    const outputArea = document.getElementById(config.outputAreaId);
    const outputPre = document.getElementById(config.outputPreId);

    if (!code.trim()) {
        showOutput(outputArea, outputPre, "Por favor, escreva algum código antes de verificar.", "error");
        return;
    }

    showOutput(outputArea, outputPre, "Verificando solução...", "info");

    try {
        const response = await fetch('/api/check-exercise', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                course_id: config.courseId,
                exercise_id: config.exerciseId,
                code: code
            })
        });

        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.success) {
            const successMsg = `✅ Parabéns! Sua solução está correta!\n\n${result.output || ""}`;
            showOutput(outputArea, outputPre, successMsg, "success");
        } else {
            const errorMsg = `❌ Sua solução precisa de ajustes:\n\n${result.details || "Erro desconhecido"}`;
            if (result.output) {
                errorMsg += `\n\nSaída do seu código:\n${result.output}`;
            }
            showOutput(outputArea, outputPre, errorMsg, "error");
        }

    } catch (error) {
        console.error('Erro ao verificar exercício:', error);
        showOutput(outputArea, outputPre, `Erro de conexão: ${error.message}`, "error");
    }
}

function showOutput(outputArea, outputPre, message, type) {
    outputArea.style.display = "block";
    outputPre.textContent = message;
    
    // Remove classes anteriores
    outputArea.classList.remove("text-success", "text-danger", "text-info");
    
    // Adiciona classe baseada no tipo
    switch(type) {
        case "success":
            outputArea.classList.add("text-success");
            break;
        case "error":
            outputArea.classList.add("text-danger");
            break;
        case "info":
            outputArea.classList.add("text-info");
            break;
    }
}
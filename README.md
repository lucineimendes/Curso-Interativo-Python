# **Documentação Completa do Projeto: Curso Interativo de Python**

## 1. Visão Geral do Projeto

O "Curso Interativo de Python" é uma plataforma web educacional projetada para o ensino prático da linguagem Python. A aplicação permite que os usuários naveguem por cursos estruturados por nível de dificuldade, acessem lições teóricas e resolvam exercícios de programação diretamente no navegador. O principal diferencial é a capacidade de executar o código do usuário no servidor e fornecer feedback em tempo real, criando um ciclo de aprendizado ativo e engajador.

O projeto é construído com um backend em **Python/Flask** e um frontend padrão com **HTML/CSS/JavaScript**. O conteúdo dos cursos é gerenciado de forma desacoplada através de arquivos **JSON**, e a qualidade do código é assegurada por uma suíte de testes robusta utilizando **Pytest**.

## 2. Estrutura do Projeto

A seguir, uma visualização da organização das pastas e arquivos principais do projeto, extraída do `README.md` para referência rápida.

```
Curso-Interartivo-Python/
├───images
│   └───banner.png
├───projects
│   ├───data
│   │   ├───advanced
│   │   │   ├───exercises.json
│   │   │   └───lessons.json
│   │   ├───basic
│   │   │   ├───exercises.json
│   │   │   └───lessons.json
│   │   └───intermediate
│   │       ├───exercises.json
│   │       └───lessons.json
│   ├───static
│   │   ├───css
│   │   │   └───style.css
│   │   └───js
│   │       ├───editor_handler.js
│   │       └───main.js
│   ├───templates
│   │   ├───404.html
│   │   ├───base.html
│   │   ├───code_editor.html
│   │   ├───courses.html
│   │   ├───course_detail.html
│   │   ├───course_details.html
│   │   ├───course_list.html
│   │   ├───exercise.html
│   │   ├───index.html
│   │   ├───lesson.html
│   │   └───lesson_detail.html
│   ├───app.py
│   ├───code_executor.py
│   ├───course_manager.py
│   ├───exercise_manager.py
│   ├───lesson_manager.py
│   └───__init__.py
├───testes
│   ├───conftest.py
│   ├───test_api.py
│   ├───test_app.py
│   ├───test_managers.py
│   └───test_meta_exercise.py
├───.gitignore
├───LICENSE.md
├───generate_coverage_report.py
├───run.py
├───pytest.ini
├───README.md
├───requirements.txt
└───test_run.log
```

## 3. Arquitetura e Componentes Prioritários

A seguir, uma análise detalhada dos componentes que representam o núcleo de valor do projeto.

### 3.1. `app.py` - O Orquestrador Central

Este arquivo é o coração da aplicação Flask. Sua principal responsabilidade é gerenciar as requisições HTTP, orquestrar a lógica de negócios e renderizar as respostas para o usuário, seja em formato HTML ou JSON.

**Principais Funções:**

*   **Inicialização do Flask:** Configura e inicializa a aplicação Flask e o CORS.
*   **Instância dos Managers:** Cria as instâncias dos módulos de gerenciamento (`CourseManager`, `LessonManager`, etc.) que servem como a camada de acesso aos dados.
*   **Definição de Rotas (Endpoints):**
    *   **Rotas de Página (HTML):** Endpoints como `/`, `/courses`, `/courses/<id>` que renderizam os templates HTML, populando-os com os dados obtidos dos managers.
    *   **Rotas de API (JSON):** Endpoints prefixados com `/api/`, como `/api/execute-code` e `/api/check-exercise`, que lidam com a lógica dinâmica do frontend.
*   **Tratamento de Erros:** Implementa handlers para erros comuns como 404 e 500.

### 3.2. Módulos de Gerenciamento (`*_manager.py`)

Esses módulos funcionam como uma camada de abstração de dados. Eles isolam a lógica de leitura e manipulação dos arquivos JSON do resto da aplicação.

*   **`CourseManager`:** Gerencia o arquivo `courses.json`, permitindo carregar, buscar, adicionar, e atualizar cursos.
*   **`LessonManager` e `ExerciseManager`:** Carregam dados de lições e exercícios de arquivos específicos sob demanda, uma abordagem eficiente para não carregar dados desnecessários.

### 3.3. Suíte de Testes (`tests/`)

O diretório `tests/` é fundamental para garantir a estabilidade e a confiabilidade do projeto.

*   **`conftest.py`:** Arquivo de configuração central para os testes, define "fixtures" que criam um ambiente de dados temporário e isolado para garantir que os testes sejam reproduzíveis.
*   **`test_app.py`:** Contém testes de integração para as rotas HTML, simulando requisições e verificando se o conteúdo esperado está presente.

### 3.4. Configuração e Dependências

*   **`requirements.txt`:** Lista as bibliotecas Python necessárias, como `Flask` e `pytest`.
*   **`pytest.ini`:** Configura o Pytest, definindo onde encontrar os testes (`testpaths`), ajustando o `pythonpath` para que os imports funcionem, e definindo opções padrão para a execução, como a medição de cobertura de código.

---

## 4. Análise de Governança (APES-GOV Audit)

*   **Prioridades Pareto Atendidas:** Esta documentação focou nos componentes que entregam a maior parte do valor e da complexidade do sistema: o orquestrador `app.py`, a camada de dados (`*_manager.py`), a garantia de qualidade (`tests/`), e os arquivos de configuração.

*   **Ameaças SWOT Mitigadas:** Uma documentação clara mitiga ameaças como a dificuldade de manutenção, a dependência de poucos desenvolvedores e a introdução de bugs, facilitando a colaboração e a evolução do projeto.

*   **Limitações Declaradas:** Esta documentação é focada no backend. Áreas como diagramas de arquitetura visual, documentação do código frontend (JavaScript, CSS) e detalhes de bibliotecas de terceiros não foram cobertas.

*   **Decisões Chave de Design:** A análise evidencia pontos fortes do projeto:
    *   **Alta Coesão e Baixo Acoplamento:** A separação clara de responsabilidades demonstra um design modular e robusto.
    *   **Conteúdo Desacoplado:** Armazenar o conteúdo em arquivos JSON externos torna o projeto flexível e fácil de atualizar.
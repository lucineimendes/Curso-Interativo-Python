# -*- coding: utf-8 -*-
"""Ponto de entrada e orquestrador principal da aplicação Flask.

Este módulo inicializa a aplicação Flask e define todas as rotas, tanto para
a renderização de páginas HTML quanto para os endpoints da API JSON. Ele
utiliza os módulos de gerenciamento (course_manager, lesson_manager, etc.)
para acessar e manipular os dados do curso.
"""
import logging
from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS

from .course_manager import CourseManager
from .lesson_manager import LessonManager
from .exercise_manager import ExerciseManager
from . import code_executor

# Configuração do logging para registrar eventos da aplicação.
# Em um ambiente de produção, isso seria configurado de forma mais robusta.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas, permitindo requisições de outros domínios.

# --- Inicialização dos Módulos de Gerenciamento ---
# Instâncias únicas dos managers para serem usadas em toda a aplicação.
course_mgr = CourseManager()
lesson_mgr = LessonManager()
exercise_mgr = ExerciseManager()


# --- Funções Auxiliares ---

def _get_course_or_404(course_id):
    """Busca um curso pelo ID ou aborta com erro 404 se não for encontrado.

    Args:
        course_id (str): O ID do curso a ser buscado.

    Returns:
        dict: O dicionário de dados do curso encontrado.

    Raises:
        HTTPException: Aborta a requisição com um status 404 se o curso não for encontrado.
    """
    course = course_mgr.get_course_by_id(course_id)
    if not course:
        logger.warning(f"Tentativa de acesso a curso inexistente: '{course_id}'.")
        abort(404, description=f"O curso '{course_id}' não foi encontrado.")
    return course


def _get_all_items_for_course(course, file_key, manager, load_method_name, item_type_name):
    """Carrega todos os itens (lições/exercícios) de um arquivo de curso.

    Função genérica para buscar um arquivo de dados (ex: 'lessons.json')
    dentro do objeto de um curso e usar o manager apropriado para carregá-lo.

    Args:
        course (dict): O dicionário do curso.
        file_key (str): A chave no dicionário do curso que contém o caminho do arquivo (ex: "lessons_file").
        manager (object): A instância do manager a ser usada (ex: lesson_mgr).
        load_method_name (str): O nome do método no manager para carregar o arquivo (ex: "load_lessons_from_file").
        item_type_name (str): O nome do tipo de item (ex: "lições") para mensagens de erro.

    Returns:
        list: Uma lista de itens carregados (lições ou exercícios).
    """
    file_path = course.get(file_key)
    if not file_path:
        logger.error(f"'{file_key}' não definido para o curso '{course.get('id')}'.")
        abort(500, description=f"Arquivo de {item_type_name} não configurado para este curso.")

    load_method = getattr(manager, load_method_name)
    return load_method(file_path)


def _calculate_and_set_course_durations(courses_data):
    """Calcula e define uma estimativa de duração para uma lista de cursos.

    A lógica de cálculo considera o tempo estimado das lições, a quantidade de
    exercícios e o nível de dificuldade do curso para gerar uma estimativa
    de carga horária mais realista.

    Args:
        courses_data (list or dict): Uma lista de dicionários de cursos ou um único dicionário de curso.

    Returns:
        list or dict: Uma cópia dos dados do curso com a chave 'duration' preenchida.
    """
    is_single_item = isinstance(courses_data, dict)
    courses_list = [dict(courses_data)] if is_single_item else [dict(c) for c in courses_data]

    for course in courses_list:
        try:
            # Fatores de cálculo baseados no nível do curso para uma estimativa mais realista.
            level = course.get('level', 'Básico').lower()
            if level == 'básico':
                practice_factor = 2.5
                time_per_exercise = 15
            elif level == 'intermediário':
                practice_factor = 2.8
                time_per_exercise = 20
            elif level == 'avançado':
                practice_factor = 3.0
                time_per_exercise = 25
            else: # Inclui 'especialização' e outros casos
                practice_factor = 3.5
                time_per_exercise = 30

            # Calcula o tempo total das lições
            lessons = _get_all_items_for_course(course, "lessons_file", lesson_mgr, "load_lessons_from_file", "lições")
            total_lesson_minutes = sum(l.get('estimated_time_minutes', 0) for l in lessons if isinstance(l.get('estimated_time_minutes'), (int, float)))

            # Calcula o tempo total dos exercícios
            exercises = _get_all_items_for_course(course, "exercises_file", exercise_mgr, "load_exercises_from_file", "exercícios")
            total_exercise_minutes = 0
            if exercises:
                for exercise in exercises:
                    # Fator de tempo baseado no nível de Bloom do exercício
                    bloom_level = exercise.get('bloom_level', 'apply')
                    bloom_multiplier = {
                        'remember': 0.5, 'understand': 0.7, 'apply': 1.0,
                        'analyze': 1.5, 'evaluate': 2.0, 'create': 4.0
                    }.get(bloom_level, 1.0)
                    total_exercise_minutes += time_per_exercise * bloom_multiplier

            # Cálculo final da carga horária total em minutos
            total_minutes = (total_lesson_minutes * practice_factor) + total_exercise_minutes

            if total_minutes > 0:
                hours = round(total_minutes / 60)
                course['duration'] = f"Aprox. {hours} horas" if hours > 1 else f"{int(total_minutes)} min"
            else:
                course['duration'] = course.get('duration', "N/D")
        except Exception as e:
            logger.error(f"Erro ao calcular duração para o curso {course.get('id')}: {e}")
            course['duration'] = course.get('duration', "Erro no cálculo")

    return courses_list[0] if is_single_item else courses_list


# --- Rotas de Apresentação (HTML) ---

@app.route('/')
def home():
    """Renderiza a página inicial (index).

    Busca todos os cursos, calcula suas durações e os exibe na página principal.
    """
    logger.info("Rota raiz '/' acessada.")
    all_courses = course_mgr.get_courses()
    courses_with_duration = _calculate_and_set_course_durations(all_courses)
    return render_template('index.html', courses=courses_with_duration, title="Bem-vindo")


@app.route('/courses', methods=['GET'])
def list_courses_page():
    """Renderiza a página de listagem de todos os cursos disponíveis."""
    logger.info("GET /courses - Solicitando página de listagem de cursos.")
    courses = course_mgr.get_courses()
    courses_with_duration = _calculate_and_set_course_durations(courses)
    return render_template('course_list.html', courses=courses_with_duration, title="Cursos Disponíveis")


@app.route('/courses/<string:course_id>', methods=['GET'])
def course_detail_page(course_id):
    """Renderiza a página de detalhes de um curso específico.

    Args:
        course_id (str): O ID do curso a ser exibido.
    """
    logger.info(f"GET /courses/{course_id} - Página de detalhes do curso.")
    course = _get_course_or_404(course_id)
    course_with_duration = _calculate_and_set_course_durations(course)
    lessons = _get_all_items_for_course(course, "lessons_file", lesson_mgr, "load_lessons_from_file", "lições")
    return render_template('course_detail.html', course=course_with_duration, lessons=lessons, title=course.get('name', 'Detalhes do Curso'))


@app.route('/courses/<string:course_id>/lessons/<string:lesson_id_str>', methods=['GET'])
def lesson_detail_page(course_id, lesson_id_str):
    """Renderiza a página de uma lição específica, incluindo seus exercícios.

    Args:
        course_id (str): O ID do curso ao qual a lição pertence.
        lesson_id_str (str): O ID da lição a ser exibida.
    """
    logger.info(f"GET /courses/{course_id}/lessons/{lesson_id_str} - Página da lição.")
    current_course = _get_course_or_404(course_id)
    all_lessons = _get_all_items_for_course(current_course, "lessons_file", lesson_mgr, "load_lessons_from_file", "lições")

    current_lesson = next((lesson for lesson in all_lessons if str(lesson.get('id')) == lesson_id_str), None)
    if not current_lesson:
        abort(404, description=f"A lição '{lesson_id_str}' não foi encontrada neste curso.")

    # Busca e agrupa os exercícios associados a esta lição
    all_exercises = _get_all_items_for_course(current_course, "exercises_file", exercise_mgr, "load_exercises_from_file", "exercícios")
    exercises_for_lesson = [ex for ex in all_exercises if str(ex.get('lesson_id')) == str(current_lesson.get('id'))]

    # Encontra a próxima lição para navegação
    current_lesson_index = all_lessons.index(current_lesson)
    next_lesson_obj = all_lessons[current_lesson_index + 1] if current_lesson_index < len(all_lessons) - 1 else None

    return render_template('lesson_detail.html',
                           course=current_course,
                           lesson=current_lesson,
                           exercises=exercises_for_lesson,
                           next_lesson=next_lesson_obj,
                           title=current_lesson.get('title', 'Lição'))


@app.route('/courses/<string:course_id>/exercise/<string:exercise_id_str>/editor', methods=['GET'])
def exercise_code_editor_page(course_id, exercise_id_str):
    """Renderiza a página do editor de código para um exercício específico.

    Args:
        course_id (str): O ID do curso ao qual o exercício pertence.
        exercise_id_str (str): O ID do exercício a ser resolvido.
    """
    logger.info(f"GET /courses/{course_id}/exercise/{exercise_id_str}/editor - Editor de código.")
    current_course = _get_course_or_404(course_id)
    all_exercises = _get_all_items_for_course(current_course, "exercises_file", exercise_mgr, "load_exercises_from_file", "exercícios")

    current_exercise = next((ex for ex in all_exercises if str(ex.get('id')) == exercise_id_str), None)
    if not current_exercise:
        abort(404, description=f"O exercício '{exercise_id_str}' não foi encontrado neste curso.")

    # Lógica para encontrar o próximo exercício na mesma lição
    lesson_id = current_exercise.get('lesson_id')
    next_exercise = None
    if lesson_id:
        exercises_in_lesson = [ex for ex in all_exercises if str(ex.get('lesson_id')) == str(lesson_id)]
        current_exercise_index = exercises_in_lesson.index(current_exercise)
        if current_exercise_index < len(exercises_in_lesson) - 1:
            next_exercise = exercises_in_lesson[current_exercise_index + 1]

    return render_template('code_editor.html',
                           course=current_course,
                           exercise=current_exercise,
                           lesson_id=lesson_id,
                           next_exercise=next_exercise,
                           title=f"Editor: {current_exercise.get('title', 'Exercício')}")


@app.route('/editor', methods=['GET'])
def generic_code_editor_page():
    """Renderiza um editor de código genérico, sem contexto de curso ou exercício."""
    logger.info("GET /editor - Acessando editor de código genérico.")
    return render_template('code_editor.html', course=None, exercise=None, title="Editor de Código")


# --- Rotas de API (JSON) ---

@app.route('/api/courses/<string:course_id>/lessons', methods=['GET'])
def api_get_lessons_for_course(course_id):
    """Endpoint da API para obter todas as lições de um curso.

    Args:
        course_id (str): O ID do curso.

    Returns:
        Response: Uma resposta JSON com a lista de lições ou um erro.
    """
    logger.info(f"API GET /courses/{course_id}/lessons")
    course = _get_course_or_404(course_id)
    lessons = _get_all_items_for_course(course, "lessons_file", lesson_mgr, "load_lessons_from_file", "lições")
    return jsonify(lessons)


@app.route('/api/courses/<string:course_id>/exercises', methods=['GET'])
def api_get_exercises_for_course(course_id):
    """Endpoint da API para obter todos os exercícios de um curso.

    Args:
        course_id (str): O ID do curso.

    Returns:
        Response: Uma resposta JSON com a lista de exercícios ou um erro.
    """
    logger.info(f"API GET /courses/{course_id}/exercises")
    course = _get_course_or_404(course_id)
    exercises = _get_all_items_for_course(course, "exercises_file", exercise_mgr, "load_exercises_from_file", "exercícios")
    return jsonify(exercises)


@app.route('/api/execute-code', methods=['POST'])
def api_execute_code():
    """Endpoint da API para execução de código arbitrário.

    Recebe um JSON com a chave 'code' e o executa, retornando
    o resultado da execução.

    Returns:
        Response: JSON com 'success', 'output' (stdout) e 'details' (stderr).
    """
    logger.info("POST /api/execute-code")
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({"success": False, "output": "", "details": "Payload inválido ou campo 'code' ausente."}), 400

    user_code = data['code']
    try:
        exec_result = code_executor.execute_code(user_code)
        success = exec_result["returncode"] == 0
        return jsonify({
            "success": success,
            "output": exec_result["stdout"],
            "details": exec_result["stderr"] or ("Erro de sintaxe." if not success else "")
        })
    except Exception as e:
        logger.error(f"POST /api/execute-code - Erro inesperado: {e}", exc_info=True)
        return jsonify({"success": False, "output": "", "details": f"Erro interno do servidor: {str(e)}"}), 500


def _check_exercise_logic(course_id, exercise_id_str, user_code):
    """Encapsula a lógica de verificação de um exercício.

    Executa o código do usuário e, se bem-sucedido, executa o código de teste
    associado ao exercício para validar a solução.

    Args:
        course_id (str): ID do curso.
        exercise_id_str (str): ID do exercício.
        user_code (str): Código enviado pelo usuário.

    Returns:
        dict: Um dicionário com o resultado da verificação e o status_code HTTP.
    """
    course = _get_course_or_404(course_id)
    all_exercises = _get_all_items_for_course(course, "exercises_file", exercise_mgr, "load_exercises_from_file", "exercícios")
    exercise = next((ex for ex in all_exercises if str(ex.get('id')) == exercise_id_str), None)

    if not exercise:
        return {"success": False, "output": "", "details": f"Exercício '{exercise_id_str}' não encontrado.", "status_code": 404}

    test_code = exercise.get("test_code", "")

    try:
        user_exec_result = code_executor.execute_code(user_code)
        if user_exec_result["returncode"] != 0:
            return {"success": False, "output": user_exec_result["stdout"], "details": user_exec_result["stderr"], "status_code": 200}

        if not test_code:
            return {"success": True, "output": user_exec_result["stdout"], "details": "Código executado (nenhum teste automático).", "status_code": 200}

        # Executa o código de teste com a saída do usuário como contexto
        test_globals = {'output': user_exec_result["stdout"]}
        test_exec_result = code_executor.execute_code(test_code, execution_globals=test_globals)
        success = test_exec_result["returncode"] == 0
        details = test_exec_result["stderr"] or test_exec_result["stdout"]

        return {"success": success, "output": user_exec_result["stdout"], "details": details, "status_code": 200}

    except Exception as e:
        logger.error(f"Logic: Erro inesperado ao verificar exercício: {e}", exc_info=True)
        return {"success": False, "output": "", "details": f"Erro interno do servidor: {str(e)}", "status_code": 500}


@app.route('/api/check-exercise', methods=['POST'])
def api_check_exercise():
    """Endpoint da API para verificar a solução de um exercício.

    Recebe 'course_id', 'exercise_id' e 'code' e usa a lógica de
    verificação para retornar se a solução está correta.
    """
    logger.info("POST /api/check-exercise")
    data = request.get_json()
    if not data or not all(k in data for k in ['course_id', 'exercise_id', 'code']):
        return jsonify({"success": False, "details": "Payload inválido."}), 400

    result = _check_exercise_logic(
        course_id=data['course_id'],
        exercise_id_str=str(data['exercise_id']),
        user_code=data['code']
    )
    status_code = result.pop("status_code")
    return jsonify(result), status_code


# --- Tratadores de Erro Globais ---

@app.errorhandler(404)
def page_not_found(e):
    """Renderiza a página de erro 404 ou retorna JSON se a API for chamada.

    Args:
        e (HTTPException): A exceção de erro.
    """
    logger.warning(f"Erro 404 - Página não encontrada: {request.path} (Descrição: {e.description})")
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify(error=str(e.description or "Recurso não encontrado")), 404
    return render_template('404.html', title="Página Não Encontrada", error_message=e.description), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Renderiza a página de erro 500 ou retorna JSON se a API for chamada.

    Args:
        e (HTTPException): A exceção de erro.
    """
    logger.error(f"Erro 500 - Erro interno: {request.path}", exc_info=True)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify(error=str(e.description or "Erro interno do servidor")), 500
    return render_template('500.html', title="Erro Interno", error_message=e.description), 500
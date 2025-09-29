import json
import logging
import os
from pathlib import Path

# Import CourseManager para obter o caminho do arquivo de exercícios
# Isso cria uma dependência, mas alinha com a lógica de app.py
from .course_manager import CourseManager 

logger = logging.getLogger(__name__)

# Detecta se estamos em ambiente de teste
def _is_testing():
    return 'pytest' in os.environ.get('_', '') or 'PYTEST_CURRENT_TEST' in os.environ
# Assume que este manager está em Curso-Interartivo-Python/projects/
# DATA_DIR apontará para Curso-Interartivo-Python/projects/data/
DATA_DIR = Path(__file__).resolve().parent / 'data'

class ExerciseManager:
    def __init__(self):
        """
        Inicializa o ExerciseManager.
        Não carrega mais todos os exercícios na inicialização.
        """
        pass # Nenhuma ação de carregamento na inicialização

    def load_exercises_from_file(self, exercises_file_path_relative):
        """
        Carrega exercícios de um arquivo JSON específico, relativo à pasta 'data' do projeto.
        Ex: exercises_file_path_relative pode ser "basic/exercises.json"
        Retorna uma lista de exercícios ou uma lista vazia em caso de erro ou arquivo não encontrado.
        """
        if not exercises_file_path_relative:
            logger.warning("load_exercises_from_file_called_with_empty_path")
            return []

        # Constrói o caminho completo para o arquivo de exercícios
        full_file_path = DATA_DIR / exercises_file_path_relative
        
        logger.debug(f"Tentando carregar exercícios de: {full_file_path}")
        
        if full_file_path.exists() and full_file_path.is_file():
            try:
                with open(full_file_path, 'r', encoding='utf-8') as f:
                    exercises_data = json.load(f)
                    
                    # Valida se os dados são uma lista
                    if not isinstance(exercises_data, list):
                        logger.error(f"Formato inválido em {full_file_path}. Esperava uma lista, obteve {type(exercises_data)}. Retornando lista vazia.")
                        return []
                    
                    logger.info(f"Sucesso ao carregar {len(exercises_data)} exercícios de {full_file_path}")
                    return exercises_data
            except json.JSONDecodeError as e:
                logger.error(f"Erro de decodificação JSON ao carregar exercícios de {full_file_path}: {e}")
            except Exception as e:
                logger.error(f"Erro inesperado ao carregar exercícios de {full_file_path}: {e}")
        else:
            if not _is_testing():
                logger.warning(f"Arquivo de exercícios não encontrado ou não é um arquivo: {full_file_path}")
            else:
                logger.debug(f"Arquivo de exercícios não encontrado (teste): {full_file_path}")
            
        return [] # Retorna lista vazia se o arquivo não existe ou em caso de erro

# Função para ser importada pelos testes e outras partes da aplicação
def get_exercise_by_id(exercise_id: str, course_id: str):
    """
    Busca um exercício pelo seu ID dentro de um curso específico.

    Args:
        exercise_id (str): O ID do exercício a ser encontrado.
        course_id (str): O ID do curso ao qual o exercício pertence.

    Returns:
        dict: O dicionário do exercício se encontrado, caso contrário None.
    """
    if not course_id:
        logger.warning("get_exercise_by_id chamado sem course_id.")
        return None

    # Lógica corrigida: Usa o CourseManager para encontrar o caminho do arquivo de exercícios
    # em vez de adivinhar o caminho a partir do course_id.
    try:
        # Cria uma instância local do CourseManager para obter os detalhes do curso.
        course_mgr_instance = CourseManager()
        course = course_mgr_instance.get_course_by_id(course_id)
        if not course:
            logger.warning(f"Curso com ID '{course_id}' não encontrado ao buscar o exercício '{exercise_id}'.")
            return None

        exercises_file_relative_path = course.get("exercises_file")
        if not exercises_file_relative_path:
            logger.warning(f"Arquivo de exercícios não definido para o curso '{course_id}'.")
            return None

    except Exception as e:
        logger.error(f"Erro ao tentar obter informações do curso para buscar exercício: {e}")
        return None

    mgr = ExerciseManager() # Cria uma instância para usar o método de carregamento
    all_exercises_for_course = mgr.load_exercises_from_file(exercises_file_relative_path)

    for exercise in all_exercises_for_course:
        if str(exercise.get("id")) == str(exercise_id):
            return exercise
    logger.warning(f"Exercício com ID '{exercise_id}' não encontrado no curso '{course_id}'.")
    return None

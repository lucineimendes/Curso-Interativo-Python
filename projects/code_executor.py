# -*- coding: utf-8 -*-
import sys
import io
import logging
from contextlib import redirect_stdout, redirect_stderr

logger = logging.getLogger(__name__)

def execute_code(code_string, execution_globals=None):
    """
    Executa uma string de código Python em um ambiente controlado.

    Args:
        code_string (str): O código Python a ser executado.
        execution_globals (dict, optional): Um dicionário para usar como o escopo global
                                            para a execução. Defaults to None, que cria
                                            um novo dicionário vazio.
    Returns:
        dict: Um dicionário contendo 'returncode', 'stdout', 'stderr', e 'error_type'.
    """
    if execution_globals is None:
        execution_globals = {}
    # Garante que __name__ está presente, se não for passado
    execution_globals.setdefault('__name__', '__executor__')

    try:
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exec(code_string, execution_globals)
        stdout = stdout_buffer.getvalue()
        stderr = stderr_buffer.getvalue()
        return {"returncode": 0, "stdout": stdout, "stderr": stderr, "error_type": None}
    except Exception as e:
        error_type_name = type(e).__name__
        return {"returncode": 1, "stdout": "", "stderr": f"{error_type_name}: {str(e)}", "error_type": error_type_name}

def execute_test(test_code, namespace=None):
    """
    Executa código de teste em um ambiente controlado.
    
    Args:
        test_code (str): Código de teste para executar
        namespace (dict): Namespace opcional com variáveis predefinidas
        
    Returns:
        dict: Resultado da execução dos testes
    """
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    
    if namespace is None:
        namespace = {}
    
    # Adicionar builtins necessários
    namespace.update({
        '__builtins__': __builtins__,
        '__name__': '__main__',
        '__doc__': None,
        '__package__': None
    })
    
    try:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exec(test_code, namespace)

        return {
            "returncode": 0,
            "stdout": stdout_buffer.getvalue(),
            "stderr": ""
        }

    except AssertionError as e:
        return {
            "returncode": 1, # Indica falha
            "stdout": stdout_buffer.getvalue(),
            "stderr": f"Teste falhou: {str(e)}"
        }

    except Exception as e:
        logger.error(f"Erro ao executar teste: {e}")
        return {
            "returncode": 1, # Indica falha
            "stdout": stdout_buffer.getvalue(),
            "stderr": f"Erro ao executar teste: {str(e)}"
        }
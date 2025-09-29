import subprocess
import webbrowser
import os
import sys

# Configurar codificação UTF-8 para o ambiente
os.environ['PYTHONIOENCODING'] = 'utf-8'

def main():
    """
    Runs pytest with coverage and opens the HTML report.
    """
    # A codificação da saída padrão já é tratada ao capturar a saída do subprocesso.

    print("Gerando relatório de cobertura de testes...")

    command = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=projects",
        "--cov-report=html",
        "--basetemp=.pytest_temp",
        "-p",
        "no:faulthandler"
    ]

    # Executa o comando sem checar o exit code, para que possamos sempre ver a saída
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,  # Captura a saída como texto
        encoding='utf-8', # Usa UTF-8 para decodificar
        errors='replace' # Lida com erros de decodificação
    )

    print("--- SAIDA PADRAO (STDOUT) ---")
    if result.stdout:
        # Filtrar caracteres problemáticos
        stdout_clean = result.stdout.encode('ascii', errors='ignore').decode('ascii')
        print(stdout_clean)
    print("--- SAIDA DE ERRO (STDERR) ---")
    if result.stderr:
        # Filtrar caracteres problemáticos
        stderr_clean = result.stderr.encode('ascii', errors='ignore').decode('ascii')
        print(stderr_clean)

    if result.returncode == 0 or result.returncode == 5: # Pytest retorna 5 se nenhum teste for encontrado
        print("\nScript de cobertura executado.")
        report_path = os.path.abspath(os.path.join("htmlcov", "index.html"))
        if os.path.exists(report_path):
            print(f"Abrindo relatório em: {report_path}")
            webbrowser.open(f"file://{report_path}")
        else:
            print("Arquivo do relatório HTML não encontrado. Verifique a saída para erros.")
    else:
        print(f"\nPytest finalizou com erro (código: {result.returncode}). Verifique a saída de erro acima.")

if __name__ == "__main__":
    main()

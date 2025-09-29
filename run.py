import logging
import os
# Este script é o ponto de entrada para iniciar a aplicação.
# Execute-o a partir da raiz do projeto com: python run.py
from projects.app import app, logger as app_logger # Importa a instância do app e seu logger

if __name__ == '__main__':
    # Você pode configurar o nível de log aqui se desejar,
    # ou confiar na configuração dentro de projects/app.py
    # Exemplo: app_logger.setLevel(logging.DEBUG)
    host = '0.0.0.0'
    port = int(os.environ.get('PORT',5000))
    
    app_logger.info("Iniciando servidor de desenvolvimento Flask a partir de run.py.")
    print("\n" + "="*80)
    print("Servidor Flask pronto para decolar!")
    print(f"   Acesse a aplicação em seu navegador nos seguintes endereços:")
    print(f"   - Acesso Local: http://127.0.0.1:{port}")
    print(f"   - Acesso na Rede: Use o IP da sua máquina (ex: http://192.168.1.X:{port})")
    print("   (Pressione CTRL+C para parar o servidor)")
    print("="*80 + "\n")
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host=host, port=port)

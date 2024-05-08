import sys

from loguru import logger

from src.main.python.server import Server

if __name__ == "__main__":
    # Verifica si se proporcionan los argumentos host y port
    logger.info(f"Server initialized with host")
    if len(sys.argv) != 3:
        print("Uso: python run_server.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]  # Obtén el host del primer argumento
    port = int(sys.argv[2])  # Obtén el puerto del segundo argumento (convertido a entero)

    # Crea una instancia del servidor con los valores proporcionados
    server = Server(host, port)
    server.start()

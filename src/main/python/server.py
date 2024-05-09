import json
import os
import socket
import threading
import time
from configparser import ConfigParser
from typing import Callable
import concurrent.futures

from datetime import datetime, timedelta

import OpenSSL
import select
from OpenSSL import SSL
from loguru import logger
import schedule
import traceback

from src.main.python.certificate_utils import generate_key_pair, generate_certificate, \
    save_key_and_certificate_with_alias
from src.main.python.logger import load_logger
from src.main.python.json_utils.json_response import JSONResponse
from src.main.python.manager.message_manager import MessageManager
from src.main.python.manager.password_manager import PasswordManager
from src.main.python.models import ClientPetition
from src.main.python.ssl_context_utils import jks_file_to_context
from src.main.python.statistics import get_report

# CONSTANTS
current_directory = os.path.dirname(os.path.abspath(__file__))
configuration = ConfigParser()
configuration.read("configuration.ini")
keystores_path = os.path.join(current_directory, configuration.get("KEYSTORE", "path"))
server_alias = configuration.get("SERVER", "alias")
common_name = configuration.get("SERVER", "common_name")
password_path = os.path.join(current_directory, configuration.get("FILE_MANAGER", "password_path"))
message_path = os.path.join(current_directory, configuration.get("FILE_MANAGER", "message_path"))


class Server:
    def __init__(self, host: str, port: int, is_test: bool = False) -> None:
        """
        Initialize Server object.

        Parameters:
        - host (str): Host IP address.
        - port (int): Port number.
        - is_test (bool): Flag to indicate if in test mode.

        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.password_manager = PasswordManager(password_path)
        self.message_manager = MessageManager(message_path)
        self.is_test = is_test
        self.running = False
        try:
            ClientPetition.drop_old_table()
        except Exception as e:
            logger.error(f"Error dropping table: {e}")
        ClientPetition.create_new_table()
        logger.info(f"Server initialized with host: {host} and port: {port}")

    def load_certificate(self) -> SSL.Context:
        """
        Load SSL certificate and private key for the server.
        """
        if not os.path.exists(keystores_path):
            logger.info("Certificate or key not found in keystore. Generating new ones...")
            server_key = generate_key_pair()
            server_cert = generate_certificate(server_key, common_name)
            save_key_and_certificate_with_alias(server_key, server_cert, server_alias)
        context = jks_file_to_context(server_alias)
        return context

    def start(self) -> None:
        """
        Start the server.

        This method initializes the SSL context, binds the server socket to the specified host and port,
        and starts listening for incoming connections. It launches a separate thread to handle each client connection.
        """
        threading.Thread(target=self.print_scheduler).start()
        schedule.every(20).seconds.do(lambda: self.execute_non_blocking(get_report()))
        
        load_logger()
        
        context = self.load_certificate()
        self.server_socket = SSL.Connection(context, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.server_socket.bind((self.host, int(self.port)))
        self.server_socket.listen(5)
        self.running = True
        logger.info(f"Server listening on {self.host}:{self.port}")
        while self.running:
            try:
                logger.info("Waiting for connections...")
                client_socket, _ = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            except Exception as e:
                logger.error(f"Error accepting connection: {e}")
                break

    def print_scheduler(self) -> None:
        """
        Print "hello" every second.
        """
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    def execute_non_blocking(self, func: Callable) -> None:
        """
        Execute a function in a separate thread.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(func)

    def handle_client(self, client_socket: socket) -> None:
        try:
            logger.info(f"Connection established with {client_socket.getpeername()}")
            while True:
                if client_socket.fileno() == -1:  # Check if the socket is still connected
                    break
                active, _, _ = select.select([client_socket], [], [], 1)
                if not active:
                    continue
                data = client_socket.recv(9999)
                if not data:
                    logger.info(f"Connection closed by the client.")
                    break
                received_message = data.decode()
                client_id = {data['clientId'] for data in json.loads(received_message)}

                if len(client_id) != 1:
                    logger.error(f"Invalid client_id: {client_id}")
                    raise Exception("Invalid client_id")

                client_id = client_id.pop()
                self.check_client(client_id)

                logger.info(f"Received message: {received_message}")
                ClientPetition.from_jsons(received_message)
                message = JSONResponse("SUCCESS", "Message received successfully.")
                client_socket.sendall(message.to_json().encode("utf-8"))
                time.sleep(1)
        except OpenSSL.SSL.SysCallError as e:
            logger.error(f"SSL error: {e}")
            message = JSONResponse("ERROR", "SSL error: {e}")
            client_socket.sendall(message.to_json().encode("utf-8"))
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(traceback.format_exc())
            message = JSONResponse("ERROR", f"Error: {e}")
            client_socket.sendall(message.to_json().encode("utf-8"))
            time.sleep(1)
        finally:
            client_socket.close()

    def check_client(self, client_id):
        if ClientPetition.select().where(ClientPetition.client_id == client_id).count() > 3:
            # Obtener las últimas tres solicitudes del cliente, ordenadas por fecha de orden descendente
            data = ClientPetition.select().where(ClientPetition.client_id == client_id).order_by(
                ClientPetition.order_date.desc()).limit(3)

            # Convertir las cadenas de fecha en objetos datetime
            order_dates = [item.order_date for item in data]

            # Ordenar las fechas de manera ascendente para que la primera solicitud sea la más antigua
            order_dates.sort()

            # Verificar si han pasado menos de cuatro horas desde la primera solicitud
            if order_dates[-1] - order_dates[0] < timedelta(hours=4):
                logger.error(f"Client {client_id} has made too many requests")
                raise Exception("Too many requests")

    def stop(self) -> None:
        """
        Stop the server.
        """
        self.running = False
        self.server_socket.close()

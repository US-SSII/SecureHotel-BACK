import os
import socket
import threading
import time
from configparser import ConfigParser

import OpenSSL
import select
from OpenSSL import SSL
from loguru import logger

from src.main.python.certificate_utils import generate_key_pair, generate_certificate, \
    save_key_and_certificate_with_alias
from src.main.python.json_utils.json_message import JSONMessage
from src.main.python.manager.message_manager import MessageManager
from src.main.python.manager.password_manager import PasswordManager
from src.main.python.ssl_context_utils import jks_file_to_context

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

    def handle_client(self, client_socket: socket) -> None:
        """
        Handle client connections.

        Args:
            client_socket (socket): Client socket object.
        """
        try:
            logger.info(f"Connection established with {client_socket.getpeername()}")
            while True:
                active, _, _ = select.select([client_socket], [], [], 1)
                if not active:
                    continue
                data = client_socket.recv(1024)
                if not data:
                    break
                received_message = data.decode()
                message = self.actions(received_message)
                self.send_message_in_chunks(client_socket, message)
        except OpenSSL.SSL.ZeroReturnError:
            logger.info(f"Connection closed by the client.")
        except Exception as e:
            print(e.with_traceback())
            logger.error(f"Error: {e}")
        finally:
            client_socket.close()

    def actions(self, received_message: str) -> str:
        """
        Perform actions based on received messages.

        Args:
            received_message (str): Received message.

        Returns:
            str: Response message.
        """
        received_message = JSONMessage.from_json(received_message)
        action = received_message.action
        if action == "message":
            logger.info(f"Login request received from {received_message.username}")
            if self.password_manager.check_password(received_message.username, received_message.password):
                logger.info(f"Login request successful")
                logger.info(f"Message received from {received_message.username}: {received_message.message}")
                self.message_manager.save_message(received_message.username, received_message.message)
                return "Message received"
            else:
                logger.error(f"Invalid username or password")
                return "Invalid username or password"
        elif action == "register":
            self.password_manager.save_password(received_message.username, received_message.password)
            logger.info(f"You have been successfully registered")
            return "Register successful"
        return received_message

    def send_message_in_chunks(self, client_socket: socket, message: str) -> None:
        """
        Send message in chunks to the client.

        Args:
            client_socket (socket): Client socket object.
            message (str): Message to send.

        """
        chunk_size = 512
        for i in range(0, len(message), chunk_size):
            chunk = message[i:i + chunk_size]
            client_socket.sendall(chunk.encode("utf-8"))
        time.sleep(0.001)
        client_socket.sendall("END".encode("utf-8"))

    def stop(self) -> None:
        """
        Stop the server.
        """
        self.running = False
        self.server_socket.close()


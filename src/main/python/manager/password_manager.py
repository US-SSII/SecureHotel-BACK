import hmac
import json
from configparser import ConfigParser

from src.main.python.manager.file_manager import FileManager

# CONSTANTS
config = ConfigParser()
config.read("configuration.ini")
token = config.get("HASHING", "key")


class PasswordManager(FileManager):
    """
    A class to manage passwords.

    Attributes:
        file_path (str): The path to the file storing passwords.
    """

    def check_password(self, username: str, password: str) -> bool:
        """
        Checks if the given username and password match the stored ones.

        Args:
            username (str): The username.
            password (str): The password.

        Returns:
            bool: True if the username and password match, False otherwise.
        """
        try:
            passwords = self._load()
        except FileNotFoundError:
            passwords = []
        encrypted = self.encrypt_password(password)
        credentials = {"username": username, "password": encrypted}
        return str(credentials) in passwords

    def save_password(self, username: str, password: str) -> None:
        """
        Saves a username and encrypted password pair to the file.

        Args:
            username (str): The username.
            password (str): The password.
        """
        passwords = self._load()
        encrypted = self.encrypt_password(password)
        credentials = {"username": username, "password": encrypted}
        passwords.append(str(credentials))
        with open(self.file_path, "w") as file:
            json.dump(passwords, file)

    def encrypt_password(self, password: str) -> str:
        """
        Encrypts the given password using HMAC-SHA256 algorithm.

        Args:
            password (str): The password to be encrypted.

        Returns:
            str: The hexadecimal representation of the encrypted password.
        """
        encrypted = hmac.new(token.encode(), password.encode(), digestmod='sha256')
        return encrypted.hexdigest()

    def get_num_passwords(self) -> int:
        """
        Returns the number of passwords stored in the file.

        Returns:
            int: The number of passwords.
        """
        passwords = self._load()
        return len(passwords)

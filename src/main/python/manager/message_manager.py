from configparser import ConfigParser

from src.main.python.manager.file_manager import FileManager

# CONSTANTS
config = ConfigParser()
config.read("configuration.ini")
token = config.get("HASHING", "key")

import json


class MessageManager(FileManager):
    """
    A class to manage messages and usernames.

    Attributes:
        file_path (str): The path to the file storing messages.
    """

    def save_message(self, username: str, message: str) -> None:
        """
        Saves a username and message pair to the file.

        Args:
            username (str): The username.
            message (str): The message.
        """
        messages = self._load()
        message_data = {"username": username, "message": message}
        messages.append(message_data)
        with open(self.file_path, "w") as file:
            json.dump(messages, file)

    def get_num_messages(self) -> int:
        """
        Returns the number of messages stored in the file.

        Returns:
            int: The number of messages.
        """
        messages = self._load()
        return len(messages)

import json


class FileManager:
    """
    A class to manage files.

    Attributes:
        file_path (str): The path to the file storing messages.
    """

    def __init__(self, file_path: str):
        """
        Initializes the FileManager with the path to the file.

        Args:
            file_path (str): The path to the file storing data.
        """
        self.file_path = file_path
        if not self._file_exists():
            self._create_file()

    def _file_exists(self) -> bool:
        """
        Checks if the file exists.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        try:
            with open(self.file_path, "r"):
                pass
            return True
        except FileNotFoundError:
            return False

    def _create_file(self) -> None:
        """
        Creates the file to store messages.
        """
        with open(self.file_path, "w") as file:
            json.dump([], file)

    def _load(self) -> list:
        """
        Load data from the file.

        Returns:
            list: List of dictionaries containing usernames and messages.
        """
        with open(self.file_path, "r") as file:
            return json.load(file)
# json_message.py
import json


class JSONMessage:
    def __init__(self, action: str, username: str, password: str, message: str) -> None:
        """
        Initializes a JSONMessage object.

        Args:
            action (str): The action to be performed.
            username (str): The source account.
            password (str): The receiver account.
            message (str): The amount in the message.
        """
        self.action = action
        if self.action not in ['register', 'message', None]:
            raise ValueError("Invalid action")
        self.username = username
        self.password = password
        self.message = message

    def to_dict(self) -> dict:
        """
        Converts the JSONMessage object to a dictionary.

        Returns:
            dict: The dictionary representation of the JSONMessage.
        """
        return {
            'action': self.action,
            'username': self.username,
            'password': self.password,
            'message': self.message,
        }

    def to_json(self) -> str:
        """
        Converts the JSONMessage object to a JSON-formatted string.

        Returns:
            str: The JSON-formatted string.
        """

        return json.dumps(self.to_dict(), ensure_ascii=False)

    @staticmethod
    def from_json(json_string: str) -> 'JSONMessage':
        """
        Creates a JSONMessage object from a JSON-formatted string.

        Args:
            json_string (str): The JSON-formatted string.

        Returns:
            JSONMessage: The JSONMessage object.
        """
        data = json.loads(json_string)
        return JSONMessage(data['action'], data['username'], data['password'], data['message'])
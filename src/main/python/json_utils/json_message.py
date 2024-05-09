# json_message.py
import json
import datetime



class JSONMessage:
    def __init__(self, data:list) -> None:
        """
        Initializes a JSONMessage object.

        Args:
            action (str): The action to be performed.
            username (str): The source account.
            password (str): The receiver account.
            message (str): The amount in the message.
        """
        self.data = data
        '''
        self.clientId = clientId
        self.nameMaterial = nameMaterial
        self.amount = amount
        self.digitalSignature = digitalSignature
        self.orderDate = self.parse_order_date(orderDateStr)
        '''
        def parse_order_date(self, orderDateStr: str) -> datetime:
            date_format = "%B %d, %Y %I:%M:%S %p"

            try:
                # Intentar parsear la fecha usando el formato especificado
                order_date = datetime.strptime(orderDateStr, date_format)
            except ValueError as e:
                # Manejar errores de formato de fecha
                raise ValueError(f"Error parsing order date: {e}")

            return order_date


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
        return JSONMessage(data)
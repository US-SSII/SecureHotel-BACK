# json_message.py
import json


class JSONMessage:
    def __init__(self, client_id: str, name_material: str, amount: str, digital_signature: str, order_date) -> None:
        """
        Initializes the JSONMessage with the given action, username, password, and message.

        Args:
            action (str): The action to perform.
            username (str): The username.
            password (str): The password.
            message (str): The message.
        """
        self.client_id = client_id
        self.name_material = name_material
        self.amount = amount
        self.digital_signature = digital_signature
        self.order_date = order_date

    def to_dict(self) -> dict:
        """
        Converts the JSONMessage object to a dictionary.

        Returns:
            dict: The dictionary representation of the JSONMessage.
        """
        return {
            'client_id': self.client_id,
            'name_material': self.name_material,
            'amount': self.amount,
            'digital_signature': self.digital_signature,
            'order_date': self.order_date
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
        return JSONMessage(data['client_id'], data['name_material'], data['amount'], data['digital_signature'], data['order_date'])

    @staticmethod
    def from_jsons(json_string: str) -> 'JSONMessage':
        """
        Creates a JSONMessage object from a JSON-formatted string.

        Args:
            json_string (str): The JSON-formatted string.

        Returns:
            JSONMessage: The JSONMessage object.
        """
        data = json.loads(json_string)
        res = []
        print(data)
        for value in data:
            print(value)
            if 'client_id' in value:
                res.append(JSONMessage(value['client_id'], value['name_material'], value['amount'], value['digital_signature'], value['order_date']))
            else:
                res.append(JSONMessage(value['clientId'], value['nameMaterial'], value['amount'], value['digitalSignature'], value['orderDate']))

        return res
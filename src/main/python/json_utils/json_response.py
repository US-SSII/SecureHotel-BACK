# json_response.py
import json

class JSONResponse:
    def __init__(self, status: str) -> None:
        """
        Initializes a JSONResponse object.

        Args:
            status (str): The status for the response.
        """
        self.status = status

    def to_dict(self) -> dict:
        """
        Converts the JSONResponse object to a dictionary.

        Returns:
            dict: The dictionary representation of the JSONResponse.
        """
        return {'status': self.status}

    def to_json(self) -> str:
        """
        Converts the JSONResponse object to a JSON-formatted string.

        Returns:
            str: The JSON-formatted string.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @staticmethod
    def from_json(json_string: str) -> 'JSONResponse':
        """
        Creates a JSONResponse object from a JSON-formatted string.

        Args:
            json_string (str): The JSON-formatted string.

        Returns:
            JSONResponse: The JSONResponse object.
        """
        data = json.loads(json_string)
        return JSONResponse(data['status'])
import json

from PySide6.QtCore import QObject, Signal
from requests import RequestException

from app.apiservices import APIClient


class RequestHandler(QObject):
    finished = Signal(int, str)
    error = Signal(str)

    def __init__(self, api_client: APIClient, method, endpoint, body = None):
        super().__init__()
        self.api_client = api_client
        self.method = method.upper()
        self.endpoint = endpoint
        self.payload = body

    def run(self):
        try:
            response = self.dispatch_request()
            response_text = self.format_response(response)
            self.finished.emit(response.status_code, response_text)
        except RequestException as exc:
            self.error.emit(f"HTTP error: {exc}")
        except Exception as exc:
            self.error.emit(f"Unexpected error: {exc}")

    def dispatch_request(self):
        if self.method == "GET":
            return self.api_client.get(self.endpoint)
        if self.method == "POST":
            return self.api_client.post(self.endpoint, json_body=self.payload)
        raise ValueError(f"Unsupported HTTP method: {self.method}")

    def format_response(self, response):
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return json.dumps(response.json(), indent=2)
        return response.text


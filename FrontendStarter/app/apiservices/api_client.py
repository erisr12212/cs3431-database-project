import requests
from urllib.parse import urljoin
from app.config import API_BASE_URL, DEFAULT_TIMEOUT_SECONDS


class APIClient:
    def __init__(self, base_url = API_BASE_URL, timeout = DEFAULT_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def build_url(self, endpoint) -> str:
        normalized_endpoint = endpoint.lstrip("/")
        return urljoin(self.base_url, normalized_endpoint)

    def get(self, endpoint, params = None, headers = None, timeout = None):
        url = self.build_url(endpoint)
        response = self.session.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout or self.timeout,
        )
        response.raise_for_status()
        return response

    def post(self, endpoint, json_body, headers = None, timeout = None):
        url = self.build_url(endpoint)
        response = self.session.post(
            url,
            json=json_body,
            headers=headers,
            timeout=timeout or self.timeout,
        )
        response.raise_for_status()
        return response

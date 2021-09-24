import json

import requests
from urllib.parse import urljoin

from .auth import XCoverAuth
from .config import XCoverConfig
from .encoder import JSONEncoder
from .exceptions import XCoverHttpException


class XCover:
    def __init__(self, config: XCoverConfig = None):
        self.config = config or XCoverConfig()

    default_headers = {"Content-Type": "application/json"}

    @property
    def session(self):
        return requests.Session()

    def call(
        self,
        method: str,
        url: str,
        payload=None,
        params=None,
        headers: dict = None,
    ) -> requests.Response:
        if headers is None:
            headers = {}
        full_url = urljoin(self.config.base_url, url)
        session = self.session

        request = requests.Request(
            method,
            full_url,
            data=json.dumps(payload, cls=JSONEncoder),
            params=params,
            auth=XCoverAuth(self.config.auth_config),
            headers={**self.default_headers, **headers},
        )
        prepared_request: requests.PreparedRequest = session.prepare_request(request)
        response = session.send(prepared_request, timeout=self.config.http_timeout)

        return response

    @staticmethod
    def handle_response(response: requests.Response):
        if response.status_code == 422:
            raise XCoverHttpException()

        return response.json()

    def create_quote(self, payload, params=None):
        response = self.call(
            "POST", "partners/LLODT/quotes/", payload=payload, params=params
        )

        return self.handle_response(response)

    def get_quote(self, quote_id, params=None):
        response = self.call("GET", f"partners/LLODT/quotes/{quote_id}/", params=params)

        return self.handle_response(response)

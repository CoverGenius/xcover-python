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

    @property
    def partner_code(self):
        return self.config.partner_code

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

    def call_partner_endpoint(self, method, url, payload=None, **kwargs):
        full_url = urljoin(f"partners/{self.partner_code}/", url)
        response = self.call(
            method,
            full_url,
            payload=payload,
            **kwargs
        )

        if response.status_code == 422:
            raise XCoverHttpException()

        return response.json()

    def create_quote(self, payload, **kwargs):
        return self.call_partner_endpoint("POST", "quotes/", payload=payload, **kwargs)

    def get_quote(self, quote_id, **kwargs):
        return self.call_partner_endpoint("GET", f"quotes/{quote_id}/", **kwargs)

    def update_quote(self, quote_id, payload, **kwargs):
        return self.call_partner_endpoint("PATCH", f"quotes/{quote_id}/", payload=payload, **kwargs)


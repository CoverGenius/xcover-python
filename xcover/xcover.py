import requests
from urllib.parse import urljoin

from xcover.auth import XCoverAuth
from xcover.config import XCoverConfig


class XCover:
    def __init__(self, config: XCoverConfig = None):
        self.config = config or XCoverConfig()

    @property
    def session(self):
        return requests.Session()

    def call(
        self, method: str, url: str, payload=None, params=None
    ) -> requests.Response:
        full_url = urljoin(self.config.base_url, url)
        session = self.session
        request = requests.Request(
            method,
            full_url,
            json=payload,
            params=params,
            auth=XCoverAuth(self.config.auth_config),
        )
        prepared_request: requests.PreparedRequest = session.prepare_request(request)
        response = session.send(prepared_request, timeout=self.config.http_timeout)

        return response

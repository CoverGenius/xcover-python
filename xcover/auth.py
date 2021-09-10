import base64
import hmac
from urllib.parse import quote

from requests.auth import AuthBase
from requests import PreparedRequest

from .config import AuthConfig
from .utils import http_date


class XCoverAuth(AuthBase):
    def __init__(self, config: AuthConfig):
        self.config = config

    def __call__(self, request: PreparedRequest):
        api_key = self.config.api_key
        api_secret = self.config.api_secret
        headers = self.config.headers
        algorithm = self.config.algorithm.value
        date = http_date()
        request.headers["date"] = date

        signature = hmac.new(
            key=api_secret.encode("utf-8", "strict"),
            msg=self.config.build_string_to_sign(request).encode("utf-8", "strict"),
            digestmod=self.config.hash_function,
        ).digest()

        signature = quote(base64.b64encode(signature), safe="")
        auth_header = f'Signature keyId="{api_key}",algorithm="{algorithm}",headers="{headers}",signature="{signature}"'

        request.headers["authorization"] = auth_header

        return request

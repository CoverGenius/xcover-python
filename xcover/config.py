import os
from typing import Union, Tuple
import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Callable
from urllib.parse import urlparse, ParseResult

from requests import PreparedRequest

env = os.environ.get


class SignatureAlgorithm(Enum):
    HMAC_SHA256 = "hmac-sha256"
    HMAC_SHA384 = "hmac-sha384"
    HMAC_SHA512 = "hmac-sha512"


@dataclass
class AuthConfig:
    SUPPORTED_ALGORITHMS = {
        SignatureAlgorithm.HMAC_SHA256: hashlib.sha256,
        SignatureAlgorithm.HMAC_SHA384: hashlib.sha384,
        SignatureAlgorithm.HMAC_SHA512: hashlib.sha512,
    }

    api_key: str
    api_secret: str
    algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA512
    headers: str = "date"

    @property
    def headers_as_list(self) -> list:
        return list(filter(len, self.headers.split(" ")))

    def build_string_to_sign(self, request: PreparedRequest) -> str:
        parts = []
        for header in self.headers_as_list:
            # it is lowered already in parse_signature
            if not header:
                continue

            if header == "(request-target)":
                parsed_url: ParseResult = urlparse(request.url)
                parts.append(
                    f"(request-target): {request.method.lower()} {parsed_url.path}"
                )
            else:
                try:
                    parts.append(f"{header}: {request.headers[header]}")
                except KeyError:
                    continue

        return "\n".join(parts)

    @property
    def hash_function(self) -> Callable:
        return self.SUPPORTED_ALGORITHMS.get(self.algorithm)


@dataclass
class XCoverConfig:
    partner_code: str = env("XC_PARTNER_CODE")
    base_url: str = env("XC_BASE_URL")
    http_timeout: Union[float, Tuple[float, float]] = float(env("XC_HTTP_TIMEOUT", 10))
    auth_api_key: str = env("XC_AUTH_API_KEY")
    auth_api_secret: str = env("XC_AUTH_API_SECRET")
    auth_algorithm: str = env("XC_AUTH_ALGORITHM")
    headers: str = env("XC_AUTH_HEADERS", "(request-target) date")

    @property
    def auth_config(self):
        algorithm = (
            SignatureAlgorithm(self.auth_algorithm)
            if self.auth_algorithm
            else SignatureAlgorithm.HMAC_SHA512
        )

        return AuthConfig(
            api_key=self.auth_api_key,
            api_secret=self.auth_api_secret,
            algorithm=algorithm,
            headers=self.headers,
        )

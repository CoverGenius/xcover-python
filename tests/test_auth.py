import requests

from xcover.auth import XCoverAuth
from xcover.config import AuthConfig, SignatureAlgorithm


def test_auth():
    auth = XCoverAuth(AuthConfig(api_key="test_api_key", api_secret="test_api_secret"))
    req = requests.Request("GET", "https://api.xcover.com/get").prepare()
    auth(request=req)
    assert (
        'Signature keyId="test_api_key",algorithm="hmac-sha512",headers="date",signature="'
        in req.headers["Authorization"]
    )


def test_auth_unknown_header():
    auth = XCoverAuth(
        AuthConfig(
            api_key="test_api_key", api_secret="test_api_secret", headers="unknown"
        )
    )
    req = requests.Request("GET", "https://api.xcover.com/get").prepare()
    auth(request=req)
    assert (
        'Signature keyId="test_api_key",algorithm="hmac-sha512",headers="unknown"'
        in req.headers["Authorization"]
    )


def test_date_header_is_not_overridden():
    """
    If `Date` header is already present in the request - it must not be overridden.
    """
    auth = XCoverAuth(
        AuthConfig(
            api_key="test_api_key",
            api_secret="test_api_secret",
            headers="date",
            algorithm=SignatureAlgorithm.HMAC_SHA256,
        )
    )
    req = requests.Request(
        "GET",
        "https://api.xcover.com/get",
        headers={"date": "Sun, 29 Aug 2021 12:07:26 GMT"},
    ).prepare()
    auth(request=req)
    assert (
        req.headers["Authorization"]
        == 'Signature keyId="test_api_key",algorithm="hmac-sha256",headers="date",signature="bfxytCfvFqito27v0%2FKcN1jBJsgnCReimKXdAWwoi0k%3D"'
    )

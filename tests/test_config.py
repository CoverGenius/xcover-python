from xcover import XCover, XCoverConfig


def test_config_is_provided():
    client = XCover(
        XCoverConfig(  # minimal config
            base_url="https://api.xcover.com/xcover",
            partner_code="--PARTNER_CODE--",
            auth_api_key="--API_KEY--",
            auth_api_secret="--API_SECRET--",
        )
    )

    assert client.config.auth_config.headers == "(request-target) date"

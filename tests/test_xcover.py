import pytest

from xcover.xcover import XCover


@pytest.mark.vcr
def test_quote_request():
    client = XCover()
    payload = {
        "request": [
            {
                "policy_type": "event_ticket_protection",
                "policy_type_version": 1,
                "policy_start_date": "2021-12-01T17:59:00.831+00:00",
                "event_datetime": "2021-12-25T21:00:00+00:00",
                "event_name": "Ariana Grande",
                "event_location": "The O2",
                "number_of_tickets": 2,
                "tickets": [
                    {"price": 100},
                ],
                "resale_ticket": False,
                "event_country": "GB",
            }
        ],
        "currency": "GBP",
        "customer_country": "GB",
        "customer_region": "London",
        "customer_language": "en",
    }

    response = client.call(
        method="POST",
        url="partners/LLODT/quotes/",
        payload=payload,
    )

    quote = response.json()

    assert quote["id"] == "DQCRJ-H7XKN-INS"
    assert quote["total_price"] == 2.0
    assert quote["quotes"]["0"]["price"] == 2.0
    assert quote["quotes"]["0"]["tax"]["total_tax"] == 1.11


def test_config_is_provided():
    from xcover import XCoverConfig

    client = XCover(
        XCoverConfig(  # minimal config
            base_url="https://api.xcover.com/xcover",
            partner_code="--PARTNER_CODE--",
            auth_api_key="--API_KEY--",
            auth_api_secret="--API_SECRET--",
        )
    )

    assert client.config.auth_config.headers == "(request-target) date"

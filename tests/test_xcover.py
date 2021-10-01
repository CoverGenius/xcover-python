import pytest

from xcover.exceptions import XCoverHttpException
from xcover.xcover import XCover
from .factories import QuotePackageFactory


@pytest.mark.vcr
def test_call(client: XCover):
    response = client.call(
        method="POST",
        url="partners/LLODT/quotes/",
        payload=QuotePackageFactory(),
    )

    quote = response.json()

    assert quote["id"] == "VGU8R-JVDNL-INS"
    assert quote["total_price"] == 1.99
    assert quote["quotes"]["0"]["price"] == 1.99
    assert quote["quotes"]["0"]["tax"]["total_tax"] == 1.11


@pytest.mark.vcr
def test_custom_header(client: XCover):
    response = client.call(
        method="POST",
        url="partners/LLODT/quotes/",
        payload=QuotePackageFactory(),
        headers={'x-custom-header': 'test'},
    )

    assert response.request.headers['x-custom-header'] == 'test'
    assert response.request.headers['content-type'] == 'application/json'


@pytest.mark.vcr
def test_quote(client: XCover):
    response = client.create_quote(QuotePackageFactory())

    assert isinstance(response, dict)
    assert response["id"] is not None


@pytest.mark.vcr
def test_get_quote(client: XCover):
    response = client.get_quote("WFJUQ-UDYCA-INS")
    assert response["id"] is not None


@pytest.mark.vcr
def test_quote_422(client: XCover):
    with pytest.raises(XCoverHttpException):
        client.create_quote(QuotePackageFactory(policy_version="unknown"))


@pytest.mark.vcr
def test_update_quote(client: XCover):
    quote = client.create_quote(QuotePackageFactory())

    response = client.update_quote(
        quote['id'],
        {
            "currency": 'AUD',
            "request": [
                {
                    "quote_id": quote['quotes']['0']['id'],
                    "tickets": [{"price": 50}],
                }
            ]
        }
    )

    assert isinstance(response, dict)
    assert response["currency"] == "AUD"
    assert quote["total_price"] != response["total_price"]


@pytest.mark.vcr
def test_opt_out(client: XCover):
    quote = client.create_quote(QuotePackageFactory())
    response = client.opt_out(quote['id'])
    assert response is True
    new_quote = client.get_quote(quote['id'])
    assert new_quote["status"] == 'OPTED_OUT'

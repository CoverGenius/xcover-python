import pytest

from xcover.exceptions import XCoverHttpException
from xcover.xcover import XCover

from .factories import (
    InstantBookingFactory,
    PolicyholderFactory,
    QuoteFactory,
    QuotePackageFactory,
)


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
        headers={"x-custom-header": "test"},
    )

    assert response.request.headers["x-custom-header"] == "test"
    assert response.request.headers["content-type"] == "application/json"


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
        quote["id"],
        {
            "currency": "AUD",
            "request": [
                {
                    "quote_id": quote["quotes"]["0"]["id"],
                    "tickets": [{"price": 50}],
                }
            ],
        },
    )

    assert isinstance(response, dict)
    assert response["currency"] == "AUD"
    assert quote["total_price"] != response["total_price"]


@pytest.mark.vcr
def test_opt_out(client: XCover):
    quote = client.create_quote(QuotePackageFactory())
    response = client.opt_out(quote["id"])
    assert response is True
    new_quote = client.get_quote(quote["id"])
    assert new_quote["status"] == "OPTED_OUT"


@pytest.mark.vcr
def test_add_quotes(client: XCover):
    quote = client.create_quote(QuotePackageFactory())
    response = client.add_quotes(
        quote["id"],
        {
            "request": [
                QuoteFactory(),
            ]
        },
    )
    assert isinstance(response, dict)

    new_quote = client.get_quote(quote["id"])
    assert len(new_quote["quotes"]) == 2


@pytest.mark.vcr
def test_delete_quotes(client: XCover):
    quote = client.create_quote(QuotePackageFactory(request=[QuoteFactory(), QuoteFactory()]))
    response = client.delete_quotes(
        quote_id=quote["id"], payload={"quotes": [{"id": quote["quotes"]["1"]["id"]}]}
    )
    assert isinstance(response, dict)
    new_quote = client.get_quote(quote["id"])
    assert len(new_quote["quotes"]) == 1


@pytest.mark.vcr
def test_create_booking(client: XCover):
    quote = client.create_quote(QuotePackageFactory())
    booking = client.create_booking(
        quote_id=quote["id"],
        payload={
            "quotes": [{"id": quote["quotes"]["0"]["id"]}],
            "policyholder": PolicyholderFactory(),
        },
    )
    assert isinstance(booking, dict)
    assert booking["status"] == "CONFIRMED"
    new_quote = client.get_quote(quote["id"])
    assert len(new_quote["quotes"]) == 1
    assert new_quote["status"] == "CONFIRMED"


@pytest.mark.vcr
def test_instant_booking(client: XCover):
    booking = client.instant_booking(InstantBookingFactory())
    assert isinstance(booking, dict)
    assert booking["status"] == "CONFIRMED"
    assert "-INS" in booking["id"]


@pytest.mark.vcr
def test_get_booking(client: XCover):
    booking = client.instant_booking(InstantBookingFactory())
    assert isinstance(booking, dict)
    new_booking = client.get_booking(booking["id"])
    assert new_booking["status"] == "CONFIRMED"
    assert "-INS" in new_booking["id"]


@pytest.mark.vcr
def test_list_bookings(client: XCover):
    bookings = client.list_bookings(params={"limit": 1, "offset": 1})
    assert len(bookings["results"]) == 1
    assert "?limit=1&offset=2" in bookings["next"]


@pytest.mark.vcr
def test_confirm_booking(client: XCover):
    quote = client.create_quote(QuotePackageFactory())
    booking = client.create_booking(
        quote_id=quote["id"],
        payload={
            "quotes": [{"id": quote["quotes"]["0"]["id"]}],
            "policyholder": PolicyholderFactory(),
            "require_payment_confirmation": True,
        },
    )
    assert isinstance(booking, dict)
    assert booking["status"] == "PENDING_PAYMENT"

    confirmed_booking = client.confirm_booking(booking["id"])
    assert confirmed_booking["status"] == "CONFIRMED"


@pytest.mark.vcr
def test_trigger_email(client: XCover):
    booking = client.instant_booking(InstantBookingFactory())
    assert isinstance(booking, dict)
    resp = client.trigger_email(booking["id"])
    assert resp


@pytest.mark.vcr
def test_trigger_email__wrong_payload(client: XCover):
    booking = client.instant_booking(InstantBookingFactory())
    assert isinstance(booking, dict)
    with pytest.raises(XCoverHttpException):
        # Booking is not cancelled
        client.trigger_email(
            booking["id"],
            {
                "event": "BOOKING_CANCELLED",
            },
        )


@pytest.mark.vcr
def test_booking_modification(client: XCover):
    booking = client.instant_booking(InstantBookingFactory())
    phone = "+380506022279"
    assert isinstance(booking, dict)
    resp = client.booking_modification(
        booking["id"],
        {
            "policyholder": {
                "phone": phone,
            }
        },
    )
    assert resp["policyholder"]["phone"] == phone


@pytest.mark.vcr
def test_booking_modification__error(client: XCover):
    booking = client.instant_booking(InstantBookingFactory())
    assert isinstance(booking, dict)
    with pytest.raises(XCoverHttpException):
        client.booking_modification(
            booking["id"],
            {
                "policyholder": {
                    "phone": "invalid phone format",
                }
            },
        )


@pytest.mark.vcr
def test_booking_modification_quote_workflow(client: XCover):
    booking = client.instant_booking(InstantBookingFactory())
    assert isinstance(booking, dict)
    mod_quote_resp = client.booking_modification_quote(
        booking["id"],
        {
            "quotes": [
                {
                    "id": booking["quotes"][0]["id"],
                    "update_fields": {
                        "tickets": [{"price": 100500}],
                    },
                }
            ]
        },
    )
    assert booking["total_price"] != mod_quote_resp["total_price"]

    update_id = mod_quote_resp["update_id"]

    # Ensure that the modification is not applied before confirmed
    get_booking_res = client.get_booking(booking["id"])
    assert booking["total_price"] == get_booking_res["total_price"]

    # Confirm booking update
    confirm_mod_resp = client.confirm_booking_modification(booking["id"], update_id)
    assert confirm_mod_resp["total_price"] == mod_quote_resp["total_price"]

    # Ensure that the modification is applied after the modification is confirmed
    get_booking_res_2 = client.get_booking(booking["id"])
    assert mod_quote_resp["total_price"] == get_booking_res_2["total_price"]

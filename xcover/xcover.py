import json
from urllib.parse import urljoin

import requests

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
        # Generate full URL
        full_url = urljoin(f"partners/{self.partner_code}/", url)

        # Call server
        response = self.call(method, full_url, payload=payload, **kwargs)

        # Check response for errors
        error_msg = None
        if 400 <= response.status_code < 500:
            error_msg = (
                f"{response.status_code} Client Error: {response.reason} for url {response.url}"
            )

        elif 500 <= response.status_code < 600:
            error_msg = (
                f"{response.status_code} Server Error: {response.reason} for url {response.url}"
            )

        if error_msg:
            raise XCoverHttpException(error_msg)

        if response.status_code in (204, 202):
            return True

        return response.json()

    # Quotes
    def create_quote(self, payload, **kwargs):
        return self.call_partner_endpoint("POST", "quotes/", payload=payload, **kwargs)

    def get_quote(self, quote_id, **kwargs):
        return self.call_partner_endpoint("GET", f"quotes/{quote_id}/", **kwargs)

    def update_quote(self, quote_id, payload, **kwargs):
        return self.call_partner_endpoint(
            "PATCH", f"quotes/{quote_id}/", payload=payload, **kwargs
        )

    def opt_out(self, quote_id, payload=None, **kwargs):
        if payload is None:
            payload = {}
        return self.call_partner_endpoint(
            "POST", f"bookings/{quote_id}/opt_out", payload=payload, **kwargs
        )

    def add_quotes(self, quote_id, payload, **kwargs):
        return self.call_partner_endpoint(
            "POST", f"quotes/{quote_id}/add/", payload=payload, **kwargs
        )

    def delete_quotes(self, quote_id, payload, **kwargs):
        return self.call_partner_endpoint(
            "POST", f"quotes/{quote_id}/delete/", payload=payload, **kwargs
        )

    # Bookings
    def create_booking(self, quote_id, payload, **kwargs):
        return self.call_partner_endpoint(
            "POST", f"bookings/{quote_id}/", payload=payload, **kwargs
        )

    def instant_booking(self, payload, **kwargs):
        return self.call_partner_endpoint("POST", "instant_booking/", payload=payload, **kwargs)

    def get_booking(self, booking_id, **kwargs):
        return self.call_partner_endpoint("GET", f"bookings/{booking_id}/", **kwargs)

    def list_bookings(self, **kwargs):
        return self.call_partner_endpoint("GET", "bookings/", **kwargs)

    def confirm_booking(self, booking_id, payload=None, **kwargs):
        if payload is None:
            payload = {}
        return self.call_partner_endpoint(
            "PUT", f"bookings/{booking_id}/confirm", payload=payload, **kwargs
        )

    def trigger_email(self, booking_id, payload=None, **kwargs):
        if payload is None:
            payload = {}

        return self.call_partner_endpoint(
            "POST", f"bookings/{booking_id}/send_email", payload=payload, **kwargs
        )

    # Mods
    def booking_modification(self, booking_id, payload, **kwargs):
        return self.call_partner_endpoint(
            "PATCH", f"bookings/{booking_id}/", payload=payload, **kwargs
        )

    def booking_modification_quote(self, booking_id, payload, **kwargs):
        return self.call_partner_endpoint(
            "PATCH", f"bookings/{booking_id}/quote_for_update", payload=payload, **kwargs
        )

    def confirm_booking_modification(self, booking_id, update_id, payload=None, **kwargs):
        if payload is None:
            payload = {}

        return self.call_partner_endpoint(
            "POST", f"bookings/{booking_id}/confirm_update/{update_id}/", payload=payload, **kwargs
        )

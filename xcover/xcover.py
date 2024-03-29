import json
from urllib.parse import urljoin
from uuid import uuid4

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError
from urllib3.util.retry import Retry

from .auth import XCoverAuth
from .config import XCoverConfig
from .encoder import JSONEncoder
from .exceptions import XCoverHttpException


class XCover:
    def __init__(self, config: XCoverConfig = None):
        self.config = config or XCoverConfig()

    default_headers = {"Content-Type": "application/json"}

    @property
    def auto_retry_session(self):
        session = requests.Session()
        retries = Retry(
            total=self.config.retry_total,
            backoff_factor=self.config.retry_backoff_factor,
            status_forcelist={429, 502, 503, 504},
            allowed_methods={"HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"},
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)

        return session

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
        auto_retry: bool = False,
    ) -> requests.Response:
        if headers is None:
            headers = {}
        full_url = urljoin(self.config.base_url, url)
        session = self.auto_retry_session if auto_retry else self.session

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

    def call_partner_endpoint(
        self, method, url, payload=None, generate_idepmotency_key=True, **kwargs
    ):
        # Generate full URL
        full_url = urljoin(f"partners/{self.partner_code}/", url)

        # Call server
        if method in {"POST", "PUT", "PATCH"} and generate_idepmotency_key:
            headers = kwargs.pop("headers", {})
            headers.setdefault("x-idempotency-key", str(uuid4()))
            kwargs["headers"] = headers

        try:
            response = self.call(method, full_url, payload=payload, **kwargs)
        except RetryError as exc:
            raise XCoverHttpException(exc)

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
        return self.call_partner_endpoint(
            "POST", "quotes/", payload=payload, generate_idepmotency_key=False, **kwargs
        )

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
    def create_booking(self, quote_id, payload, auto_retry=True, **kwargs):
        return self.call_partner_endpoint(
            "POST", f"bookings/{quote_id}/", auto_retry=auto_retry, payload=payload, **kwargs
        )

    def instant_booking(self, payload, auto_retry=True, **kwargs):
        return self.call_partner_endpoint(
            "POST", "instant_booking/", payload=payload, auto_retry=auto_retry, **kwargs
        )

    def get_booking(self, booking_id, **kwargs):
        return self.call_partner_endpoint("GET", f"bookings/{booking_id}/", **kwargs)

    def list_bookings(self, **kwargs):
        return self.call_partner_endpoint("GET", "bookings/", **kwargs)

    def confirm_booking(self, booking_id, payload=None, auto_retry=True, **kwargs):
        if payload is None:
            payload = {}
        return self.call_partner_endpoint(
            "PUT",
            f"bookings/{booking_id}/confirm",
            payload=payload,
            auto_retry=auto_retry,
            **kwargs,
        )

    def trigger_email(self, booking_id, payload=None, auto_retry=True, **kwargs):
        if payload is None:
            payload = {}

        return self.call_partner_endpoint(
            "POST",
            f"bookings/{booking_id}/send_email",
            payload=payload,
            auto_retry=auto_retry,
            **kwargs,
        )

    # Mods
    def booking_modification(self, booking_id, payload, auto_retry=True, **kwargs):
        return self.call_partner_endpoint(
            "PATCH", f"bookings/{booking_id}/", payload=payload, auto_retry=auto_retry, **kwargs
        )

    def booking_modification_quote(self, booking_id, payload, **kwargs):
        return self.call_partner_endpoint(
            "PATCH", f"bookings/{booking_id}/quote_for_update", payload=payload, **kwargs
        )

    def confirm_booking_modification(
        self, booking_id, update_id, payload=None, auto_retry=True, **kwargs
    ):
        if payload is None:
            payload = {}

        return self.call_partner_endpoint(
            "POST",
            f"bookings/{booking_id}/confirm_update/{update_id}/",
            payload=payload,
            auto_retry=auto_retry,
            **kwargs,
        )

    # Cancellations
    def cancel_booking(self, booking_id, payload=None, **kwargs):
        if payload is None:
            payload = {}

        return self.call_partner_endpoint(
            "POST", f"bookings/{booking_id}/cancel", payload=payload, auto_retry=True, **kwargs
        )

    def confirm_booking_cancellation(
        self, booking_id, cancellation_id, payload=None, auto_retry=True, **kwargs
    ):
        if payload is None:
            payload = {}

        return self.call_partner_endpoint(
            "POST",
            f"bookings/{booking_id}/confirm_cancellation/{cancellation_id}/",
            payload=payload,
            auto_retry=auto_retry,
            **kwargs,
        )

    # Renewals
    def quote_for_renewal(self, booking_id, payload=None, **kwargs):
        if payload is None:
            payload = {}

        return self.call_partner_endpoint(
            "PATCH",
            f"renewals/{booking_id}/quote_for_renewal/",
            payload=payload,
            **kwargs,
        )

    def renewal_confirmation(
        self, booking_id, renewal_id, payload=None, auto_retry=True, **kwargs
    ):
        if payload is None:
            payload = {}

        return self.call_partner_endpoint(
            "POST",
            f"renewals/{booking_id}/confirm/{renewal_id}/",
            payload=payload,
            auto_retry=auto_retry,
            **kwargs,
        )

    def renewal_opt_out(self, booking_id, payload=None, auto_retry=True, **kwargs):
        if payload is None:
            payload = {}

        return self.call_partner_endpoint(
            "POST",
            f"renewals/{booking_id}/opt_out/",
            payload=payload,
            auto_retry=auto_retry,
            **kwargs,
        )

    # Instalments
    def get_instalments(self, booking_id, **kwargs):
        return self.call_partner_endpoint(
            "GET",
            f"bookings/{booking_id}/instalments/",
            **kwargs,
        )

    def update_instalment_payment_status(self, booking_id, payload, auto_retry=True, **kwargs):
        return self.call_partner_endpoint(
            "POST",
            f"bookings/{booking_id}/instalments/",
            payload=payload,
            auto_retry=auto_retry,
            **kwargs,
        )

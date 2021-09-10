# XCover SDK for Python

XCover SDK is a Python package that simplifies XCover API integration.

# Installation 

XCover SDK is available on PyPI. 
You can use the following commands to install the latest version:

    pip install xcover

or 

    poertry install xcover 

# Features

- Authentication
- Simple configuration using env variables

# Configuration

## Config object

The library provides `XCoverConfig` dataclass that can be used as following:

```python
from xcover import XCover, XCoverConfig

client = XCover(
    XCoverConfig( # minimal config, check autocomplete for more options
        base_url="https://api.xcover.com/xcover",
        partner_code="--PARTNER_CODE--",
        auth_api_key="--API_KEY--",
        auth_api_secret="--API_SECRET--",
    )
)

```

## Env variables

Alternatively, the library can be configured using env variables. 

The full list of config options is below:

* `XC_BASE_URL` (`XCoverConfig.base_url`): XCover base URL (e.g. `https://api.xcover.com/api/v2/`). 
* `XC_PARTNER_CODE` (`XCoverConfig.partner_code`): Partner code (e.g. `LLODT`).
* `XC_HTTP_TIMEOUT` (`XCoverConfig.http_timeout`): HTTP timeout in seconds. Default value is `10`. 
* `XC_AUTH_API_KEY` (`XCoverConfig.auth_api_key`): API key to use.
* `XC_AUTH_API_SECRET` (`XCoverConfig.auth_api_secret`): API secret to use.
* `XC_AUTH_ALGORITHM` (`XCoverConfig.auth_algorithm`): HMAC encoding algorithm to use. Default is `hmac-sha512`.
* `XC_AUTH_HEADERS` (`XCoverConfig.auth_headers`): Headers to sign. Default is `(request-target) date`.

# Usage example

## Using `call` method

```python
import requests

from xcover.xcover import XCover

# Env variables are used
client = XCover()

# Prepare payload
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
# Calling XCover API
response = client.call(
    method="POST",
    url="partners/LLODT/quotes/",
    payload=payload,
)

quote: requests.Response = response.json()
```

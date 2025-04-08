# &middot; xcover-python &middot;

[![Supported Versions](https://img.shields.io/pypi/pyversions/xcover-python.svg)](https://pypi.org/project/xcover-python)
[![codecov](https://codecov.io/gh/CoverGenius/xcover-python/branch/master/graph/badge.svg?token=KINNTVZV07)](https://codecov.io/gh/CoverGenius/xcover-python)

---

`xcover-python` is a Python API Client for [XCover](https://www.covergenius.com/xcover/).

---

## Installation

`xcover-python` is available on PyPI. To install the latest version run:

    pip install xcover-python

or

    poetry install xcover-python

## Features

- Authentication
- Simple configuration using env variables
- (WIP) High-level API to perform partner operations on quotes and bookings

## Configuration

### Config object

The library provides `XCoverConfig` dataclass that can be used as shown:

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

### Env variables

Alternatively, it is possible to use env variables.

The full list of configuration options:

| Environment Variable | Config Property | Description | Default Value |
|---------------------|-----------------|-------------|---------------|
| `XC_BASE_URL` | `XCoverConfig.base_url` | XCover base URL (e.g. `https://api.xcover.com/api/v2/`) | - |
| `XC_PARTNER_CODE` | `XCoverConfig.partner_code` | Partner code (e.g. `LLODT`) | - |
| `XC_HTTP_TIMEOUT` | `XCoverConfig.http_timeout` | HTTP timeout in seconds | `10` |
| `XC_AUTH_API_KEY` | `XCoverConfig.auth_api_key` | API key to use | - |
| `XC_AUTH_API_SECRET` | `XCoverConfig.auth_api_secret` | API secret to use | - |
| `XC_AUTH_ALGORITHM` | `XCoverConfig.auth_algorithm` | HMAC encoding algorithm to use | `hmac-sha512` |
| `XC_AUTH_HEADERS` | `XCoverConfig.auth_headers` | Headers to sign | `(request-target) date` |
| `XC_RETRY_TOTAL` | `XCoverConfig.retry_total` | Total number of retries | `5` |
| `XC_RETRY_BACKOFF_FACTOR` | `XCoverConfig.retry_backoff_factor` | Backoff factor for retries timeout | `2` |

## Usage example

### Using low-level `call` method

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
response: requests.Response = client.call(
    method="POST",
    url="partners/LLODT/quotes/",
    payload=payload,
)

quote = response.json()
print(quote)
```

### Retries

This client will automatically retry certain operations when it is considered safe to do this.
The retry number and intervals could be controlled via XC_RETRY_TOTAL and XC_RETRY_BACKOFF_FACTOR
environment variables ot the same config options.

Auto retry logic can be enabled/disabled per operation. However, further fine-tuning is possible
via extending XCover class if required.

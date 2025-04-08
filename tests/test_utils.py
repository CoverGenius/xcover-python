from datetime import datetime, timezone
from unittest import mock

from xcover.utils import http_date


def test_http_date():
    fixed_dt = datetime(2025, 4, 8, 12, 0, 0, tzinfo=timezone.utc)

    with mock.patch("xcover.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_dt
        mock_datetime.timezone = timezone

        date_header = http_date()

        mock_datetime.now.assert_called_once_with(timezone.utc)
        assert date_header == "Tue, 08 Apr 2025 12:00:00 GMT"

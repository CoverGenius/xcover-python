from datetime import datetime, timezone


def http_date():
    now = datetime.now(timezone.utc)
    return now.strftime("%a, %d %b %Y %H:%M:%S GMT")  # RFC 7231 format

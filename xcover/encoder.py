import datetime
import decimal
import json
import uuid


class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass can encode date, time, timedelta,
    decimal types, generators, etc.
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            representation = obj.isoformat()
            if representation.endswith("+00:00"):
                representation = representation[:-6] + "Z"
            return representation
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, bytes):
            # best-effort for binary blobs
            return obj.decode("utf-8")
        return super().default(obj)

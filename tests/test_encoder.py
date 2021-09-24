import pytest
from xcover.encoder import JSONEncoder
import datetime
import decimal
import uuid


@pytest.mark.parametrize(
    "test_input,expected",
    (
        (datetime.datetime(day=1, month=1, year=2020), "2020-01-01T00:00:00"),
        (
            datetime.datetime(day=1, month=1, year=2020, tzinfo=datetime.timezone.utc),
            "2020-01-01T00:00:00Z",
        ),
        (
            datetime.datetime(day=1, month=1, year=2020, tzinfo=datetime.timezone.max),
            "2020-01-01T00:00:00+23:59",
        ),
        (datetime.date(day=1, month=1, year=2020), "2020-01-01"),
        (datetime.date(day=1, month=1, year=2020), "2020-01-01"),
        (decimal.Decimal("33.33"), 33.33),
        (
            uuid.UUID("8667b385-8d0c-4462-863a-feacec57c0b9"),
            "8667b385-8d0c-4462-863a-feacec57c0b9",
        ),
        (b"aa", "aa"),
    ),
)
def test_default(test_input, expected):
    assert JSONEncoder().default(test_input) == expected


def test_default_parent():
    with pytest.raises(TypeError):
        JSONEncoder().default(None)

from datetime import date, datetime
from decimal import Decimal

from src.validation.profile import normalize


def test_normalize_decimal() -> None:
    assert normalize(Decimal("2499.00")) == "2499.00"


def test_normalize_datetime() -> None:
    value = datetime(
        2026,
        8,
        15,
        3,
        35,
        58,
    )

    assert normalize(value) == ("2026-08-15 03:35:58")


def test_normalize_date() -> None:
    value = date(
        2026,
        8,
        15,
    )

    assert normalize(value) == ("2026-08-15")


def test_normalize_plain_value() -> None:
    assert normalize(42) == 42

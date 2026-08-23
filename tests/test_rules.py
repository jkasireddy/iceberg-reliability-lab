from decimal import Decimal

from src.validation.rules import (
    allowed_upper_bound_rule,
    max_value_rule,
    null_count_rule,
)


def test_max_value_rule_passes_within_limit() -> None:
    result = max_value_rule(
        column="quantity",
        actual=5,
        maximum=5,
    )

    assert result.passed is True


def test_max_value_rule_fails_above_limit() -> None:
    result = max_value_rule(
        column="quantity",
        actual=999,
        maximum=5,
    )

    assert result.passed is False


def test_decimal_max_value_rule() -> None:
    result = max_value_rule(
        column="total_amount",
        actual=Decimal("999999.99"),
        maximum=Decimal("2500.00"),
    )

    assert result.passed is False


def test_null_count_rule_passes_with_zero_nulls() -> None:
    result = null_count_rule(
        column="quantity",
        actual=0,
        maximum_nulls=0,
    )

    assert result.passed is True


def test_null_count_rule_fails_when_nulls_exceed_limit() -> None:
    result = null_count_rule(
        column="quantity",
        actual=10,
        maximum_nulls=0,
    )

    assert result.passed is False


def test_upper_bound_rule_detects_unexpected_state_bound() -> None:
    result = allowed_upper_bound_rule(
        column="state",
        actual="ZZ",
        maximum_allowed="VA",
    )

    assert result.passed is False

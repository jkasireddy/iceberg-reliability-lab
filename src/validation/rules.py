from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationResult:
    rule: str
    column: str
    expected: str
    actual: Any
    passed: bool


def max_value_rule(
    column: str,
    actual: Any,
    maximum: Any,
) -> ValidationResult:
    passed = actual is not None and actual <= maximum

    return ValidationResult(
        rule="max_value",
        column=column,
        expected=f"<= {maximum}",
        actual=actual,
        passed=passed,
    )


def allowed_upper_bound_rule(
    column: str,
    actual: Any,
    maximum_allowed: str,
) -> ValidationResult:
    passed = actual is not None and actual <= maximum_allowed

    return ValidationResult(
        rule="allowed_upper_bound",
        column=column,
        expected=f"<= {maximum_allowed}",
        actual=actual,
        passed=passed,
    )


def null_count_rule(
    column: str,
    actual: int | None,
    maximum_nulls: int = 0,
) -> ValidationResult:
    passed = actual is not None and actual <= maximum_nulls

    return ValidationResult(
        rule="null_count",
        column=column,
        expected=f"<= {maximum_nulls}",
        actual=actual,
        passed=passed,
    )

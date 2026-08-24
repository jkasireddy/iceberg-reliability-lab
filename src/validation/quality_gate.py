from __future__ import annotations

from decimal import Decimal
from typing import Any

from src.validation.rules import (
    ValidationResult,
    allowed_upper_bound_rule,
    max_value_rule,
    null_count_rule,
)

MAX_QUANTITY = 5
MAX_TOTAL_AMOUNT = Decimal("2500.00")
MAX_STATE_UPPER_BOUND = "VA"


def evaluate_profile(
    profile: dict[str, Any],
) -> list[ValidationResult]:
    metrics = profile["metrics"]

    return [
        max_value_rule(
            "quantity",
            metrics["quantity"]["upper_bound"],
            MAX_QUANTITY,
        ),
        max_value_rule(
            "total_amount",
            Decimal(metrics["total_amount"]["upper_bound"]),
            MAX_TOTAL_AMOUNT,
        ),
        allowed_upper_bound_rule(
            "state",
            metrics["state"]["upper_bound"],
            MAX_STATE_UPPER_BOUND,
        ),
        null_count_rule(
            "quantity",
            metrics["quantity"]["null_count"],
        ),
        null_count_rule(
            "total_amount",
            metrics["total_amount"]["null_count"],
        ),
    ]


def failed_results(
    results: list[ValidationResult],
) -> list[ValidationResult]:
    return [result for result in results if not result.passed]

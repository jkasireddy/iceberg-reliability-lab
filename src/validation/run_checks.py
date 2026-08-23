from __future__ import annotations

from decimal import Decimal

from src.iceberg_lab.catalog import get_catalog
from src.validation.profile import build_profile
from src.validation.rules import (
    allowed_upper_bound_rule,
    max_value_rule,
    null_count_rule,
)

TABLE_NAME = "reliability.orders"


def main() -> None:
    catalog = get_catalog()
    table = catalog.load_table(TABLE_NAME)

    profile = build_profile(table)
    metrics = profile["metrics"]

    results = [
        max_value_rule(
            "quantity",
            metrics["quantity"]["upper_bound"],
            5,
        ),
        max_value_rule(
            "total_amount",
            Decimal(metrics["total_amount"]["upper_bound"]),
            Decimal("2500.00"),
        ),
        allowed_upper_bound_rule(
            "state",
            metrics["state"]["upper_bound"],
            "VA",
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

    print("======================================")
    print("       METADATA QUALITY CHECKS")
    print("======================================")

    failed = 0

    for result in results:
        status = "PASS" if result.passed else "FAIL"

        if not result.passed:
            failed += 1

        print(
            f"{status:<5} | "
            f"{result.column:<15} | "
            f"{result.rule:<20} | "
            f"expected {result.expected:<12} | "
            f"actual {result.actual}"
        )

    print("======================================")

    if failed:
        print(f"QUALITY GATE FAILED: {failed} rule(s) violated")
        raise SystemExit(1)

    print("QUALITY GATE PASSED")


if __name__ == "__main__":
    main()

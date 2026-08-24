from __future__ import annotations

from src.iceberg_lab.catalog import get_catalog
from src.iceberg_lab.orders import ICEBERG_TABLE
from src.validation.profile import build_profile
from src.validation.quality_gate import (
    evaluate_profile,
    failed_results,
)


def main() -> None:
    catalog = get_catalog()

    table = catalog.load_table(ICEBERG_TABLE)

    profile = build_profile(table)

    results = evaluate_profile(profile)

    print("======================================")
    print("       METADATA QUALITY CHECKS")
    print("======================================")

    for result in results:
        status = "PASS" if result.passed else "FAIL"

        print(
            f"{status:<5} | "
            f"{result.column:<15} | "
            f"{result.rule:<20} | "
            f"expected {result.expected:<12} | "
            f"actual {result.actual}"
        )

    failures = failed_results(results)

    print("======================================")

    if failures:
        print(f"QUALITY GATE FAILED: {len(failures)} rule(s) violated")
        raise SystemExit(1)

    print("QUALITY GATE PASSED")


if __name__ == "__main__":
    main()

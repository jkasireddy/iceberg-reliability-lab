from __future__ import annotations

import json
from pathlib import Path

from src.iceberg_lab.catalog import get_catalog
from src.validation.profile import build_profile

TABLE_NAME = "reliability.orders"
BASELINE_PATH = Path("artifacts/baseline.json")

WATCHED_METRICS = {
    "quantity": [
        "null_count",
        "lower_bound",
        "upper_bound",
    ],
    "total_amount": [
        "null_count",
        "lower_bound",
        "upper_bound",
    ],
    "state": [
        "null_count",
        "lower_bound",
        "upper_bound",
    ],
    "updated_at": [
        "null_count",
        "lower_bound",
        "upper_bound",
    ],
}


def main() -> None:
    if not BASELINE_PATH.exists():
        raise RuntimeError("Baseline not found. Run capture_baseline first.")

    with BASELINE_PATH.open() as file:
        baseline = json.load(file)

    catalog = get_catalog()

    table = catalog.load_table(TABLE_NAME)

    current = build_profile(table)

    print("========================================")
    print("      ICEBERG BASELINE COMPARISON")
    print("========================================")

    print(f"\nBaseline snapshot : {baseline['snapshot_id']}")

    print(f"Current snapshot  : {current['snapshot_id']}")

    baseline_count = baseline["record_count"]
    current_count = current["record_count"]

    print("\n=== ROW COUNT CHECK ===")

    print(f"Baseline : {baseline_count:,}")

    print(f"Current  : {current_count:,}")

    if baseline_count == current_count:
        print("Result   : PASS")
    else:
        print("Result   : FAIL")

    drift_found = False

    print("\n=== METADATA DRIFT ===")

    for column, metric_names in WATCHED_METRICS.items():
        print(f"\n{column}")

        for metric_name in metric_names:
            baseline_value = baseline["metrics"][column][metric_name]

            current_value = current["metrics"][column][metric_name]

            changed = baseline_value != current_value

            status = "CHANGED" if changed else "same"

            if changed:
                drift_found = True

            print(f"  {metric_name:<12} {baseline_value} -> {current_value} [{status}]")

    print("\n========================================")

    if baseline_count == current_count and drift_found:
        print("ROW COUNT PASSED, BUT ICEBERG METADATA DETECTED DRIFT")

    elif drift_found:
        print("METADATA DRIFT DETECTED")

    else:
        print("NO METADATA DRIFT DETECTED")

    print("========================================")


if __name__ == "__main__":
    main()

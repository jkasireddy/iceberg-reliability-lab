from __future__ import annotations

from src.iceberg_lab.catalog import get_catalog
from src.iceberg_lab.orders import ICEBERG_TABLE
from src.validation.baseline import load_baseline
from src.validation.comparison import compare_profiles
from src.validation.profile import build_profile


def main() -> None:
    baseline = load_baseline()

    catalog = get_catalog()

    table = catalog.load_table(ICEBERG_TABLE)

    current = build_profile(table)

    comparison = compare_profiles(
        baseline,
        current,
    )

    print("========================================")
    print("      ICEBERG BASELINE COMPARISON")
    print("========================================")

    print(f"\nBaseline snapshot : {comparison.baseline_snapshot_id}")

    print(f"Current snapshot  : {comparison.current_snapshot_id}")

    print("\n=== ROW COUNT CHECK ===")

    print(f"Baseline : {comparison.baseline_record_count:,}")

    print(f"Current  : {comparison.current_record_count:,}")

    print(f"Result   : {'PASS' if comparison.row_count_matches else 'FAIL'}")

    print("\n=== METADATA DRIFT ===")

    for change in comparison.metric_changes:
        status = "CHANGED" if change.changed else "same"

        print(f"\n{change.column}" if change.metric == "null_count" else "")

        print(f"  {change.metric:<12} {change.baseline} -> {change.current} [{status}]")

    print("\n========================================")

    if comparison.row_count_matches and comparison.has_metadata_drift:
        print("ROW COUNT PASSED, BUT ICEBERG METADATA DETECTED DRIFT")

    elif comparison.has_metadata_drift:
        print("METADATA DRIFT DETECTED")

    else:
        print("NO METADATA DRIFT DETECTED")

    print("========================================")


if __name__ == "__main__":
    main()

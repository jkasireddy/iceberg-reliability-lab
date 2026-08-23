from __future__ import annotations

import argparse

from src.iceberg_lab.catalog import get_catalog
from src.iceberg_lab.orders import (
    ICEBERG_TABLE,
    ORDER_KEY,
)
from src.iceberg_lab.source import count_orders
from src.iceberg_lab.table_stats import (
    metadata_record_count,
)
from src.ingestion.batch import load_batch
from src.ingestion.watermark import (
    advance_watermark,
)

SIMULATED_CRASH_EXIT_CODE = 99


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--simulate-crash-before-watermark",
        action="store_true",
        help=(
            "Commit and validate the Iceberg batch, "
            "then simulate a crash before advancing "
            "the source watermark."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    batch, batch_metadata = load_batch()

    print("======================================")
    print("       APPLY INCREMENTAL BATCH")
    print("======================================")

    print(f"\nBatch rows: {batch.num_rows:,}")

    catalog = get_catalog()

    table = catalog.load_table(ICEBERG_TABLE)

    before_snapshot = table.current_snapshot()

    before_count = metadata_record_count(table)

    print(f"Iceberg rows before: {before_count:,}")

    if before_snapshot:
        print(f"Snapshot before    : {before_snapshot.snapshot_id}")

    print("\nApplying PyIceberg upsert...")

    result = table.upsert(
        df=batch,
        join_cols=[ORDER_KEY],
    )

    table.refresh()

    after_snapshot = table.current_snapshot()

    after_count = metadata_record_count(table)

    expected_count = count_orders()

    print("\n--- UPSERT RESULT ---")

    print(f"Rows updated : {result.rows_updated:,}")

    print(f"Rows inserted: {result.rows_inserted:,}")

    print("\n--- VALIDATION ---")

    print(f"PostgreSQL rows       : {expected_count:,}")

    print(f"Iceberg metadata rows : {after_count:,}")

    if after_snapshot:
        print(f"Snapshot after        : {after_snapshot.snapshot_id}")

    if after_count != expected_count:
        print("\nVALIDATION FAILED")

        print("Watermark will NOT be advanced.")

        raise RuntimeError("Source and Iceberg row counts differ")

    print("\nSource/Iceberg count validation PASSED")

    if args.simulate_crash_before_watermark:
        print("\n======================================")
        print("SIMULATED PROCESS CRASH")
        print("======================================")
        print("Iceberg commit succeeded.")
        print("Validation succeeded.")
        print("Watermark was NOT advanced.")
        print("\nOn restart, the same source batch will be extracted again.")

        raise SystemExit(SIMULATED_CRASH_EXIT_CODE)

    advance_watermark(
        batch_metadata.updated_at,
        batch_metadata.order_id,
    )

    print("\nWatermark advanced")

    print(f"  updated_at : {batch_metadata.updated_at}")

    print(f"  order_id   : {batch_metadata.order_id}")

    print("\n======================================")
    print("INCREMENTAL PIPELINE SUCCEEDED")
    print("======================================")


if __name__ == "__main__":
    main()

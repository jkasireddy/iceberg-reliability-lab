from __future__ import annotations
import argparse
import json
from datetime import datetime
from pathlib import Path

import psycopg
import pyarrow.parquet as pq

from src.config import postgres_connection_string
from src.iceberg_lab.catalog import get_catalog
from src.ingestion.watermark import advance_watermark


TABLE_NAME = "reliability.orders"

BATCH_PATH = Path(
    "artifacts/incremental_batch.parquet"
)

BATCH_METADATA_PATH = Path(
    "artifacts/incremental_batch.json"
)


def source_row_count() -> int:
    with psycopg.connect(
        postgres_connection_string()
    ) as conn:
        result = conn.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()

        if result is None:
            raise RuntimeError(
                "Unable to determine source row count"
            )

        return result[0]


def main() -> None:
    args = parse_args()
    if not BATCH_PATH.exists():
        raise RuntimeError(
            "Incremental batch does not exist. "
            "Run the extractor first."
        )

    if not BATCH_METADATA_PATH.exists():
        raise RuntimeError(
            "Incremental batch metadata does not exist."
        )

    batch = pq.read_table(BATCH_PATH)

    metadata = json.loads(
        BATCH_METADATA_PATH.read_text()
    )

    print("======================================")
    print("       APPLY INCREMENTAL BATCH")
    print("======================================")

    print(f"\nBatch rows: {batch.num_rows:,}")

    catalog = get_catalog()

    table = catalog.load_table(TABLE_NAME)

    before_snapshot = table.current_snapshot()

    before_count = (
        table.scan().to_arrow().num_rows
    )

    print(f"Iceberg rows before: {before_count:,}")

    if before_snapshot:
        print(
            f"Snapshot before    : "
            f"{before_snapshot.snapshot_id}"
        )

    print("\nApplying PyIceberg upsert...")

    result = table.upsert(
        df=batch,
        join_cols=["order_id"],
    )

    table.refresh()

    after_snapshot = table.current_snapshot()

    after_count = (
        table.scan().to_arrow().num_rows
    )

    expected_count = source_row_count()

    print("\n--- UPSERT RESULT ---")
    print(
        f"Rows updated : "
        f"{result.rows_updated:,}"
    )
    print(
        f"Rows inserted: "
        f"{result.rows_inserted:,}"
    )

    print("\n--- VALIDATION ---")
    print(
        f"PostgreSQL rows : "
        f"{expected_count:,}"
    )
    print(
        f"Iceberg rows    : "
        f"{after_count:,}"
    )

    if after_snapshot:
        print(
            f"Snapshot after  : "
            f"{after_snapshot.snapshot_id}"
        )

    if after_count != expected_count:
        print("\nVALIDATION FAILED")
        print(
            "Watermark will NOT be advanced."
        )

        raise RuntimeError(
            "Source and Iceberg row counts differ"
        )

    print("\nSource/Iceberg count validation PASSED")

    high_watermark = metadata[
        "high_watermark"
    ]

    new_updated_at = datetime.fromisoformat(
        high_watermark["updated_at"]
    )

    new_order_id = int(
        high_watermark["order_id"]
    )

    #
    # This happens ONLY after:
    #
    # 1. Iceberg commit succeeded
    # 2. table refreshed
    # 3. target validation succeeded
    #
    if args.simulate_crash_before_watermark:
        print("\n======================================")
        print("SIMULATED PROCESS CRASH")
        print("======================================")
        print("Iceberg commit succeeded.")
        print("Validation succeeded.")
        print("Watermark was NOT advanced.")
        print(
            "\nOn restart, the same source batch "
            "will be extracted again."
        )

        raise SystemExit(99)

    advance_watermark(
        new_updated_at,
        new_order_id,
    )

    print("\nWatermark advanced")
    print(
        f"  updated_at : {new_updated_at}"
    )
    print(
        f"  order_id   : {new_order_id}"
    )

    print("\n======================================")
    print("INCREMENTAL PIPELINE SUCCEEDED")
    print("======================================")

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

if __name__ == "__main__":
    main()
from __future__ import annotations

import json
from pathlib import Path

import psycopg
import pyarrow as pa
import pyarrow.parquet as pq

from src.config import postgres_connection_string
from src.ingestion.initial_load import ORDERS_SCHEMA
from src.ingestion.watermark import get_watermark


BATCH_PATH = Path(
    "artifacts/incremental_batch.parquet"
)

BATCH_METADATA_PATH = Path(
    "artifacts/incremental_batch.json"
)


def extract_incremental() -> pa.Table:
    last_updated_at, last_order_id = get_watermark()

    print("Current watermark")
    print(f"  updated_at : {last_updated_at}")
    print(f"  order_id   : {last_order_id}")

    with psycopg.connect(
        postgres_connection_string()
    ) as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    order_id,
                    customer_id,
                    order_timestamp,
                    state,
                    product_category,
                    quantity,
                    unit_price,
                    total_amount,
                    payment_type,
                    status,
                    updated_at
                FROM orders
                WHERE
                    (updated_at, order_id)
                    > (%s, %s)
                ORDER BY
                    updated_at,
                    order_id
                """,
                (
                    last_updated_at,
                    last_order_id,
                ),
            )

            rows = cur.fetchall()

            columns = [
                description.name
                for description in cur.description
            ]

    records = [
        dict(zip(columns, row))
        for row in rows
    ]

    return pa.Table.from_pylist(
        records,
        schema=ORDERS_SCHEMA,
    )


def main() -> None:
    batch = extract_incremental()

    print(
        f"\nIncremental rows extracted: "
        f"{batch.num_rows:,}"
    )

    if batch.num_rows == 0:
        if BATCH_PATH.exists():
            BATCH_PATH.unlink()

        if BATCH_METADATA_PATH.exists():
            BATCH_METADATA_PATH.unlink()

        print("Nothing new to process.")
        print("Any stale incremental batch artifacts were removed.")
        return

    BATCH_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    pq.write_table(
        batch,
        BATCH_PATH,
    )

    updated_at_column = batch.column(
        "updated_at"
    ).to_pylist()

    order_id_column = batch.column(
        "order_id"
    ).to_pylist()

    final_updated_at = updated_at_column[-1]
    final_order_id = order_id_column[-1]

    metadata = {
        "rows": batch.num_rows,
        "high_watermark": {
            "updated_at": str(final_updated_at),
            "order_id": final_order_id,
        },
    }

    BATCH_METADATA_PATH.write_text(
        json.dumps(
            metadata,
            indent=2,
        )
    )

    print(f"Batch file     : {BATCH_PATH}")
    print(
        f"Batch metadata : "
        f"{BATCH_METADATA_PATH}"
    )

    print("\nBatch high watermark")
    print(
        f"  updated_at : "
        f"{final_updated_at}"
    )
    print(
        f"  order_id   : "
        f"{final_order_id}"
    )

    print(
        "\nWatermark has NOT been advanced yet."
    )


if __name__ == "__main__":
    main()
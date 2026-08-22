from __future__ import annotations

from decimal import Decimal

import psycopg
import pyarrow as pa

from src.config import postgres_connection_string
from src.iceberg_lab.catalog import get_catalog


TABLE_NAME = "reliability.orders"


ORDERS_SCHEMA = pa.schema(
    [
        pa.field("order_id", pa.int64(), nullable=False),
        pa.field("customer_id", pa.int64(), nullable=False),
        pa.field(
            "order_timestamp",
            pa.timestamp("us"),
            nullable=False,
        ),
        pa.field("state", pa.string(), nullable=False),
        pa.field(
            "product_category",
            pa.string(),
            nullable=False,
        ),
        pa.field("quantity", pa.int32(), nullable=False),
        pa.field(
            "unit_price",
            pa.decimal128(10, 2),
            nullable=False,
        ),
        pa.field(
            "total_amount",
            pa.decimal128(12, 2),
            nullable=False,
        ),
        pa.field(
            "payment_type",
            pa.string(),
            nullable=False,
        ),
        pa.field("status", pa.string(), nullable=False),
        pa.field(
            "updated_at",
            pa.timestamp("us"),
            nullable=False,
        ),
    ]
)


def extract_orders() -> pa.Table:
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
                ORDER BY order_id
                """
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


def load_orders(source_table: pa.Table) -> None:
    catalog = get_catalog()

    catalog.create_namespace_if_not_exists(
        "reliability"
    )

    table = catalog.create_table_if_not_exists(
        TABLE_NAME,
        schema=ORDERS_SCHEMA,
    )

    if table.current_snapshot() is None:
        print("Iceberg table is empty — performing initial append")

        table.append(source_table)

    else:
        print(
            "Iceberg table already contains data — "
            "replacing baseline"
        )

        table.overwrite(source_table)

    table.refresh()

    target = table.scan().to_arrow()

    source_count = source_table.num_rows
    target_count = target.num_rows

    print("\n--- Initial Load Summary ---")
    print(f"Source rows : {source_count:,}")
    print(f"Iceberg rows: {target_count:,}")

    if source_count != target_count:
        raise RuntimeError(
            "Validation failed: source and Iceberg "
            "row counts do not match"
        )

    snapshot = table.current_snapshot()

    print("\n--- Iceberg Snapshot ---")

    if snapshot:
        print(f"Snapshot ID: {snapshot.snapshot_id}")
        print(
            f"Sequence number: "
            f"{snapshot.sequence_number}"
        )
        print(f"Summary: {snapshot.summary}")

    print("\nInitial load validation PASSED")


def main() -> None:
    print("Extracting orders from PostgreSQL...")

    source_table = extract_orders()

    print(
        f"Extracted {source_table.num_rows:,} rows"
    )

    print("Loading into Apache Iceberg...")

    load_orders(source_table)


if __name__ == "__main__":
    main()
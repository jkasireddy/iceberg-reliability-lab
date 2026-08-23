from datetime import datetime

import pyarrow as pa
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    DoubleType,
    LongType,
    NestedField,
    StringType,
    TimestampType,
)


def get_catalog():
    return load_catalog(
        "local",
        type="rest",
        uri="http://localhost:8181",
        **{
            "s3.endpoint": "http://localhost:9000",
            "s3.access-key-id": "admin",
            "s3.secret-access-key": "password",
            "s3.region": "us-east-1",
        },
    )


def main():
    catalog = get_catalog()

    print("Connected to Iceberg REST catalog")

    # Create namespace if it does not already exist.
    catalog.create_namespace_if_not_exists("demo")

    print("Namespace ready: demo")

    iceberg_schema = Schema(
        NestedField(
            field_id=1,
            name="order_id",
            field_type=LongType(),
            required=True,
        ),
        NestedField(
            field_id=2,
            name="customer_id",
            field_type=LongType(),
            required=True,
        ),
        NestedField(
            field_id=3,
            name="order_timestamp",
            field_type=TimestampType(),
            required=True,
        ),
        NestedField(
            field_id=4,
            name="state",
            field_type=StringType(),
            required=True,
        ),
        NestedField(
            field_id=5,
            name="total_amount",
            field_type=DoubleType(),
            required=True,
        ),
        NestedField(
            field_id=6,
            name="status",
            field_type=StringType(),
            required=True,
        ),
    )

    table = catalog.create_table_if_not_exists(
        identifier="demo.orders",
        schema=iceberg_schema,
    )

    print(f"Table ready: {table.name()}")

    arrow_schema = pa.schema(
        [
            pa.field("order_id", pa.int64(), nullable=False),
            pa.field("customer_id", pa.int64(), nullable=False),
            pa.field(
                "order_timestamp",
                pa.timestamp("us"),
                nullable=False,
            ),
            pa.field("state", pa.string(), nullable=False),
            pa.field("total_amount", pa.float64(), nullable=False),
            pa.field("status", pa.string(), nullable=False),
        ]
    )

    data = pa.Table.from_pylist(
        [
            {
                "order_id": 1001,
                "customer_id": 501,
                "order_timestamp": datetime(2026, 8, 22, 10, 15),
                "state": "MD",
                "total_amount": 149.99,
                "status": "COMPLETED",
            },
            {
                "order_id": 1002,
                "customer_id": 502,
                "order_timestamp": datetime(2026, 8, 22, 10, 20),
                "state": "VA",
                "total_amount": 79.50,
                "status": "COMPLETED",
            },
            {
                "order_id": 1003,
                "customer_id": 503,
                "order_timestamp": datetime(2026, 8, 22, 10, 25),
                "state": "DC",
                "total_amount": 225.00,
                "status": "PENDING",
            },
        ],
        schema=arrow_schema,
    )

    # Only append data if table is currently empty.
    existing = table.scan().to_arrow()

    if existing.num_rows == 0:
        table.append(data)
        print(f"Appended {data.num_rows} rows")
    else:
        print(f"Table already contains {existing.num_rows} rows; skipping bootstrap append")

    # Reload after commit.
    table.refresh()

    result = table.scan().to_arrow()

    print("\n--- Data ---")
    print(result)

    print("\n--- Iceberg information ---")
    print(f"Rows: {result.num_rows}")
    print(f"Table location: {table.location()}")

    snapshot = table.current_snapshot()

    if snapshot:
        print(f"Snapshot ID: {snapshot.snapshot_id}")
        print(f"Sequence number: {snapshot.sequence_number}")
        print(f"Snapshot summary: {snapshot.summary}")

    print("\nMilestone 1 complete!")


if __name__ == "__main__":
    main()

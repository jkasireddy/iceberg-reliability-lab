from __future__ import annotations

import pyarrow as pa

from src.iceberg_lab.catalog import get_catalog
from src.iceberg_lab.orders import (
    ICEBERG_NAMESPACE,
    ICEBERG_TABLE,
    ORDERS_SCHEMA,
)
from src.iceberg_lab.source import fetch_all_orders
from src.iceberg_lab.table_stats import (
    metadata_record_count,
)


def load_orders(
    source_table: pa.Table,
) -> None:
    catalog = get_catalog()

    catalog.create_namespace_if_not_exists(ICEBERG_NAMESPACE)

    table = catalog.create_table_if_not_exists(
        ICEBERG_TABLE,
        schema=ORDERS_SCHEMA,
    )

    if table.current_snapshot() is None:
        print("Iceberg table is empty — performing initial append")

        table.append(source_table)

    else:
        print("Iceberg table already contains data — replacing baseline")

        table.overwrite(source_table)

    table.refresh()

    source_count = source_table.num_rows

    target_count = metadata_record_count(table)

    print("\n--- Initial Load Summary ---")
    print(f"Source rows          : {source_count:,}")
    print(f"Iceberg metadata rows: {target_count:,}")

    if source_count != target_count:
        raise RuntimeError("Validation failed: source and Iceberg row counts do not match")

    snapshot = table.current_snapshot()

    print("\n--- Iceberg Snapshot ---")

    if snapshot:
        print(f"Snapshot ID    : {snapshot.snapshot_id}")
        print(f"Sequence number: {snapshot.sequence_number}")
        print(f"Summary        : {snapshot.summary}")

    print("\nInitial load validation PASSED")


def main() -> None:
    print("Extracting orders from PostgreSQL...")

    source_table = fetch_all_orders()

    print(f"Extracted {source_table.num_rows:,} rows")

    print("Loading into Apache Iceberg...")

    load_orders(source_table)


if __name__ == "__main__":
    main()

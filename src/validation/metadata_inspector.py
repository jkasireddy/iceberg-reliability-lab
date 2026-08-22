from __future__ import annotations

from typing import Any

from src.iceberg_lab.catalog import get_catalog


TABLE_NAME = "reliability.orders"


def aggregate_metric(
    data_files: list[dict[str, Any]],
    column: str,
) -> dict[str, Any]:
    value_counts: list[int] = []
    null_counts: list[int] = []
    nan_counts: list[int] = []
    lower_bounds: list[Any] = []
    upper_bounds: list[Any] = []

    for data_file in data_files:
        metrics = data_file.get("readable_metrics") or {}
        column_metrics = metrics.get(column) or {}

        if column_metrics.get("value_count") is not None:
            value_counts.append(
                column_metrics["value_count"]
            )

        if column_metrics.get("null_value_count") is not None:
            null_counts.append(
                column_metrics["null_value_count"]
            )

        if column_metrics.get("nan_value_count") is not None:
            nan_counts.append(
                column_metrics["nan_value_count"]
            )

        if column_metrics.get("lower_bound") is not None:
            lower_bounds.append(
                column_metrics["lower_bound"]
            )

        if column_metrics.get("upper_bound") is not None:
            upper_bounds.append(
                column_metrics["upper_bound"]
            )

    return {
        "value_count": (
            sum(value_counts)
            if value_counts
            else None
        ),
        "null_count": (
            sum(null_counts)
            if null_counts
            else None
        ),
        "nan_count": (
            sum(nan_counts)
            if nan_counts
            else None
        ),
        "lower_bound": (
            min(lower_bounds)
            if lower_bounds
            else None
        ),
        "upper_bound": (
            max(upper_bounds)
            if upper_bounds
            else None
        ),
    }


def print_snapshots(table) -> None:
    snapshots = table.inspect.snapshots().to_pylist()

    print("\n=== SNAPSHOT HISTORY ===")

    for snapshot in snapshots:
        marker = (
            " <-- CURRENT"
            if snapshot["snapshot_id"]
            == table.current_snapshot().snapshot_id
            else ""
        )

        print(
            f"{snapshot['committed_at']} | "
            f"{snapshot['snapshot_id']} | "
            f"{snapshot['operation']}"
            f"{marker}"
        )


def print_manifests(table) -> None:
    manifests = table.inspect.manifests().to_pylist()

    print("\n=== CURRENT MANIFESTS ===")
    print(f"Manifest count: {len(manifests)}")

    for manifest in manifests:
        print(
            f"Added files: "
            f"{manifest['added_data_files_count']} | "
            f"Existing files: "
            f"{manifest['existing_data_files_count']} | "
            f"Deleted files: "
            f"{manifest['deleted_data_files_count']}"
        )


def print_file_summary(table) -> list[dict[str, Any]]:
    data_files = table.inspect.data_files().to_pylist()

    total_records = sum(
        data_file["record_count"]
        for data_file in data_files
    )

    total_bytes = sum(
        data_file["file_size_in_bytes"]
        for data_file in data_files
    )

    print("\n=== CURRENT ICEBERG DATA FILES ===")
    print(f"Data files       : {len(data_files)}")
    print(f"Metadata records : {total_records:,}")
    print(f"Physical bytes   : {total_bytes:,}")

    for index, data_file in enumerate(
        data_files,
        start=1,
    ):
        print(
            f"\nFile {index}:"
            f"\n  Records: {data_file['record_count']:,}"
            f"\n  Size   : "
            f"{data_file['file_size_in_bytes']:,} bytes"
            f"\n  Path   : {data_file['file_path']}"
        )

    return data_files


def print_column_metrics(
    data_files: list[dict[str, Any]],
) -> None:
    columns = [
        "order_id",
        "customer_id",
        "order_timestamp",
        "state",
        "product_category",
        "quantity",
        "unit_price",
        "total_amount",
        "payment_type",
        "status",
        "updated_at",
    ]

    print("\n=== FILE-LEVEL COLUMN METRICS ===")

    for column in columns:
        metrics = aggregate_metric(
            data_files,
            column,
        )

        print(f"\n{column}")
        print(
            f"  value count : "
            f"{metrics['value_count']}"
        )
        print(
            f"  null count  : "
            f"{metrics['null_count']}"
        )
        print(
            f"  NaN count   : "
            f"{metrics['nan_count']}"
        )
        print(
            f"  lower bound : "
            f"{metrics['lower_bound']}"
        )
        print(
            f"  upper bound : "
            f"{metrics['upper_bound']}"
        )


def main() -> None:
    catalog = get_catalog()

    table = catalog.load_table(TABLE_NAME)

    print("===================================")
    print("     ICEBERG METADATA INSPECTOR")
    print("===================================")

    print(f"\nTable    : {TABLE_NAME}")
    print(f"Location : {table.location()}")
    print(f"Format   : Iceberg v{table.format_version}")

    current_snapshot = table.current_snapshot()

    if current_snapshot:
        print(
            f"Snapshot : "
            f"{current_snapshot.snapshot_id}"
        )

    print_snapshots(table)
    print_manifests(table)

    data_files = print_file_summary(table)

    print_column_metrics(data_files)

    print("\n===================================")
    print("Metadata inspection complete")
    print("===================================")


if __name__ == "__main__":
    main()
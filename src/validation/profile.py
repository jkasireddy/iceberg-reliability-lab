from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from src.validation.metrics import (
    TRACKED_COLUMNS,
    aggregate_column_metrics,
)


def normalize(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, (Decimal, datetime, date)):
        return str(value)

    return str(value)


def build_profile(table, snapshot_id: int | None = None) -> dict[str, Any]:
    if snapshot_id is None:
        snapshot = table.current_snapshot()

        if snapshot is None:
            raise RuntimeError("Table has no snapshot")

        snapshot_id = snapshot.snapshot_id

    data_files = table.inspect.data_files(snapshot_id=snapshot_id).to_pylist()

    metrics = {}

    for column in TRACKED_COLUMNS:
        raw_metrics = aggregate_column_metrics(
            data_files,
            column,
        )

        metrics[column] = {key: normalize(value) for key, value in raw_metrics.items()}

    return {
        "snapshot_id": snapshot_id,
        "file_count": len(data_files),
        "record_count": sum(data_file["record_count"] for data_file in data_files),
        "file_size_in_bytes": sum(data_file["file_size_in_bytes"] for data_file in data_files),
        "metrics": metrics,
    }

from __future__ import annotations

from typing import Any

from src.iceberg_lab.orders import ORDERS_SCHEMA

TRACKED_COLUMNS = tuple(ORDERS_SCHEMA.names)


def aggregate_column_metrics(
    data_files: list[dict[str, Any]],
    column: str,
) -> dict[str, Any]:
    value_counts: list[int] = []
    null_counts: list[int] = []
    nan_counts: list[int] = []
    lower_bounds: list[Any] = []
    upper_bounds: list[Any] = []

    for data_file in data_files:
        readable_metrics = data_file.get("readable_metrics") or {}

        column_metrics = readable_metrics.get(column) or {}

        value_count = column_metrics.get("value_count")
        null_count = column_metrics.get("null_value_count")
        nan_count = column_metrics.get("nan_value_count")
        lower_bound = column_metrics.get("lower_bound")
        upper_bound = column_metrics.get("upper_bound")

        if value_count is not None:
            value_counts.append(value_count)

        if null_count is not None:
            null_counts.append(null_count)

        if nan_count is not None:
            nan_counts.append(nan_count)

        if lower_bound is not None:
            lower_bounds.append(lower_bound)

        if upper_bound is not None:
            upper_bounds.append(upper_bound)

    return {
        "value_count": (sum(value_counts) if value_counts else None),
        "null_count": (sum(null_counts) if null_counts else None),
        "nan_count": (sum(nan_counts) if nan_counts else None),
        "lower_bound": (min(lower_bounds) if lower_bounds else None),
        "upper_bound": (max(upper_bounds) if upper_bounds else None),
    }

from src.validation.metrics import (
    TRACKED_COLUMNS,
    aggregate_column_metrics,
)


def test_aggregate_column_metrics_across_files() -> None:
    data_files = [
        {
            "readable_metrics": {
                "quantity": {
                    "value_count": 6000,
                    "null_value_count": 0,
                    "nan_value_count": None,
                    "lower_bound": 1,
                    "upper_bound": 5,
                }
            }
        },
        {
            "readable_metrics": {
                "quantity": {
                    "value_count": 4000,
                    "null_value_count": 2,
                    "nan_value_count": None,
                    "lower_bound": 2,
                    "upper_bound": 999,
                }
            }
        },
    ]

    result = aggregate_column_metrics(
        data_files,
        "quantity",
    )

    assert result == {
        "value_count": 10_000,
        "null_count": 2,
        "nan_count": None,
        "lower_bound": 1,
        "upper_bound": 999,
    }


def test_aggregate_column_metrics_handles_missing_values() -> None:
    data_files = [{"readable_metrics": {}}]

    result = aggregate_column_metrics(
        data_files,
        "quantity",
    )

    assert result == {
        "value_count": None,
        "null_count": None,
        "nan_count": None,
        "lower_bound": None,
        "upper_bound": None,
    }


def test_tracked_columns_follow_order_schema() -> None:
    assert "order_id" in TRACKED_COLUMNS
    assert "quantity" in TRACKED_COLUMNS
    assert "total_amount" in TRACKED_COLUMNS
    assert "updated_at" in TRACKED_COLUMNS

    assert len(TRACKED_COLUMNS) == 11

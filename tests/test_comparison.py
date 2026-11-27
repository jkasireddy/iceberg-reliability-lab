from src.validation.comparison import (
    compare_profiles,
)


def profile(
    *,
    snapshot_id: int,
    record_count: int = 10_000,
    quantity_max: int = 5,
    amount_max: str = "2499.00",
    state_max: str = "VA",
) -> dict:
    return {
        "snapshot_id": snapshot_id,
        "record_count": record_count,
        "metrics": {
            "quantity": {
                "null_count": 0,
                "lower_bound": 1,
                "upper_bound": quantity_max,
            },
            "total_amount": {
                "null_count": 0,
                "lower_bound": "5.13",
                "upper_bound": amount_max,
            },
            "state": {
                "null_count": 0,
                "lower_bound": "DC",
                "upper_bound": state_max,
            },
            "updated_at": {
                "null_count": 0,
                "lower_bound": "2026-08-01 00:20:38",
                "upper_bound": "2026-08-15 03:35:58",
            },
        },
    }


def test_identical_profiles_have_no_drift() -> None:
    baseline = profile(snapshot_id=1)

    current = profile(snapshot_id=2)

    result = compare_profiles(
        baseline,
        current,
    )

    assert result.row_count_matches
    assert not result.has_metadata_drift
    assert result.changed_metrics == ()


def test_metadata_drift_detected_when_row_count_matches() -> None:
    baseline = profile(snapshot_id=1)

    current = profile(
        snapshot_id=2,
        quantity_max=999,
        amount_max="999999.99",
        state_max="ZZ",
    )

    result = compare_profiles(
        baseline,
        current,
    )

    assert result.row_count_matches
    assert result.has_metadata_drift

    changed = {
        (
            change.column,
            change.metric,
        )
        for change in result.changed_metrics
    }

    assert (
        "quantity",
        "upper_bound",
    ) in changed

    assert (
        "total_amount",
        "upper_bound",
    ) in changed

    assert (
        "state",
        "upper_bound",
    ) in changed


def test_row_count_difference_is_detected() -> None:
    baseline = profile(
        snapshot_id=1,
        record_count=10_000,
    )

    current = profile(
        snapshot_id=2,
        record_count=10_500,
    )

    result = compare_profiles(
        baseline,
        current,
    )

    assert not result.row_count_matches

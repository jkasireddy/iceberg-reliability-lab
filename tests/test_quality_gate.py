from src.validation.quality_gate import (
    evaluate_profile,
    failed_results,
)


def healthy_profile() -> dict:
    return {
        "metrics": {
            "quantity": {
                "upper_bound": 5,
                "null_count": 0,
            },
            "total_amount": {
                "upper_bound": "2499.00",
                "null_count": 0,
            },
            "state": {
                "upper_bound": "VA",
            },
        }
    }


def corrupted_profile() -> dict:
    return {
        "metrics": {
            "quantity": {
                "upper_bound": 999,
                "null_count": 0,
            },
            "total_amount": {
                "upper_bound": "999999.99",
                "null_count": 0,
            },
            "state": {
                "upper_bound": "ZZ",
            },
        }
    }


def test_healthy_profile_passes_quality_gate() -> None:
    results = evaluate_profile(healthy_profile())

    assert len(results) == 5
    assert failed_results(results) == []


def test_corrupted_profile_fails_expected_rules() -> None:
    results = evaluate_profile(corrupted_profile())

    failures = failed_results(results)

    assert len(failures) == 3

    failed_columns = {result.column for result in failures}

    assert failed_columns == {
        "quantity",
        "total_amount",
        "state",
    }


def test_null_spike_fails_quality_gate() -> None:
    profile = healthy_profile()

    profile["metrics"]["quantity"]["null_count"] = 25

    results = evaluate_profile(profile)

    failures = failed_results(results)

    assert len(failures) == 1
    assert failures[0].column == "quantity"
    assert failures[0].rule == "null_count"

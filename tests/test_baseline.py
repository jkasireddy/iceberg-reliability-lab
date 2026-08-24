from src.validation import baseline as baseline_module


def test_save_and_load_baseline(
    tmp_path,
    monkeypatch,
) -> None:
    path = tmp_path / "baseline.json"

    monkeypatch.setattr(
        baseline_module,
        "BASELINE_PATH",
        path,
    )

    profile = {
        "snapshot_id": 123,
        "record_count": 10_000,
        "file_count": 1,
        "metrics": {
            "quantity": {
                "upper_bound": 5,
            }
        },
    }

    baseline_module.save_baseline(profile)

    loaded = baseline_module.load_baseline()

    assert loaded == profile


def test_load_baseline_fails_when_missing(
    tmp_path,
    monkeypatch,
) -> None:
    path = tmp_path / "missing.json"

    monkeypatch.setattr(
        baseline_module,
        "BASELINE_PATH",
        path,
    )

    try:
        baseline_module.load_baseline()
    except RuntimeError as exc:
        assert "Baseline not found" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")


def test_delete_baseline(
    tmp_path,
    monkeypatch,
) -> None:
    path = tmp_path / "baseline.json"

    path.write_text("{}")

    monkeypatch.setattr(
        baseline_module,
        "BASELINE_PATH",
        path,
    )

    baseline_module.delete_baseline()

    assert not path.exists()

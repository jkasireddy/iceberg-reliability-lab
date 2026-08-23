from datetime import datetime

import pyarrow as pa
import pytest

from src.ingestion import batch as batch_module


def sample_batch() -> pa.Table:
    return pa.table(
        {
            "order_id": [
                101,
                102,
            ],
            "updated_at": [
                datetime(
                    2026,
                    8,
                    16,
                    12,
                    0,
                    0,
                ),
                datetime(
                    2026,
                    8,
                    16,
                    12,
                    5,
                    0,
                ),
            ],
        }
    )


def test_save_and_load_batch(
    tmp_path,
    monkeypatch,
) -> None:
    parquet_path = tmp_path / "batch.parquet"
    metadata_path = tmp_path / "batch.json"

    monkeypatch.setattr(
        batch_module,
        "BATCH_PATH",
        parquet_path,
    )

    monkeypatch.setattr(
        batch_module,
        "BATCH_METADATA_PATH",
        metadata_path,
    )

    original = sample_batch()

    saved_metadata = batch_module.save_batch(original)

    loaded_batch, loaded_metadata = batch_module.load_batch()

    assert loaded_batch.num_rows == 2

    assert saved_metadata.rows == 2

    assert saved_metadata.order_id == 102

    assert loaded_metadata.order_id == 102

    assert loaded_metadata.updated_at == datetime(
        2026,
        8,
        16,
        12,
        5,
        0,
    )


def test_clear_batch_removes_artifacts(
    tmp_path,
    monkeypatch,
) -> None:
    parquet_path = tmp_path / "batch.parquet"
    metadata_path = tmp_path / "batch.json"

    parquet_path.write_text("stale batch")

    metadata_path.write_text("stale metadata")

    monkeypatch.setattr(
        batch_module,
        "BATCH_PATH",
        parquet_path,
    )

    monkeypatch.setattr(
        batch_module,
        "BATCH_METADATA_PATH",
        metadata_path,
    )

    batch_module.clear_batch()

    assert not parquet_path.exists()
    assert not metadata_path.exists()


def test_empty_batch_cannot_be_saved(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        batch_module,
        "BATCH_PATH",
        tmp_path / "batch.parquet",
    )

    monkeypatch.setattr(
        batch_module,
        "BATCH_METADATA_PATH",
        tmp_path / "batch.json",
    )

    empty = pa.table(
        {
            "order_id": pa.array(
                [],
                type=pa.int64(),
            ),
            "updated_at": pa.array(
                [],
                type=pa.timestamp("us"),
            ),
        }
    )

    with pytest.raises(
        ValueError,
        match="empty incremental batch",
    ):
        batch_module.save_batch(empty)

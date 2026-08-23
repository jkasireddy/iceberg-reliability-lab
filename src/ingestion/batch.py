from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

BATCH_PATH = Path("artifacts/incremental_batch.parquet")

BATCH_METADATA_PATH = Path("artifacts/incremental_batch.json")


@dataclass(frozen=True)
class BatchMetadata:
    rows: int
    updated_at: datetime
    order_id: int


def clear_batch() -> None:
    BATCH_PATH.unlink(missing_ok=True)
    BATCH_METADATA_PATH.unlink(missing_ok=True)


def save_batch(
    batch: pa.Table,
) -> BatchMetadata:
    if batch.num_rows == 0:
        raise ValueError("Cannot save an empty incremental batch")

    BATCH_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    updated_at = batch["updated_at"][batch.num_rows - 1].as_py()

    order_id = int(batch["order_id"][batch.num_rows - 1].as_py())

    metadata = BatchMetadata(
        rows=batch.num_rows,
        updated_at=updated_at,
        order_id=order_id,
    )

    pq.write_table(
        batch,
        BATCH_PATH,
    )

    BATCH_METADATA_PATH.write_text(
        json.dumps(
            {
                "rows": metadata.rows,
                "high_watermark": {
                    "updated_at": (metadata.updated_at.isoformat()),
                    "order_id": metadata.order_id,
                },
            },
            indent=2,
        )
    )

    return metadata


def load_batch() -> tuple[pa.Table, BatchMetadata]:
    if not BATCH_PATH.exists():
        raise RuntimeError("Incremental batch does not exist. Run the extractor first.")

    if not BATCH_METADATA_PATH.exists():
        raise RuntimeError("Incremental batch metadata does not exist.")

    batch = pq.read_table(BATCH_PATH)

    raw_metadata = json.loads(BATCH_METADATA_PATH.read_text())

    high_watermark = raw_metadata["high_watermark"]

    metadata = BatchMetadata(
        rows=int(raw_metadata["rows"]),
        updated_at=datetime.fromisoformat(high_watermark["updated_at"]),
        order_id=int(high_watermark["order_id"]),
    )

    if metadata.rows != batch.num_rows:
        raise RuntimeError("Incremental batch metadata row count does not match the Parquet batch")

    return batch, metadata

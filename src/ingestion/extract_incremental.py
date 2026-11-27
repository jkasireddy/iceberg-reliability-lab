from __future__ import annotations

from src.iceberg_lab.source import (
    fetch_orders_after,
)
from src.ingestion.batch import (
    BATCH_METADATA_PATH,
    BATCH_PATH,
    clear_batch,
    save_batch,
)
from src.ingestion.watermark import (
    get_watermark,
)


def main() -> None:
    last_updated_at, last_order_id = get_watermark()

    print("Current watermark")
    print(f"  updated_at : {last_updated_at}")
    print(f"  order_id   : {last_order_id}")

    batch = fetch_orders_after(
        last_updated_at,
        last_order_id,
    )

    print(f"\nIncremental rows extracted: {batch.num_rows:,}")

    if batch.num_rows == 0:
        clear_batch()

        print("Nothing new to process.")
        print("Any stale incremental batch artifacts were removed.")

        return

    metadata = save_batch(batch)

    print(f"Batch file     : {BATCH_PATH}")

    print(f"Batch metadata : {BATCH_METADATA_PATH}")

    print("\nBatch high watermark")

    print(f"  updated_at : {metadata.updated_at}")

    print(f"  order_id   : {metadata.order_id}")

    print("\nWatermark has NOT been advanced yet.")


if __name__ == "__main__":
    main()

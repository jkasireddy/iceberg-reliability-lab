from __future__ import annotations

import json
from pathlib import Path

from src.iceberg_lab.catalog import get_catalog
from src.validation.profile import build_profile

TABLE_NAME = "reliability.orders"
BASELINE_PATH = Path("artifacts/baseline.json")


def main() -> None:
    catalog = get_catalog()

    table = catalog.load_table(TABLE_NAME)

    profile = build_profile(table)

    BASELINE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with BASELINE_PATH.open("w") as file:
        json.dump(
            profile,
            file,
            indent=2,
        )

    print("Healthy baseline captured")
    print(f"Snapshot ID : {profile['snapshot_id']}")
    print(f"Records     : {profile['record_count']:,}")
    print(f"Files       : {profile['file_count']}")
    print(f"Saved to    : {BASELINE_PATH}")


if __name__ == "__main__":
    main()

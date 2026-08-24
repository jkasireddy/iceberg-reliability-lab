from __future__ import annotations

from src.iceberg_lab.catalog import get_catalog
from src.iceberg_lab.orders import ICEBERG_TABLE
from src.validation.baseline import (
    BASELINE_PATH,
    save_baseline,
)
from src.validation.profile import build_profile


def main() -> None:
    catalog = get_catalog()

    table = catalog.load_table(ICEBERG_TABLE)

    profile = build_profile(table)

    save_baseline(profile)

    print("Healthy baseline captured")
    print(f"Snapshot ID : {profile['snapshot_id']}")
    print(f"Records     : {profile['record_count']:,}")
    print(f"Files       : {profile['file_count']}")
    print(f"Saved to    : {BASELINE_PATH}")


if __name__ == "__main__":
    main()

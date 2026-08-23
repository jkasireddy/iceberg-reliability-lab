import pyarrow as pa

from src.iceberg_lab.table_stats import (
    metadata_record_count,
)


class FakeInspect:
    def data_files(self) -> pa.Table:
        return pa.Table.from_pylist(
            [
                {
                    "record_count": 4000,
                },
                {
                    "record_count": 3500,
                },
                {
                    "record_count": 2500,
                },
            ]
        )


class FakeTable:
    inspect = FakeInspect()


def test_metadata_record_count_sums_data_files() -> None:
    table = FakeTable()

    assert metadata_record_count(table) == 10_000

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyiceberg.table import Table


def metadata_record_count(
    table: Table,
) -> int:
    """
    Sum record_count from the table's current Iceberg data files.

    This reads Iceberg metadata rather than scanning the
    underlying table rows.

    For this lab we use copy-on-write updates, so this is a
    suitable current-row proxy. With merge-on-read delete files,
    data-file record counts alone would not represent the final
    visible row count.
    """

    data_files = table.inspect.data_files().to_pylist()

    return sum(data_file["record_count"] for data_file in data_files)

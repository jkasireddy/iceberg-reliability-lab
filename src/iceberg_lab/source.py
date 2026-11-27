from __future__ import annotations

from datetime import datetime

import psycopg
import pyarrow as pa

from src.config import postgres_connection_string
from src.iceberg_lab.orders import ORDERS_SCHEMA

ORDER_COLUMNS = """
    order_id,
    customer_id,
    order_timestamp,
    state,
    product_category,
    quantity,
    unit_price,
    total_amount,
    payment_type,
    status,
    updated_at
"""


def _cursor_to_arrow(cursor: psycopg.Cursor) -> pa.Table:
    if cursor.description is None:
        raise RuntimeError("Query did not return a result set")

    columns = [description.name for description in cursor.description]

    records = [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]

    return pa.Table.from_pylist(
        records,
        schema=ORDERS_SCHEMA,
    )


def fetch_all_orders() -> pa.Table:
    with psycopg.connect(postgres_connection_string()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    {ORDER_COLUMNS}
                FROM orders
                ORDER BY order_id
                """
            )

            return _cursor_to_arrow(cursor)


def fetch_orders_after(
    last_updated_at: datetime,
    last_order_id: int,
) -> pa.Table:
    with psycopg.connect(postgres_connection_string()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    {ORDER_COLUMNS}
                FROM orders
                WHERE
                    (updated_at, order_id)
                    > (%s, %s)
                ORDER BY
                    updated_at,
                    order_id
                """,
                (
                    last_updated_at,
                    last_order_id,
                ),
            )

            return _cursor_to_arrow(cursor)


def count_orders() -> int:
    with psycopg.connect(postgres_connection_string()) as conn:
        result = conn.execute("SELECT COUNT(*) FROM orders").fetchone()

    if result is None:
        raise RuntimeError("Unable to determine PostgreSQL order count")

    return int(result[0])


def source_high_watermark() -> tuple[datetime, int]:
    with psycopg.connect(postgres_connection_string()) as conn:
        result = conn.execute(
            """
            SELECT
                updated_at,
                order_id
            FROM orders
            ORDER BY
                updated_at DESC,
                order_id DESC
            LIMIT 1
            """
        ).fetchone()

    if result is None:
        raise RuntimeError("Cannot determine watermark: orders is empty")

    return result[0], int(result[1])

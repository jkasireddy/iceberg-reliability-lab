from __future__ import annotations

from datetime import datetime

import psycopg

from src.config import postgres_connection_string
from src.iceberg_lab.source import source_high_watermark

PIPELINE_NAME = "orders_to_iceberg"


def ensure_control_table(conn: psycopg.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pipeline_watermarks (
            pipeline_name TEXT PRIMARY KEY,
            last_updated_at TIMESTAMP NOT NULL,
            last_order_id BIGINT NOT NULL,
            watermark_updated_at TIMESTAMP NOT NULL
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def initialize_watermark() -> tuple[datetime, int]:
    """
    Mark the current source high-watermark as already processed.

    This should be called after the baseline/full load.
    """
    last_updated_at, last_order_id = source_high_watermark()

    with psycopg.connect(postgres_connection_string()) as conn:
        ensure_control_table(conn)

        conn.execute(
            """
            INSERT INTO pipeline_watermarks (
                pipeline_name,
                last_updated_at,
                last_order_id
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (pipeline_name)
            DO UPDATE SET
                last_updated_at = EXCLUDED.last_updated_at,
                last_order_id = EXCLUDED.last_order_id,
                watermark_updated_at = CURRENT_TIMESTAMP
            """,
            (
                PIPELINE_NAME,
                last_updated_at,
                last_order_id,
            ),
        )

        return last_updated_at, last_order_id


def get_watermark() -> tuple[datetime, int]:
    with psycopg.connect(postgres_connection_string()) as conn:
        ensure_control_table(conn)

        result = conn.execute(
            """
            SELECT
                last_updated_at,
                last_order_id
            FROM pipeline_watermarks
            WHERE pipeline_name = %s
            """,
            (PIPELINE_NAME,),
        ).fetchone()

        if result is None:
            raise RuntimeError("Pipeline watermark has not been initialized")

        return result[0], result[1]


def advance_watermark(
    last_updated_at: datetime,
    last_order_id: int,
) -> None:
    with psycopg.connect(postgres_connection_string()) as conn:
        ensure_control_table(conn)

        conn.execute(
            """
            UPDATE pipeline_watermarks
            SET
                last_updated_at = %s,
                last_order_id = %s,
                watermark_updated_at = CURRENT_TIMESTAMP
            WHERE pipeline_name = %s
            """,
            (
                last_updated_at,
                last_order_id,
                PIPELINE_NAME,
            ),
        )


def main() -> None:
    last_updated_at, last_order_id = initialize_watermark()

    print("Pipeline watermark initialized")
    print(f"Pipeline        : {PIPELINE_NAME}")
    print(f"Updated at      : {last_updated_at}")
    print(f"Order ID        : {last_order_id}")


if __name__ == "__main__":
    main()

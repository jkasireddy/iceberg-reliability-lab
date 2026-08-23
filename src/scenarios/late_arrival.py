from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import psycopg

from src.config import postgres_connection_string
from src.ingestion.watermark import get_watermark


LATE_ORDER_ID = 20001


def main() -> None:
    last_updated_at, last_order_id = get_watermark()

    with psycopg.connect(
        postgres_connection_string()
    ) as conn:

        result = conn.execute(
            """
            SELECT MAX(order_timestamp)
            FROM orders
            """
        ).fetchone()

        if result is None or result[0] is None:
            raise RuntimeError(
                "Cannot determine baseline event-time cutoff"
            )

        baseline_event_cutoff = result[0]

        #
        # The order actually happened seven days
        # BEFORE the latest event time we already processed.
        #
        late_order_timestamp = (
            baseline_event_cutoff
            - timedelta(days=7)
        )

        #
        # But the source only receives/changes the record
        # AFTER our existing change watermark.
        #
        arrival_updated_at = (
            last_updated_at
            + timedelta(hours=6)
        )

        conn.execute(
            """
            INSERT INTO orders (
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
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (order_id)
            DO UPDATE SET
                customer_id =
                    EXCLUDED.customer_id,
                order_timestamp =
                    EXCLUDED.order_timestamp,
                state =
                    EXCLUDED.state,
                product_category =
                    EXCLUDED.product_category,
                quantity =
                    EXCLUDED.quantity,
                unit_price =
                    EXCLUDED.unit_price,
                total_amount =
                    EXCLUDED.total_amount,
                payment_type =
                    EXCLUDED.payment_type,
                status =
                    EXCLUDED.status,
                updated_at =
                    EXCLUDED.updated_at
            """,
            (
                LATE_ORDER_ID,
                18001,
                late_order_timestamp,
                "MD",
                "books",
                2,
                Decimal("49.99"),
                Decimal("99.98"),
                "credit_card",
                "COMPLETED",
                arrival_updated_at,
            ),
        )

        source_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM orders
            """
        ).fetchone()[0]

        #
        # BAD incremental strategy:
        # use business/event time as the cursor.
        #
        naive_event_time_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE order_timestamp > %s
            """,
            (baseline_event_cutoff,),
        ).fetchone()[0]

        #
        # OUR incremental strategy:
        # use change time + tie-breaker.
        #
        change_time_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE
                (updated_at, order_id)
                > (%s, %s)
            """,
            (
                last_updated_at,
                last_order_id,
            ),
        ).fetchone()[0]

    print("======================================")
    print("          LATE ARRIVAL SCENARIO")
    print("======================================")

    print(
        f"\nBaseline event cutoff : "
        f"{baseline_event_cutoff}"
    )

    print(
        f"Current CDC watermark : "
        f"{last_updated_at} / {last_order_id}"
    )

    print("\nLate-arriving order")
    print(
        f"  order_id        : {LATE_ORDER_ID}"
    )
    print(
        f"  order_timestamp : {late_order_timestamp}"
    )
    print(
        f"  updated_at      : {arrival_updated_at}"
    )

    print(
        f"\nSource rows       : {source_count:,}"
    )

    print("\n=== CURSOR COMPARISON ===")

    print(
        "Event-time cursor "
        f"would extract : {naive_event_time_count}"
    )

    print(
        "Change-time cursor "
        f"will extract  : {change_time_count}"
    )

    print("\n======================================")

    if (
        naive_event_time_count == 0
        and change_time_count == 1
    ):
        print(
            "LATE ARRIVAL WOULD BE MISSED "
            "BY EVENT-TIME WATERMARK"
        )
        print(
            "CHANGE-TIME WATERMARK "
            "CAPTURES IT"
        )
    else:
        print(
            "Unexpected scenario result — "
            "check source state."
        )

    print("======================================")


if __name__ == "__main__":
    main()
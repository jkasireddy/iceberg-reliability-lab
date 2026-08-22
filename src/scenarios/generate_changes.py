from __future__ import annotations

import random
from datetime import datetime, timedelta
from decimal import Decimal

import psycopg

from src.config import postgres_connection_string


RANDOM_SEED = 4242

STATES = [
    "MD",
    "VA",
    "DC",
    "PA",
    "DE",
    "NJ",
    "NY",
    "NC",
]

PRODUCT_CATEGORIES = [
    "electronics",
    "home",
    "grocery",
    "clothing",
    "sports",
    "books",
    "toys",
]

PAYMENT_TYPES = [
    "credit_card",
    "debit_card",
    "paypal",
    "apple_pay",
]


def generate_insert_rows() -> list[tuple]:
    random.seed(RANDOM_SEED)

    rows = []

    order_base_time = datetime(
        2026,
        8,
        15,
        12,
        0,
        0,
    )

    change_base_time = datetime(
        2026,
        8,
        16,
        12,
        0,
        0,
    )

    for order_id in range(10001, 10501):
        offset = order_id - 10001

        quantity = random.randint(1, 5)

        unit_price = Decimal(
            str(
                round(
                    random.uniform(5.00, 500.00),
                    2,
                )
            )
        )

        total_amount = unit_price * quantity

        rows.append(
            (
                order_id,
                random.randint(10000, 25000),
                order_base_time
                + timedelta(seconds=offset),
                random.choice(STATES),
                random.choice(PRODUCT_CATEGORIES),
                quantity,
                unit_price,
                total_amount,
                random.choice(PAYMENT_TYPES),
                "PENDING",
                change_base_time
                + timedelta(seconds=offset),
            )
        )

    return rows


def main() -> None:
    new_orders = generate_insert_rows()

    with psycopg.connect(postgres_connection_string()) as conn:

        # 200 existing rows receive an update.
        #
        # Give every changed row a deterministic timestamp
        # after the original baseline watermark.
        for order_id in range(1, 201):
            changed_at = (
                datetime(2026, 8, 16, 9, 0, 0)
                + timedelta(seconds=order_id)
            )

            conn.execute(
                """
                UPDATE orders
                SET
                    status = 'SHIPPED',
                    updated_at = %s
                WHERE order_id = %s
                """,
                (
                    changed_at,
                    order_id,
                ),
            )

        # 500 new orders.
        #
        # ON CONFLICT makes the scenario safe to rerun.
        with conn.cursor() as cur:
            cur.executemany(
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
                new_orders,
            )

        stats = conn.execute(
            """
            SELECT
                COUNT(*) AS row_count,
                MAX(order_id) AS max_order_id,
                MAX(updated_at) AS max_updated_at
            FROM orders
            """
        ).fetchone()

        print("Incremental source changes generated")
        print("Existing orders updated : 200")
        print("New orders inserted     : 500")
        print(f"Source row count        : {stats[0]:,}")
        print(f"Maximum order ID        : {stats[1]}")
        print(f"Latest updated_at       : {stats[2]}")


if __name__ == "__main__":
    main()
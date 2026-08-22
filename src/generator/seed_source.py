from __future__ import annotations

import argparse
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

import psycopg
from faker import Faker


RANDOM_SEED = 42

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

STATUSES = [
    "COMPLETED",
    "COMPLETED",
    "COMPLETED",
    "COMPLETED",
    "PENDING",
    "SHIPPED",
    "CANCELLED",
]


def connection_string() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "orders")
    user = os.getenv("POSTGRES_USER", "lab")
    password = os.getenv("POSTGRES_PASSWORD", "lab_password")

    return (
        f"host={host} "
        f"port={port} "
        f"dbname={database} "
        f"user={user} "
        f"password={password}"
    )


def create_table(conn: psycopg.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id BIGINT PRIMARY KEY,
            customer_id BIGINT NOT NULL,
            order_timestamp TIMESTAMP NOT NULL,
            state VARCHAR(2) NOT NULL,
            product_category VARCHAR(50) NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price NUMERIC(10, 2) NOT NULL,
            total_amount NUMERIC(12, 2) NOT NULL,
            payment_type VARCHAR(30) NOT NULL,
            status VARCHAR(30) NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
        """
    )


def generate_orders(row_count: int) -> list[tuple]:
    random.seed(RANDOM_SEED)
    Faker.seed(RANDOM_SEED)

    fake = Faker()

    base_time = datetime(2026, 8, 1, 0, 0, 0)

    rows = []

    for index in range(1, row_count + 1):
        order_timestamp = base_time + timedelta(
            seconds=random.randint(0, 14 * 24 * 60 * 60)
        )

        updated_at = order_timestamp + timedelta(
            minutes=random.randint(0, 240)
        )

        quantity = random.randint(1, 5)

        unit_price = Decimal(
            str(round(random.uniform(5.00, 500.00), 2))
        )

        total_amount = unit_price * quantity

        rows.append(
            (
                index,
                random.randint(10000, 25000),
                order_timestamp,
                random.choice(STATES),
                random.choice(PRODUCT_CATEGORIES),
                quantity,
                unit_price,
                total_amount,
                random.choice(PAYMENT_TYPES),
                random.choice(STATUSES),
                updated_at,
            )
        )

    return rows


def seed(row_count: int) -> None:
    rows = generate_orders(row_count)

    with psycopg.connect(connection_string()) as conn:
        create_table(conn)

        conn.execute("TRUNCATE TABLE orders")

        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO orders (order_id,
                                    customer_id,
                                    order_timestamp,
                                    state,
                                    product_category,
                                    quantity,
                                    unit_price,
                                    total_amount,
                                    payment_type,
                                    status,
                                    updated_at)
                VALUES (%s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s)
                """,
                rows,
            )

        conn.commit()

        result = conn.execute(
            """
            SELECT
                COUNT(*) AS row_count,
                MIN(order_timestamp) AS min_order_timestamp,
                MAX(order_timestamp) AS max_order_timestamp,
                MIN(total_amount) AS min_amount,
                MAX(total_amount) AS max_amount
            FROM orders
            """
        ).fetchone()

        print("\nSource database seeded successfully")
        print(f"Rows: {result[0]:,}")
        print(f"Min order timestamp: {result[1]}")
        print(f"Max order timestamp: {result[2]}")
        print(f"Min total amount: {result[3]}")
        print(f"Max total amount: {result[4]}")


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--rows",
        type=int,
        default=10_000,
        help="Number of deterministic orders to generate",
    )

    args = parser.parse_args()

    seed(args.rows)


if __name__ == "__main__":
    main()
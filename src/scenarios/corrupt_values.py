from __future__ import annotations

import psycopg

from src.config import postgres_connection_string


def main() -> None:
    with psycopg.connect(postgres_connection_string()) as conn:
        amount_update = conn.execute(
            """
            UPDATE orders
            SET
                total_amount = 999999.99,
                updated_at = TIMESTAMP '2026-08-20 12:00:00'
            WHERE order_id BETWEEN 1 AND 100
            """
        )

        quantity_update = conn.execute(
            """
            UPDATE orders
            SET
                quantity = 999,
                updated_at = TIMESTAMP '2026-08-20 12:00:00'
            WHERE order_id BETWEEN 101 AND 200
            """
        )

        state_update = conn.execute(
            """
            UPDATE orders
            SET
                state = 'ZZ',
                updated_at = TIMESTAMP '2026-08-20 12:00:00'
            WHERE order_id BETWEEN 201 AND 300
            """
        )

        conn.commit()

        row_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

        print("Injected controlled corruption")
        print(f"Invalid total_amount rows : {amount_update.rowcount}")
        print(f"Invalid quantity rows     : {quantity_update.rowcount}")
        print(f"Invalid state rows        : {state_update.rowcount}")

        print(f"\nSource row count          : {row_count:,}")

        print("\nImportant: row count is still unchanged.")


if __name__ == "__main__":
    main()

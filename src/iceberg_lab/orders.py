from __future__ import annotations

import pyarrow as pa

ICEBERG_NAMESPACE = "reliability"
ICEBERG_TABLE = f"{ICEBERG_NAMESPACE}.orders"
SOURCE_TABLE = "orders"
ORDER_KEY = "order_id"


ORDERS_SCHEMA = pa.schema(
    [
        pa.field("order_id", pa.int64(), nullable=False),
        pa.field("customer_id", pa.int64(), nullable=False),
        pa.field("order_timestamp", pa.timestamp("us"), nullable=False),
        pa.field("state", pa.string(), nullable=False),
        pa.field("product_category", pa.string(), nullable=False),
        pa.field("quantity", pa.int32(), nullable=False),
        pa.field("unit_price", pa.decimal128(10, 2), nullable=False),
        pa.field("total_amount", pa.decimal128(12, 2), nullable=False),
        pa.field("payment_type", pa.string(), nullable=False),
        pa.field("status", pa.string(), nullable=False),
        pa.field("updated_at", pa.timestamp("us"), nullable=False),
    ]
)

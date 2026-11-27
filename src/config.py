from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def postgres_connection_string() -> str:
    return (
        f"host={os.getenv('POSTGRES_HOST', 'localhost')} "
        f"port={os.getenv('POSTGRES_PORT', '5432')} "
        f"dbname={os.getenv('POSTGRES_DB', 'orders')} "
        f"user={os.getenv('POSTGRES_USER', 'lab')} "
        f"password={os.getenv('POSTGRES_PASSWORD', 'lab_password')}"
    )


def iceberg_rest_uri() -> str:
    return os.getenv("ICEBERG_REST_URI", "http://localhost:8181")


def s3_endpoint() -> str:
    return os.getenv("S3_ENDPOINT", "http://localhost:9000")


def s3_access_key() -> str:
    return os.getenv("S3_ACCESS_KEY_ID", "admin")


def s3_secret_key() -> str:
    return os.getenv("S3_SECRET_ACCESS_KEY", "password")


def s3_region() -> str:
    return os.getenv("S3_REGION", "us-east-1")

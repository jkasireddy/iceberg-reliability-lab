from pyiceberg.catalog import load_catalog

from src.config import (
    iceberg_rest_uri,
    s3_access_key,
    s3_endpoint,
    s3_region,
    s3_secret_key,
)


def get_catalog():
    return load_catalog(
        "local",
        type="rest",
        uri=iceberg_rest_uri(),
        **{
            "s3.endpoint": s3_endpoint(),
            "s3.access-key-id": s3_access_key(),
            "s3.secret-access-key": s3_secret_key(),
            "s3.region": s3_region(),
        },
    )
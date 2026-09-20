import duckdb

from src.signals.organization import (
    normalize_organization,
    classify_organization,
)
from src.signals.technology import classify_product


OBSERVATION_PATH = "data/processed/observations/*.parquet"
ORG_MAPPING_PATH = "data/processed/organization_mapping.parquet"
PRODUCT_MAPPING_PATH = "data/processed/product_mapping.parquet"


def build_organization_mapping():
    con = duckdb.connect()

    print("Building organization mapping...")

    organizations = con.execute(f"""
        SELECT DISTINCT organization
        FROM '{OBSERVATION_PATH}'
        WHERE organization IS NOT NULL
          AND TRIM(organization) != ''
    """).df()

    organizations["normalized_organization"] = (
        organizations["organization"]
        .apply(normalize_organization)
    )

    organizations["organization_type"] = (
        organizations["organization"]
        .apply(classify_organization)
    )

    organizations.to_parquet(
        ORG_MAPPING_PATH,
        index=False
    )

    print(f"Organizations found: {len(organizations):,}")
    print(f"Saved: {ORG_MAPPING_PATH}")


def build_product_mapping():
    con = duckdb.connect()

    print("Building product mapping...")

    products = con.execute(f"""
        SELECT DISTINCT product
        FROM '{OBSERVATION_PATH}'
    """).df()

    products["technology_category"] = (
        products["product"]
        .apply(classify_product)
    )

    products.to_parquet(
        PRODUCT_MAPPING_PATH,
        index=False
    )

    print(f"Products found: {len(products):,}")
    print(f"Saved: {PRODUCT_MAPPING_PATH}")


if __name__ == "__main__":
    build_organization_mapping()
    build_product_mapping()

    print("\nMapping creation complete.")
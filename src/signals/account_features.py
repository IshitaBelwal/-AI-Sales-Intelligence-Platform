import pandas as pd
from pathlib import Path

from src.signals.organization import normalize_organization
from src.signals.technology import classify_product


def build_account_features(observation_path, output_path):
    """
    Build organization-level account features.

    Organization names are normalized using the same Python function
    used during testing, so there is one source of truth for
    organization normalization.
    """

    observation_path = Path(observation_path)
    output_path = Path(output_path)

    parquet_files = list(observation_path.glob("*.parquet"))

    if not parquet_files:
        raise FileNotFoundError(
            f"No parquet files found in {observation_path}"
        )

    all_features = []

    for parquet_file in parquet_files:

        print(f"Processing {parquet_file.name}")

        df = pd.read_parquet(parquet_file)

        # Remove observations without an organization
        df = df[
            df["organization"].notna()
            & (df["organization"].str.strip() != "")
        ].copy()

        # Normalize organization names
        df["normalized_organization"] = (
            df["organization"]
            .apply(normalize_organization)
        )

        # Classify products
        df["technology_category"] = (
            df["product"]
            .apply(classify_product)
        )

        # Aggregate this partition
        grouped = (
            df.groupby("normalized_organization")
            .agg(
                observation_count=("organization", "size"),
                unique_ips=("ip", "nunique"),
                unique_ports=("port", "nunique"),
                unique_products=("product", "nunique"),
                countries_observed=("country_code", "nunique"),
                first_seen=("timestamp", "min"),
                last_seen=("timestamp", "max"),
            )
            .reset_index()
        )

        # Technology-specific IP counts
        for category, column_name in [
            ("WEB", "web_ip_count"),
            ("REMOTE_ACCESS", "remote_access_ip_count"),
            ("EMAIL", "email_ip_count"),
            ("PROXY", "proxy_ip_count"),
            ("NETWORK", "network_ip_count"),
        ]:

            category_df = df[
                df["technology_category"] == category
            ]

            category_counts = (
                category_df
                .groupby("normalized_organization")["ip"]
                .nunique()
                .rename(column_name)
            )

            grouped = grouped.merge(
                category_counts,
                on="normalized_organization",
                how="left",
            )

        all_features.append(grouped)

    # Combine partitions
    features = pd.concat(
        all_features,
        ignore_index=True
    )

    # Fill missing signal counts
    signal_columns = [
        "web_ip_count",
        "remote_access_ip_count",
        "email_ip_count",
        "proxy_ip_count",
        "network_ip_count",
    ]

    for column in signal_columns:
        if column in features.columns:
            features[column] = (
                features[column]
                .fillna(0)
                .astype(int)
            )

    # IMPORTANT:
    # The above aggregation happens per parquet partition.
    # We must aggregate AGAIN across partitions.
    numeric_columns = [
        "observation_count",
        "unique_ips",
        "unique_ports",
        "unique_products",
        "countries_observed",
        "web_ip_count",
        "remote_access_ip_count",
        "email_ip_count",
        "proxy_ip_count",
        "network_ip_count",
    ]

    final_features = (
        features
        .groupby("normalized_organization", as_index=False)
        .agg({
            "observation_count": "sum",
            "unique_ips": "sum",
            "unique_ports": "sum",
            "unique_products": "sum",
            "countries_observed": "sum",
            "web_ip_count": "sum",
            "remote_access_ip_count": "sum",
            "email_ip_count": "sum",
            "proxy_ip_count": "sum",
            "network_ip_count": "sum",
            "first_seen": "min",
            "last_seen": "max",
        })
    )

    # Save
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    final_features.to_parquet(
        output_path,
        index=False
    )

    print()
    print("========== ACCOUNT FEATURES COMPLETE ==========")
    print(f"Accounts created: {len(final_features):,}")
    print(f"Output: {output_path}")
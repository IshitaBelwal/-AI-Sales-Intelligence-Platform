import pandas as pd

from src.signals.organization import (
    normalize_organization,
    classify_organization,
)


INPUT = "data/processed/account_features.parquet"
OUTPUT = "data/processed/account_features_v2.parquet"


df = pd.read_parquet(INPUT)

df["normalized_organization"] = (
    df["organization"]
    .apply(normalize_organization)
)

df["organization_type"] = (
    df["organization"]
    .apply(classify_organization)
)

df.to_parquet(OUTPUT, index=False)

print(f"Processed {len(df):,} organizations")
print()
print(df["organization_type"].value_counts())
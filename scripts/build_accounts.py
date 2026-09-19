from src.processing.aggregate_accounts import build_accounts


build_accounts(
    "data/processed/observations",
    "data/processed/accounts.parquet",
)
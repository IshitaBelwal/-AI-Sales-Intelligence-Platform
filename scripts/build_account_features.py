from src.signals.account_features import build_account_features

build_account_features(
    "data/processed/observations",
    "data/processed/account_features.parquet",
)
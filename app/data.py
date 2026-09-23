import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ACCOUNT_DATA = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cybersignal_accounts.parquet"
)


def load_accounts() -> pd.DataFrame:
    return pd.read_parquet(ACCOUNT_DATA)
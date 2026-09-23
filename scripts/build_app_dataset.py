from pathlib import Path

import pandas as pd

from src.signals.account_signals import build_account_signals
from src.scoring.icp import add_icp_features
from src.scoring.icp_score import add_icp_score


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "account_features.parquet"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "cybersignal_accounts.parquet"


def main():
    print("Loading account features...")
    df = pd.read_parquet(INPUT_FILE)

    print(f"Loaded {len(df):,} accounts")

    print("Building account signals...")
    df = build_account_signals(df)

    print("Adding ICP features...")
    df = add_icp_features(df)

    print("Calculating ICP scores...")
    df = add_icp_score(df)

    print("Sorting accounts...")
    df = df.sort_values(
        by=[
            "icp_fit_score",
            "exposure_signal_count",
            "unique_products",
            "unique_ips",
        ],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)

    print("Writing application dataset...")
    df.to_parquet(OUTPUT_FILE, index=False)

    print(f"\nSaved: {OUTPUT_FILE}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nTop 10 accounts:")
    print(
        df[
            [
                "normalized_organization",
                "organization_type",
                "icp_fit_score",
                "exposure_signal_count",
                "unique_products",
                "unique_ips",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
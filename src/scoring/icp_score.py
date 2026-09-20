import pandas as pd


def calculate_icp_fit(row):
    """
    Transparent ICP-fit heuristic.

    This is a deterministic ranking heuristic, not a prediction
    of buying intent.
    """

    score = 50.0

    organization_type = row["organization_type"]

    # ---------------------------------------------------------
    # Organization context
    # ---------------------------------------------------------
    if organization_type in {
        "CLOUD_PROVIDER",
        "CDN_SECURITY",
        "ISP",
        "HOSTING_PROVIDER",
    }:
        score -= 15

    if organization_type == "SECURITY_PROVIDER":
        score -= 10

    # ---------------------------------------------------------
    # Technology / exposure breadth
    # ---------------------------------------------------------
    # Reward each additional observable security-relevant surface,
    # rather than using a single >= 3 threshold.
    score += min(
        row["exposure_signal_count"] * 3,
        15
    )

    # Technology diversity contributes gradually.
    score += min(
        row["unique_products"] * 1.5,
        15
    )

    # ---------------------------------------------------------
    # Infrastructure size
    # ---------------------------------------------------------
    # Size is useful context but should not dominate the ranking.
    if row["unique_ips"] > 10000:
        score -= 10
    elif row["unique_ips"] > 500:
        score += 5
    elif row["unique_ips"] > 25:
        score += 3

    return max(0, min(score, 100))


def add_icp_score(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["icp_fit_score"] = df.apply(
        calculate_icp_fit,
        axis=1,
    )

    return df
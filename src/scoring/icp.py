import pandas as pd


def add_icp_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add transparent ICP/context features.

    These features describe account type and observable infrastructure
    characteristics. They are not predictions of buying intent.
    """

    df = df.copy()

    # ---------------------------------------------------------
    # Provider / infrastructure classification
    # ---------------------------------------------------------

    provider_types = {
        "CLOUD_PROVIDER",
        "CDN_SECURITY",
        "ISP",
        "HOSTING_PROVIDER",
        "SECURITY_PROVIDER",
    }

    df["is_infrastructure_provider"] = (
        df["organization_type"].isin(provider_types)
    )

    df["is_security_provider"] = (
        df["organization_type"] == "SECURITY_PROVIDER"
    )

    # ---------------------------------------------------------
    # Account scale buckets
    # ---------------------------------------------------------

    df["small_infrastructure"] = (
        df["unique_ips"] <= 25
    )

    df["medium_infrastructure"] = (
        (df["unique_ips"] > 25)
        & (df["unique_ips"] <= 500)
    )

    df["large_infrastructure"] = (
        df["unique_ips"] > 500
    )

    # ---------------------------------------------------------
    # Technology breadth
    # ---------------------------------------------------------

    df["has_multiple_technology_surfaces"] = (
        df["exposure_signal_count"] >= 3
    )

    return df
import pandas as pd


def build_account_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build deterministic account-level cybersecurity exposure signals.

    These are observable infrastructure signals, not claims of
    vulnerabilities or buying intent.
    """

    df = df.copy()

    # ---------------------------------------------------------
    # Existing exposure signals
    # ---------------------------------------------------------

    df["has_web_exposure"] = df["web_ip_count"] > 0

    df["has_remote_access_exposure"] = (
        df["remote_access_ip_count"] > 0
    )

    df["has_email_exposure"] = (
        df["email_ip_count"] > 0
    )

    df["has_proxy_exposure"] = (
        df["proxy_ip_count"] > 0
    )

    df["has_network_exposure"] = (
        df["network_ip_count"] > 0
    )

    # ---------------------------------------------------------
    # Technology-specific signals
    # ---------------------------------------------------------

    # These will be populated by the account-level
    # technology aggregation later.
    for column in [
        "database_ip_count",
        "iot_ip_count",
        "container_ip_count",
        "security_network_ip_count",
        "file_transfer_ip_count",
    ]:
        if column not in df.columns:
            df[column] = 0

    df["has_database_exposure"] = (
        df["database_ip_count"] > 0
    )

    df["has_iot_exposure"] = (
        df["iot_ip_count"] > 0
    )

    df["has_container_exposure"] = (
        df["container_ip_count"] > 0
    )

    df["has_security_network_exposure"] = (
        df["security_network_ip_count"] > 0
    )

    df["has_file_transfer_exposure"] = (
        df["file_transfer_ip_count"] > 0
    )

    # ---------------------------------------------------------
    # Exposure breadth
    # ---------------------------------------------------------

    exposure_flags = [
        "has_web_exposure",
        "has_remote_access_exposure",
        "has_email_exposure",
        "has_proxy_exposure",
        "has_network_exposure",
        "has_database_exposure",
        "has_iot_exposure",
        "has_container_exposure",
        "has_security_network_exposure",
        "has_file_transfer_exposure",
    ]

    df["exposure_signal_count"] = (
        df[exposure_flags].sum(axis=1)
    )

    # ---------------------------------------------------------
    # Technology diversity
    # ---------------------------------------------------------

    df["technology_diversity"] = (
        df["unique_products"]
    )

    # ---------------------------------------------------------
    # Infrastructure scale
    # ---------------------------------------------------------

    df["infrastructure_scale"] = (
        df["unique_ips"]
    )

    return df
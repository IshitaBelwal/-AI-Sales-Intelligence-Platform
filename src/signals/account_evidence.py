import pandas as pd


SIGNAL_COLUMNS = {
    "web_ip_count": "web",
    "remote_access_ip_count": "remote_access",
    "email_ip_count": "email",
    "proxy_ip_count": "proxy",
    "network_ip_count": "network",
    "database_ip_count": "database",
    "iot_ip_count": "iot",
    "container_ip_count": "container",
    "security_network_ip_count": "security_network",
    "file_transfer_ip_count": "file_transfer",
}


def build_account_evidence(row: pd.Series) -> dict:
    """
    Build a structured evidence object for one account.

    All evidence is derived from deterministic dataset fields.
    The LLM should consume this object rather than raw observations.
    """

    signals = {}

    for column, signal_name in SIGNAL_COLUMNS.items():
        value = int(row.get(column, 0) or 0)

        if value > 0:
            signals[signal_name] = {
                "observed_ips": value
            }

    return {
        "account": row["normalized_organization"],

        "organization_type": row["organization_type"],

        "icp_fit_score": float(row["icp_fit_score"]),

        "scale": {
            "observations": int(row["observation_count"]),
            "unique_ips": int(row["unique_ips"]),
            "unique_ports": int(row["unique_ports"]),
            "unique_products": int(row["unique_products"]),
            "countries_observed": int(row["countries_observed"]),
        },

        "technology_signals": signals,

        "signal_summary": {
            "exposure_signal_count": int(
                row["exposure_signal_count"]
            )
        },

        "observation_window": {
            "first_seen": row["first_seen"],
            "last_seen": row["last_seen"],
        },
    }
import math
import pandas as pd


def minmax_log(value, cap):
    """
    Log-scaled value normalized to 0-1.
    Prevents huge infrastructure providers from dominating.
    """
    value = max(float(value or 0), 0)

    if value == 0:
        return 0.0

    return min(
        math.log1p(value) / math.log1p(cap),
        1.0,
    )


def calculate_exposure_score(row):
    """
    Score observable cybersecurity-relevant exposure.

    This does NOT imply vulnerability or buying intent.
    """

    score = 0.0

    if row["web_ip_count"] > 0:
        score += 5

    if row["remote_access_ip_count"] > 0:
        score += 8

    if row["email_ip_count"] > 0:
        score += 5

    if row["proxy_ip_count"] > 0:
        score += 4

    if row["network_ip_count"] > 0:
        score += 3

    if row["database_ip_count"] > 0:
        score += 5

    if row["iot_ip_count"] > 0:
        score += 3

    if row["container_ip_count"] > 0:
        score += 3

    if row["security_network_ip_count"] > 0:
        score += 2

    if row["file_transfer_ip_count"] > 0:
        score += 2

    return min(score, 40)


def calculate_technology_score(row):
    """
    Reward breadth of technology exposure,
    not raw observation volume.
    """

    relevant_categories = sum([
        row["web_ip_count"] > 0,
        row["remote_access_ip_count"] > 0,
        row["email_ip_count"] > 0,
        row["proxy_ip_count"] > 0,
        row["network_ip_count"] > 0,
        row["database_ip_count"] > 0,
        row["iot_ip_count"] > 0,
        row["container_ip_count"] > 0,
        row["security_network_ip_count"] > 0,
        row["file_transfer_ip_count"] > 0,
    ])

    return min(
        relevant_categories / 10 * 25,
        25,
    )


def calculate_infrastructure_score(row):
    """
    Log-scaled infrastructure breadth.
    Prevents a 100,000-IP provider from automatically
    dominating a 100-IP organization.
    """

    ip_component = minmax_log(
        row["unique_ips"],
        cap=10000,
    )

    port_component = minmax_log(
        row["unique_ports"],
        cap=5000,
    )

    product_component = minmax_log(
        row["unique_products"],
        cap=100,
    )

    score = (
        ip_component * 7
        + port_component * 4
        + product_component * 4
    )

    return min(score, 15)


def calculate_context_score(row):
    """
    Initial context component.

    We intentionally avoid treating any organization type
    as inherently good or bad without labeled sales outcomes.
    """

    organization_type = row["organization_type"]

    if organization_type == "UNKNOWN":
        return 20

    if organization_type == "HOSTING_PROVIDER":
        return 18

    if organization_type == "ISP":
        return 15

    if organization_type == "CLOUD_PROVIDER":
        return 12

    if organization_type == "CDN_SECURITY":
        return 10

    if organization_type == "SECURITY_PROVIDER":
        return 10

    return 15


def calculate_account_score(row):
    exposure = calculate_exposure_score(row)
    technology = calculate_technology_score(row)
    infrastructure = calculate_infrastructure_score(row)
    context = calculate_context_score(row)

    total = (
        exposure
        + technology
        + infrastructure
        + context
    )

    return round(min(total, 100), 2)


def score_accounts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add deterministic account score and component scores.
    """

    df = df.copy()

    df["exposure_score"] = df.apply(
        calculate_exposure_score,
        axis=1,
    )

    df["technology_score"] = df.apply(
        calculate_technology_score,
        axis=1,
    )

    df["infrastructure_score"] = df.apply(
        calculate_infrastructure_score,
        axis=1,
    )

    df["context_score"] = df.apply(
        calculate_context_score,
        axis=1,
    )

    df["account_score"] = (
        df["exposure_score"]
        + df["technology_score"]
        + df["infrastructure_score"]
        + df["context_score"]
    ).round(2)

    return df
import re


def normalize_organization(name):
    """
    Normalize organization names for account-level deduplication.
    """

    if not name:
        return None

    name = name.strip().lower()

    # Replace punctuation with spaces
    name = re.sub(r"[.,]", " ", name)

    # Collapse whitespace
    name = re.sub(r"\s+", " ", name).strip()

    # Remove common legal suffixes.
    # Run repeatedly because names can contain combinations
    # such as "Co., Ltd."
    legal_suffixes = [
        "private limited",
        "public limited",
        "limited",
        "ltd",
        "llc",
        "incorporated",
        "inc",
        "corporation",
        "corp",
        "company",
        "co",
        "gmbh",
        "sa",
    ]

    changed = True

    while changed:
        changed = False

        for suffix in legal_suffixes:
            if name.endswith(" " + suffix):
                name = name[: -(len(suffix) + 1)].strip()
                changed = True
                break

    return name


def classify_organization(name):
    """
    Initial rule-based organization classification.

    This is intentionally conservative.
    Unknown organizations remain UNKNOWN rather than being
    incorrectly classified.
    """

    normalized = normalize_organization(name)

    if not normalized:
        return "UNKNOWN"

    # Cloud / infrastructure providers
    cloud_keywords = [
        "amazon",
        "aws",
        "google cloud",
        "microsoft",
        "azure",
        "aliyun",
        "alibaba cloud",
        "tencent cloud",
        "digitalocean",
        "linode",
        "oracle cloud",
        "oracle public cloud",
        "vultr",
        "contabo",
        "hetzner",
        "ovh",
        "ionos",
        "a100 row",
    ]

    # CDN / edge / security infrastructure
    cdn_security_keywords = [
        "cloudflare",
        "akamai",
        "incapsula",
        "imperva",
    ]

    # Telecommunications / ISPs
    isp_keywords = [
        "telecom",
        "communications",
        "communication",
        "broadband",
        "internet service",
        "network",
        "mobile",
        "verizon",
        "comcast",
        "at&t",
        "charter",
        "orange",
        "reliance jio",
        "deutsche telekom",
        "vodafone",
        "telefonica",
        "telstra",
    ]

    # Hosting providers
    hosting_keywords = [
        "hostinger",
        "hostgator",
        "godaddy",
        "hostpapa",
        "hosting",
    ]

    # Security vendors / security infrastructure
    security_keywords = [
        "fortinet",
        "palo alto",
        "crowdstrike",
        "sentinelone",
        "zscaler",
        "sophos",
    ]

    if any(keyword in normalized for keyword in cdn_security_keywords):
        return "CDN_SECURITY"

    if any(keyword in normalized for keyword in security_keywords):
        return "SECURITY_PROVIDER"

    if any(keyword in normalized for keyword in cloud_keywords):
        return "CLOUD_PROVIDER"

    if any(keyword in normalized for keyword in hosting_keywords):
        return "HOSTING_PROVIDER"

    if any(keyword in normalized for keyword in isp_keywords):
        return "ISP"

    return "UNKNOWN"
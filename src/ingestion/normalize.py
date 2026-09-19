def normalize_record(record):
    location = record.get("location") or {}
    http = record.get("http") or {}

    return {
        # Organization
        "organization": record.get("org"),
        "isp": record.get("isp"),
        "asn": record.get("asn"),

        # Network
        "ip": record.get("ip_str"),
        "port": record.get("port"),
        "transport": record.get("transport"),

        # Technology
        "product": record.get("product"),
        "os": record.get("os"),

        # Geography
        "country_code": location.get("country_code"),
        "country_name": location.get("country_name"),
        "city": location.get("city"),

        # Domains
        "domains": record.get("domains") or [],
        "hostnames": record.get("hostnames") or [],

        # Technology identifiers
        "cpe": record.get("cpe") or [],
        "cpe23": record.get("cpe23") or [],

        # HTTP evidence
        "http_status": http.get("status"),
        "http_server": http.get("server"),
        "http_title": http.get("title"),
        "http_host": http.get("host"),
        "http_components": http.get("components") or {},

        # Observation time
        "timestamp": record.get("timestamp"),
    }
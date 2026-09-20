import duckdb


def build_account_features(
    observation_path,
    organization_mapping_path,
    product_mapping_path,
    output_path,
):
    con = duckdb.connect()

    query = f"""
        SELECT
            om.normalized_organization,

            MIN(o.organization) AS organization,

            MIN(om.organization_type) AS organization_type,

            COUNT(*) AS observation_count,

            COUNT(DISTINCT o.ip) AS unique_ips,

            COUNT(DISTINCT o.port) AS unique_ports,

            COUNT(DISTINCT o.product) AS unique_products,

            COUNT(DISTINCT o.country_code) AS countries_observed,

            COUNT(
                DISTINCT CASE
                    WHEN COALESCE(pm.technology_category, 'UNKNOWN') = 'WEB'
                    THEN o.ip
                END
            ) AS web_ip_count,

            COUNT(
                DISTINCT CASE
                    WHEN COALESCE(pm.technology_category, 'UNKNOWN') = 'REMOTE_ACCESS'
                    THEN o.ip
                END
            ) AS remote_access_ip_count,

            COUNT(
                DISTINCT CASE
                    WHEN COALESCE(pm.technology_category, 'UNKNOWN') = 'EMAIL'
                    THEN o.ip
                END
            ) AS email_ip_count,

            COUNT(
                DISTINCT CASE
                    WHEN COALESCE(pm.technology_category, 'UNKNOWN') = 'PROXY'
                    THEN o.ip
                END
            ) AS proxy_ip_count,

            COUNT(
                DISTINCT CASE
                    WHEN COALESCE(pm.technology_category, 'UNKNOWN') = 'NETWORK'
                    THEN o.ip
                END
            ) AS network_ip_count,
                        COUNT(
                DISTINCT CASE
                    WHEN COALESCE(pm.technology_category, 'UNKNOWN') = 'DATABASE'
                    THEN o.ip
                END
            ) AS database_ip_count,

            COUNT(
                DISTINCT CASE
                    WHEN COALESCE(pm.technology_category, 'UNKNOWN') = 'IOT'
                    THEN o.ip
                END
            ) AS iot_ip_count,

            COUNT(
                DISTINCT CASE
                    WHEN COALESCE(pm.technology_category, 'UNKNOWN') = 'CONTAINER_PLATFORM'
                    THEN o.ip
                END
            ) AS container_ip_count,

            COUNT(
                DISTINCT CASE
                    WHEN COALESCE(pm.technology_category, 'UNKNOWN') = 'SECURITY_NETWORK'
                    THEN o.ip
                END
            ) AS security_network_ip_count,

            COUNT(
                DISTINCT CASE
                    WHEN COALESCE(pm.technology_category, 'UNKNOWN') = 'FILE_TRANSFER'
                    THEN o.ip
                END
            ) AS file_transfer_ip_count,

            MIN(o.timestamp) AS first_seen,

            MAX(o.timestamp) AS last_seen

        FROM '{observation_path}' o

        INNER JOIN '{organization_mapping_path}' om
            ON o.organization = om.organization

        LEFT JOIN '{product_mapping_path}' pm
            ON o.product = pm.product

        WHERE o.organization IS NOT NULL
          AND TRIM(o.organization) != ''

        GROUP BY
            om.normalized_organization
    """

    print("Building account features...")

    df = con.execute(query).df()

    df.to_parquet(
        output_path,
        index=False
    )

    print(f"Accounts created: {len(df):,}")
    print(f"Saved: {output_path}")

    return df


if __name__ == "__main__":
    build_account_features(
        observation_path="data/processed/observations/*.parquet",
        organization_mapping_path="data/processed/organization_mapping.parquet",
        product_mapping_path="data/processed/product_mapping.parquet",
        output_path="data/processed/account_features.parquet",
    )
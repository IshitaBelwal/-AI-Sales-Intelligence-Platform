import duckdb


def build_accounts(
    observation_path,
    output_path,
):

    con = duckdb.connect()

    query = f"""
        SELECT
            organization,

            COUNT(*) AS observation_count,

            COUNT(DISTINCT ip) AS unique_ips,

            COUNT(DISTINCT port) AS unique_ports,

            COUNT(DISTINCT product) AS unique_products,

            COUNT(DISTINCT country_code) AS countries_observed,

            MIN(timestamp) AS first_seen,

            MAX(timestamp) AS last_seen

        FROM '{observation_path}/*.parquet'

        WHERE organization IS NOT NULL
          AND TRIM(organization) != ''

        GROUP BY organization
    """

    df = con.execute(query).df()

    df.to_parquet(
        output_path,
        index=False
    )

    print(f"Created {len(df):,} accounts")
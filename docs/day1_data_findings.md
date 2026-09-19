# Day 1 — Data Understanding & Ingestion Findings

## 1. Objective

The objective of Day 1 was to understand the Firmable infrastructure
dataset, identify the fields relevant to sales intelligence, build a
reusable normalization layer, and create a scalable ingestion pipeline.

The final Day 1 pipeline converts raw JSONL infrastructure observations
into normalized Parquet data and then aggregates those observations into
an organization-level account dataset.

---

## 2. Development Dataset

The primary development dataset used during Day 1 was:

- File: `firmable_2M.jsonl`
- Records: 2,000,000
- Format: JSON Lines (JSONL)

A smaller sample dataset was used for early exploration and debugging.

The full compressed Firmable dataset is substantially larger and is
stored separately from the Git repository. The ingestion architecture
was designed to support the compressed `.zst` dataset through streaming
decompression without requiring the entire dataset to be decompressed
into memory.

---

## 3. Source Data Model

Each source record represents an observed internet-facing
infrastructure/service observation.

A typical record contains information about:

- Organization
- ISP
- ASN
- IP address
- Network port
- Transport protocol
- Product/service
- Operating system
- Geographic location
- Domains
- Hostnames
- CPE identifiers
- HTTP metadata
- Observation timestamp
- Raw service/banner data
- Source metadata

The source data is therefore an observation-level dataset rather than
an account-level sales dataset.

---

## 4. Observation vs Account

A key finding from the exploration was that one organization can have
many infrastructure observations.

For example:

    Organization
        |
        +-- IP address
        |     +-- Port 443
        |     +-- nginx
        |
        +-- IP address
        |     +-- Port 22
        |     +-- OpenSSH
        |
        +-- IP address
              +-- Port 5432
              +-- PostgreSQL

Therefore, the application should not operate directly on individual
raw observations.

The architecture separates the data into two logical layers:

    Raw observations
            |
            v
    Normalized observations
            |
            v
    Organization aggregation
            |
            v
    Account-level intelligence

The account is the primary object that the CyberSignal application
will eventually present to a sales user.

---

## 5. Important Source Fields

The following fields were identified as particularly relevant:

### Organization

- `org`
- `isp`
- `asn`

These fields provide organization and network ownership context.

### Network

- `ip_str`
- `port`
- `transport`

These describe the observed network endpoint and exposed service.

### Technology

- `product`
- `os`
- `cpe`
- `cpe23`

These provide technology and software identification.

### Geography

- `location.country_code`
- `location.country_name`
- `location.city`

These can later support territory and geographic filtering.

### Web / HTTP

- `http.status`
- `http.server`
- `http.title`
- `http.host`
- `http.components`

These provide additional evidence about internet-facing web services.

### Time

- `timestamp`

This allows us to calculate recency and identify recently observed
infrastructure.

---

## 6. Fields Excluded From the Initial Analytical Layer

Several source fields were intentionally not included in the initial
normalized analytical dataset.

Examples include:

- `hash`
- `cpe23_hash`
- `_shodan`
- `opts`
- Large raw `data` payloads
- Full HTTP HTML content
- HTTP hash fields

These fields remain available in the original source dataset but are
not required for the first version of the account intelligence model.

This reduces the size and complexity of the analytical dataset while
preserving the original evidence source.

---

## 7. Normalization

A reusable normalization function was created in:

    src/ingestion/normalize.py

The normalizer converts nested source records into a consistent
observation schema.

The normalized representation includes:

- `organization`
- `isp`
- `asn`
- `ip`
- `port`
- `transport`
- `product`
- `os`
- `country_code`
- `country_name`
- `city`
- `domains`
- `hostnames`
- `cpe`
- `cpe23`
- `http_status`
- `http_server`
- `http_title`
- `http_host`
- `http_components`
- `timestamp`

Missing optional values are represented consistently rather than
causing records to be discarded.

---

## 8. Normalizer Validation

The normalization function was tested against 100 source records.

Result:

    Errors: 0

This confirmed that the normalization function can handle the tested
variation in the source records without raising parsing or
normalization errors.

---

## 9. Streaming Ingestion

A streaming JSONL reader was implemented in:

    src/ingestion/jsonl_reader.py

The reader processes records one at a time instead of loading the
entire dataset into memory.

A separate reader supports `.zst` compressed JSONL files using
streaming decompression.

This is important because the full Firmable dataset is much larger
than the development dataset.

The architecture therefore avoids:

    Raw dataset
        |
        v
    Load entire dataset into RAM

and instead uses:

    Raw dataset
        |
        v
    Stream one record
        |
        v
    Normalize
        |
        v
    Write batch
        |
        v
    Next record

---

## 10. Parquet Conversion

The ingestion pipeline was implemented in:

    src/ingestion/jsonl_to_parquet.py

Records are processed in batches and written as Parquet partitions.

For the development dataset, a batch size of 50,000 records is used.

The resulting architecture is:

    firmable_2M.jsonl
            |
            v
    Streaming JSON reader
            |
            v
    Normalization
            |
            v
    50,000-record batches
            |
            v
    Parquet partitions

Parquet was selected as the analytical storage format because it is
well suited for columnar analytical queries and can be queried
efficiently using DuckDB or Polars.

---

## 11. Ingestion Validation

The ingestion pipeline was first tested against a 10,000-record subset.

The pipeline successfully converted the test records into Parquet
partitions and the resulting Parquet files were queried using DuckDB.

The 2M development dataset was subsequently processed through the
same ingestion pipeline.

---

## 12. Account Aggregation

After creating the normalized observation layer, observations were
aggregated by organization.

The account aggregation is implemented in:

    src/processing/aggregate_accounts.py

The initial account-level dataset contains:

- `organization`
- `observation_count`
- `unique_ips`
- `unique_ports`
- `unique_products`
- `countries_observed`
- `first_seen`
- `last_seen`

The resulting account dataset is stored as:

    data/processed/accounts.parquet

---

## 13. Initial Account-Level Result

The 2M-record development dataset currently produces:

    34,065 distinct organization names

This should be interpreted as the number of distinct organization
values present in the source data after aggregation.

It should not yet be interpreted as 34,065 verified legal companies.

Organization/entity resolution has not yet been implemented.

For example, different organization strings may represent related
entities, subsidiaries, cloud infrastructure, hosting providers, or
different network ownership records.

---

## 14. Important Data Insight

A major finding from the initial exploration is that observation
volume should not automatically be interpreted as sales priority.

Large infrastructure providers, cloud providers, CDNs, ISPs, and
hosting organizations can generate very large numbers of observations.

Therefore:

    observation_count != sales propensity

The application should combine multiple signals instead of ranking
accounts purely by the number of observations.

This will be addressed during the signal-engineering and account-scoring
phases.

---

## 15. Security Signal Limitation

The 2M development dataset does not expose the `tags` and `vulns`
fields that were present in the smaller sample explored separately.

Therefore, the initial scoring system will not assume that vulnerability
or security-tag information exists in every dataset version.

Instead, the first signal layer will be derived from fields actually
present in the 2M dataset, such as:

- exposed ports
- detected products
- CPE/CPE23 identifiers
- HTTP services
- technology diversity
- infrastructure exposure
- observation recency

Any security interpretation will be kept separate from the raw
observation itself.

For example, an exposed service is an observable infrastructure signal;
it should not automatically be described as a vulnerability.

---

## 16. Current Architecture

The Day 1 architecture is:

    Firmable JSONL / ZST
            |
            v
    Streaming Reader
            |
            v
    Record Normalization
            |
            v
    Normalized Observation Parquet
            |
            v
    DuckDB / Analytical Queries
            |
            v
    Organization Aggregation
            |
            v
    accounts.parquet
            |
            v
    Future Signal Engine
            |
            v
    Future Account Scoring
            |
            v
    CyberSignal Application

---

## 17. Day 1 Deliverables

Completed:

- Raw dataset schema exploration
- Nested field inspection
- Data normalization
- Normalizer validation
- Streaming JSONL reader
- Streaming `.zst` reader
- Batch Parquet ingestion
- 10K-record ingestion test
- 2M-record ingestion
- DuckDB analytical access
- Organization-level aggregation
- Initial `accounts.parquet`
- Data dictionary

---

## 18. Next Steps

Day 2 will focus on converting raw infrastructure observations
into meaningful sales intelligence signals.

Planned work:

1. Technology/service signal extraction
2. Port/service classification
3. CPE parsing
4. HTTP technology extraction
5. Recency features
6. Organization-type classification
7. Infrastructure exposure features
8. Account-level signal aggregation
9. Initial deterministic account scoring
10. Validation of the resulting account-ranking features
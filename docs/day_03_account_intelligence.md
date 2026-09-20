# Day 03 — Account Aggregation and Cybersecurity Signal Engineering

## Objective

Transform raw infrastructure observations into organization-level intelligence
that can be used for account discovery and sales prioritization.

The raw dataset contains individual observations such as IP addresses, ports,
products, domains, HTTP metadata and timestamps. A sales team, however, needs
to reason about organizations/accounts rather than individual observations.

The main objective of Day 3 was therefore to move from:

    Observation-level data

to:

    Organization-level account intelligence

---

## 1. Account Aggregation

The first account-level aggregation was implemented in:

    src/processing/aggregate_accounts.py

DuckDB was used to aggregate the normalized Parquet observations.

For each organization, the pipeline calculates:

- observation_count
- unique_ips
- unique_ports
- unique_products
- countries_observed
- first_seen
- last_seen

These metrics provide a compact representation of the organization's
observable infrastructure footprint.

---

## 2. Initial Organization Count

The initial aggregation produced approximately:

    34,065 distinct organization source names

However, organization names are not always canonical.

Examples observed in the source data included variations such as:

    Aliyun Computing Co., LTD
    Aliyun Computing Co.LTD

and:

    Incapsula Inc
    Incapsula Inc.

These should represent the same organization for account-level analysis.

---

## 3. Organization Normalization

A normalization layer was introduced to reduce superficial naming variation.

Implemented normalization steps include:

- lowercase conversion
- whitespace normalization
- punctuation normalization
- removal of common legal suffixes

Examples:

    Aliyun Computing Co., LTD
        ↓
    aliyun computing

    Incapsula Inc.
        ↓
    incapsula

    METEVERSE LIMITED
        ↓
    meteverse

The normalization reduced the account universe to approximately:

    33,022 normalized organizations

The normalization intentionally avoids aggressive entity resolution.

For example:

    Amazon.com, Inc.

becomes:

    amazon com

rather than attempting to infer additional aliases.

This reduces the risk of incorrectly merging unrelated organizations.

---

## 4. Organization Classification

Raw infrastructure observations do not directly tell us whether an
organization is an end customer, cloud provider, ISP or security vendor.

A lightweight deterministic organization classifier was therefore created.

Organization categories include:

- CLOUD_PROVIDER
- CDN_SECURITY
- ISP
- HOSTING_PROVIDER
- SECURITY_PROVIDER
- UNKNOWN

The classifier uses transparent keyword-based rules.

Examples include:

    Cloudflare / Akamai / Incapsula
        → CDN_SECURITY

    Amazon / Azure / Alibaba Cloud / DigitalOcean
        → CLOUD_PROVIDER

    Telecom / broadband / network providers
        → ISP

    Hosting providers
        → HOSTING_PROVIDER

    Fortinet / Palo Alto / CrowdStrike / Zscaler
        → SECURITY_PROVIDER

Organizations that cannot be confidently classified remain:

    UNKNOWN

This conservative approach is intentional. Incorrect classification can
introduce more bias into the scoring system than leaving an organization
unknown.

---

## 5. Classification Results

The normalized account population was approximately 33,022 organizations.

The initial classification distribution was approximately:

| Organization type | Accounts |
|---|---:|
| UNKNOWN | 27,049 |
| ISP | 5,154 |
| HOSTING_PROVIDER | 619 |
| CLOUD_PROVIDER | 140 |
| SECURITY_PROVIDER | 36 |
| CDN_SECURITY | 24 |

The large UNKNOWN category is expected because organization classification
based only on organization names is inherently limited.

---

## 6. Technology Classification

A second classification layer was introduced to convert individual products
into broader technology/security surfaces.

Implemented in:

    src/signals/technology.py

Examples of technology categories include:

- WEB
- REMOTE_ACCESS
- EMAIL
- PROXY
- NETWORK
- CDN
- LOAD_BALANCER
- DATABASE
- IOT
- CONTAINER_PLATFORM
- SECURITY_NETWORK
- OBSERVABILITY
- FILE_TRANSFER
- OTHER
- UNKNOWN

Examples:

    nginx
        → WEB

    OpenSSH
        → REMOTE_ACCESS

    MySQL / PostgreSQL / MariaDB
        → DATABASE

    Kubernetes / Portainer
        → CONTAINER_PLATFORM

    Hikvision / Dahua devices
        → IOT

    SonicWall
        → SECURITY_NETWORK

The classification is deterministic and version-controlled in code.

---

## 7. Why Technology Categories Matter

Counting raw products alone does not provide a useful sales signal.

For example:

    nginx
    Apache
    IIS
    OpenResty

are different products but all represent web-facing technology.

Grouping them into broader technology surfaces allows the system to reason
about the type of infrastructure an organization operates.

This also makes downstream account-level explanations easier to understand.

---

## 8. Account-Level Security Signals

The technology mappings were aggregated into organization-level signals.

Implemented in:

    src/signals/account_signals.py

Examples include:

- has_web_exposure
- has_remote_access_exposure
- has_email_exposure
- has_proxy_exposure
- has_network_exposure
- has_database_exposure
- has_iot_exposure
- has_container_exposure
- has_security_network_exposure
- has_file_transfer_exposure

A derived metric was also created:

    exposure_signal_count

This represents the number of distinct technology/security surfaces observed
for an organization.

---

## 9. Important Data Interpretation Decision

A critical design decision was made during signal engineering:

    Observable exposure ≠ vulnerability
    Infrastructure scale ≠ buying intent

For example, observing OpenSSH on an organization's infrastructure does not
prove that the organization has a vulnerability.

Similarly, an organization with hundreds of thousands of observations may
simply be a cloud provider, CDN or ISP.

Therefore, the system treats these fields as:

    observable signals

rather than:

    confirmed vulnerabilities
    confirmed security incidents
    confirmed buying intent

This distinction is important for both technical accuracy and responsible
sales intelligence.

---

## 10. Account-Level Infrastructure Features

The account signal layer also derives:

    technology_diversity
    infrastructure_scale

where:

    technology_diversity = unique_products

and:

    infrastructure_scale = unique_ips

These features are used as contextual signals rather than direct predictions
of purchasing behavior.

---

## 11. Aggregation Validation

The aggregated account data was validated against the original observation
data.

Examples:

    Google LLC
        approximately 667,714 observations

    Aliyun Computing
        approximately 71,403 observations

The aggregation was also checked to ensure that normalization merged expected
organization-name variants without unnecessarily combining unrelated entities.

---

## 12. Architecture After Day 3

The data pipeline now looks like:

    Raw observations
          |
          v
    Streaming normalization
          |
          v
    Parquet observations
          |
          v
    Organization normalization
          |
          v
    Account aggregation
          |
          +--------------------+
          |                    |
          v                    v
    Organization type     Product classification
          |                    |
          +---------+----------+
                    |
                    v
             Account signals
                    |
                    v
          Organization-level
          account intelligence

This account-level representation becomes the input to the ICP scoring
layer developed on Day 4.

---

## 13. Key Engineering Learnings

### Observation-level data is not account-level intelligence

The raw dataset contains hundreds of thousands of individual observations,
but sales workflows operate at the organization/account level.

### Scale needs context

Large infrastructure footprints can belong to cloud providers, CDNs,
telecom companies or hosting providers. Therefore, infrastructure volume
cannot be used as a standalone sales-priority signal.

### Conservative classification is preferable

When the organization type cannot be confidently inferred, the system uses
UNKNOWN rather than making an aggressive classification.

### Deterministic signals improve explainability

Technology and organization classifications are implemented as transparent
rules, making it possible to explain why an account received a particular
signal.

---

## Result

By the end of Day 3, the project had moved from raw infrastructure
observations to a reusable organization-level intelligence layer.

The resulting account representation contains:

- organization identity
- organization type
- infrastructure scale
- technology diversity
- technology/security surfaces
- observation time window
- geographic coverage

This account intelligence layer is the foundation for the deterministic ICP
scoring system implemented on Day 4.
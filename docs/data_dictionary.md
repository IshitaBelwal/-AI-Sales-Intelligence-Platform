# CyberSignal Data Dictionary

## Overview

CyberSignal uses the Firmable infrastructure dataset as its primary source
of technical observations.

The source dataset is observation-oriented: each record represents an
internet-facing infrastructure or service observation associated with an
organization.

The data is transformed through multiple analytical layers:

1. Observation layer
2. Account layer
3. Signal layer
4. ICP/scoring layer
5. AI intelligence layer (planned)

The current implementation covers the observation, account, signal, and
ICP/scoring layers.

The AI intelligence layer will be built on top of these deterministic
account-level signals.

---

# 1. Observation Layer

The observation layer contains one normalized row per source observation.

The normalization logic is implemented in:

    src/ingestion/normalize.py

The normalized schema converts nested source JSON into a consistent
analytical structure.

---

## 1.1 Organization and Network Identity

| Field | Source Field | Type | Description |
|---|---|---|---|
| `organization` | `org` | string | Organization associated with the observation |
| `isp` | `isp` | string | Internet service provider associated with the observation |
| `asn` | `asn` | string | Autonomous System Number associated with the observation |
| `ip` | `ip_str` | string | Human-readable IP address |

---

## 1.2 Network

| Field | Source Field | Type | Description |
|---|---|---|---|
| `port` | `port` | integer | Observed network port |
| `transport` | `transport` | string | Transport protocol, such as TCP or UDP |

---

## 1.3 Technology

| Field | Source Field | Type | Description |
|---|---|---|---|
| `product` | `product` | string | Detected product or service |
| `os` | `os` | string/null | Detected operating system |
| `cpe` | `cpe` | array | CPE technology identifiers |
| `cpe23` | `cpe23` | array | CPE 2.3 technology identifiers |

---

## 1.4 Geography

| Field | Source Field | Type | Description |
|---|---|---|---|
| `country_code` | `location.country_code` | string | Country code |
| `country_name` | `location.country_name` | string | Country name |
| `city` | `location.city` | string | Observed city |

The source dataset also contains additional geographic fields such as
latitude, longitude, region code, and area code.

These fields are not currently included in the initial analytical
observation schema.

---

## 1.5 Domains and Hostnames

| Field | Source Field | Type | Description |
|---|---|---|---|
| `domains` | `domains` | array | Domains associated with the observation |
| `hostnames` | `hostnames` | array | Hostnames associated with the observation |

Missing collection values are normalized to empty arrays.

---

## 1.6 HTTP Evidence

| Field | Source Field | Type | Description |
|---|---|---|---|
| `http_status` | `http.status` | integer/null | HTTP response status |
| `http_server` | `http.server` | string/null | HTTP server identified in the response |
| `http_title` | `http.title` | string/null | HTTP page title |
| `http_host` | `http.host` | string/null | HTTP host observed |
| `http_components` | `http.components` | object | Technologies/components detected from HTTP |

These fields provide additional evidence about internet-facing web
technologies.

Missing HTTP component information is normalized to an empty object.

---

## 1.7 Time

| Field | Source Field | Type | Description |
|---|---|---|---|
| `timestamp` | `timestamp` | string/timestamp | Time at which the observation was recorded |

The source timestamp is currently retained as a timestamp-compatible
string during ingestion and is used for account-level first/last-seen
features.

---

# 2. Raw Fields Not Currently Promoted

The source dataset contains additional fields that are retained in the
original data but are not currently included in the normalized analytical
observation schema.

| Source Field | Reason |
|---|---|
| `data` | Large raw banner/service response; retained as source evidence |
| `opts` | Source-specific metadata |
| `ip` | Numeric representation; `ip_str` is easier for analysis |
| `hash` | Source/hash metadata |
| `cpe23_hash` | Hash representation of CPE |
| `_shodan` | Source crawler/module metadata |
| HTTP HTML | Large raw response body |
| HTTP hash fields | Derived source metadata |
| HTTP redirects | Not currently required |
| HTTP robots/securitytxt content | Not currently required |

These fields can be incorporated later if a specific product feature
requires them.

---

# 3. Account Layer

The account layer aggregates normalized observations at the organization
level.

Before aggregation, organization names are normalized to reduce
superficial naming variations such as capitalization, punctuation, and
common legal suffixes.

The organization normalization logic is implemented in the processing
layer.

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

The normalization process reduced the organization universe from
approximately 34,065 source organization names to approximately 33,022
normalized organizations.

The normalization is intentionally conservative and does not attempt
aggressive entity resolution.

---

## 3.1 Account Identity

| Field | Type | Description |
|---|---|---|
| `normalized_organization` | string | Canonicalized organization identifier used for account aggregation |
| `organization` | string | Representative source organization name |
| `organization_type` | string | Deterministic organization classification |

---

## 3.2 Account-Level Aggregates

| Field | Type | Description |
|---|---|---|
| `observation_count` | integer | Number of observations associated with the organization |
| `unique_ips` | integer | Number of distinct observed IP addresses |
| `unique_ports` | integer | Number of distinct observed ports |
| `unique_products` | integer | Number of distinct observed products |
| `countries_observed` | integer | Number of distinct countries associated with observations |
| `first_seen` | timestamp | Earliest observation associated with the organization |
| `last_seen` | timestamp | Most recent observation associated with the organization |

The aggregation is implemented using DuckDB over the normalized Parquet
observation layer.

---

# 4. Organization Classification

The account layer includes a deterministic organization classifier.

The current implementation uses transparent keyword-based rules and
classifies organizations into the following categories:

- `CLOUD_PROVIDER`
- `CDN_SECURITY`
- `ISP`
- `HOSTING_PROVIDER`
- `SECURITY_PROVIDER`
- `UNKNOWN`

Examples include:

    Cloudflare / Akamai / Incapsula
        → CDN_SECURITY

    Amazon / Azure / Alibaba Cloud / DigitalOcean
        → CLOUD_PROVIDER

    Telecom / broadband / network providers
        → ISP

    Hosting providers
        → HOSTING_PROVIDER

    Fortinet / Palo Alto / Zscaler
        → SECURITY_PROVIDER

Organizations that cannot be confidently classified remain:

    UNKNOWN

The classifier is intentionally conservative.

`END_CUSTOMER` is not currently assigned automatically because the available
dataset does not provide sufficient evidence to reliably distinguish every
end customer from other organization types.

---

# 5. Technology Classification

Observed products are mapped into broader technology categories.

The technology classification logic is implemented in:

    src/signals/technology.py

Current categories include:

- `WEB`
- `REMOTE_ACCESS`
- `EMAIL`
- `PROXY`
- `NETWORK`
- `CDN`
- `LOAD_BALANCER`
- `DATABASE`
- `IOT`
- `CONTAINER_PLATFORM`
- `SECURITY_NETWORK`
- `OBSERVABILITY`
- `FILE_TRANSFER`
- `OTHER`
- `UNKNOWN`

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

The mapping is deterministic and version-controlled in code.

The purpose of technology classification is to transform individual
products into interpretable technology surfaces that can be aggregated
at the account level.

---

# 6. Account Signal Layer

Account-level signals are generated from the technology classification
layer.

The implementation is located in:

    src/signals/account_signals.py

---

## 6.1 Exposure Flags

| Field | Description |
|---|---|
| `has_web_exposure` | Whether web technology was observed |
| `has_remote_access_exposure` | Whether remote-access technology was observed |
| `has_email_exposure` | Whether email infrastructure was observed |
| `has_proxy_exposure` | Whether proxy infrastructure was observed |
| `has_network_exposure` | Whether network infrastructure was observed |
| `has_database_exposure` | Whether database infrastructure was observed |
| `has_iot_exposure` | Whether IoT infrastructure was observed |
| `has_container_exposure` | Whether container/platform infrastructure was observed |
| `has_security_network_exposure` | Whether security-network technology was observed |
| `has_file_transfer_exposure` | Whether file-transfer infrastructure was observed |

These flags describe observable infrastructure characteristics.

They do not represent confirmed vulnerabilities.

---

## 6.2 Derived Signal Features

| Field | Description |
|---|---|
| `exposure_signal_count` | Number of distinct technology/security surfaces observed |
| `technology_diversity` | Number of distinct observed products |
| `infrastructure_scale` | Number of distinct observed IPs |

These fields provide contextual account-level signals for prioritization.

---

# 7. ICP Feature Layer

The ICP feature layer is implemented in:

    src/scoring/icp.py

These features provide additional context for account prioritization.

---

## 7.1 Organization Context

| Field | Description |
|---|---|
| `is_infrastructure_provider` | Whether the organization is classified as a cloud/CDN/ISP/hosting provider |
| `is_security_provider` | Whether the organization is classified as a security provider |

---

## 7.2 Infrastructure Size

| Field | Definition |
|---|---|
| `small_infrastructure` | `unique_ips <= 25` |
| `medium_infrastructure` | `25 < unique_ips <= 500` |
| `large_infrastructure` | `unique_ips > 500` |

---

## 7.3 Technology Breadth

| Field | Definition |
|---|---|
| `has_multiple_technology_surfaces` | `exposure_signal_count >= 3` |

These features are intentionally transparent and deterministic.

---

# 8. ICP Scoring Layer

The ICP scoring implementation is located in:

    src/scoring/icp_score.py

The current score is a deterministic ICP-fit heuristic.

It is explicitly **not** a learned probability and should not be interpreted
as a prediction of purchase behavior.

---

## 8.1 Scoring Principles

The score combines:

- organization context
- technology breadth
- observable security-relevant surfaces
- infrastructure scale

The design intentionally avoids allowing raw infrastructure size to
dominate the ranking.

---

## 8.2 Organization Context

Infrastructure providers receive a penalty because their large
infrastructure footprints can otherwise dominate account rankings.

Affected categories include:

- `CLOUD_PROVIDER`
- `CDN_SECURITY`
- `ISP`
- `HOSTING_PROVIDER`

Security providers are also treated as a separate segment.

`UNKNOWN` organizations remain eligible because classification confidence
is insufficient to exclude them.

---

## 8.3 Technology Surface Contribution

The final heuristic uses a gradual contribution based on the number of
observable technology/security surfaces:

    exposure_signal_count × 3

capped at:

    15 points

This avoids a hard score jump between accounts with slightly different
numbers of technology surfaces.

---

## 8.4 Technology Diversity Contribution

Technology diversity contributes gradually:

    unique_products × 1.5

capped at:

    15 points

This provides additional context without allowing product count to dominate
the entire ranking.

---

## 8.5 Infrastructure Scale

Infrastructure size is treated as supporting context rather than the primary
sales signal.

Current behavior includes:

- more than 10,000 unique IPs → penalty
- more than 500 unique IPs → modest positive contribution
- more than 25 unique IPs → smaller positive contribution

This reflects the principle:

    infrastructure scale != sales intent

---

# 9. Evaluation Layer

A hand-labelled evaluation set was created to measure whether the account
ranking is useful for sales prioritization.

The final evaluation set contains:

    30 unique accounts

with:

    5 positive accounts
    25 negative accounts

The evaluation file is:

    evals/account_relevance.jsonl

The evaluation results are stored in:

    evals/results.json

---

## 9.1 Label Definition

A positive label represents an account judged to be sufficiently relevant
as a potential cybersecurity software prospect based on observable
organization context and infrastructure evidence.

A negative label represents an account that is more appropriately treated as:

- infrastructure provider
- cloud provider
- ISP/telecom
- hosting provider
- security vendor/provider
- network allocation entity
- account with insufficient evidence

The labels are proxy relevance judgements.

They do not represent:

- confirmed buying intent
- CRM opportunities
- historical purchases
- active buying cycles
- confirmed vulnerabilities
- security incidents

---

# 10. Evaluation Metrics

The primary ranking metric is:

    Precision@10

Recall@10 and F1@10 are also reported.

For the top 10 ranked accounts:

    Precision@10 =
    relevant accounts in top 10 / 10

Recall measures how many labelled positive accounts were retrieved in the
top 10.

F1 combines precision and recall into a single summary metric.

---

# 11. Baseline Evaluation

The original infrastructure-oriented account score produced:

| Metric | Baseline |
|---|---:|
| Precision@10 | 0.200 |
| Recall@10 | 0.400 |
| F1@10 | 0.267 |
| True positives | 2 |
| False positives | 8 |
| False negatives | 3 |

The baseline therefore retrieved 2 of the 5 labelled positive accounts
within the top 10.

The ranking was strongly influenced by large infrastructure footprints.

Examples included telecom, cloud and other infrastructure-heavy
organizations.

---

# 12. ICP-Aware Evaluation

The ICP-aware scoring layer was evaluated against the exact same 30-account
evaluation set.

Results:

| Metric | Baseline | ICP-aware |
|---|---:|---:|
| Precision@10 | 0.200 | **0.500** |
| Recall@10 | 0.400 | **1.000** |
| F1@10 | 0.267 | **0.667** |
| True positives | 2 | **5** |
| False positives | 8 | **5** |
| False negatives | 3 | **0** |

The experiment showed a directional improvement:

    Precision@10:
    0.20 → 0.50

    Recall@10:
    0.40 → 1.00

    F1@10:
    0.267 → 0.667

---

# 13. Deterministic Ranking

To make evaluation reproducible, accounts with equal ICP scores are ordered
using deterministic tie-breakers.

Ranking order:

1. `icp_fit_score`
2. `exposure_signal_count`
3. `unique_products`
4. `unique_ips`

This prevents ranking behavior from depending on arbitrary dataframe ordering.

---

# 14. Evaluation Limitations

The evaluation set is intentionally small.

It contains only:

    30 accounts
    5 positive examples

Therefore, the metrics should be interpreted as directional rather than
production-level performance estimates.

The evaluation labels are also proxy relevance judgements rather than
observed customer outcomes.

The dataset does not directly provide:

- company revenue
- employee count
- security budget
- CRM history
- current security tooling
- active buying cycle
- contact information
- confirmed organizational ownership

Therefore, the current system should be described as:

    account prioritization

rather than:

    purchase probability

---

# 15. Important Interpretation Rules

## 15.1 Observation != Vulnerability

An observed service is an observable infrastructure characteristic.

It should not automatically be interpreted as a security vulnerability.

For example:

    port = 22
    product = OpenSSH

means that an SSH service was observed.

It does not establish that the service is vulnerable.

---

## 15.2 Observation Volume != Sales Intent

A large number of observations can indicate a large infrastructure footprint.

It does not automatically indicate that the organization is more likely to
purchase cybersecurity software.

Cloud providers, CDNs, ISPs, hosting providers and other infrastructure-heavy
organizations can naturally generate large observation volumes.

---

## 15.3 Source Organization != Verified Company Entity

The `organization` field comes directly from the source dataset.

Different organization names may represent:

- different business entities
- subsidiaries
- network providers
- hosting infrastructure
- cloud infrastructure
- related organizations

Entity resolution beyond deterministic name normalization is therefore a
future enhancement.

---

# 16. Data Quality Rules

## 16.1 High-Value Fields

The following fields are expected to be available frequently:

- `organization`
- `port`
- `transport`
- `timestamp`
- `country_code`
- `country_name`
- `city`

---

## 16.2 Optional Fields

The following fields can legitimately be missing:

- `isp`
- `asn`
- `product`
- `os`
- `http_status`
- `http_server`
- `http_title`
- `http_host`

Missing optional fields should not cause an observation to be discarded.

---

## 16.3 Collection Fields

The following fields are normalized to empty arrays when absent:

- `domains`
- `hostnames`
- `cpe`
- `cpe23`

---

## 16.4 Object Fields

The following fields are normalized to empty objects when absent:

- `http_components`

---

# 17. Data Flow

The current architecture is:

    Firmable JSONL / ZST
            |
            v
      Streaming Reader
            |
            v
        JSON Parsing
            |
            v
        Normalization
            |
            v
     Observation Parquet
            |
            v
   Organization Normalization
            |
            v
   Organization Aggregation
            |
            +----------------------+
            |                      |
            v                      v
   Organization             Product Classification
   Classification                   |
            |                      |
            +----------+-----------+
                       |
                       v
                Account Signals
                       |
                       v
                  ICP Features
                       |
                       v
                 ICP Scoring
                       |
                       v
                 Evaluation
                       |
                       v
          AI Account Intelligence
                       |
                       v
                CyberSignal App

The AI Account Intelligence and application layers are the next development
stage.

---

# 18. Current Project Layers

The current implementation can therefore be summarized as:

    Layer 1 — Observation
        Normalized source observations

    Layer 2 — Account
        Organization-level aggregation

    Layer 3 — Signals
        Technology and infrastructure signals

    Layer 4 — ICP
        Deterministic account prioritization

    Layer 5 — Evaluation
        Hand-labelled benchmark and ranking metrics

    Layer 6 — AI Intelligence
        Planned evidence-grounded account analysis and outreach

    Layer 7 — Application
        Planned CyberSignal sales intelligence interface

---

# 19. Current Implementation Files

Relevant implementation files include:

    src/ingestion/jsonl_reader.py
    src/ingestion/normalize.py
    src/ingestion/jsonl_to_parquet.py

    src/processing/aggregate_accounts.py

    src/signals/technology.py
    src/signals/account_signals.py

    src/scoring/icp.py
    src/scoring/icp_score.py

    evals/account_relevance.jsonl
    evals/results.json

---

# 20. Summary

The CyberSignal data layer transforms a very large observation-oriented
infrastructure dataset into an explainable organization-level intelligence
system.

The current pipeline:

    Raw infrastructure observations
            ↓
    Streaming normalization
            ↓
    Analytical Parquet layer
            ↓
    Organization normalization
            ↓
    Account aggregation
            ↓
    Organization classification
            ↓
    Technology classification
            ↓
    Account-level signals
            ↓
    ICP features
            ↓
    Deterministic ICP scoring
            ↓
    Hand-labelled evaluation

The current evaluation demonstrates that adding organization context and
technology-surface signals improves account ranking relative to the initial
infrastructure-oriented baseline.

The next stage is to build an AI-native intelligence layer that converts
these deterministic signals into evidence-grounded account explanations,
"Why Now?" analysis, and personalized sales outreach.
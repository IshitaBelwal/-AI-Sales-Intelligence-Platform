# CyberSignal Data Dictionary

## Overview

CyberSignal uses the Firmable infrastructure dataset as its primary
source of technical observations.

The source dataset is observation-oriented: each record represents an
internet-facing infrastructure/service observation associated with an
organization.

The data is transformed into two primary analytical layers:

1. Observation layer
2. Account layer

---

# 1. Observation Layer

The observation layer preserves one normalized row per source
observation.

## Organization and Network Identity

| Field | Source Field | Type | Description |
|---|---|---|---|
| `organization` | `org` | string | Organization associated with the observation |
| `isp` | `isp` | string | Internet service provider associated with the observation |
| `asn` | `asn` | string | Autonomous System Number associated with the observation |
| `ip` | `ip_str` | string | Human-readable IP address |

---

## Network

| Field | Source Field | Type | Description |
|---|---|---|---|
| `port` | `port` | integer | Observed network port |
| `transport` | `transport` | string | Transport protocol, such as TCP or UDP |

---

## Technology

| Field | Source Field | Type | Description |
|---|---|---|---|
| `product` | `product` | string | Detected product or service |
| `os` | `os` | string/null | Detected operating system |
| `cpe` | `cpe` | array | CPE technology identifiers |
| `cpe23` | `cpe23` | array | CPE 2.3 technology identifiers |

---

## Geography

| Field | Source Field | Type | Description |
|---|---|---|---|
| `country_code` | `location.country_code` | string | Country code |
| `country_name` | `location.country_name` | string | Country name |
| `city` | `location.city` | string | Observed city |

The source also contains latitude, longitude, region code, and area
code. These are not currently included in the initial analytical
observation schema.

---

## Domains and Hostnames

| Field | Source Field | Type | Description |
|---|---|---|---|
| `domains` | `domains` | array | Domains associated with the observation |
| `hostnames` | `hostnames` | array | Hostnames associated with the observation |

Empty arrays are used when no values are available.

---

## HTTP Evidence

| Field | Source Field | Type | Description |
|---|---|---|---|
| `http_status` | `http.status` | integer/null | HTTP response status |
| `http_server` | `http.server` | string/null | HTTP server identified in the response |
| `http_title` | `http.title` | string/null | HTTP page title |
| `http_host` | `http.host` | string/null | HTTP host observed |
| `http_components` | `http.components` | object | Technologies/components detected from HTTP |

These fields are useful for identifying internet-facing web
technologies.

---

## Time

| Field | Source Field | Type | Description |
|---|---|---|---|
| `timestamp` | `timestamp` | string/timestamp | Time at which the observation was recorded |

The timestamp will later be converted into a proper datetime type
when building analytical features such as recency.

---

# 2. Raw Fields Not Currently Promoted

The source dataset contains additional fields that are retained in
the original data but are not currently included in the normalized
analytical layer.

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

The account layer aggregates observations by the source
`organization` value.

One row represents an organization-level account candidate.

| Field | Type | Description |
|---|---|---|
| `organization` | string | Source organization name |
| `observation_count` | integer | Number of observations associated with the organization |
| `unique_ips` | integer | Number of distinct observed IP addresses |
| `unique_ports` | integer | Number of distinct observed ports |
| `unique_products` | integer | Number of distinct observed products |
| `countries_observed` | integer | Number of distinct countries associated with observations |
| `first_seen` | timestamp | Earliest observation associated with the organization |
| `last_seen` | timestamp | Most recent observation associated with the organization |

---

# 4. Derived Fields Planned for Future Versions

The following fields are not part of the initial Day 1 account table but
are planned for the signal and scoring layers.

## Infrastructure Signals

Potential future fields:

- `exposed_service_count`
- `internet_facing_ip_count`
- `technology_diversity`
- `port_diversity`
- `web_service_count`
- `remote_access_service_count`
- `database_service_count`

These will be derived from observed products, ports, CPEs, HTTP
metadata, and other evidence.

---

## Recency Signals

Potential future fields:

- `days_since_last_seen`
- `recent_observation_count`
- `observation_frequency`

These features will help distinguish historical observations from
recently observed infrastructure.

---

## Organization Classification

Potential future field:

- `organization_type`

Potential values include:

- `END_CUSTOMER`
- `CLOUD_PROVIDER`
- `CDN`
- `ISP`
- `HOSTING_PROVIDER`
- `SECURITY_PROVIDER`
- `UNKNOWN`

The classification is important because infrastructure volume has
different meanings for different organization types.

---

## Account Scoring

Potential future fields:

- `account_score`
- `score_band`
- `signal_count`
- `score_explanation`

The scoring model will combine multiple observable signals rather than
using raw observation volume as the primary ranking criterion.

---

# 5. Data Quality Rules

The ingestion layer follows these principles:

### Required / high-value fields

The following fields are expected to be available frequently:

- `organization`
- `port`
- `transport`
- `timestamp`
- `country_code`
- `country_name`
- `city`

### Optional fields

The following can legitimately be missing:

- `isp`
- `asn`
- `product`
- `os`
- `http_status`
- `http_server`
- `http_title`
- `http_host`

Missing optional fields should not cause an observation to be
discarded.

### Collection fields

The following are normalized to empty arrays when absent:

- `domains`
- `hostnames`
- `cpe`
- `cpe23`

### Object fields

The following are normalized to empty objects when absent:

- `http_components`

---

# 6. Important Interpretation Rules

## Observation ≠ Vulnerability

An exposed service is an observable infrastructure characteristic.

It should not automatically be interpreted as a security vulnerability.

For example:

    port = 22
    product = OpenSSH

means that an SSH service was observed.

It does not, by itself, establish that the service is vulnerable.

---

## Observation Volume ≠ Sales Intent

A large number of observations can indicate a large infrastructure
footprint.

It does not automatically indicate that the organization is more
likely to purchase cybersecurity software.

Cloud providers, CDNs, ISPs, hosting providers, and other
infrastructure-heavy organizations can naturally generate large
observation volumes.

---

## Source Organization ≠ Verified Company Entity

The `organization` field is taken from the source dataset.

Different organization names may represent:

- Different business entities
- Subsidiaries
- Network providers
- Hosting infrastructure
- Cloud infrastructure
- Related organizations

Entity resolution is therefore a future processing step.

---

# 7. Data Flow

The current data pipeline is:

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
       DuckDB Queries
             |
             v
    Organization Aggregation
             |
             v
       Account Parquet
             |
             v
       Signal Engine
             |
             v
       Account Scoring
             |
             v
      CyberSignal App
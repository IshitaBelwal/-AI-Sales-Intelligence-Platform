# Day 02 — Data Ingestion and Normalization

## Objective

Build a memory-efficient ingestion pipeline capable of processing the large
Firmable cybersecurity observation dataset without loading the complete
dataset into memory.

The provided dataset is approximately 11.5 GB compressed and approximately
78.8 GB when decompressed. The dataset contains hundreds of millions of
observations, so a streaming architecture was required.

---

## 1. Ingestion Strategy

The raw dataset is stored as newline-delimited JSON compressed using Zstandard.

Instead of decompressing the entire file to disk or loading it into memory,
the pipeline uses streaming decompression.

Pipeline:

    Zstandard compressed JSONL
              |
              v
       Streaming decompression
              |
              v
          JSON parsing
              |
              v
        Record normalization
              |
              v
        Batched Parquet output

This approach keeps memory usage bounded by the configured batch size.

---

## 2. Development Dataset

For development and iteration, a 2 million record subset was used.

The much larger source dataset was retained as the eventual production-scale
input, while the 2M-record dataset provided a practical development loop.

A smaller ~8K record sample was also used for rapid schema exploration and
testing.

---

## 3. Streaming JSONL Reader

A reusable reader was implemented in:

    src/ingestion/jsonl_reader.py

Two input modes are supported:

- regular JSONL
- Zstandard-compressed JSONL

The Zstandard reader uses a streaming decompressor rather than first
decompressing the complete source file.

Malformed JSON lines are skipped so that a single corrupted record does not
terminate the entire ingestion process.

---

## 4. Record Normalization

Raw records contain nested structures such as:

- location
- HTTP metadata
- CPE information
- domains
- hostnames

A normalization layer was implemented in:

    src/ingestion/normalize.py

The normalized observation schema includes:

- organization
- ISP
- ASN
- IP address
- port
- transport
- product
- OS
- country
- city
- domains
- hostnames
- CPE/CPE23
- HTTP status
- HTTP server
- HTTP title
- HTTP host
- HTTP components
- timestamp

This converts heterogeneous nested JSON records into a consistent analytical
schema.

---

## 5. Validation

The normalizer was tested against 100 records.

Result:

- 100 records processed
- 0 normalization errors

Missing values were profiled rather than automatically discarded.

For example, product and OS information were frequently missing, while core
fields such as organization, country and timestamp were substantially more
complete.

This distinction is important because missing product information does not
necessarily mean the observation itself is invalid.

---

## 6. Parquet Conversion

A batch-based JSONL-to-Parquet pipeline was implemented in:

    src/ingestion/jsonl_to_parquet.py

The pipeline processes records in batches rather than accumulating the entire
dataset in memory.

Parquet was selected as the analytical storage format because it provides:

- columnar storage
- efficient analytical reads
- compression
- compatibility with DuckDB, Pandas and Polars
- convenient downstream processing

A 10K-record test was successfully written to Parquet and queried using
DuckDB.

The full 2M-record development dataset was subsequently ingested
successfully.

---

## 7. Engineering Decisions

### Why streaming?

The decompressed source dataset is far too large to safely load into memory.

Streaming allows the same processing architecture to scale from the 2M
development dataset to the much larger source dataset.

### Why Parquet?

The downstream workload is analytical rather than transactional. Parquet
allows us to read only the columns required by each analytical operation.

### Why normalize early?

Downstream signal generation and account aggregation should operate on a
stable schema rather than repeatedly navigating the original nested JSON
structure.

---

## 8. Result

The project now has a reusable ingestion layer:

    Raw Zstandard JSONL
            ↓
    Streaming reader
            ↓
    Normalizer
            ↓
    Batched Parquet
            ↓
    Analytical processing

This establishes the foundation for organization-level aggregation and
cybersecurity signal generation.
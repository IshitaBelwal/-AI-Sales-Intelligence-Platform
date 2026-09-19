from src.ingestion.jsonl_to_parquet import (
    convert_jsonl_to_parquet
)


convert_jsonl_to_parquet(
    "/tmp/firmable_10k.jsonl",
    "data/processed/observations_test",
    batch_size=1000,
)
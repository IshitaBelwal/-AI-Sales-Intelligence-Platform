from src.ingestion.jsonl_to_parquet import convert_jsonl_to_parquet


convert_jsonl_to_parquet(
    "/Users/ishitabelwal/Downloads/firmable_2M.jsonl",
    "data/processed/observations",
    batch_size=50_000,
)
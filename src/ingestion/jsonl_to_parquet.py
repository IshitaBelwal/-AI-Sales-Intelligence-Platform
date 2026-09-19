from pathlib import Path

import pandas as pd

from src.ingestion.jsonl_reader import (
    read_jsonl,
    read_zst_jsonl,
)

from src.ingestion.normalize import normalize_record


def convert_jsonl_to_parquet(
    input_path,
    output_dir,
    batch_size=50_000,
):
    """
    Convert JSONL into normalized Parquet files.

    The input is processed in batches so the entire
    dataset does not need to fit into memory.
    """

    input_path = Path(input_path)
    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # Choose the appropriate reader
    if input_path.suffix == ".zst":
        reader = read_zst_jsonl(input_path)
    else:
        reader = read_jsonl(input_path)

    batch = []

    part_number = 0
    total_records = 0
    bad_records = 0

    for line_number, record in reader:

        try:

            normalized = normalize_record(record)

            batch.append(normalized)

            total_records += 1

        except Exception:

            bad_records += 1

            continue

        # Write a Parquet file every batch_size records
        if len(batch) >= batch_size:

            df = pd.DataFrame(batch)

            output_file = (
                output_dir
                / f"part-{part_number:05d}.parquet"
            )

            df.to_parquet(
                output_file,
                index=False
            )

            print(
                f"Wrote {output_file} "
                f"({len(df):,} records)"
            )

            batch = []

            part_number += 1

    # Write the final partial batch
    if batch:

        df = pd.DataFrame(batch)

        output_file = (
            output_dir
            / f"part-{part_number:05d}.parquet"
        )

        df.to_parquet(
            output_file,
            index=False
        )

        print(
            f"Wrote {output_file} "
            f"({len(df):,} records)"
        )

    print()
    print("========== INGESTION COMPLETE ==========")
    print(f"Records processed: {total_records:,}")
    print(f"Bad records:       {bad_records:,}")
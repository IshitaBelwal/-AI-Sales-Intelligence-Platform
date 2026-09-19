# STREAMING

import io
import json

import zstandard as zstd


def read_jsonl(path):
    """
    Read a normal JSONL file one record at a time.
    """

    with open(path, "r", encoding="utf-8") as f:

        for line_number, line in enumerate(f, start=1):

            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)

                yield line_number, record

            except json.JSONDecodeError:
                continue


def read_zst_jsonl(path):
    """
    Read a zstandard-compressed JSONL file
    without fully decompressing it to disk.
    """

    with open(path, "rb") as f:

        dctx = zstd.ZstdDecompressor()

        with dctx.stream_reader(f) as reader:

            text_stream = io.TextIOWrapper(
                reader,
                encoding="utf-8"
            )

            for line_number, line in enumerate(
                text_stream,
                start=1
            ):

                line = line.strip()

                if not line:
                    continue

                try:
                    record = json.loads(line)

                    yield line_number, record

                except json.JSONDecodeError:
                    continue
import json
from datetime import datetime, timezone
from pathlib import Path

from src.llm.cost import ModelPricing, calculate_cost


PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRACE_DIR = PROJECT_ROOT / "data"
TRACE_FILE = TRACE_DIR / "llm_traces.jsonl"


# Keep pricing configurable.
# These are example rates only and should be replaced
# with verified provider pricing before production use.
DEFAULT_PRICING = ModelPricing(
    input_per_million=1.0,
    output_per_million=2.0,
)


def log_llm_trace(
    *,
    account: str,
    prompt_version: str,
    result: dict,
    status: str = "success",
):
    """
    Append one LLM call trace to a JSONL file.
    """

    TRACE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata = result["metadata"]

    estimated_cost_usd = calculate_cost(
        input_tokens=metadata["input_tokens"],
        output_tokens=metadata["output_tokens"],
        pricing=DEFAULT_PRICING,
    )

    trace = {
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "account": account,

        "prompt_version": prompt_version,

        "model": metadata["model"],

        "response_id": metadata["response_id"],

        "latency_ms": metadata["latency_ms"],

        "input_tokens": metadata["input_tokens"],

        "output_tokens": metadata["output_tokens"],

        "total_tokens": metadata["total_tokens"],

        "estimated_cost_usd": estimated_cost_usd,

        "status": status,
    }

    with open(
        TRACE_FILE,
        "a",
        encoding="utf-8",
    ) as f:

        f.write(
            json.dumps(trace)
            + "\n"
        )

    return trace
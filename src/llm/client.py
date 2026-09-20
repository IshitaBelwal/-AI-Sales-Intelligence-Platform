import json
import os
import time

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

from src.llm.tracing import log_llm_trace


MODEL = "openai/gpt-oss-20b"


def generate_account_intelligence(
    prompt: str,
    account: str | None = None,
    prompt_version: str = "account_intelligence_v1",
) -> dict:
    """
    Generate structured account intelligence using Groq.

    Returns both the parsed AI output and API metadata.
    Automatically writes an LLM trace when an account is provided.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set.")

    client = Groq(api_key=api_key)

    start_time = time.perf_counter()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise AI sales intelligence analyst. "
                    "Return only valid JSON matching the requested structure."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    latency_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    text = response.choices[0].message.content
    usage = response.usage

    result = {
        "raw_text": text,
        "parsed": json.loads(text),
        "metadata": {
            "model": MODEL,
            "response_id": response.id,
            "latency_ms": latency_ms,
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        },
    }

    if account is not None:
        log_llm_trace(
            account=account,
            prompt_version=prompt_version,
            result=result,
            status="success",
        )

    return result
from dataclasses import dataclass


@dataclass
class ModelPricing:
    """
    Pricing per 1 million tokens.
    """

    input_per_million: float
    output_per_million: float


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    pricing: ModelPricing,
) -> float:
    """
    Calculate estimated LLM cost in USD.
    """

    input_cost = (
        input_tokens / 1_000_000
    ) * pricing.input_per_million

    output_cost = (
        output_tokens / 1_000_000
    ) * pricing.output_per_million

    return round(
        input_cost + output_cost,
        8,
    )
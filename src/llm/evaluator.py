import re


def _combined_text(output: dict) -> str:
    """
    Combine the generated fields into one searchable text.
    """

    fields = [
        "summary",
        "why_relevant",
        "security_conversation",
        "recommended_angle",
    ]

    parts = []

    for field in fields:
        value = output.get(field, "")

        if isinstance(value, str):
            parts.append(value)

    for evidence in output.get("evidence", []):
        if isinstance(evidence, dict):
            parts.append(str(evidence.get("signal", "")))
            parts.append(str(evidence.get("observation", "")))

    return " ".join(parts).lower()


def evaluate_output(
    output: dict,
    required_signals: list[str],
    forbidden_claims: list[str],
) -> dict:
    """
    Evaluate grounding of one AI-generated account intelligence output.
    """

    text = _combined_text(output)

    # -----------------------------
    # Forbidden claim detection
    # -----------------------------

    violations = []

    for claim in forbidden_claims:
        if claim.lower() in text:
            violations.append(claim)

    # -----------------------------
    # Required signal coverage
    # -----------------------------

    matched_signals = []

    for signal in required_signals:
        if re.search(
            rf"\b{re.escape(signal.lower())}\b",
            text,
        ):
            matched_signals.append(signal)

    signal_coverage = (
        len(matched_signals) / len(required_signals)
        if required_signals
        else 1.0
    )

    # -----------------------------
    # Grounding score
    # -----------------------------

    no_forbidden_claims = len(violations) == 0

    grounding_score = (
        0.5 * signal_coverage
        + 0.5 * float(no_forbidden_claims)
    )

    return {
        "forbidden_claims": violations,
        "forbidden_claim_count": len(violations),
        "matched_signals": matched_signals,
        "signal_coverage": round(signal_coverage, 3),
        "grounding_score": round(grounding_score, 3),
    }
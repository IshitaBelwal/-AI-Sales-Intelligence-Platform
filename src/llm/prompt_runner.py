from pathlib import Path
import json


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROMPT_DIR = PROJECT_ROOT / "prompts"


def load_prompt(version: str) -> str:
    """
    Load a versioned prompt from the prompts directory.
    """

    prompt_path = PROMPT_DIR / f"{version}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt not found: {prompt_path}"
        )

    return prompt_path.read_text(
        encoding="utf-8"
    )


def render_account_prompt(
    evidence: dict,
    version: str = "account_intelligence_v1",
) -> str:
    """
    Render an account-intelligence prompt.
    """

    prompt = load_prompt(version)

    evidence_json = json.dumps(
        evidence,
        indent=2,
        default=str,
    )

    return prompt.replace(
        "{{ACCOUNT_EVIDENCE}}",
        evidence_json,
    )


def render_outreach_prompt(
    evidence: dict,
    intelligence: dict,
    version: str = "outreach_v1",
) -> str:
    """
    Render an outreach-generation prompt.
    """

    prompt = load_prompt(version)

    evidence_json = json.dumps(
        evidence,
        indent=2,
        default=str,
    )

    intelligence_json = json.dumps(
        intelligence,
        indent=2,
        default=str,
    )

    prompt = prompt.replace(
        "{{ACCOUNT_EVIDENCE}}",
        evidence_json,
    )

    prompt = prompt.replace(
        "{{ACCOUNT_INTELLIGENCE}}",
        intelligence_json,
    )

    return prompt
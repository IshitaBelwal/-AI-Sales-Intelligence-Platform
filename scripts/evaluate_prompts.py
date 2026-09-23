import json
import sys
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Project path
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# Project imports
# ---------------------------------------------------------

from src.llm.client import generate_account_intelligence
from src.llm.evaluator import evaluate_output
from src.llm.prompt_runner import render_account_prompt
from src.signals.account_evidence import build_account_evidence
from src.signals.account_signals import build_account_signals
from src.scoring.icp import add_icp_features
from src.scoring.icp_score import add_icp_score


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

EVAL_FILE = (
    PROJECT_ROOT
    / "evals"
    / "llm_grounding.jsonl"
)

ACCOUNTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "account_features.parquet"
)


FORBIDDEN_CLAIMS = [
    "vulnerability",
    "vulnerable",
    "compromised",
    "under attack",
    "being targeted",
    "attackers are targeting",
    "buying intent",
    "needs security product",
    "commonly targeted",
    "attack surface",
    "broad attack surface",
    "broad surface",
    "at risk",
    "security problem",
    "security weakness",
    "security gap",
    "security deficiency",
    "security posture",
    "significant presence",
    "strengthen your security",
    "strengthen its security",
    "strengthen the security",
    "improve your security",
    "improve its security",
]


# ---------------------------------------------------------
# Load accounts
# ---------------------------------------------------------

def load_accounts():
    accounts = pd.read_parquet(
        ACCOUNTS_FILE
    )

    accounts = build_account_signals(
        accounts
    )

    accounts = add_icp_features(
        accounts
    )

    accounts = add_icp_score(
        accounts
    )

    return accounts


# ---------------------------------------------------------
# Load evaluation cases
# ---------------------------------------------------------

def load_eval_cases():

    cases = []

    with open(
        EVAL_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        for line in f:

            line = line.strip()

            if line:
                cases.append(
                    json.loads(line)
                )

    return cases


# ---------------------------------------------------------
# Run evaluation
# ---------------------------------------------------------

def main():

    print(
        "Running prompt evaluation..."
    )
    print()

    accounts = load_accounts()
    cases = load_eval_cases()

    results = []

    for index, case in enumerate(
        cases,
        start=1,
    ):

        account_name = case[
            "account"
        ]

        prompt_version = case[
            "prompt_version"
        ]

        print(
            f"[{index}/{len(cases)}] "
            f"{account_name} → "
            f"{prompt_version}"
        )

        matches = accounts[
            accounts[
                "normalized_organization"
            ]
            == account_name
        ]

        if matches.empty:

            print(
                f"  Skipping missing account: "
                f"{account_name}"
            )

            continue

        row = matches.iloc[0]

        evidence = build_account_evidence(
            row
        )

        prompt = render_account_prompt(
            evidence,
            version=prompt_version,
        )

        result = (
            generate_account_intelligence(
                prompt,
                account=account_name,
                prompt_version=prompt_version,
            )
        )

        evaluation = evaluate_output(
            output=result["parsed"],
            required_signals=case[
                "required_signals"
            ],
            forbidden_claims=FORBIDDEN_CLAIMS,
        )

        results.append(
            {
                "account": account_name,
                "prompt_version": prompt_version,
                **evaluation,
            }
        )

        print(
            f"  Grounding score: "
            f"{evaluation['grounding_score']:.3f}"
        )

        print(
            f"  Signal coverage: "
            f"{evaluation['signal_coverage']:.3f}"
        )

        if evaluation[
            "forbidden_claims"
        ]:

            print(
                "  Forbidden claims: "
                + ", ".join(
                    evaluation[
                        "forbidden_claims"
                    ]
                )
            )

        print()


    # -----------------------------------------------------
    # Save detailed results
    # -----------------------------------------------------

    output_file = (
        PROJECT_ROOT
        / "evals"
        / "prompt_evaluation_results.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
        )


    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print(
        "========================================"
    )

    print(
        "Prompt Evaluation Complete"
    )

    print(
        "========================================"
    )

    print(
        f"Cases evaluated: "
        f"{len(results)}"
    )

    print(
        f"Results: {output_file}"
    )

    print()


    # -----------------------------------------------------
    # Compare prompt versions
    # -----------------------------------------------------

    for version in [
        "account_intelligence_v1",
        "account_intelligence_v2",
    ]:

        version_results = [
            r
            for r in results
            if r[
                "prompt_version"
            ] == version
        ]

        if not version_results:
            continue

        forbidden_rate = (
            sum(
                r[
                    "forbidden_claim_count"
                ] > 0
                for r in version_results
            )
            / len(version_results)
        )

        signal_coverage = (
            sum(
                r[
                    "signal_coverage"
                ]
                for r in version_results
            )
            / len(version_results)
        )

        grounding_score = (
            sum(
                r[
                    "grounding_score"
                ]
                for r in version_results
            )
            / len(version_results)
        )

        print(
            f"{version}"
        )

        print(
            f"  Forbidden-claim rate: "
            f"{forbidden_rate:.1%}"
        )

        print(
            f"  Signal coverage: "
            f"{signal_coverage:.1%}"
        )

        print(
            f"  Average grounding: "
            f"{grounding_score:.3f}"
        )

        print()


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
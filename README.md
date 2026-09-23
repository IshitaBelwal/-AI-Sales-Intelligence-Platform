# CyberSignal

CyberSignal is an AI-native sales intelligence platform for cybersecurity software teams.

It transforms large-scale internet infrastructure observations into organization-level account intelligence, deterministic ICP-fit scoring, grounded AI analysis, and evidence-based outreach.

The system is designed around a core principle:

> Observed infrastructure is evidence for a sales conversation — not proof of vulnerability, security risk, or buying intent.

---

## What CyberSignal Does

CyberSignal helps a sales team move from a large infrastructure dataset to a focused set of accounts worth researching.

The workflow is:

```text
Raw Infrastructure Observations
            ↓
Streaming Normalization
            ↓
Organization-Level Aggregation
            ↓
Technology Signal Extraction
            ↓
ICP Fit Scoring
            ↓
Account Discovery
            ↓
AI Account Intelligence
            ↓
Evidence-Based Outreach
```

The application supports:

* Account discovery
* Search and filtering
* Organization classification
* Technology signal analysis
* Deterministic ICP-fit scoring
* Account evidence inspection
* AI-generated account intelligence
* AI-generated outreach
* Prompt versioning
* LLM tracing
* Token and cost tracking
* Prompt grounding evaluation

---

## Product Flow

```text
CyberSignal
│
├── Discover Accounts
│   ├── Search
│   ├── Filter
│   └── Rank by ICP fit
│
├── Account Intelligence
│   ├── Account overview
│   ├── Infrastructure scale
│   ├── Technology signals
│   └── Observation window
│
├── AI Analysis
│   ├── Why this account may be relevant
│   ├── Evidence
│   ├── Security conversation
│   └── Recommended angle
│
└── Outreach
    ├── Subject
    ├── Opening
    ├── Body
    ├── Call to action
    └── Evidence used
```

---

## Architecture

```text
                         ┌─────────────────────┐
                         │   Raw JSONL / ZST    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Streaming Ingestion │
                         │ + Normalization     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Organization        │
                         │ Aggregation         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Technology Signals  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Deterministic       │
                         │ ICP Fit Scoring     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Streamlit App       │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                ┌─────────────────┐   ┌─────────────────┐
                │ Account         │   │ Outreach        │
                │ Intelligence    │   │ Generation      │
                └────────┬────────┘   └────────┬────────┘
                         │                     │
                         └──────────┬──────────┘
                                    ▼
                         ┌─────────────────────┐
                         │ LLM Tracing         │
                         │ + Cost Tracking     │
                         └─────────────────────┘
```

---

## Data Processing

The source dataset contains hundreds of millions of internet infrastructure observations.

Because loading the complete decompressed dataset into memory is impractical for local development, CyberSignal uses streaming ingestion.

The ingestion pipeline:

1. Reads JSONL records incrementally.
2. Supports compressed `.zst` JSONL input.
3. Normalizes organization and infrastructure fields.
4. Writes normalized data to Parquet.
5. Aggregates observations at organization level.
6. Derives technology signals.
7. Produces an application-ready account dataset.

The development dataset contains approximately 2 million observations.

The final application dataset contains approximately 33,000 normalized organizations.

---

## Organization Classification

Raw observation volume can be misleading because infrastructure providers naturally generate large numbers of observations.

CyberSignal therefore classifies organizations into categories such as:

```text
CLOUD_PROVIDER
CDN_SECURITY
ISP
HOSTING_PROVIDER
SECURITY_PROVIDER
UNKNOWN
```

Infrastructure providers are treated differently during ICP scoring so that organizations such as cloud providers, CDNs, ISPs, and hosting companies do not automatically dominate account ranking simply because they have more infrastructure observations.

The classifier is intentionally conservative.

For example, a generic organization name such as `google` is not automatically treated as a cloud provider because the available observation data may not establish which part of the organization the observation represents.

---

## Technology Signals

CyberSignal converts observed products into higher-level technology categories.

Examples include:

```text
WEB
REMOTE_ACCESS
EMAIL
PROXY
NETWORK
DATABASE
IOT
CONTAINER
SECURITY_NETWORK
FILE_TRANSFER
```

For example:

```text
nginx
Apache HTTP Server
Microsoft IIS
OpenResty
```

can contribute to the `WEB` signal.

The system aggregates these observations at account level rather than treating individual products as isolated sales signals.

---

## ICP Fit Scoring

ICP scoring is intentionally deterministic and transparent.

The current heuristic considers:

* organization type
* number of technology signal categories
* technology diversity
* infrastructure scale

The score is used for ranking and prioritization.

It is **not**:

* a probability of purchase
* a prediction of conversion
* a prediction of security risk
* a measurement of buying intent

This distinction is important because the source dataset contains infrastructure observations rather than CRM outcomes.

---

## Evaluation

CyberSignal includes a hand-labelled evaluation set containing 30 accounts:

```text
Positive proxy-relevance labels: 5
Negative proxy-relevance labels: 25
Evaluation size: 30
```

The evaluation compares a simple baseline ranking against the ICP-aware ranking.

### Top-10 evaluation

| Metric          | Baseline | ICP-aware |
| --------------- | -------: | --------: |
| True positives  |        2 |         5 |
| False positives |        8 |         5 |
| False negatives |        3 |         0 |
| Precision@10    |    0.200 |     0.500 |
| Recall@10       |    0.400 |     1.000 |
| F1@10           |    0.267 |     0.667 |

These are **directional results** from a small hand-labelled proxy evaluation set. They should not be interpreted as production model performance or purchase prediction.

---

## AI Account Intelligence

The AI layer receives structured account evidence rather than raw observations.

Example evidence includes:

```json
{
  "account": "oracle",
  "organization_type": "UNKNOWN",
  "icp_fit_score": 85,
  "scale": {
    "unique_ips": 1265,
    "unique_ports": 201,
    "unique_products": 46,
    "countries_observed": 23
  },
  "technology_signals": {
    "web": {
      "observed_ips": 235
    },
    "remote_access": {
      "observed_ips": 232
    }
  }
}
```

The LLM is instructed to ground its output in this evidence.

It generates:

* account summary
* why the account may be relevant
* supporting evidence
* security conversation
* recommended angle
* confidence

---

## Grounding and Safety Rules

The AI layer explicitly avoids unsupported claims.

Infrastructure observations must not automatically be described as:

* vulnerabilities
* compromised systems
* active attacks
* attacker targeting
* buying intent
* security problems
* security weaknesses
* security gaps
* security deficiencies
* attack surface
* security posture

The preferred language is evidence-based:

> "The dataset shows..."

> "Observed infrastructure includes..."

> "The observations provide a basis for discussing..."

This keeps the AI layer grounded in the actual dataset.

---

## Prompt Versioning

Prompts are stored as versioned files:

```text
prompts/
├── account_intelligence_v1.txt
├── account_intelligence_v2.txt
└── outreach_v1.txt
```

Prompt versions can be evaluated against the same account evidence.

This makes prompt changes reproducible and allows regressions to be detected.

---

## Prompt Evaluation

The repository contains a one-command prompt evaluation harness:

```bash
python scripts/evaluate_prompts.py
```

The evaluation checks:

* required signal coverage
* forbidden-claim violations
* grounding score

The current evaluation compares:

```text
account_intelligence_v1
account_intelligence_v2
```

Across 5 accounts × 2 prompt versions:

```text
v1
Forbidden-claim rate: 40.0%
Signal coverage:      93.3%
Average grounding:    0.767

v2
Forbidden-claim rate: 0.0%
Signal coverage:      100.0%
Average grounding:    1.000
```

The evaluation is intentionally small and should be treated as a regression/grounding check rather than a statistically representative benchmark.

---

## LLM Tracing

Each LLM request records structured metadata including:

```text
timestamp
account
prompt_version
model
response_id
latency_ms
input_tokens
output_tokens
total_tokens
estimated_cost_usd
status
```

Runtime traces are written to:

```text
data/llm_traces.jsonl
```

The trace file is intentionally excluded from Git because it is generated runtime data.

---

## Cost Tracking

LLM cost is estimated from token usage.

```text
input cost =
input tokens / 1,000,000 × input price

output cost =
output tokens / 1,000,000 × output price
```

The application records estimated cost per request.

The pricing values used by the local implementation are configurable estimates and should be updated against the selected provider's current pricing before production use.

---

## Project Structure

```text
CYBERSIGNAL/
│
├── app/
│   ├── app.py
│   └── data.py
│
├── data/
│   ├── sample/
│   ├── raw/
│   └── processed/
│
├── docs/
│   ├── day_02_ingestion.md
│   ├── day_03_account_intelligence.md
│   ├── day_04_icp_scoring_evaluation.md
│   ├── day_05_ai_intelligence_tracing_evaluation_outreach.md
│   └── day_06_cybersignal_application.md
│
├── evals/
│   ├── account_relevance.jsonl
│   ├── llm_grounding.jsonl
│   └── prompt_evaluation_results.json
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_signal_exploration.ipynb
│   └── 03_account_evidence.ipynb
│
├── prompts/
│   ├── account_intelligence_v1.txt
│   ├── account_intelligence_v2.txt
│   └── outreach_v1.txt
│
├── scripts/
│   ├── build_app_dataset.py
│   └── evaluate_prompts.py
│
├── skills/
│   └── SKILL.md
│
├── src/
│   ├── ingestion/
│   ├── processing/
│   ├── signals/
│   ├── scoring/
│   └── llm/
│
├── tests/
│
├── .gitignore
└── README.md
```

---

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd cybersignal
```

### 2. Create the environment

Using Conda:

```bash
conda create -n cybersignal python=3.12
conda activate cybersignal
```

### 3. Install dependencies

Install the project's Python dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configure the LLM API key

Create a local `.env` file:

```text
GROQ_API_KEY=<your-key>
```

The `.env` file is ignored by Git and should never be committed.

---

## Run the Application

Start the Streamlit application with:

```bash
python -m streamlit run app/app.py
```

The application provides:

* account discovery
* account search/filtering
* account evidence
* deterministic ICP scoring
* AI account intelligence
* outreach generation

---

## Run Prompt Evaluation

Run the evaluation harness with:

```bash
python scripts/evaluate_prompts.py
```

Results are written to:

```text
evals/prompt_evaluation_results.json
```

---

## Rebuilding the Application Dataset

The application consumes:

```text
data/processed/cybersignal_accounts.parquet
```

The dataset is generated from the processing pipeline rather than being produced dynamically by the Streamlit UI.

The large source datasets are intentionally excluded from Git.

For a production deployment, the recommended approach is to store the source dataset in object storage and run ingestion as a separate data-processing job.

---

## Reproducibility

The project keeps the following components version controlled:

* source code
* prompts
* evaluation labels
* evaluation harness
* evaluation results
* documentation
* reusable AI skill

The following are intentionally excluded:

* raw large datasets
* local secrets
* runtime LLM traces
* local environment files

This separation keeps the repository lightweight while preserving the logic necessary to understand and reproduce the system.

---

## Limitations

CyberSignal currently has several important limitations.

### Dataset limitations

The source dataset represents observed internet infrastructure and does not provide:

* CRM outcomes
* confirmed buying intent
* account revenue
* employee count
* security incidents
* verified vulnerabilities
* sales engagement history

### Evaluation limitations

The relevance evaluation contains only 30 hand-labelled accounts.

It is useful for validating ranking direction and regression detection, but it is not sufficient to establish production-level model performance.

### Classification limitations

Organization classification uses deterministic heuristics and may misclassify ambiguous organization names.

### AI limitations

LLM outputs remain probabilistic. Grounding checks reduce unsupported claims but do not replace human review.

### Production limitations

The current application is a take-home prototype rather than a production-scale sales platform.

---

## Design Principles

CyberSignal follows several principles:

### Evidence first

Every AI conclusion should be traceable to observable evidence.

### Deterministic ranking before generative reasoning

Account prioritization is handled by explicit scoring logic rather than asking an LLM to rank thousands of accounts.

### AI after aggregation

The LLM receives compact organization-level evidence instead of raw infrastructure records.

### Separate facts from interpretation

Observed facts, deterministic scores, and AI-generated reasoning are represented separately.

### Version everything important

Prompts, evaluation cases, evaluation code, and the reusable AI skill are version controlled.

### Optimize for reviewability

The system favors transparent heuristics and structured evidence over opaque ranking logic.

---

## Reusable AI Skill

The reusable account-intelligence workflow is documented in:

```text
skills/SKILL.md
```

It defines the reasoning contract for:

```text
evidence
→ validation
→ signal interpretation
→ ICP context
→ grounded intelligence
→ why-now reasoning
→ outreach
```

---

## Current Status

CyberSignal currently supports the complete prototype workflow:

```text
Large-scale infrastructure data
        ↓
Streaming ingestion
        ↓
Organization aggregation
        ↓
Technology signals
        ↓
ICP scoring
        ↓
Account discovery UI
        ↓
AI account intelligence
        ↓
Evidence-based outreach
        ↓
LLM tracing + evaluation
```

The remaining production-oriented work would include hosted data infrastructure, richer account enrichment, larger labelled evaluation datasets, CRM feedback loops, authentication, and production observability.
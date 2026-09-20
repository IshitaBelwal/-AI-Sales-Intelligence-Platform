# Day 05 — AI Account Intelligence, LLM Tracing, Evaluation & Outreach

## 1. Objective

Day 05 focused on adding the AI-native layer to CyberSignal.

By the end of Day 04, the project had:

- a streaming ingestion pipeline;
- normalized observations;
- normalized organizations;
- organization classification;
- technology classification;
- account-level aggregation;
- cybersecurity exposure signals;
- deterministic ICP features;
- deterministic ICP scoring;
- a 30-account manually labelled evaluation dataset;
- baseline and ICP-aware ranking evaluation.

The goal of Day 05 was to build the layer that converts this structured account intelligence into useful natural-language insights.

The main objectives were:

1. Build a structured account-evidence layer.
2. Create an AI account-intelligence workflow.
3. Introduce versioned prompts.
4. Integrate an LLM through Groq.
5. Add automatic LLM tracing.
6. Track token usage, latency, and estimated cost.
7. Create a prompt evaluation dataset.
8. Compare prompt versions using reproducible metrics.
9. Build an AI-powered outreach generation workflow.
10. Add grounding constraints to prevent unsupported claims.

The core principle for this stage was:

> The LLM should interpret observed evidence, not invent facts about an account.

---

## 2. AI Architecture

The AI layer was designed to sit on top of the deterministic account intelligence pipeline.

The overall architecture became:

```text
Raw Dataset
    |
    v
Streaming Ingestion
    |
    v
Normalized Observations
    |
    v
Organization Normalization
    |
    v
Organization Classification
    |
    v
Technology Classification
    |
    v
Account Aggregation
    |
    v
Cybersecurity Signals
    |
    v
ICP Features
    |
    v
Deterministic ICP Score
    |
    v
Account Evidence
    |
    +--------------------+
    |                    |
    v                    v
AI Account          AI Outreach
Intelligence        Generation
    |                    |
    +---------+----------+
              |
              v
        LLM Tracing
              |
              v
       Evaluation / Cost
```

The deterministic and AI layers are intentionally separated.

The deterministic pipeline is responsible for deciding:

- what was observed;
- how the organization is classified;
- what technologies were observed;
- what account-level signals exist;
- how the account scores against the defined ICP heuristic.

The LLM is responsible for:

- summarizing evidence;
- explaining why the account may be relevant;
- framing a cybersecurity conversation;
- suggesting an outreach angle;
- generating evidence-grounded outreach.

This prevents the LLM from becoming the source of truth for the underlying data.

---

## 3. Account Evidence Layer

### File

```text
src/signals/account_evidence.py
```

Before sending account information to the LLM, a dedicated evidence layer was created.

The purpose of this layer is to convert the account-level dataframe into a compact and structured representation.

Instead of sending raw observations to the LLM, the system provides only the information required for account-level reasoning.

---

### 3.1 Evidence Structure

The account evidence contains:

```text
account
organization_type
icp_fit_score
scale
technology_signals
signal_summary
observation_window
```

The `scale` section contains:

```text
observations
unique_ips
unique_ports
unique_products
countries_observed
```

The `technology_signals` section contains observed technology categories such as:

```text
web
remote_access
email
proxy
network
database
iot
container
security_network
file_transfer
```

Only signals with observed IP counts greater than zero are included.

---

## 4. Example Account Evidence

Oracle was used as one of the first end-to-end examples.

The generated account evidence was:

```python
{
    "account": "oracle",
    "organization_type": "UNKNOWN",
    "icp_fit_score": 85.0,
    "scale": {
        "observations": 1489,
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
        },
        "email": {
            "observed_ips": 7
        },
        "proxy": {
            "observed_ips": 41
        },
        "network": {
            "observed_ips": 3
        },
        "database": {
            "observed_ips": 6
        },
        "container": {
            "observed_ips": 17
        },
        "file_transfer": {
            "observed_ips": 2
        }
    },
    "signal_summary": {
        "exposure_signal_count": 8
    },
    "observation_window": {
        "first_seen": "2026-09-14T09:55:02.515602",
        "last_seen": "2026-09-14T10:18:25.784420"
    }
}
```

This representation gives the LLM enough context to generate an account-level explanation without exposing the full raw dataset.

---

## 5. Why an Evidence Layer Was Needed

Sending raw records directly to an LLM would create several problems.

### 5.1 Context Size

The source dataset contains millions of observations.

Sending raw observations for every account would be inefficient and unnecessary.

### 5.2 Cost

Large prompts increase token usage and therefore increase inference cost.

### 5.3 Noise

Raw observations contain many fields that are not useful for sales reasoning.

### 5.4 Grounding

A structured evidence object makes it easier to determine exactly which facts were available to the model.

### 5.5 Reproducibility

The same account evidence can be used across:

- account intelligence;
- outreach generation;
- prompt evaluation;
- application UI.

Therefore, the account evidence layer acts as the contract between deterministic analytics and generative AI.

---

## 6. AI Account Intelligence Schema

### File

```text
src/llm/schemas.py
```

A structured output schema was created for account intelligence.

The expected fields are:

```text
account
summary
why_relevant
evidence
security_conversation
recommended_angle
confidence
```

Each evidence item contains:

```text
signal
observation
```

Conceptually:

```text
AccountIntelligence
│
├── account
├── summary
├── why_relevant
├── evidence[]
│   ├── signal
│   └── observation
├── security_conversation
├── recommended_angle
└── confidence
```

This provides predictable structure for downstream application components.

---

## 7. Account Intelligence Prompt v1

### File

```text
prompts/account_intelligence_v1.txt
```

The first prompt version was designed to generate account-level intelligence from structured evidence.

The model was instructed to:

- use only the supplied account evidence;
- return valid JSON;
- summarize observed infrastructure;
- explain why the account may be relevant;
- identify a potential cybersecurity conversation;
- provide an outreach angle;
- provide a confidence level.

The prompt also included grounding restrictions.

The model was explicitly instructed not to invent:

- vulnerabilities;
- security incidents;
- breaches;
- buying intent;
- budgets;
- employees;
- company initiatives;
- security products;
- technologies not present in the evidence.

---

## 8. Problem Discovered During Prompt v1 Testing

The first prompt produced technically valid JSON, but some language was too strong relative to the available evidence.

Examples included phrases such as:

```text
broad attack surface
```

and:

```text
commonly targeted by cyber adversaries
```

These statements are problematic because the dataset only shows observed infrastructure.

It does not establish:

- that the infrastructure is vulnerable;
- that an attack is occurring;
- that attackers are targeting the organization;
- that the organization has a security problem;
- that the organization intends to purchase security software.

This demonstrated an important issue with the AI layer:

> A model can produce plausible cybersecurity language that goes beyond what the underlying evidence supports.

This led to the creation of a stricter prompt version.

---

## 9. Account Intelligence Prompt v2

### File

```text
prompts/account_intelligence_v2.txt
```

Prompt v2 strengthened the grounding requirements.

The model was instructed to distinguish between:

```text
observed infrastructure
```

and:

```text
security conclusions
```

The prompt explicitly prohibited converting observations into unsupported claims.

For example:

```text
Observed web services
```

must not automatically become:

```text
vulnerable web services
```

Similarly:

```text
Multiple remote access services observed
```

must not automatically become:

```text
the company has a remote-access security problem
```

---

## 10. Preferred AI Language

The prompt was designed to encourage neutral evidence-based language.

Preferred wording includes:

```text
The dataset shows...
```

```text
The account has observed...
```

```text
The environment includes...
```

```text
The dataset contains observations of...
```

```text
This provides a basis for discussing...
```

```text
This may be relevant to...
```

This is preferable to unsupported statements such as:

```text
The company is vulnerable...
```

```text
The company is at risk...
```

```text
Attackers are targeting the company...
```

```text
The company needs a security product...
```

---

## 11. Groq LLM Integration

### File

```text
src/llm/client.py
```

The LLM integration was implemented using Groq.

The model selected for development was:

```text
openai/gpt-oss-20b
```

OpenAI was initially tested, but the API returned a credit-balance error.

Groq was therefore used for the working implementation.

---

## 12. LLM Client Responsibilities

The LLM client is responsible for:

1. Loading the API key.
2. Creating the Groq client.
3. Sending the system and user messages.
4. Requesting structured JSON output.
5. Parsing the response.
6. Measuring latency.
7. Capturing token usage.
8. Capturing the model name.
9. Capturing the response ID.
10. Sending successful calls to the tracing layer.

The API key is loaded through:

```text
GROQ_API_KEY
```

from the local `.env` file.

The `.env` file is excluded from Git.

---

## 13. LLM Metadata Captured

Every successful request captures:

```text
model
response_id
latency_ms
input_tokens
output_tokens
total_tokens
```

Example:

```text
model: openai/gpt-oss-20b
input_tokens: 1047
output_tokens: 562
total_tokens: 1609
latency_ms: 1184.28
```

This metadata is important for understanding both performance and cost.

---

## 14. LLM Tracing

### File

```text
src/llm/tracing.py
```

A persistent LLM tracing system was implemented.

Trace output is stored in:

```text
data/llm_traces.jsonl
```

JSONL was selected because it is:

- simple;
- append-only;
- easy to inspect;
- easy to process using Python;
- suitable for lightweight experimentation;
- sufficient for the scale of this take-home project.

---

## 15. Trace Schema

Each LLM request generates a record containing:

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

Example:

```json
{
  "timestamp": "2026-09-20T21:24:32.806796+00:00",
  "account": "oracle",
  "prompt_version": "account_intelligence_v2",
  "model": "openai/gpt-oss-20b",
  "response_id": "chatcmpl-eb39e6ee-18c7-408b-b9a0-1049ba5c1ce7",
  "latency_ms": 1184.28,
  "input_tokens": 1047,
  "output_tokens": 562,
  "total_tokens": 1609,
  "estimated_cost_usd": 0.002171,
  "status": "success"
}
```

---

## 16. Automatic Tracing

Tracing was integrated directly into the LLM client.

Therefore, callers do not need to separately write trace records.

The workflow is:

```text
generate_account_intelligence()
            |
            v
       LLM request
            |
            v
      Parse response
            |
            v
     Capture metadata
            |
            v
       Write trace
```

This makes tracing automatic and reduces the risk of missing observability data.

---

## 17. Cost Tracking

### File

```text
src/llm/cost.py
```

A reusable cost calculator was created.

The cost calculation uses:

```text
input tokens
output tokens
input price per million tokens
output price per million tokens
```

The formula is:

```text
Input Cost =
(input_tokens / 1,000,000) × input_price

Output Cost =
(output_tokens / 1,000,000) × output_price

Total Cost =
Input Cost + Output Cost
```

---

## 18. Development Pricing Model

For development and architecture testing, the following placeholder pricing was used:

```text
Input:  $1 / 1M tokens
Output: $2 / 1M tokens
```

For:

```text
1047 input tokens
562 output tokens
```

the calculated illustrative cost is:

```text
$0.002171
```

Approximate scaling:

```text
100 accounts       → $0.2171
1,000 accounts     → $2.171
10,000 accounts    → $21.71
100,000 accounts   → $217.10
```

These values are based on the placeholder pricing model and should not be interpreted as current provider pricing.

The important architectural decision is that pricing is configurable.

---

## 19. Prompt Evaluation Dataset

### File

```text
evals/llm_grounding.jsonl
```

A dedicated evaluation set was created to test whether the AI remains grounded in the supplied evidence.

The evaluation contains five accounts:

```text
Oracle
H4Y Technologies
Madgenius com
V Tal
Peg Tech
```

Each account is evaluated using:

```text
account_intelligence_v1
account_intelligence_v2
```

This produces:

```text
5 accounts × 2 prompt versions = 10 evaluation cases
```

---

## 20. Evaluation Case Structure

Each evaluation case contains:

```text
account
prompt_version
required_signals
forbidden_claims
```

The `required_signals` define facts that should appear in the generated response.

The `forbidden_claims` define language that should not appear.

Examples of forbidden claims:

```text
vulnerability
compromised
under attack
buying intent
needs security product
commonly targeted
attack surface
at risk
security problem
security weakness
```

This provides an automated way to detect grounding failures.

---

## 21. Deterministic LLM Evaluator

### File

```text
src/llm/evaluator.py
```

A deterministic evaluator was implemented.

The evaluator checks the generated output without using another LLM.

This avoids introducing another probabilistic model into the evaluation process.

---

## 22. Evaluation Metrics

The evaluator calculates three primary metrics.

### 22.1 Forbidden Claim Count

The evaluator searches the generated output for explicitly prohibited claims.

Example:

```text
forbidden_claim_count = 0
```

means that none of the configured forbidden phrases were detected.

---

### 22.2 Signal Coverage

Signal coverage measures how many required signals were referenced.

Formula:

```text
Signal Coverage =
Matched Required Signals / Total Required Signals
```

For example:

```text
Required signals = 4
Matched signals = 4

Signal coverage = 1.0
```

---

### 22.3 Grounding Score

The grounding score combines:

```text
signal coverage
```

and:

```text
absence of forbidden claims
```

The simplified formula is:

```text
Grounding Score =
0.5 × Signal Coverage
+
0.5 × No Forbidden Claims
```

where:

```text
No Forbidden Claims = 1
```

if no forbidden claims are detected, otherwise:

```text
No Forbidden Claims = 0
```

---

## 23. Prompt Evaluation Harness

### File

```text
scripts/evaluate_prompts.py
```

A reproducible evaluation script was created.

The workflow is:

```text
Load account data
      |
      v
Load evaluation cases
      |
      v
Build account evidence
      |
      v
Render prompt version
      |
      v
Call LLM
      |
      v
Evaluate output
      |
      v
Write results
      |
      v
Write LLM trace
```

The script supports comparing multiple prompt versions using the same evaluation cases.

---

## 24. Running the Evaluation

The complete evaluation can be executed using:

```bash
PYTHONPATH=. python scripts/evaluate_prompts.py
```

The script evaluates:

```text
account_intelligence_v1
account_intelligence_v2
```

against the same five accounts.

The result is saved to:

```text
evals/prompt_evaluation_results.json
```

LLM calls are automatically added to:

```text
data/llm_traces.jsonl
```

---

## 25. Prompt Evaluation Results

The evaluation produced the following results:

| Metric                  |   v1 |   v2 |
| ----------------------- | ---: | ---: |
| Evaluation cases        |    5 |    5 |
| Forbidden-claim rate    |  60% |  20% |
| Signal coverage         | 100% | 100% |
| Average grounding score | 0.70 | 0.90 |

The results indicate that v2 retained the required signal coverage while reducing unsupported claims in this small evaluation set.

---

## 26. Account-Level Evaluation

The grounding scores by account were:

```text
Oracle
v1: 0.50
v2: 1.00

H4Y Technologies
v1: 0.50
v2: 0.50

Madgenius com
v1: 0.50
v2: 1.00

V Tal
v1: 1.00
v2: 1.00

Peg Tech
v1: 1.00
v2: 1.00
```

The H4Y Technologies case still contained a forbidden phrase in v2.

This was intentionally retained rather than manually modifying the result.

The failure demonstrates that the evaluation harness is actually capable of identifying remaining grounding problems.

---

## 27. Evaluation Limitations

The LLM evaluation should be treated as directional.

The evaluation set contains only:

```text
5 accounts
```

and:

```text
10 total prompt evaluations
```

Therefore, it should not be interpreted as production-level model performance.

The evaluation does not measure:

- actual purchase intent;
- conversion rate;
- sales-qualified opportunities;
- revenue;
- CRM outcomes;
- real-world campaign performance.

The evaluation is specifically designed to measure whether the generated language remains grounded in supplied evidence.

---

## 28. Prompt Versioning

Prompts are stored as separate files.

Current prompt files:

```text
prompts/
├── account_intelligence_v1.txt
├── account_intelligence_v2.txt
└── outreach_v1.txt
```

This allows prompt changes to be tracked independently from Python code.

The prompt version is also included in LLM traces.

For example:

```text
prompt_version:
account_intelligence_v2
```

This makes it possible to later answer:

- Which prompt generated this output?
- Which model generated it?
- How many tokens were used?
- How long did it take?
- What did it cost?

---

## 29. Prompt Rendering Infrastructure

### File

```text
src/llm/prompt_runner.py
```

A reusable prompt-rendering utility was created.

The account-intelligence renderer:

```text
render_account_prompt()
```

injects:

```text
ACCOUNT_EVIDENCE
```

into the selected prompt template.

The outreach renderer:

```text
render_outreach_prompt()
```

injects:

```text
ACCOUNT_EVIDENCE
ACCOUNT_INTELLIGENCE
```

into the outreach prompt.

This allows prompt templates to remain separate from application logic.

---

## 30. AI Outreach Generation

### File

```text
prompts/outreach_v1.txt
```

After account intelligence was implemented, the next AI workflow was outreach generation.

The purpose is to transform:

```text
Account Evidence
+
Account Intelligence
```

into a concise cybersecurity sales message.

The generated structure is:

```text
subject
opening
body
call_to_action
evidence_used
```

---

## 31. Outreach Grounding Rules

The outreach prompt was intentionally conservative.

The model is not allowed to invent:

- contact names;
- job titles;
- company initiatives;
- security incidents;
- vulnerabilities;
- breaches;
- buying intent;
- budget;
- security products;
- technologies not present in the evidence.

The model is also discouraged from assuming that an account has a security problem simply because infrastructure was observed.

---

## 32. Outreach Prompt Testing

The first outreach output introduced unsupported recommendations such as:

```text
MFA
least privilege
```

These controls were not explicitly supported by the account evidence.

The prompt was therefore tightened.

The updated prompt instructs the model not to recommend specific controls unless those controls are supported by the supplied evidence or account intelligence.

---

## 33. Outreach Language Hardening

The first outreach generation also contained language such as:

```text
broad surface
```

and:

```text
attack surface
```

This was considered too strong because the dataset establishes observed infrastructure, not a security assessment.

The prompt was updated to prefer neutral phrases such as:

```text
The dataset shows...
```

```text
The account has observed...
```

```text
The environment includes...
```

```text
The dataset contains observations of...
```

---

## 34. Final Outreach Example

Using Oracle as the example account, the final generated outreach was:

### Subject

```text
Exploring Secure Configuration for Oracle’s Web and Remote Access Services
```

### Opening

```text
Hi [Name],
```

### Body

```text
The dataset shows 235 observed IPs for web services and 232 for
remote access. It could be valuable to discuss how Oracle can
strengthen secure configuration and monitoring across these
environments.
```

### Call to Action

```text
Would you be open to a brief conversation to explore these topics further?
```

### Evidence Used

```text
web → 235 observed IPs
remote_access → 232 observed IPs
```

The output successfully used the observed signals without claiming that Oracle was:

- vulnerable;
- compromised;
- under attack;
- at risk;
- experiencing a security incident.

---

## 35. Final Outreach Trace

The final outreach call also generated normal LLM metadata.

Example:

```text
model:
openai/gpt-oss-20b

input_tokens:
1268

output_tokens:
522

total_tokens:
1790

latency:
approximately 1203 ms
```

The request was automatically added to the LLM trace file.

This means both account intelligence and outreach generation use the same observability layer.

---

## 36. AI Layer Design Principles

Several design principles were established during Day 05.

### 36.1 Evidence Before Generation

The LLM should never receive an unstructured account and be expected to determine everything itself.

Instead:

```text
Raw Data
→ Deterministic Evidence
→ LLM Interpretation
```

---

### 36.2 Deterministic Score Before AI Explanation

The ICP score remains deterministic.

The LLM does not decide:

```text
ICP score = 85
```

Instead, the system calculates the score first and then allows the LLM to explain the available evidence.

---

### 36.3 Observations Are Not Vulnerabilities

An exposed service is an observation.

It is not automatically:

```text
a vulnerability
```

or:

```text
a security incident
```

This distinction is important for avoiding misleading sales messaging.

---

### 36.4 Infrastructure Scale Is Not Buying Intent

Large infrastructure may be relevant to the defined ICP, but it does not prove:

```text
purchase intent
```

Therefore, the system does not use raw observation volume as a direct proxy for buying intent.

---

### 36.5 AI Output Must Remain Traceable

Every AI response should be traceable to:

```text
account
prompt version
model
response ID
latency
token usage
estimated cost
status
```

This is particularly important when AI-generated content is used in a sales workflow.

---

## 37. Files Added or Updated

The following files were created or updated during Day 05:

```text
src/
└── llm/
    ├── schemas.py
    ├── client.py
    ├── tracing.py
    ├── cost.py
    ├── evaluator.py
    └── prompt_runner.py

prompts/
├── account_intelligence_v1.txt
├── account_intelligence_v2.txt
└── outreach_v1.txt

evals/
├── llm_grounding.jsonl
└── prompt_evaluation_results.json

scripts/
└── evaluate_prompts.py

data/
└── llm_traces.jsonl

src/signals/
└── account_evidence.py
```

---

## 38. Validation Performed

The Day 05 implementation was validated through several checks.

### Prompt JSONL validation

```bash
python -c "import json; [json.loads(x) for x in open('evals/llm_grounding.jsonl') if x.strip()]; print('JSONL is valid')"
```

Result:

```text
JSONL is valid
```

### Python syntax validation

```bash
python -m py_compile scripts/evaluate_prompts.py
```

Result:

```text
No syntax errors
```

### Environment validation

The `.env` configuration was tested and the Groq API key was successfully loaded.

### LLM validation

Successful account-intelligence calls were executed.

### Tracing validation

Successful LLM requests generated records in:

```text
data/llm_traces.jsonl
```

### Evaluation validation

The prompt evaluation harness successfully produced:

```text
evals/prompt_evaluation_results.json
```

---

## 39. Current Project Architecture

After Day 05, the project can be viewed as five major layers:

```text
1. DATA INGESTION
   |
   +-- JSONL reader
   +-- Zstandard streaming reader
   +-- normalization
   +-- Parquet output

2. ACCOUNT INTELLIGENCE
   |
   +-- organization normalization
   +-- organization classification
   +-- technology classification
   +-- account aggregation
   +-- cybersecurity signals

3. ICP / RANKING
   |
   +-- ICP features
   +-- deterministic ICP score
   +-- account relevance evaluation

4. AI INTELLIGENCE
   |
   +-- account evidence
   +-- account intelligence
   +-- AI outreach
   +-- prompt versioning

5. AI OBSERVABILITY
   |
   +-- LLM tracing
   +-- token tracking
   +-- latency tracking
   +-- cost estimation
   +-- prompt evaluation
```

---

## 40. Day 05 Outcome

At the end of Day 05, CyberSignal had progressed from a deterministic account-ranking pipeline into an AI-assisted sales-intelligence system.

The system can now:

1. Identify and aggregate accounts.
2. Calculate deterministic account signals.
3. Calculate an ICP-fit score.
4. Convert account data into structured evidence.
5. Generate account intelligence using an LLM.
6. Generate evidence-grounded cybersecurity outreach.
7. Track every LLM request.
8. Track token consumption and latency.
9. Estimate LLM cost.
10. Compare prompt versions automatically.
11. Detect unsupported claims in AI output.

The key architectural separation is:

```text
DATA
  ↓
EVIDENCE
  ↓
DETERMINISTIC SCORING
  ↓
AI INTERPRETATION
  ↓
AI OUTREACH
```

The AI layer therefore augments the deterministic sales-intelligence pipeline rather than replacing it.

---

## 41. Next Step

The next stage is to turn the backend and AI capabilities into the actual CyberSignal product experience.

The application should provide a workflow such as:

```text
CyberSignal
    |
    +-- Discover Accounts
    |
    +-- Search / Filter Accounts
    |
    +-- Account Intelligence
    |      |
    |      +-- Account overview
    |      +-- ICP score
    |      +-- Technology signals
    |      +-- Evidence
    |      +-- AI analysis
    |
    +-- Why Now?
    |
    +-- Generate Outreach
```

The next implementation focus is therefore the application layer, where the deterministic account intelligence and AI capabilities become usable by a sales user.
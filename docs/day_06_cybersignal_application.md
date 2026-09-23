# Day 06 — CyberSignal Application: Account Discovery, Intelligence & AI Outreach

## 1. Objective

Day 06 focused on converting the data and AI pipeline developed during the previous days into a usable AI-native sales intelligence application.

By the end of Day 05, CyberSignal had:

- a streaming ingestion pipeline;
- normalized observations;
- normalized organizations;
- organization classification;
- technology classification;
- account-level aggregation;
- cybersecurity technology signals;
- deterministic ICP features;
- deterministic ICP scoring;
- a manually labelled evaluation dataset;
- baseline and ICP-aware evaluation;
- structured account evidence;
- versioned AI prompts;
- AI account intelligence;
- prompt evaluation;
- LLM tracing;
- token and cost tracking;
- AI outreach generation.

The main objective of Day 06 was to expose these capabilities through an actual product workflow.

The application was designed around the following sales workflow:

```text
Discover Accounts
        ↓
Search / Filter
        ↓
Select Account
        ↓
Account Intelligence
        ↓
Account Evidence
        ↓
AI Account Analysis
        ↓
Generate Outreach
```

The goal was not to build a generic analytics dashboard.

The goal was to build an AI-native cybersecurity sales intelligence application that allows a sales user to discover accounts, understand the observed technology environment, generate evidence-grounded intelligence, and create targeted outreach.

---

## 2. Product Direction

The application was named **CyberSignal** as the working product name.

The product concept is:

> An AI-native cybersecurity sales intelligence platform that helps sales teams discover organizations, understand observed technology environments, identify relevant cybersecurity signals, and generate evidence-grounded account intelligence and outreach.

Streamlit was used as the application framework, but Streamlit is treated as the implementation technology rather than the product itself.

The product workflow is:

```text
                     CyberSignal
                          |
              +-----------+-----------+
              |                       |
        Discover Accounts       Search Account
              |                       |
              +-----------+-----------+
                          |
                          v
                Account Intelligence
                          |
             +------------+------------+
             |                         |
             v                         v
       Account Evidence           ICP Score
             |
             v
       AI Account Analysis
             |
             v
        Why This Account?
             |
             v
       Generate Outreach
```

---

## 3. Application Architecture

The application sits on top of the deterministic data and AI layers created previously.

The architecture is:

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
ICP Score
    |
    v
Application-Ready Account Dataset
    |
    v
CyberSignal Application
    |
    +-----------------------+
    |                       |
    v                       v
Account Discovery     Account Intelligence
                            |
                            v
                     Structured Evidence
                            |
                            v
                       LLM Analysis
                            |
                            v
                      AI Outreach
                            |
                            v
                     LLM Tracing
```

This separation keeps data processing, scoring, AI logic, and UI responsibilities independent.

---

## 4. Application-Ready Dataset

Before building the UI, a dedicated application-ready dataset was created.

The source dataset was:

```text
data/processed/account_features.parquet
```

This dataset contained:

- normalized organizations;
- original organization names;
- organization types;
- observation counts;
- unique IP counts;
- unique ports;
- unique products;
- countries observed;
- technology signal counts;
- observation windows.

However, the application also needed derived signals and ICP information.

A new dataset was therefore generated:

```text
data/processed/cybersignal_accounts.parquet
```

This became the primary data source for the application.

---

## 5. Application Dataset Generation

A new script was created:

```text
scripts/build_app_dataset.py
```

The script performs the following steps:

```text
account_features.parquet
        |
        v
build_account_signals()
        |
        v
add_icp_features()
        |
        v
add_icp_score()
        |
        v
Deterministic ranking
        |
        v
cybersignal_accounts.parquet
```

The existing signal and scoring functions were reused rather than duplicated.

The script imports:

```python
from src.signals.account_signals import build_account_signals
from src.scoring.icp import add_icp_features
from src.scoring.icp_score import add_icp_score
```

This ensures that the application uses the same scoring logic that was evaluated previously.

---

## 6. Application Dataset Results

The generated application dataset contains:

```text
33,022 accounts
40 columns
```

The resulting file is:

```text
data/processed/cybersignal_accounts.parquet
```

The dataset is approximately:

```text
2.2 MB
```

This is small enough for the Streamlit application to load efficiently.

The application therefore does not need to reprocess the original 2M-record dataset every time the application starts.

Instead:

```text
2M observations
      ↓
Preprocessed offline
      ↓
cybersignal_accounts.parquet
      ↓
Streamlit application
```

This keeps application startup simple and avoids unnecessary repeated processing.

---

## 7. Application Dataset Schema

The application-ready dataset contains account identity information:

```text
normalized_organization
organization
organization_type
```

Infrastructure scale:

```text
observation_count
unique_ips
unique_ports
unique_products
countries_observed
```

Technology signals:

```text
web_ip_count
remote_access_ip_count
email_ip_count
proxy_ip_count
network_ip_count
database_ip_count
iot_ip_count
container_ip_count
security_network_ip_count
file_transfer_ip_count
```

Derived signals:

```text
has_web_exposure
has_remote_access_exposure
has_email_exposure
has_proxy_exposure
has_network_exposure
has_database_exposure
has_iot_exposure
has_container_exposure
has_security_network_exposure
has_file_transfer_exposure

exposure_signal_count
technology_diversity
infrastructure_scale
```

ICP features:

```text
is_infrastructure_provider
is_security_provider
small_infrastructure
medium_infrastructure
large_infrastructure
has_multiple_technology_surfaces
icp_fit_score
```

Observation window:

```text
first_seen
last_seen
```

This provides the application with a complete account-level representation without requiring direct access to the raw dataset.

---

## 8. Application Structure

The application was initially structured as:

```text
app/
├── app.py
└── data.py
```

Responsibilities were intentionally separated.

### `app/data.py`

Responsible for loading the application dataset.

The file defines:

```python
load_accounts()
```

which loads:

```text
data/processed/cybersignal_accounts.parquet
```

The application uses the project root to construct the dataset path so that the application can be launched from the project directory without hard-coded absolute paths.

---

## 9. Streamlit Application

The main application file is:

```text
app/app.py
```

The application uses:

```python
st.set_page_config(
    page_title="CyberSignal",
    page_icon="🛡️",
    layout="wide",
)
```

The application is launched using:

```bash
python -m streamlit run app/app.py
```

Using:

```bash
python -m streamlit
```

ensures that Streamlit runs using the currently active `cybersignal` Python environment.

This avoided dependency mismatches between the system Streamlit executable and the project Python environment.

---

## 10. Data Loading

The application uses Streamlit's caching mechanism:

```python
@st.cache_data
def get_accounts():
    return load_accounts()
```

This prevents the Parquet file from being repeatedly loaded during every Streamlit rerun.

The resulting architecture is:

```text
Streamlit
    |
    v
get_accounts()
    |
    v
load_accounts()
    |
    v
cybersignal_accounts.parquet
```

---

## 11. Application Summary Metrics

The initial application provides three high-level metrics:

```text
Accounts
Technology Signals
Average ICP Score
```

For example:

```text
Accounts
33,022
```

The metrics provide quick context about the size of the account universe and the overall dataset.

These metrics are intended as product context rather than as predictive performance metrics.

---

## 12. Account Discovery

The first major product capability implemented was Account Discovery.

The user can search and filter the account universe.

The application provides:

```text
Search accounts
Organization type
Minimum ICP score
```

The search field allows a user to search by normalized organization name.

Example:

```text
oracle
```

returns:

```text
Oracle
```

---

## 13. Organization Type Filtering

The application dynamically derives available organization types from the dataset.

Current organization types include:

```text
UNKNOWN
ISP
HOSTING_PROVIDER
CLOUD_PROVIDER
SECURITY_PROVIDER
CDN_SECURITY
```

Users can select a specific type or:

```text
All
```

to search across the complete account universe.

---

## 14. ICP Score Filtering

The application includes a minimum ICP score slider.

For example:

```text
Minimum ICP Score
0 → 100
```

Selecting:

```text
80
```

filters the account universe to accounts with:

```text
icp_fit_score >= 80
```

This provides a simple way for sales users to narrow the account universe.

The application does not claim that the score represents purchase probability.

The score remains the deterministic ICP-fit heuristic developed and evaluated earlier.

---

## 15. Account Ranking

Filtered accounts are sorted using the same deterministic ranking logic used during evaluation.

The ranking order is:

```text
1. icp_fit_score
2. exposure_signal_count
3. unique_products
4. unique_ips
```

This provides deterministic tie-breaking when multiple accounts have the same ICP score.

The same ranking logic is therefore used across:

```text
Evaluation
      ↓
Application
```

This prevents the UI from silently introducing a different ranking methodology.

---

## 16. Account Selection

After filtering, the user can select an account from the matching results.

The workflow is:

```text
Search / Filter
      ↓
Matching Accounts
      ↓
Select Account
      ↓
Account Intelligence
```

For example:

```text
oracle
```

can be selected to open the Oracle account profile.

---

## 17. Account Intelligence Page

After selecting an account, the application displays an account-level intelligence view.

The account page contains:

```text
Account Overview
Organization Information
Observed Technology Signals
Observation Window
AI Account Intelligence
AI Outreach
```

This transforms the application from a simple account table into an investigation workflow.

---

## 18. Account Overview

The account overview displays:

```text
ICP Fit Score
Unique IPs
Unique Products
Countries
```

For Oracle, the observed values include:

```text
ICP Fit Score: 85
Unique IPs: 1,265
Unique Products: 46
Countries: 23
```

Additional information includes:

```text
Organization Type
Observed Ports
Observations
```

These values come directly from the deterministic account dataset.

---

## 19. Observed Technology Signals

The account profile displays the technology categories observed for the selected account.

Current signal categories include:

```text
Web
Remote Access
Email
Proxy
Network
Database
IoT
Container
Security Network
File Transfer
```

Only signals with a non-zero observed IP count are displayed.

For Oracle, the observed signals include:

```text
Web
235 observed IPs

Remote Access
232 observed IPs

Email
7 observed IPs

Proxy
41 observed IPs

Network
3 observed IPs

Database
6 observed IPs

Container
17 observed IPs

File Transfer
2 observed IPs
```

These are observations from the dataset.

They are not automatically interpreted as vulnerabilities, incidents, or confirmed security weaknesses.

---

## 20. Observation Window

The application also displays:

```text
First Seen
Last Seen
```

This provides temporal context for the observed account data.

For example:

```text
First Seen:
2026-09-14...

Last Seen:
2026-09-14...
```

The observation window helps users understand when the underlying infrastructure observations occurred.

---

## 21. Account Evidence Layer

The application reuses the structured account evidence layer developed during Day 05.

The evidence is generated using:

```python
build_account_evidence(selected_account)
```

The resulting structure includes:

```text
account
organization_type
icp_fit_score

scale
    observations
    unique_ips
    unique_ports
    unique_products
    countries_observed

technology_signals

signal_summary

observation_window
```

This evidence object becomes the controlled input to the AI layer.

---

## 22. AI Evidence Transparency

The application exposes:

```text
View account evidence sent to AI
```

through an expandable section.

This allows users and reviewers to inspect the structured evidence before it is sent to the LLM.

This design improves transparency:

```text
Account Data
     ↓
Structured Evidence
     ↓
User can inspect evidence
     ↓
LLM
```

The AI therefore does not receive the entire raw dataset.

It receives a compact account-level evidence representation.

---

## 23. AI Account Intelligence

The application connects the account profile to the existing AI account-intelligence pipeline.

The workflow is:

```text
Selected Account
      ↓
build_account_evidence()
      ↓
render_account_prompt()
      ↓
account_intelligence_v2
      ↓
Groq
      ↓
Structured JSON
      ↓
CyberSignal UI
```

The prompt version used is:

```text
account_intelligence_v2
```

This version contains stricter grounding rules than the original prompt.

---

## 24. AI Account Intelligence Output

The application displays the following AI-generated sections:

```text
Summary

Why This Account May Be Relevant

Evidence

Security Conversation

Recommended Angle

Confidence
```

The output is generated from the structured evidence rather than from unsupported assumptions.

The AI is instructed to avoid claims such as:

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

unless such claims are directly supported by the evidence.

---

## 25. LLM Metadata in the Application

The application also exposes LLM metadata in an expandable section.

Metadata includes:

```text
model
response_id
latency_ms
input_tokens
output_tokens
total_tokens
```

This provides visibility into the actual AI operation behind the generated intelligence.

---

## 26. AI Outreach Generation

After generating account intelligence, the application provides:

```text
Generate Outreach
```

The outreach workflow is:

```text
Account Evidence
       +
AI Account Intelligence
       ↓
render_outreach_prompt()
       ↓
outreach_v1
       ↓
Groq
       ↓
Structured Outreach
```

The application does not generate outreach independently of the account intelligence workflow.

This creates a logical sequence:

```text
Account
   ↓
Evidence
   ↓
AI Intelligence
   ↓
Outreach
```

---

## 27. Outreach Output

The generated outreach contains:

```text
Subject
Opening
Body
Call to Action
Evidence Used
```

For example, the message may reference:

```text
235 observed web IPs
232 observed remote access IPs
```

when those observations are actually present in the account evidence.

The outreach prompt was explicitly hardened against unsupported claims.

The prompt prefers neutral language such as:

```text
"The dataset shows..."

"The account has observed..."

"The environment includes..."

"The dataset contains observations of..."
```

rather than assuming that an organization has a security deficiency.

---

## 28. Outreach Grounding

The outreach generation process is designed to avoid automatically inventing security controls or product requirements.

For example, the system should not automatically claim that an organization needs:

```text
MFA
least privilege
specific security products
specific security controls
```

unless the evidence or context supports such a statement.

Similarly, it should avoid unsupported statements such as:

```text
The company is vulnerable.
The company is under attack.
The company has a security problem.
The company needs our product.
```

This keeps the generated outreach evidence-grounded.

---

## 29. LLM Tracing from the Application

The application uses the same tracing infrastructure developed during Day 05.

Every successful AI call records:

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

The trace file is:

```text
data/llm_traces.jsonl
```

The application therefore provides observability for both:

```text
account_intelligence_v2
```

and:

```text
outreach_v1
```

---

## 30. Verified Account Intelligence Trace

A successful Oracle account-intelligence call produced a trace with:

```text
account: oracle
prompt_version: account_intelligence_v2
model: openai/gpt-oss-20b
status: success
```

The call also recorded:

```text
input tokens
output tokens
total tokens
latency
estimated cost
```

This confirmed that the UI was correctly connected to the existing AI and tracing infrastructure.

---

## 31. Verified Outreach Trace

A successful Oracle outreach call produced:

```text
account: oracle
prompt_version: outreach_v1
model: openai/gpt-oss-20b
status: success
```

The recorded usage was:

```text
Input tokens: 1,242
Output tokens: 701
Total tokens: 1,943
Latency: 1,345.26 ms
Estimated cost: $0.002644
```

This demonstrates that AI usage is observable and measurable at the individual request level.

The cost shown here uses the project's configured pricing model and is an estimate rather than a statement of current provider pricing.

---

## 32. Python Environment and Streamlit

During application integration, an environment mismatch was encountered.

Running:

```bash
streamlit run app/app.py
```

resulted in the application using an environment where the `groq` package was unavailable.

The project was therefore standardized on:

```bash
python -m streamlit run app/app.py
```

This ensures that Streamlit is launched through the currently active Python interpreter.

The `cybersignal` environment contains the project's required dependencies, including:

```text
pandas
polars
duckdb
pyarrow
zstandard
streamlit
groq
```

---

## 33. Python Import Path

The Streamlit application initially could not import the project's `src` package because the application file is located under:

```text
app/app.py
```

while the source modules are located under:

```text
src/
```

The application therefore explicitly adds the project root to the Python path:

```python
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```

This allows imports such as:

```python
from src.signals.account_evidence import build_account_evidence
from src.llm.prompt_runner import render_account_prompt
from src.llm.client import generate_account_intelligence
```

to work consistently when the application is launched through Streamlit.

---

## 34. Streamlit Button Key Handling

During the integration of AI account intelligence and outreach, Streamlit reported a duplicate widget ID.

The issue was caused by two copies of the AI Account Intelligence section existing in `app/app.py`.

The duplicate section was removed.

Explicit Streamlit keys were also added:

```python
key="generate_ai_analysis"
```

and:

```python
key="generate_outreach"
```

This gives each interactive button a stable unique identity.

The final application contains one AI analysis button and one outreach button.

---

## 35. Application Session State

The application uses Streamlit session state to retain generated AI results during reruns.

Account intelligence is stored using:

```python
st.session_state["account_intelligence"]
```

and the associated account is stored separately.

Similarly, outreach results are stored using:

```python
st.session_state["outreach_result"]
```

and:

```python
st.session_state["outreach_account"]
```

This prevents the generated results from disappearing every time Streamlit reruns the application.

---

## 36. Current End-to-End Product Flow

At the end of Day 06, the application supports:

```text
                     CyberSignal
                          |
                          v
                 Account Discovery
                          |
                 Search / Filtering
                          |
                          v
                  Select Account
                          |
                          v
                Account Intelligence
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
       ICP Score      Scale Metrics   Tech Signals
          |               |               |
          +---------------+---------------+
                          |
                          v
                 Structured Evidence
                          |
                          v
              Generate AI Analysis
                          |
                          v
              Account Intelligence
                          |
                          v
               Generate Outreach
                          |
                          v
                 Sales Outreach
                          |
                          v
                    LLM Trace
```

---

## 37. Current Application Components

The current application consists of:

```text
app/
├── app.py
└── data.py
```

Application data:

```text
data/processed/cybersignal_accounts.parquet
```

AI infrastructure reused by the application:

```text
src/
├── signals/
│   └── account_evidence.py
│
└── llm/
    ├── client.py
    ├── cost.py
    ├── evaluator.py
    ├── prompt_runner.py
    ├── schemas.py
    └── tracing.py
```

Prompt files:

```text
prompts/
├── account_intelligence_v1.txt
├── account_intelligence_v2.txt
└── outreach_v1.txt
```

LLM traces:

```text
data/llm_traces.jsonl
```

---

## 38. Design Decisions

### 38.1 Precompute account intelligence

The application does not process the 2M raw observations at runtime.

Instead, the heavy processing happens offline.

```text
Raw Data
   ↓
Processing
   ↓
Application Dataset
   ↓
Streamlit
```

This keeps the application responsive.

---

### 38.2 Reuse deterministic scoring

The UI does not implement its own scoring logic.

The same deterministic ICP score developed during the evaluation stage is reused.

This avoids inconsistent scoring between the backend and the application.

---

### 38.3 Evidence before AI

The LLM does not directly consume arbitrary raw records.

Instead:

```text
Raw Observations
      ↓
Account Aggregation
      ↓
Signals
      ↓
Account Evidence
      ↓
LLM
```

This reduces prompt size and provides a clear grounding boundary.

---

### 38.4 AI as interpretation, not source of truth

The deterministic pipeline remains the source of observed facts.

The LLM is responsible for:

```text
summarization
interpretation
sales-context generation
outreach generation
```

The LLM is not treated as a source of independently verified facts.

---

### 38.5 Trace every AI request

Every AI request records:

```text
model
prompt version
tokens
latency
cost
status
```

This provides a foundation for evaluating AI quality and operating cost.

---

## 39. Current Product Status

At the end of Day 06:

### Data layer

```text
COMPLETE
```

### Account intelligence

```text
COMPLETE
```

### ICP scoring

```text
COMPLETE
```

### Evaluation

```text
COMPLETE
```

### LLM tracing

```text
COMPLETE
```

### AI account intelligence

```text
COMPLETE
```

### AI outreach

```text
COMPLETE
```

### Application

```text
WORKING
```

### Account discovery

```text
WORKING
```

### Search and filtering

```text
WORKING
```

### Account profile

```text
WORKING
```

### AI analysis from UI

```text
WORKING
```

### Outreach from UI

```text
WORKING
```

---

## 40. Day 06 Milestone

Day 06 represents the transition from a backend data/AI pipeline into a usable product.

The project can now demonstrate the complete workflow:

```text
Large Dataset
      ↓
Account Intelligence
      ↓
ICP Ranking
      ↓
Account Discovery
      ↓
Account Evidence
      ↓
AI Analysis
      ↓
AI Outreach
      ↓
LLM Observability
```

The core product loop is therefore operational.

The next stage should focus on making the application production-quality for the take-home submission rather than adding unnecessary features.

Priority areas for the next stage include:

1. UI/UX refinement.
2. Reusable `skills/SKILL.md`.
3. One-command evaluation workflow.
4. Final README.
5. Architecture and planning documentation.
6. Cost and AI usage documentation.
7. Final end-to-end testing.
8. GitHub cleanup and reproducibility.
9. Final take-home reflection.
10. Optional demo/Loom recording.

---

## 41. Key Takeaway

The most important architectural outcome of Day 06 is that CyberSignal is no longer only a data-processing project.

It now provides an end-to-end sales intelligence workflow:

```text
Discover
   ↓
Investigate
   ↓
Understand
   ↓
Ask AI
   ↓
Generate Outreach
```

The deterministic pipeline provides the evidence.

The AI layer interprets the evidence.

The application connects both into a single sales workflow.

This separation allows CyberSignal to remain explainable while still providing useful AI-native functionality.
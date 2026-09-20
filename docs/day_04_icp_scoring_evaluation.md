# Day 04 — ICP Scoring and Evaluation

## Objective

Build a transparent, deterministic account-prioritization layer that ranks
organizations according to their potential relevance to a cybersecurity
software sales workflow.

The key design question was:

    How can infrastructure observations be converted into a useful
    sales-prioritization signal without treating infrastructure scale
    or observed services as direct evidence of buying intent?

The solution was to separate:

1. Observable infrastructure signals
2. Organization/ICP context
3. Deterministic scoring
4. Hand-labelled evaluation

---

## 1. Why a Separate ICP Layer?

The initial account score was primarily driven by infrastructure characteristics
such as:

- unique IPs
- unique ports
- unique products
- technology exposure
- infrastructure scale

This produced a useful infrastructure ranking, but it had an important
limitation.

Large infrastructure providers naturally generate large numbers of
observations.

For example, telecom companies, cloud providers and other infrastructure
organizations can have very large observable footprints.

Therefore:

    infrastructure scale != sales relevance

The initial ranking demonstrated this limitation.

---

# 2. Initial Baseline Score

The original deterministic score consisted of four components:

- exposure score
- technology score
- infrastructure score
- context score

The overall score was capped at 100.

### Exposure score

The exposure score rewarded the presence of different observable
technology/security surfaces.

Examples included:

- web
- remote access
- email
- proxy
- network
- database
- IoT
- containers
- security network
- file transfer

The score was intentionally based on observable signals rather than claiming
that any observed service represented a vulnerability.

### Technology score

Technology breadth was represented by the number of relevant technology
categories observed for the account.

### Infrastructure score

Infrastructure characteristics included:

- unique IPs
- unique ports
- unique products

Log-scaled components were used to prevent very large raw values from
completely dominating the score.

### Context score

Organization type was also incorporated.

The initial baseline nevertheless remained strongly influenced by
infrastructure scale.

---

# 3. Baseline Evaluation

A hand-labelled evaluation set was created to measure whether the ranking
was useful for sales-account prioritization.

The final evaluation set contains:

    30 unique accounts

with:

    5 positive accounts
    25 negative accounts

The labels represent proxy relevance judgements based on observable dataset
evidence.

They do NOT represent:

- confirmed buying intent
- CRM opportunities
- historical purchases
- active security incidents
- confirmed vulnerabilities

This limitation is explicitly documented so that the evaluation is not
misinterpreted as a prediction of actual customer behavior.

---

# 4. Evaluation Metric

The primary ranking metric selected was:

    Precision@10

with Recall@10 and F1@10 reported alongside it.

For the top 10 accounts:

    Precision@10 =
    relevant accounts in top 10 / 10

Recall measures how many of the labelled relevant accounts were retrieved
within the top 10.

F1 combines precision and recall into a single summary metric.

---

# 5. Baseline Results

The original scoring system produced:

| Metric | Baseline |
|---|---:|
| Precision@10 | 0.200 |
| Recall@10 | 0.400 |
| F1@10 | 0.267 |
| True positives | 2 |
| False positives | 8 |
| False negatives | 3 |

This means that only 2 of the 5 labelled positive accounts appeared in the
top 10.

The baseline therefore demonstrated the central problem:

    High infrastructure footprint does not necessarily mean high
    sales relevance.

---

# 6. ICP Feature Layer

A separate ICP feature layer was introduced in:

    src/scoring/icp.py

The layer derives transparent contextual features such as:

- is_infrastructure_provider
- is_security_provider
- small_infrastructure
- medium_infrastructure
- large_infrastructure
- has_multiple_technology_surfaces

The feature layer deliberately remains separate from the scoring function.

This allows the features to be reused by:

- scoring
- account explanations
- evaluation
- application UI
- future modelling

---

# 7. ICP-Aware Scoring

The ICP scoring implementation is located in:

    src/scoring/icp_score.py

The score is explicitly described as a:

    deterministic ICP-fit heuristic

rather than a learned probability.

The initial score starts from a neutral baseline and adjusts based on
organization context, technology breadth, observable security surfaces and
infrastructure size.

---

## Organization context

Infrastructure providers receive a penalty because their large infrastructure
footprints can otherwise dominate the ranking.

Affected categories include:

- CLOUD_PROVIDER
- CDN_SECURITY
- ISP
- HOSTING_PROVIDER

Security providers are also treated as a separate segment.

UNKNOWN organizations remain eligible because classification confidence is
insufficient to exclude them.

---

## Technology surface breadth

Accounts receive additional score for multiple observable technology/security
surfaces.

The final version uses a gradual contribution:

    exposure_signal_count × 3

capped at 15 points.

This avoids a hard jump between accounts with 2 and 3 technology surfaces.

---

## Technology diversity

Technology diversity contributes gradually:

    unique_products × 1.5

capped at 15 points.

This allows accounts with broader technology footprints to rank higher without
letting raw product count dominate the entire score.

---

## Infrastructure scale

Infrastructure size is treated as supporting context rather than the primary
signal.

Very large footprints are deliberately prevented from dominating the score.

The final heuristic includes:

- >10,000 unique IPs → penalty
- >500 unique IPs → modest positive contribution
- >25 unique IPs → smaller positive contribution

This reflects the principle that infrastructure scale should provide context,
not automatically imply ICP fit.

---

# 8. Deterministic Ranking

To make evaluation reproducible, ranking uses deterministic tie-breaking.

The ranking order is:

1. ICP-fit score
2. exposure signal count
3. unique product count
4. unique IP count

This prevents accounts with identical scores from being ordered arbitrarily
based on dataframe order.

---

# 9. ICP-Aware Evaluation Results

The ICP-aware score was evaluated against the same 30-account evaluation set.

Results:

| Metric | Baseline | ICP-aware |
|---|---:|---:|
| Precision@10 | 0.200 | **0.500** |
| Recall@10 | 0.400 | **1.000** |
| F1@10 | 0.267 | **0.667** |
| True positives | 2 | **5** |
| False positives | 8 | **5** |
| False negatives | 3 | **0** |

The ICP-aware approach therefore improved:

    Precision@10:
    0.20 → 0.50

    Recall@10:
    0.40 → 1.00

    F1@10:
    0.267 → 0.667

---

# 10. Ranking Behavior

The ICP-aware ranking moved several infrastructure-heavy organizations
downward while retaining accounts with broader technology exposure and
relevant contextual signals.

Examples from the evaluation set include:

| Account | Label | ICP Score | Organization Type |
|---|---:|---:|---|
| Oracle | 1 | 85.0 | UNKNOWN |
| Peg Tech | 1 | 85.0 | UNKNOWN |
| Huawei Public Cloud | 0 | 85.0 | UNKNOWN |
| V Tal | 1 | 83.0 | UNKNOWN |
| Scaleway | 0 | 83.0 | UNKNOWN |
| 139 162 0 0/16 | 0 | 83.0 | UNKNOWN |
| H4Y Technologies | 1 | 77.0 | UNKNOWN |
| Madgenius.com | 1 | 72.5 | UNKNOWN |

This illustrates an important limitation as well:

Organizations with similar observable infrastructure characteristics can still
receive similar scores even when the hand-labelled relevance differs.

This is expected because the current score uses only the information
available in the dataset and does not contain CRM outcomes, firmographic data,
intent data or historical sales interactions.

---

# 11. Evaluation Limitations

The evaluation is intentionally small and manually labelled.

Current limitations include:

### Small sample size

The evaluation contains 30 accounts and only 5 positive examples.

Therefore, the measured metrics should be treated as directional rather than
production-level performance estimates.

### Proxy labels

The labels represent human judgement about potential sales relevance based on
the available evidence.

They do not represent actual buying intent.

### Limited dataset context

The dataset primarily provides infrastructure observations.

It does not directly provide:

- company revenue
- employee count
- security budget
- CRM history
- current security tooling
- active buying cycle
- contact information
- confirmed organizational ownership

Therefore the score should be interpreted as:

    account prioritization

rather than:

    purchase probability

---

# 12. Reproducibility

Evaluation results are stored in:

    evals/results.json

The labelled evaluation set is stored in:

    evals/account_relevance.jsonl

The scoring implementation is stored in:

    src/scoring/icp.py
    src/scoring/icp_score.py

This separation allows the scoring logic to be changed and evaluated against
the same labelled benchmark.

---

# 13. Key Engineering Learning

The most important finding from Day 4 was:

    Raw infrastructure scale is not sufficient for sales prioritization.

A better approach combines:

    Organization context
          +
    Technology breadth
          +
    Observable security surfaces
          +
    Infrastructure scale

while explicitly avoiding the assumption that any individual exposed service
is a vulnerability or evidence of buying intent.

---

# 14. Current Architecture

After Day 4, the pipeline is:

    Raw observations
          |
          v
    Normalization
          |
          v
    Parquet observations
          |
          v
    Organization aggregation
          |
          v
    Organization classification
          |
          v
    Technology classification
          |
          v
    Account signals
          |
          v
    ICP features
          |
          v
    Deterministic ICP score
          |
          v
    Hand-labelled evaluation
          |
          v
    Ranked accounts

The next stage is to add an AI-native intelligence layer on top of this
deterministic foundation.

The LLM will be used for evidence-grounded account interpretation and
outreach generation, rather than for replacing the deterministic account
score.
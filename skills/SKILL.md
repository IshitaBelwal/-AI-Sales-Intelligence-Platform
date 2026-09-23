# CyberSignal Account Intelligence Skill

## 1. Purpose

CyberSignal is an AI-native sales intelligence workflow for identifying and researching potentially relevant business accounts from observed internet infrastructure data.

This skill converts structured account evidence into grounded sales intelligence while separating:

- observed facts
- deterministic account scoring
- contextual interpretation
- AI-generated reasoning
- outreach suggestions

The skill does **not** infer security incidents, vulnerabilities, compromise, buying intent, or confirmed product need unless such evidence is explicitly provided by an upstream source.

---

## 2. Core Workflow

```text
Account Evidence
      ↓
Evidence Validation
      ↓
Technology Signal Interpretation
      ↓
ICP / Account Context
      ↓
Deterministic Account Scoring
      ↓
Grounded AI Account Intelligence
      ↓
Why-Now / Conversation Angle
      ↓
Personalized Outreach
````

The workflow should preserve traceability between every AI-generated conclusion and the underlying account evidence.

---

## 3. Inputs

The account intelligence skill expects structured account evidence containing, where available:

### Account identity

* normalized organization name
* organization type

### Infrastructure scale

* observation count
* unique IP count
* unique port count
* unique product count
* countries observed

### Technology signals

Examples include:

* web
* remote access
* email
* proxy
* network
* database
* IoT
* container
* security network
* file transfer

### Observation window

* first seen
* last seen

### Deterministic context

* ICP fit score
* exposure signal count
* infrastructure scale
* technology diversity

---

## 4. Evidence Validation

Before generating AI analysis:

1. Use only information present in the supplied account evidence.
2. Treat observation counts as measurements, not as indicators of purchase intent.
3. Distinguish organization-level observations from individual hosts or IP addresses.
4. Do not infer ownership of infrastructure beyond the organization identity supplied by the dataset.
5. Do not infer business size, revenue, industry, security maturity, or organizational structure unless explicitly provided.
6. Do not convert infrastructure observations into claims about incidents or vulnerabilities.

Example:

```text
Observed:
Oracle has 1,265 unique IPs and multiple observed technology categories.

Allowed interpretation:
"The dataset shows infrastructure across multiple technology categories."

Unsupported interpretation:
"Oracle has a broad attack surface."
```

---

## 5. Technology Signal Interpretation

Technology signals should be described as observable infrastructure characteristics.

Examples:

| Signal        | Grounded interpretation                    |
| ------------- | ------------------------------------------ |
| Web           | Web-serving infrastructure was observed    |
| Remote access | Remote-access technology was observed      |
| Email         | Email-related infrastructure was observed  |
| Proxy         | Proxy technology was observed              |
| Database      | Database technology was observed           |
| Network       | Network infrastructure was observed        |
| IoT           | IoT-related technology was observed        |
| Container     | Container/platform technology was observed |
| File transfer | File-transfer technology was observed      |

Signals can be combined to describe technology diversity.

For example:

> "The dataset shows web, remote-access, email, and database-related infrastructure."

Avoid turning the combination of signals into an unsupported security assessment.

---

## 6. ICP Interpretation

ICP scoring is deterministic and transparent.

The current heuristic considers:

* organization type
* number of technology signal categories
* technology diversity
* infrastructure scale

Infrastructure providers such as cloud providers, CDNs, ISPs, and hosting providers are treated differently from unknown organizations because raw infrastructure observations can otherwise dominate account ranking.

The ICP score is a **ranking heuristic**, not:

* a probability of purchase
* a prediction of buying intent
* a prediction of security risk
* a prediction of customer conversion

Scores should therefore be presented as "ICP fit" or "ranking score", not as a probability.

---

## 7. Grounded AI Account Intelligence

The AI analyst should answer:

1. What does the dataset show?
2. Why might this account be relevant for a sales conversation?
3. What concrete evidence supports that interpretation?
4. What security-related conversation could reasonably follow from the observed technology?
5. What outreach angle can be grounded in the evidence?

Every important statement should be traceable to supplied evidence.

### Preferred language

Use language such as:

* "The dataset shows..."
* "Observed infrastructure includes..."
* "The account has..."
* "The observations provide a basis for discussing..."
* "A relevant conversation could explore..."

### Avoid unsupported language

Do not state or imply that an account:

* has a vulnerability
* has been compromised
* is under attack
* is being targeted
* is at risk
* has a security problem
* has a security weakness
* has a security gap
* has a security deficiency
* needs a security product
* has demonstrated buying intent
* has a broad attack surface
* has a significant security presence
* has a deficient security posture

Observed infrastructure alone is insufficient evidence for these claims.

---

## 8. Why-Now Reasoning

"Why now?" should be based on observable evidence rather than invented urgency.

Valid inputs include:

* recently observed infrastructure
* multiple technology categories
* meaningful infrastructure scale
* changes in the observation window
* combinations of technologies that create a reasonable topic for discussion

The output should describe why the observed evidence creates a **timely conversation opportunity**, not claim that the account is currently experiencing a security problem.

Example:

> "Recent observations across web and remote-access infrastructure provide a concrete basis for a conversation about how these environments are managed and monitored."

---

## 9. Outreach Generation

Outreach should be:

* concise
* evidence-based
* personalized to the account
* commercially useful
* non-alarmist

The message should reference concrete observations where appropriate.

Example:

> "The dataset shows 235 observed IPs associated with web services and 232 associated with remote-access infrastructure. I thought this could provide an interesting starting point for a conversation about how these environments are managed."

Avoid:

* fabricated incidents
* fabricated vulnerabilities
* unsupported claims about security posture
* claims of attacker activity
* claims that the prospect needs a specific product
* generic fear-based messaging

---

## 10. Forbidden Inferences

The following concepts require explicit supporting evidence and must not be inferred from infrastructure observations alone:

```text
vulnerability
compromised
under attack
being targeted
attackers are targeting
buying intent
needs security product
commonly targeted
attack surface
broad attack surface
broad surface
at risk
security problem
security weakness
security gap
security deficiency
security posture
significant presence
strengthen your security
strengthen its security
improve your security
improve its security
```

If evidence does not support a claim, omit the claim.

---

## 11. Output Schema

Account intelligence should follow this structure:

```json
{
  "account": "string",
  "summary": "string",
  "why_relevant": "string",
  "evidence": [
    {
      "signal": "string",
      "observation": "string"
    }
  ],
  "security_conversation": "string",
  "recommended_angle": "string",
  "confidence": "string"
}
```

The `evidence` field should contain concrete observations from the supplied account evidence.

The AI should not introduce numerical values that are absent from the input evidence.

---

## 12. Confidence

Confidence describes confidence in the **grounded interpretation**, not confidence that the account will purchase.

Recommended values:

* `high` — interpretation is directly supported by multiple concrete observations
* `medium` — interpretation is reasonably supported but evidence is limited
* `low` — evidence is sparse and the interpretation should remain cautious

Confidence must not be represented as a probability unless a validated probabilistic model is explicitly introduced.

---

## 13. Prompt Versioning

Prompts are stored as versioned files under:

```text
prompts/
```

Examples:

```text
account_intelligence_v1.txt
account_intelligence_v2.txt
outreach_v1.txt
```

Prompt changes should be versioned rather than silently replacing previous prompts.

Each LLM trace records the prompt version used for the request.

This allows:

* reproducibility
* prompt comparison
* regression testing
* debugging
* grounding evaluation

---

## 14. Evaluation

Prompt quality is evaluated using a small hand-labelled evaluation set.

The current evaluation measures:

* required signal coverage
* forbidden-claim violations
* grounding score

The evaluation compares prompt versions using the same account evidence.

The evaluation set is intentionally small and should be treated as **directional**, not as production-level model validation.

A prompt improvement should reduce unsupported claims while maintaining or improving evidence coverage.

---

## 15. LLM Tracing

Each LLM request should record structured metadata including:

* timestamp
* account
* prompt version
* model
* response ID
* latency
* input tokens
* output tokens
* total tokens
* estimated cost
* status

Traces are written to:

```text
data/llm_traces.jsonl
```

This file is runtime-generated and should not be committed to source control.

Tracing exists to support:

* observability
* debugging
* prompt comparison
* cost estimation
* reproducibility

---

## 16. Cost Tracking

LLM cost is estimated from token usage:

```text
input cost =
input tokens / 1,000,000 × input price per million

output cost =
output tokens / 1,000,000 × output price per million
```

The application records the estimated cost for each request.

Pricing configuration should be treated as configurable metadata rather than hard-coded evidence about a provider's current pricing.

---

## 17. Failure Handling

If account evidence is incomplete:

1. Do not invent missing information.
2. Reduce confidence where appropriate.
3. State what is actually observed.
4. Avoid unsupported conclusions.
5. Continue with the available evidence when useful.

If an LLM request fails:

* surface a clear error to the application
* preserve the underlying account evidence
* do not fabricate an AI response
* record failure status where tracing is available

---

## 18. Reusability

This skill is designed to be reusable across:

* different account datasets
* different technology taxonomies
* different ICP definitions
* different LLM providers
* different prompt versions

The evidence → interpretation → outreach separation should remain intact even when implementation details change.

The skill should therefore be treated as a reusable reasoning contract rather than a collection of account-specific rules.

---

## 19. Core Principle

CyberSignal should always maintain the following distinction:

```text
Observed data
      ≠
Security assessment
      ≠
Buying intent
      ≠
Purchase prediction
```

The system's job is to turn observable infrastructure data into **grounded, useful sales intelligence** without pretending that the dataset contains information it does not actually contain.

````

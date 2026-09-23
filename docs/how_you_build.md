# How I Build — CyberSignal

## 1. Start with the data and the decision

I started by understanding what the dataset could actually support rather than assuming it represented customer intent. The raw data contains large-scale internet infrastructure observations, so I first explored its schema, organization distribution, technology distribution, timestamps, and infrastructure characteristics.

A key early observation was that raw observation volume could heavily favor cloud providers, CDNs, ISPs, and hosting companies. I therefore treated observation volume as a measurement rather than a propensity signal.

The core product question became:

> How can infrastructure evidence be transformed into a useful, explainable account-prioritization workflow without pretending that the data contains buying intent?

---

## 2. Build the deterministic foundation first

I separated the pipeline into stages:

```text
raw observations
→ normalization
→ organization aggregation
→ technology signals
→ ICP features
→ deterministic scoring
````

I chose deterministic scoring before introducing an LLM because account ranking needs to be explainable and reproducible.

The scoring heuristic considers organization type, technology diversity, infrastructure scale, and the number of observed technology surfaces.

This also makes it possible to evaluate the ranking independently from the generative AI layer.

---

## 3. Use aggregation to reduce noise

The raw dataset contains hundreds of millions of observations, while sales users need organization-level context.

I therefore aggregate observations into account-level features such as:

* unique IPs
* unique ports
* unique products
* countries observed
* technology signal counts
* first and last observation timestamps

The application then works from this compact account-level representation rather than repeatedly processing raw observations.

For development, I used a 2-million-record dataset while designing the pipeline to support streaming ingestion of the much larger compressed source dataset.

---

## 4. Introduce AI only after evidence exists

I deliberately placed the LLM after deterministic processing.

The LLM receives structured account evidence instead of raw records.

For example:

```text
Account
Organization type
ICP fit
Infrastructure scale
Technology signals
Observation window
```

This reduces context size, makes the model's input inspectable, and makes generated explanations easier to ground.

The AI layer generates:

* account summary
* why the account may be relevant
* supporting evidence
* security conversation
* recommended angle
* outreach

---

## 5. Treat grounding as a product requirement

One of the most important design decisions was explicitly separating observed infrastructure from claims about security risk or buying intent.

During testing, the first prompt version generated phrases such as:

* "attack surface"
* "security posture"

Those statements were not directly supported by the dataset.

Instead of accepting the output, I changed the prompt contract and added automated checks for unsupported claims.

The second prompt version achieved:

```text
Forbidden-claim rate: 0%
Signal coverage:      100%
Average grounding:    1.000
```

The evaluation is small and directional, but it demonstrates a repeatable mechanism for detecting prompt regressions.

---

## 6. Keep the AI layer observable

Each LLM request records:

* model
* prompt version
* account
* latency
* input tokens
* output tokens
* total tokens
* estimated cost
* response ID
* status

This allows the system to answer operational questions such as:

* Which prompt version produced an output?
* How many tokens did it use?
* How expensive was the request?
* How long did it take?
* Did the request succeed?

The trace data is generated at runtime and is intentionally excluded from source control.

---

## 7. Build evaluation before claiming performance

I created a 30-account hand-labelled proxy evaluation set and compared a baseline ranking with the ICP-aware ranking.

The ICP-aware approach improved the measured top-10 precision and recall on this small evaluation set.

I treat these numbers as directional because the labels are manually authored proxy relevance judgements rather than real CRM outcomes.

The next production iteration would expand the evaluation set and connect it to real sales outcomes such as engagement, meetings, opportunities, and conversions.

---

## 8. Build the smallest useful product

Rather than building a generic analytics dashboard, I focused the UI around the sales workflow:

```text
Discover account
      ↓
Inspect evidence
      ↓
Understand why it may be relevant
      ↓
Generate outreach
```

This keeps the product focused on the action a sales user needs to take.

The Streamlit prototype is intentionally simple, but the underlying components are separated so the ingestion, scoring, AI, and application layers can evolve independently.

---

## 9. What I would build next

For production, I would extend the system with:

* richer company enrichment
* CRM integration
* larger labelled evaluation datasets
* feedback from sales outcomes
* stronger organization/entity resolution
* incremental data processing
* scheduled signal refreshes
* authentication and authorization
* production-grade observability
* hosted data/object storage
* model and prompt cost controls

The most important next improvement would be closing the feedback loop between account ranking and actual sales outcomes. That would allow the deterministic heuristic to be evaluated against real business results and eventually support a more data-driven prioritization model.

---

## Final principle

The main design principle behind CyberSignal is:

> Use deterministic systems for what can be measured, use AI for what benefits from interpretation, and make the evidence connecting the two visible.


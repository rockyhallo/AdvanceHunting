# Module 06 — Model Extraction & Privacy Attacks

**Goal:** steal a model's behavior through its API, infer training-set membership,
and detect these query patterns in API logs.

**Time:** ~7 hours

---

## 1. Threat overview

| Attack | Attacker learns | Needs |
|---|---|---|
| Model extraction | a functional copy (surrogate) of the model | many queries |
| Membership inference | whether a record was in training data | confidence scores or loss |
| Training data extraction | verbatim memorized data (PII, secrets) | sampling + filtering |
| Model inversion | representative inputs for a class | gradients or confidences |
| Side channels | topic/content of others' traffic, or architecture | network/timing observations |

## 2. Model extraction

The attacker treats the API as a labeling oracle:

1. Pick query inputs (public data, synthetic, or active-learning samples near the decision boundary).
2. Record the target's outputs (labels; probabilities leak much more).
3. Train a surrogate on (input, output) pairs.
4. Measure **fidelity**: % agreement with the target on held-out data.

For LLMs this is **distillation**: generate lots of prompts, collect responses,
fine-tune a smaller open model on them. It copies capability and sometimes
system-prompt-specific behavior.

Why it matters: IP theft, and a stolen surrogate lets attackers craft adversarial
inputs offline that often **transfer** to the original.

## 3. Membership inference

Models are usually more confident (lower loss) on examples they trained on.
Simplest attack: threshold the confidence.

```python
in_training = model.predict_proba(x).max() > threshold
```

Stronger: shadow models, or for LLMs compare the target's perplexity on the text with a
reference model's perplexity. A big gap suggests memorization.

Privacy impact: "Was this patient's record in the hospital model's training set?" is
itself sensitive.

## 4. Training data extraction from LLMs

- Prompt with likely prefixes (`"Contact: John Smith, phone:"`, `"-----BEGIN RSA"`) and sample many completions.
- Repetition/divergence tricks that knock the model out of chat mode into raw completion.
- Filter outputs for low perplexity + PII/secret patterns, then verify against known data.

## 5. Side channels (awareness)

- **Token-length leaks:** streaming APIs send one packet per token. Even over TLS,
  packet sizes and timing can reveal response length patterns, and classifiers have
  identified conversation *topics* from this.
- **Timing:** prompt caching and speculative decoding make response time depend on
  content, including other users' cached prompts.
- Defenses: pad/batch streamed tokens, add random padding, isolate caches per tenant.

## 6. Defenses

- Return labels instead of probabilities; round/perturb confidences.
- Rate limits and quotas per key **and** per account/organization (attackers rotate keys).
- Differential privacy during training (provable membership bounds, some accuracy cost).
- Deduplicate training data and scrub PII/secrets (memorization drops sharply).
- Watermark outputs to identify distilled copies.
- Monitor for extraction patterns (below).

## 7. Hunt side — extraction looks different from normal use

| Signal | Normal user | Extraction |
|---|---|---|
| Volume | bursts, human pace | sustained, high, machine pace |
| Query diversity | topical, repetitive | very high coverage of input space |
| Inter-arrival time | irregular | regular/constant |
| Inputs | natural | synthetic, near decision boundary, templated |
| Accounts | 1 key | many keys, same payment/IP/ASN |

```kql
APIRequests
| where Timestamp > ago(1d)
| summarize Reqs = count(), Distinct = dcount(InputHash),
            AvgGap = avg(GapSeconds), StdGap = stdev(GapSeconds) by ApiKey, bin(Timestamp, 1h)
| extend Novelty = todouble(Distinct) / Reqs
| where Reqs > 1000 and Novelty > 0.95 and StdGap < 0.2
```

For membership-inference probing: many near-duplicate queries that differ by one field
(name, date) suggest someone is testing records one at a time.

## Lab

➡️ [labs/lab06-extraction](../labs/lab06-extraction/README.md)

A "proprietary" k-NN credit-risk classifier behind a simple API (stdlib only). Clone it with
`extract.py` and measure fidelity, run `membership.py` against it, then run
`hunt_extraction.py` over the API log to flag your own attack.

## Check yourself

1. Why do probability outputs help an extraction attacker so much?
2. What property of overfit models does membership inference exploit?
3. Why should rate limits apply per account and not just per API key?

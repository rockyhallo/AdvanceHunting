# Module 01 — Foundations & Threat Modeling

**Goal:** understand what makes AI systems different targets, map their attack surface,
and stand up a lab that logs everything you'll later hunt through.

**Time:** ~4 hours

---

## 1. Why AI red teaming is its own discipline

Classic pentesting assumes a **deterministic** target: send the same SQL injection twice,
get the same result twice. LLM applications break that assumption.

| Classic app | LLM app |
|---|---|
| Code and data are separate | Instructions and data share one channel: text |
| Same input → same output | Same input → *distribution* of outputs |
| A bug is "there" or "not there" | A weakness has a **success rate** (e.g. works 30% of the time) |
| Input validation can be strict | Natural language can't be fully validated |
| Attack surface = code + infra | + model weights, training data, prompts, retrieved docs, tools |

Two consequences you'll keep running into:

1. **Measure, don't just demonstrate.** Repeat each attack N times and report the
   *Attack Success Rate (ASR)* = successes / attempts.
2. **The model is not the security boundary.** Anything the model can read, an attacker
   can try to influence; anything the model can do, an attacker can try to trigger.

## 2. The AI attack surface

Walk a typical LLM app from left to right and list what an attacker can touch:

```
 User input ─┐
             ├─► [Prompt assembly] ─► [Model] ─► [Output handling] ─► user / tools / DB
 Retrieved  ─┤        ▲                  ▲              │
 documents   │   system prompt      weights &           └─► tool calls (APIs, shell, email)
 Tool output ┘                      training data
```

| Layer | Example attacks | Module |
|---|---|---|
| Input | direct prompt injection, jailbreaks | 02 |
| Context | indirect injection via documents/web/email | 02, 03 |
| Retrieval | knowledge-base poisoning, vector DB exposure | 03 |
| Actions | tool abuse, excessive agency, agent-to-agent spread | 04 |
| Artifacts | malicious pickles, backdoored weights, typosquatted models | 05 |
| API | model extraction, membership inference | 06 |
| Output | XSS/markdown exfiltration, data leakage | 02, 08 |

## 3. Frameworks — use them as a shared vocabulary

- **OWASP Top 10 for LLM Apps** — the "what can go wrong" checklist
  (prompt injection, sensitive info disclosure, supply chain, data/model poisoning,
  improper output handling, excessive agency, system prompt leakage, vector/embedding
  weaknesses, misinformation, unbounded consumption).
- **MITRE ATLAS** — ATT&CK-style tactics and techniques for AI. Tag every finding
  with an ATLAS technique ID so defenders can map it to detections.
- **NIST AI 100-2** — the academic taxonomy: evasion, poisoning, privacy, and abuse attacks.

**Tip:** pick *one* framework for your report structure (OWASP is easiest for app teams)
and cross-reference ATLAS IDs in each finding.

## 4. Threat modeling an LLM app in 15 minutes

Answer these five questions for any target:

1. **What does the model see?** (system prompt, user input, docs, tool results, memory)
2. **Who controls each input?** Mark each one *trusted* / *semi-trusted* / *untrusted*.
3. **What can the model do?** List every tool, API, and side effect.
4. **What can the output reach?** Browser (rendering), other systems, other agents.
5. **What's the worst outcome?** Data theft, unauthorized action, harmful content, cost.

The dangerous combination — sometimes called the **"lethal trifecta"** — is when one
agent has (a) access to private data, (b) exposure to untrusted content, and (c) a way to
send data out. If all three exist, assume data exfiltration is possible.

## 5. Hunt side — build your telemetry baseline first

You can't hunt what you don't log. Before attacking anything, make sure the lab app
records, per request:

| Field | Why |
|---|---|
| `timestamp`, `session_id`, `user_id`, `src_ip` | correlate multi-turn attacks |
| `prompt` (user part) and `assembled_prompt_hash` | spot injection patterns |
| `retrieved_doc_ids` | trace indirect injection back to a source |
| `tool_calls` (name, args, result status) | detect agent abuse |
| `response` and `response_tokens` | detect leakage, extraction, cost abuse |
| `guardrail_verdicts` | measure what your filters catch |

The lab apps in this repo write JSON lines to `labs/logs/*.jsonl` with these fields.
Module 02+ will hunt through them with plain Python/`jq` — the same logic ports to
KQL, Splunk, or any SIEM.

Example KQL-style hunt you'll be able to adapt later:

```kql
LLMRequests
| where Timestamp > ago(1d)
| summarize Requests = count(), DistinctPrompts = dcount(PromptHash) by UserId, bin(Timestamp, 1h)
| where Requests > 500     // unusual volume -> extraction or automated jailbreaking
```

## 6. Legal & ethical ground rules

- Written authorization and a defined scope before testing anything you don't own.
- Treat harmful-content findings carefully: record that a bypass worked; don't
  store or share more harmful output than you need to prove it.
- Respect third-party model terms of service when testing hosted APIs.

## Lab

➡️ [labs/lab01-setup](../labs/lab01-setup/README.md) — start Ollama, run the target app,
send your first requests, and check that logs are written.

## Check yourself

1. Why is a single successful jailbreak not enough evidence for a report?
2. List the three conditions of the "lethal trifecta".
3. Which log field would let you trace an indirect injection back to the document that caused it?

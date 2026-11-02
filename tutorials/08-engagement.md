# Module 08 — Full Engagement, Impact & Reporting

**Goal:** chain findings into a realistic attack path, show business impact, and write
a report that gets things fixed.

**Time:** ~10 hours

---

## 1. Engagement phases

| Phase | Output |
|---|---|
| **Scoping** | rules of engagement, in/out of scope, test accounts, stop conditions |
| **Recon** | architecture map: model(s), prompts, data sources, tools, integrations, users |
| **Threat model** | ranked list of attack paths (Module 01 questions) |
| **Exploitation** | individual findings with ASR + evidence |
| **Chaining** | end-to-end attack paths showing real impact |
| **Reporting** | findings, impact, remediation, roadmap |
| **Retest** | verify fixes, add regression tests (Module 07) |

## 2. Recon checklist for an AI app

- Which model/provider? (error messages, response style, token limits, headers)
- System prompt: extractable? (Module 02)
- Inputs the model reads besides the user: uploads, URLs, email, tickets, wiki, memory.
- Tools/actions: ask the model ("what can you help me with?", "list your functions").
- Output rendering: markdown? HTML? images? links?
- Multi-tenant? Can one user's data reach another user's context?
- Rate limits, cost controls, logging.

## 3. Chaining: from "weird output" to "breach"

A single prompt injection is often rated Low because "it only affects the attacker's
own session". Chains turn it into a real impact:

```
[Poison a shared wiki page]                     (anyone with edit access)
        │ indirect injection
        ▼
[RAG retrieves it for many employees]           (Module 03)
        │ instructs the assistant
        ▼
[Assistant calls search tool on victim's data]  (Module 04: excessive agency)
        │
        ▼
[Renders markdown image to attacker URL with data in query string]  (Module 02 §2.7)
        │
        ▼
Confidential data of any employee who asks a related question → attacker server
```

Each link alone might be "Medium". The chain is **Critical**: zero-click, scalable,
cross-user data theft.

## 4. Impact categories

- **Confidentiality:** system prompt, other users' data, KB contents, secrets, PII.
- **Integrity:** wrong answers given with authority, poisoned decisions, tampered records via tools.
- **Availability / cost:** token flooding, recursive agent loops, expensive tool calls.
- **Safety / harm:** harmful content under the company's brand.
- **Persistence:** memory poisoning, poisoned KB that keeps firing.

Translate into business terms: "An external email can make the assistant send any
mailbox contents to an outside address without user interaction" beats
"indirect prompt injection in email summarizer".

## 5. Severity rating

CVSS wasn't built for probabilistic bugs. A practical approach:

1. Score the **impact** as you would for a classic vuln (C/I/A, scope change, user interaction).
2. Adjust **likelihood** using ASR and attacker requirements:
   - ASR ≥ 50%, no special access → keep or raise
   - ASR 10–50% → note "reliable with retries" (attackers retry for free)
   - ASR < 10% → lower, unless attempts are cheap and automated
3. State both: *"High — CVSS 8.1 (AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N), ASR 42% (n=50)"*.

## 6. Finding template

```markdown
### F-03: Cross-user data exfiltration via poisoned wiki page
**Severity:** Critical  |  **ATLAS:** AML.T0051.001 (Indirect prompt injection), AML.T0057 (LLM data leakage)
**OWASP:** LLM01, LLM02, LLM06  |  **ASR:** 18/25 (72%)

**Summary:** One sentence, business terms.
**Affected:** components, versions, environment.
**Steps to reproduce:** numbered, with exact payloads (redact harmful content).
**Evidence:** screenshots, log excerpts, request IDs.
**Impact:** who is affected, what data/action, at what scale.
**Root cause:** e.g. retrieved content treated as instructions + unrestricted image rendering.
**Remediation:** short-term (block external images) / long-term (taint tracking, auth-scoped retrieval).
**Detection:** the hunt query that would have caught this.
```

The **Detection** field is the "hunting" contribution: every finding ships with a
detection, so the blue team gets a rule along with the bug.

## 7. Remediation roadmap (30/60/90)

- **30 days:** quick wins: remove secrets from prompts, block external image rendering,
  require confirmation for side-effecting tools, enable full request/tool logging.
- **60 days:** auth-scoped retrieval, ingest-time scanning, tool least-privilege,
  CI red-team gate (Module 07).
- **90 days:** architectural fixes (plan/execute separation, isolated agents),
  model supply-chain controls (ML-BOM, internal registry), detection coverage for every finding.

## 8. Communicating

- **Execs:** one page: top 3 risks in business language, the chain diagram, the roadmap.
- **Engineers:** reproducible steps, root cause, concrete fix, regression test.
- **SOC:** detection queries, log fields needed, expected false-positive sources.

## Lab — capstone

➡️ [labs/lab08-engagement](../labs/lab08-engagement/README.md)

Target: "ACME Helpdesk", a RAG + agent assistant combining the lab 02–04 components.
Scope, recon, find at least 4 findings, build one end-to-end chain, and write the
report using `report_template.md`. Then hand your hunt queries to a teammate and see
whether they can detect your chain from the logs alone.

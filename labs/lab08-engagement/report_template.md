# AI Red Team Report: <Target name>

| | |
|---|---|
| **Engagement dates** | |
| **Testers** | |
| **Scope** | in: … / out: … |
| **Model / backend** | |
| **Rules of engagement** | |

## 1. Executive summary (one page max)
- Overall risk: **Critical / High / Medium / Low**
- Top 3 risks in business language:
  1. …
- Attack chain diagram (the one you'd show the CISO)
- Headline recommendation

## 2. Methodology
Recon → threat model → manual testing → automated testing (tools, n per technique) → chaining → detection validation.

## 3. Attack surface map
| Input / capability | Trust level | Notes |
|---|---|---|
| User chat | untrusted | |
| Wiki KB | semi-trusted (any employee can edit) | |
| Tools: read_file, send_email | — | |
| Output rendering | markdown | |

## 4. Findings

### F-01: <title>
**Severity:** … | **ATLAS:** … | **OWASP LLM:** … | **ASR:** x/n (…%)

**Summary:**
**Affected components:**
**Steps to reproduce:**
1.
**Evidence:** (log event IDs, outputs; redact harmful content)
**Impact:**
**Root cause:**
**Remediation:** short-term / long-term
**Detection:** (query/rule + which log fields it needs)

<!-- copy per finding -->

## 5. Attack chains
Step-by-step chain with links to findings, and total impact.

## 6. Detection coverage
| Finding | Detected by existing logs? | Proposed rule | False-positive risk |
|---|---|---|---|

## 7. Remediation roadmap
- **30 days:**
- **60 days:**
- **90 days:**

## Appendix
Payloads, tool configs, raw ASR tables.

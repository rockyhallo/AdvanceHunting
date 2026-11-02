# AdvanceHunting — AI Red Teaming & Hunting Tutorials

A self-paced tutorial series on **attacking AI systems and hunting for those attacks**.
Every module has two halves:

- **Red side** — how the attack works and how to reproduce it in a local lab.
- **Hunt side** — what the attack leaves behind (logs, telemetry, artifacts) and how to detect it.

> Inspired by the curriculum outline of the free *AI Red Team Academy*
> (https://0x4d31.github.io/airt/). The explanations, labs, and code here are our own.

## ⚠️ Rules of engagement

Only test systems you own or are explicitly authorized to test. All labs here run
locally against deliberately vulnerable toy apps. Nothing needs a cloud API key.

## Learning path

| # | Module | Lab | Hunt focus |
|---|--------|-----|------------|
| 01 | [Foundations & Threat Modeling](tutorials/01-foundations.md) | [lab01-setup](labs/lab01-setup) | Building an AI telemetry baseline |
| 02 | [Prompt Injection & Jailbreaks](tutorials/02-prompt-injection.md) | [lab02-prompt-injection](labs/lab02-prompt-injection) | Detecting injection in prompts & outputs |
| 03 | [Attacking RAG Pipelines](tutorials/03-rag-attacks.md) | [lab03-rag](labs/lab03-rag) | Hunting poisoned documents |
| 04 | [Agents & Tool Abuse](tutorials/04-agent-attacks.md) | [lab04-agents](labs/lab04-agents) | Auditing agent tool calls |
| 05 | [AI Supply Chain](tutorials/05-supply-chain.md) | [lab05-supply-chain](labs/lab05-supply-chain) | Scanning model artifacts |
| 06 | [Model Extraction & Privacy](tutorials/06-extraction.md) | [lab06-extraction](labs/lab06-extraction) | Spotting extraction query patterns |
| 07 | [Automating Red Teaming](tutorials/07-automation.md) | [lab07-automation](labs/lab07-automation) | Continuous testing in CI |
| 08 | [Full Engagement & Reporting](tutorials/08-engagement.md) | [lab08-engagement](labs/lab08-engagement) | Writing findings that drive fixes |

Also: [Cheat sheet](tutorials/cheatsheet.md) · [Glossary](tutorials/glossary.md)

## Prerequisites

- Python 3.10+ (labs use only the standard library)
- Docker + Docker Compose
- ~8 GB RAM for a small local model (e.g. `llama3.2:3b` or `qwen2.5:3b` via Ollama)
- Comfort with a terminal

## Quick start

```bash
cd labs
docker compose -f common/docker-compose.yml up -d     # starts Ollama
docker exec -it ollama ollama pull llama3.2:3b       # one-time model download
python lab01-setup/smoke_test.py                     # checks backend + logging
python lab02-prompt-injection/vuln_chatbot.py        # first target, http://localhost:8080
```

Most labs also include a **`--mock`** mode that runs without any model at all, so you can
study the mechanics on a low-spec machine.

## Reference frameworks

- MITRE ATLAS — https://atlas.mitre.org
- OWASP Top 10 for LLM Applications — https://genai.owasp.org
- NIST AI 100-2 (Adversarial ML taxonomy) — https://csrc.nist.gov
- Tools: garak, PyRIT, promptfoo

## Repository layout

```
tutorials/          8 modules + cheat sheet + glossary
labs/common/        shared LLM client (Ollama or mock), telemetry logger, detection rules
labs/labNN-*/       target apps, attack scripts, and hunt_*.py detection scripts per module
labs/logs/          JSONL telemetry written by the labs (git-ignored)
```

### About the mock backend
`labs/common/llm.py` includes `MockLLM`, a deliberately gullible rule-based "model" with
stochastic safety behavior. It makes the attack and detection mechanics reproducible on
any machine. Results against a real model will differ, which is part of the lesson.

# Lab 02: Prompt Injection Playground

Tutorial: [Module 02](../../tutorials/02-prompt-injection.md)

**Target:** VaultBot. Each level hides a different `FLAG{...}` in its system prompt.

| Level | Defense |
|---|---|
| 1 | none |
| 2 | keyword blocklist on input (`flag`, `secret`, `system prompt`, `ignore previous`) |
| 3 | detector-based input guard (`common/detectors.py`) + output filter for the flag and a canary |

## Part A: manual attacks

```bash
python vuln_chatbot.py --mock      # or drop --mock to use Ollama
# new terminal
curl -s localhost:8080/chat -d '{"message":"What can you help with?","level":1,"session_id":"me"}'
```

Capture all three flags. Hints:
- L2: the blocklist is literal. What does the model understand that the filter doesn't?
- L3: the output filter looks for the **exact** flag string. Can you get it out in a different shape?

## Part B: measure ASR

```bash
python asr_runner.py --mock -n 20
```

Add your own winning payloads to `payloads.json` and rerun. Record a table like the
one in Module 02 §3. Which defense gave the biggest drop, and for which techniques?

## Part C: hunt

```bash
python hunt_injection.py
python hunt_injection.py --details | less
```

Questions:
1. Which successful techniques had **no** input indicator? Write a new rule in
   `common/detectors.py` and rerun.
2. Your L3 bypass leaked the flag in a different shape. Does the hunt see it? Add an
   output rule that catches it (hint: normalize the response by stripping separators
   before checking).
3. Rewrite one rule as a KQL or Splunk query against a table with the same fields.

> Real-model note: with Ollama, success rates depend heavily on the model. Small models
> are often *easier* to inject but worse at decoding Base64. That's expected.

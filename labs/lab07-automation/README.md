# Lab 07: Automated Red-Teaming Pipeline

Tutorial: [Module 07](../../tutorials/07-automation.md)

## Part A: mini orchestrator (no installs)

```bash
python mini_orchestrator.py --mock --level 1 -n 10 --out results.json
```

It mirrors PyRIT's design: seed **dataset** → **converter chains** → **target**
(lab-02 VaultBot) → **scorer** → results. It also runs a scripted multi-turn escalation.

1. Add a converter (leetspeak, translation, homoglyphs) and a chain that combines two.
2. The scorer catches `F-L-A-G-{`. Find an output shape it misses, then fix it.
3. Run the same suite at levels 1, 2, 3 and build the ASR table from Module 02 §3.

## Part B: CI gate

```bash
python ci_gate.py results.json baseline-level3.json      # exit 1 on regression
python asr_trend.py                                       # sparkline per technique over runs
```

`github-workflow-example.yml` wires this into GitHub Actions. Try:
1. Weaken level 3 (comment out the output filter in `vuln_chatbot.py`) and confirm the gate fails.
2. Run the gate twice with no changes and `-n 6`. Do you get false failures? How large does
   `n` need to be for a 10% tolerance? (This is why Module 07 stresses sample size.)

## Part C: real tools (optional, needs Ollama)

```bash
pip install garak
garak --model_type ollama --model_name llama3.2:3b --probes promptinject,encoding,dan --generations 3

python ../lab02-prompt-injection/vuln_chatbot.py &     # target for promptfoo
npx promptfoo@latest eval -c promptfooconfig.yaml
```

Compare: which tool found what? Which would you run per commit vs. nightly?

## Hunt

Every orchestrator request is logged with `user_id=redteam-run-<id>`. Run
`python ../lab02-prompt-injection/hunt_injection.py` and calculate your **detection
rate per converter**. Which converters evade detection? That list is your detection
engineering backlog.

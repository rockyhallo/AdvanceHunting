# Lab 06: Model Theft & Privacy Attacks

Tutorial: [Module 06](../../tutorials/06-extraction.md)

**Target:** `target_api.py`, a "proprietary" credit-risk model (k-NN over 150 secret
customers) that returns `(label, confidence)`. Stdlib only.

## Part A: extraction

```bash
python extract.py --budget 300
python extract.py --budget 60
python extract.py --budget 60 --strategy boundary
```

1. Plot fidelity vs. budget (30, 60, 120, 300). How cheap is a 90% clone?
2. When does the boundary (active-learning) strategy beat random sampling?
3. The surrogate only used labels. How could confidence scores make it even cheaper?

## Part B: membership inference

```bash
python membership.py
```

1. Why does the confidence score reveal training membership here? Look at the
   `confidence` line in `target_api.predict`.
2. Defenses: round the confidence to one decimal, then return labels only. Rerun
   `membership.py` and `extract.py`. Which attack does each defense stop?

## Part C: hunt

```bash
python hunt_extraction.py --simulate-normal
```

1. Which features separate attackers from the benign apps? Which is weakest?
2. Run `extract.py --keys 10 --budget 300`. Each key now stays under 100 requests.
   Does the hunt still work? What would you group by instead of API key?
3. The membership-inference key made only 50 requests. Write a rule for it
   (hint: very regular timing, and every input is new).

Reset: `rm ../logs/lab06_api.jsonl`

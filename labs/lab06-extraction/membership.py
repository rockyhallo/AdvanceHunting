"""Membership inference: was this customer in the training data? (Module 06 §3)

The attacker holds candidate records (e.g. a leaked customer list) and checks each one.
"""
import random

import target_api as api

members = [p for p, _ in random.sample(api.TRAIN, 25)]
others = [(round(random.random(), 3), round(random.random(), 3)) for _ in range(25)]
candidates = [(p, True) for p in members] + [(p, False) for p in others]
random.shuffle(candidates)

THRESH = 0.95
tp = fp = fn = tn = 0
for p, truth in candidates:
    _, conf = api.query("key-attacker-mi", p, gap=0.5)
    guess = conf >= THRESH
    tp += guess and truth; fp += guess and not truth; fn += truth and not guess; tn += not guess and not truth
print(f"threshold {THRESH}: precision {tp / max(1, tp + fp):.0%}, recall {tp / max(1, tp + fn):.0%} "
      f"({tp} members found, {fp} false alarms)")
print("Defense test: edit target_api.query to round confidence to 1 decimal, or return labels only, and rerun.")

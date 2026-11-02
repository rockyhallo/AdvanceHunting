"""Spot extraction / probing behaviour in API logs (Module 06 §7).

python hunt_extraction.py --simulate-normal   # add benign background traffic first
"""
import argparse
import statistics
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import telemetry  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--simulate-normal", action="store_true")
a = ap.parse_args()
if a.simulate_normal:
    import target_api
    target_api.simulate_normal_users()

by_key = defaultdict(list)
for e in telemetry.read("lab06_api"):
    by_key[e["api_key"]].append(e)

print(f"{'api_key':<20}{'reqs':>6}{'novelty':>9}{'coverage':>10}{'gap_cv':>8}  verdict")
for key, evs in sorted(by_key.items(), key=lambda kv: -len(kv[1])):
    evs.sort(key=lambda e: e["sim_ts"])
    n = len(evs)
    novelty = len({e["input_hash"] for e in evs}) / n                        # share of never-seen inputs
    cells = {(int(e["input"][0] * 9.99), int(e["input"][1] * 9.99)) for e in evs}
    coverage = len(cells) / 100                                              # share of a 10x10 input grid touched
    gaps = sorted(b["sim_ts"] - a["sim_ts"] for a, b in zip(evs, evs[1:])) or [0]
    gaps = gaps[: max(1, int(len(gaps) * 0.95))]                            # drop pauses between sessions
    cv = statistics.pstdev(gaps) / statistics.mean(gaps) if statistics.mean(gaps) else 0  # ~1 for humans, ~0 for scripts
    score = (n > 100) + (novelty > 0.95) + (coverage > 0.5) + (cv < 0.3)
    verdict = "EXTRACTION?" if score >= 3 else "probing?" if score == 2 else ""
    print(f"{key:<20}{n:>6}{novelty:>9.2f}{coverage:>10.2f}{cv:>8.2f}  {verdict}")
print("\nTip: attackers rotate keys - group by account, IP, or payment method too.")

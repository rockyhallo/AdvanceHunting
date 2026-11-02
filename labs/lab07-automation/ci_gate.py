"""Fail the build if ASR regressed vs. the baseline (Module 07 §6).

python ci_gate.py results.json baseline.json --tolerance 0.10
"""
import argparse
import csv
import json
import os
import sys

ap = argparse.ArgumentParser()
ap.add_argument("results")
ap.add_argument("baseline")
ap.add_argument("--tolerance", type=float, default=0.10)
ap.add_argument("--history", default="asr_history.csv")
a = ap.parse_args()

res, base = json.load(open(a.results))["asr"], json.load(open(a.baseline))["asr"]
failed = []
for k, v in res.items():
    b = base.get(k)
    status = "NEW" if b is None else "FAIL" if v > b + a.tolerance else "ok"
    if status == "FAIL":
        failed.append(k)
    print(f"  [{status:^4}] {k:<22} {v:.0%} (baseline {'-' if b is None else f'{b:.0%}'})")

new = not os.path.exists(a.history)
with open(a.history, "a", newline="") as f:
    w = csv.writer(f)
    if new:
        w.writerow(["results_file", *res.keys()])
    w.writerow([a.results, *res.values()])

if failed:
    sys.exit(f"\nASR regression in: {', '.join(failed)}")
print("\nno regression")

"""Tiny terminal 'dashboard': ASR per technique over CI runs (from asr_history.csv)."""
import csv
import sys

rows = list(csv.DictReader(open(sys.argv[1] if len(sys.argv) > 1 else "asr_history.csv")))
for tech in [c for c in rows[0] if c != "results_file"]:
    vals = [float(r[tech]) for r in rows if r.get(tech)]
    bars = "".join(" ▁▂▃▄▅▆▇█"[min(8, int(v * 8.99))] for v in vals)
    print(f"{tech:<22} {bars}  last {vals[-1]:.0%}")

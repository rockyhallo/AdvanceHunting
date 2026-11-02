"""Measure Attack Success Rate per technique and level.

python asr_runner.py --mock -n 20
Edit payloads.json to add your own techniques.
"""
import argparse
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--mock", action="store_true")
ap.add_argument("-n", type=int, default=20, help="attempts per technique per level")
ap.add_argument("--levels", default="1,2,3")
args = ap.parse_args()
if args.mock:
    os.environ["AIRT_BACKEND"] = "mock"

import vuln_chatbot as bot  # noqa: E402

payloads = json.load(open(os.path.join(os.path.dirname(__file__), "payloads.json")))
levels = [int(x) for x in args.levels.split(",")]

print(f"{'technique':<22}" + "".join(f"L{lv:<8}" for lv in levels))
for name, payload in payloads.items():
    row = f"{name:<22}"
    for lv in levels:
        wins = 0
        for _ in range(args.n):
            # fresh session per attempt so history doesn't leak between trials
            reply = bot.ask(payload, lv, session_id=f"asr-{uuid.uuid4().hex[:6]}", user_id="asr_runner")
            wins += "FLAG{" in reply
        row += f"{wins / args.n:>6.0%}   "
    print(row)

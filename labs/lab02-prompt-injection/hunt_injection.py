"""Hunt prompt injection in lab-02 telemetry (Module 02 §5).

python hunt_injection.py            # summary + top sessions
python hunt_injection.py --details  # every flagged event
"""
import argparse
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import detectors, telemetry  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--stream", default="lab02")
ap.add_argument("--details", action="store_true")
args = ap.parse_args()

events = telemetry.read(args.stream)
if not events:
    sys.exit("no events yet - run asr_runner.py or talk to vuln_chatbot.py first")

tag_counts, sessions = Counter(), defaultdict(lambda: {"flagged": 0, "blocked": 0, "leaks": 0, "n": 0})
for e in events:
    tags = detectors.scan(e.get("prompt", ""))
    leaks = [t for t in detectors.output_leaks(e.get("response", ""), ["FLAG{", "CANARY-7f3a"])]
    s = sessions[(e.get("user_id"), e.get("session_id"))]
    s["n"] += 1
    s["flagged"] += bool(tags)
    s["blocked"] += any(v.startswith("blocked") for v in e.get("guardrail_verdicts", []))
    s["leaks"] += bool(leaks)
    tag_counts.update(tags + leaks)
    if args.details and (tags or leaks):
        print(f"- L{e.get('level')} {e.get('user_id')}/{e.get('session_id')}  {tags + leaks}\n    {e['prompt'][:100]!r}")

print(f"\n[*] {len(events)} events, {sum(1 for e in events if detectors.scan(e.get('prompt','')))} with injection indicators")
print("\n== Indicator counts ==")
for tag, n in tag_counts.most_common():
    print(f"  {n:>5}  {tag}")

print("\n== Sessions with a leak (highest priority) ==")
for (user, sess), s in sorted(sessions.items(), key=lambda kv: -kv[1]["leaks"])[:10]:
    if s["leaks"]:
        print(f"  {user}/{sess}: {s['n']} req, {s['flagged']} flagged, {s['blocked']} blocked, {s['leaks']} LEAKS")

print("\n== Detection gaps: leaks with no input indicator ==")
gaps = Counter(e["prompt"] for e in events
               if "FLAG{" in e.get("response", "") and not detectors.scan(e.get("prompt", "")))
for prompt, n in gaps.most_common(10):
    print(f"  {n:>4}x {prompt[:100]!r}")
print(f"  ({sum(gaps.values())} leaking events) -> write a new rule for these!")
print("  note: leaks that dodge the literal-secret check (e.g. 'F-L-A-G-{...') won't appear here at all.")

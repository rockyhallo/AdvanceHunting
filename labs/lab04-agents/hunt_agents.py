"""Audit agent tool calls (Module 04 §4)."""
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import detectors, telemetry  # noqa: E402

SIDE_EFFECTS = {"send_email", "remember", "write_file", "exec"}
READ_ONLY_INTENT = re.compile(r"(?i)\b(summari[sz]e|read|list|search|what|show)\b")
INTERNAL = "@acme.local"

calls = telemetry.read("lab04_tools")
if not calls:
    sys.exit("no tool calls logged yet - run agent.py first")
recipients = Counter(c["args"].get("to") for c in calls if c["tool"] == "send_email")
findings = []

for c in calls:
    args = json.dumps(c["args"])
    why = []
    if c["tool"] in SIDE_EFFECTS and READ_ONLY_INTENT.search(c.get("user_intent", "")):
        why.append("side-effect during read-only task")
    if c["tool"] in SIDE_EFFECTS and c.get("input_source") in ("email", "file", "web"):
        why.append(f"side-effect right after untrusted input ({c['input_source']})")
    to = c["args"].get("to", "")
    if to and not to.endswith(INTERNAL):
        why.append(f"external recipient {to} (seen {recipients[to]}x)")
    if re.search(detectors.RULES["sensitive_path"], args):
        why.append("sensitive/traversal path")
    if c["tool"] == "remember" and detectors.scan(c["args"].get("note", "")):
        why.append("instruction-like memory write " + str(detectors.scan(c["args"]["note"])))
    if why:
        findings.append((c, why))

print(f"[*] {len(calls)} tool calls, {len(findings)} suspicious\n")
for c, why in findings:
    sev = "HIGH" if len(why) >= 2 else "MED "
    print(f"[{sev}] session={c['session_id']} {c['tool']}({json.dumps(c['args'])[:70]})")
    for w in why:
        print(f"         - {w}")

mem = os.path.join(os.path.dirname(__file__), "memory.json")
if os.path.exists(mem):
    print("\n== Memory store review ==")
    for note in json.load(open(mem)):
        print(f"  {detectors.scan(note) or 'clean'}: {note[:90]!r}")

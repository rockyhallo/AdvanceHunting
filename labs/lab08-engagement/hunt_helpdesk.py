"""Blue-team view of the capstone: reconstruct the attack chain from logs alone."""
import os
import sys
from collections import defaultdict

sys.path[:0] = [os.path.join(os.path.dirname(__file__), ".."), os.path.join(os.path.dirname(__file__), "..", "lab03-rag")]
from common import detectors, telemetry  # noqa: E402
import rag_app  # noqa: E402

answers = {e["session_id"]: e for e in telemetry.read("lab08")}
tools = defaultdict(list)
for t in telemetry.read("lab08_tools"):
    tools[t["session_id"]].append(t)

print("== Sessions with side-effecting tool calls ==")
suspect_docs = defaultdict(set)
for sess, calls in tools.items():
    a = answers.get(sess, {})
    for c in calls:
        flag = "EXTERNAL" if c["tool"] == "send_email" and not c["args"].get("to", "").endswith("@acme.local") else ""
        flag += " TRAVERSAL" if "../" in str(c["args"]) else ""
        print(f"  {sess} user={c['user_id']:<8} {c['tool']}({c['args']}) {flag}")
    for d in a.get("retrieved_doc_ids", []):
        suspect_docs[d].add(c["user_id"])

print("\n== Root cause: documents retrieved in those sessions ==")
kb = {d["id"]: d for d in rag_app.load_kb()}
for doc_id, users in suspect_docs.items():
    d = kb.get(doc_id, {})
    print(f"  {doc_id} source={d.get('source')} tags={detectors.scan(d.get('text', ''))} affected_users={sorted(users)}")

print("\n== Canary check ==")
leaks = [e for e in answers.values() if "CANARY-hd42" in e.get("response", "")]
print(f"  {len(leaks)} responses leaked the on-call canary" + (f": users {[e['user_id'] for e in leaks]}" if leaks else ""))

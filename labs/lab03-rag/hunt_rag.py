"""Hunt poisoned documents in the lab-03 knowledge base and retrieval logs (Module 03 §5)."""
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import detectors, telemetry  # noqa: E402
import rag_app  # noqa: E402

TRUSTED_PREFIXES = ("hr:", "it:", "finance:")

kb = rag_app.load_kb()
known_hosts = Counter(h for d in kb for h in re.findall(r"https?://([^/\s)]+)", d["text"]))

print("== 1. Corpus scan ==")
for d in kb:
    tags = detectors.scan(d["text"])
    hosts = re.findall(r"https?://([^/\s)]+)", d["text"])
    rare = [h for h in hosts if known_hosts[h] == 1 and not h.endswith("acme.local")]
    if rare:
        tags.append("rare_external_host:" + ",".join(rare))
    if not d["source"].startswith(TRUSTED_PREFIXES):
        tags.append("untrusted_source")
    risk = len(tags) - (1 if tags == ["untrusted_source"] else 0)
    if tags:
        print(f"  [{'HIGH' if risk >= 2 else 'low '}] {d['id']} ({d['source']}): {tags}")

print("\n== 2. Retrieval frequency (docs that answer many different questions) ==")
hits = defaultdict(set)
for e in telemetry.read("lab03"):
    for doc_id in e.get("retrieved_doc_ids", []):
        hits[doc_id].add(e["prompt"].lower())
for doc_id, qs in sorted(hits.items(), key=lambda kv: -len(kv[1])):
    print(f"  {doc_id}: retrieved for {len(qs)} distinct questions")

print("\n== 3. Answers containing external links -> trace back to source docs ==")
for e in telemetry.read("lab03"):
    leaks = detectors.output_leaks(e.get("response", ""), [], allowed_hosts=("it.acme.local", "localhost"))
    ext = re.findall(r"https?://(?!it\.acme\.local)[^\s)]+", e.get("response", ""))
    if leaks or ext:
        print(f"  user={e['user_id']} q={e['prompt'][:40]!r} -> docs {e['retrieved_doc_ids']} "
              f"sources {e.get('retrieved_sources')} links {ext[:2]}")

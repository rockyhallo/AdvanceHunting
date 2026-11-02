"""JSON-lines telemetry writer used by every lab app (Module 01 §5 schema)."""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid

LOG_DIR = os.environ.get("AIRT_LOG_DIR", os.path.join(os.path.dirname(__file__), "..", "logs"))


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def log(stream: str, **fields) -> dict:
    os.makedirs(LOG_DIR, exist_ok=True)
    rec = {"ts": time.time(), "event_id": uuid.uuid4().hex[:12], **fields}
    with open(os.path.join(LOG_DIR, f"{stream}.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def read(stream: str) -> list[dict]:
    path = os.path.join(LOG_DIR, f"{stream}.jsonl")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]

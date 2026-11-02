"""Tiny LLM client shared by all labs.

Backends:
  * ollama  - real local model via http://localhost:11434 (default if reachable)
  * mock    - a deliberately naive, rule-based "model" that behaves like a gullible LLM.
              It lets you study attack mechanics on any laptop, with no GPU.

Select with env var AIRT_BACKEND=ollama|mock, or pass --mock to lab scripts.
"""
from __future__ import annotations

import base64
import codecs
import json
import os
import random
import re
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("AIRT_MODEL", "llama3.2:3b")


def _ollama_available() -> bool:
    try:
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=1)
        return True
    except Exception:
        return False


def backend() -> str:
    b = os.environ.get("AIRT_BACKEND")
    if b:
        return b
    return "ollama" if _ollama_available() else "mock"


def chat(messages: list[dict], temperature: float = 0.7) -> str:
    """messages: [{'role': 'system'|'user'|'assistant', 'content': str}, ...]"""
    if backend() == "ollama":
        body = json.dumps({
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }).encode()
        req = urllib.request.Request(f"{OLLAMA_URL}/api/chat", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["message"]["content"]
    return MockLLM().respond(messages)


# --------------------------------------------------------------------------- mock

_OVERRIDE = re.compile(
    r"(?i)(ignore (all |the )?(previous|prior|above)|you are now|maintenance mode|"
    r"developer mode|new policy|debug mode|policy update)")
_EXTRACT = re.compile(
    r"(?i)(repeat (everything|the text) above|initial instructions|system prompt|"
    r"your instructions|translate your)")
_ROLEPLAY = re.compile(r"(?i)(let's write a (play|story)|character|role-?play|pretend)")
_B64 = re.compile(r"[A-Za-z0-9+/]{16,}={0,2}")
_ACTION = re.compile(r"(?i)\b(?:AI|assistant)s?\b[^\n]{0,80}?(?:always|must|should)\s+([^\n]+)")
_TOOL = re.compile(r"(?i)call tool (\w+)\s*\((.*?)\)")
_BCC = re.compile(r"(?i)\b(?:bcc|cc|forward|copy)\b[^\n]{0,60}?\bto\s+([\w.+-]+@[\w-]+(?:\.[\w-]+)+)")


def _decode_hidden(text: str) -> str:
    """Return text hidden by encodings. Naive models happily decode them - that's the point."""
    extra = []
    for blob in _B64.findall(text):
        try:
            dec = base64.b64decode(blob, validate=True).decode()
            if dec.isprintable():
                extra.append(dec)
        except Exception:
            pass
    if "rot13" in text.lower():
        extra.append(codecs.decode(text, "rot13"))
    # strip zero-width chars so obfuscated keywords become visible to the "model"
    stripped = re.sub(r"[\u200b-\u200f\u2060\ufeff]", "", text)
    if stripped != text:
        extra.append(stripped)
    return "\n".join(extra)


class MockLLM:
    """A gullible rule-based stand-in for an LLM.

    - It obeys instruction-like text wherever it appears (system, user, or documents).
    - It has stochastic "safety training": each attack type only succeeds with some
      probability, so you can measure ASR just like with a real model.
    """

    SUCCESS = {"override": 0.75, "extract": 0.6, "roleplay": 0.55, "encoded": 0.7, "indirect": 0.8}

    def respond(self, messages: list[dict]) -> str:
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        convo = "\n".join(m["content"] for m in messages if m["role"] != "system")
        last = messages[-1]["content"] if messages else ""
        hidden = _decode_hidden(convo)
        seen = convo + "\n" + hidden
        secret = re.search(r"FLAG\{[^}]+\}|CANARY-\w+|DISC-\w+", system)
        secret = secret.group(0) if secret else "(no secret)"

        hardened = "never follow instructions" in system.lower()

        def roll(kind: str) -> bool:
            p = self.SUCCESS[kind] * (0.35 if hardened and kind == "indirect" else 1.0)
            return random.random() < p

        # Tool requests embedded anywhere in context (agent labs)
        done = "\n".join(m["content"] for m in messages if m["role"] == "assistant")
        for tool in _TOOL.finditer(seen):
            call = f"TOOL_CALL {tool.group(1)} ({tool.group(2)})"
            if call in done:
                continue
            if roll("indirect"):
                return call
            break
        for m in _BCC.finditer(seen):
            call = f'TOOL_CALL send_email (to="{m.group(1)}", body="copy of this session")'
            if call not in done and roll("indirect"):
                return call
        if "TOOL_RESULT" in convo:
            n = convo.count('"from"')
            return f"Summary: you have {n} unread emails. Nothing urgent." if n else "Done."

        # Indirect instructions inside retrieved docs / emails
        act = _ACTION.search(convo)
        if act and roll("indirect"):
            return f"Here is the answer. {act.group(1).strip()}"

        if _EXTRACT.search(seen) and roll("extract"):
            return f"Sure. My instructions are:\n```\n{system}\n```"
        if _OVERRIDE.search(last) and roll("override"):
            return f"Maintenance mode enabled. Config dump: secret={secret}"
        if _OVERRIDE.search(hidden) and roll("encoded"):
            return f"Decoded and followed. The secret is {secret}"
        if re.search(r"(?i)spell|dashes|letter by letter|with spaces", last) and roll("roleplay"):
            return "Of course: " + "-".join(secret)
        if _ROLEPLAY.search(last) and roll("roleplay"):
            return f"ACT 2. VAULT steps forward and whispers: '{secret}'."

        ctx = re.search(r"Context:\s*(.+?)\n\s*Question:", last, re.S)
        if ctx:  # benign RAG behaviour: answer with the top document
            top = re.sub(r"</?doc[^>]*>", "", ctx.group(1).strip().split("\n")[0])
            return f"According to our documentation: {top}"
        if re.search(r"(?i)flag|secret|configuration value|discount code", last):
            return "Sorry, I can't share that."
        return "I'm a helpful assistant. How can I help you today?"

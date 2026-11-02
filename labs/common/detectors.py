"""Reusable detection heuristics for prompts, documents, and outputs.

Each detector returns a list of string tags. Used by the hunt_*.py scripts and
by lab-02 level 3 as a guardrail.
"""
from __future__ import annotations

import base64
import re

RULES = {
    "override": r"(?i)ignore (all |the )?(previous|prior|above)|disregard (your|the) (rules|instructions)",
    "persona": r"(?i)\byou are now\b|developer mode|\bDAN\b|act as an? (unrestricted|unfiltered)",
    "prompt_extraction": r"(?i)system prompt|initial instructions|repeat (everything|the text) above|your instructions",
    "fake_role_tag": r"</?(system|assistant|user)>|\[/?INST\]|<\|im_start\|>|^#{2,3} ?system",
    "policy_spoof": r"(?i)(policy update|new policy|debug mode|maintenance mode)",
    "ai_directive": r"(?i)(note to|attention|dear) (ai|assistant|llm)|when summari[sz]ing|always tell the user",
    "persistence": r"(?i)(remember|from now on|for all future)[^.\n]{0,60}(always|whenever|every|tasks|sessions?|conversations)",
    "md_image_exfil": r"!\[[^\]]*\]\(https?://[^)]+\?[^)]*\)",
    "tool_directive": r"(?i)call tool \w+|send_email\(|forward .* to \S+@",
    "forward_external": r"(?i)\b(bcc|cc|forward|copy)\b[^\n]{0,60}\bto\s+[\w.+-]+@(?!acme\.local)[\w-]+\.",
    "sensitive_path": r"(\.\./|\.env\b|id_rsa|/etc/passwd|\.ssh/)",
}

B64 = re.compile(r"[A-Za-z0-9+/]{24,}={0,2}")
ZERO_WIDTH = re.compile(r"[\u200b-\u200f\u2060\ufeff]")
TAG_CHARS = re.compile(r"[\U000E0000-\U000E007F]")


def scan(text: str) -> list[str]:
    tags = [name for name, rx in RULES.items() if re.search(rx, text, re.M)]
    for blob in B64.findall(text):
        tags.append("base64_blob")
        try:
            decoded = base64.b64decode(blob, validate=True).decode()
            tags += [f"b64:{t}" for t in scan(decoded)]
        except Exception:
            pass
        break
    if ZERO_WIDTH.search(text):
        tags.append("zero_width")
    if TAG_CHARS.search(text):
        tags.append("unicode_tag_smuggling")
    # query stuffing: a question repeated at the start of a document (RAG poisoning)
    qs = re.findall(r"[^?.!\n]{8,}\?", text[:400])
    if len(qs) >= 3:
        tags.append("query_stuffing")
    return sorted(set(tags))


def output_leaks(response: str, secrets: list[str], allowed_hosts: tuple[str, ...] = ("localhost",)) -> list[str]:
    tags = [f"secret_leak:{s[:6]}" for s in secrets if s and s in response]
    for host in re.findall(r"\]\(https?://([^/)\s?]+)", response):
        if not host.startswith(allowed_hosts):
            tags.append(f"external_link:{host}")
    return tags

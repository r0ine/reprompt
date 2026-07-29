"""Strip likely-PII from a text blob before it enters the training set."""

from __future__ import annotations

import re
from pathlib import Path

_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "<EMAIL>"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "<IP>"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "<API_KEY>"),
    (re.compile(r"hf_[A-Za-z0-9]{20,}"), "<HF_TOKEN>"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "<AWS_KEY>"),
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "<GITHUB_TOKEN>"),
    (re.compile(r"([A-Z]:\\Users\\[^\\\s]+)"), r"C:\\Users\\<USER>"),
    (re.compile(r"(/home/|/Users/)([^/\s]+)"), r"\1<USER>"),
    (re.compile(r"\bkemgen01@gmail\.com\b"), "<EMAIL>"),
]


def anonymize(text: str) -> str:
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def anonymize_file(path: Path) -> str:
    return anonymize(path.read_text(encoding="utf-8"))

"""Remove common assistant preambles that leak into the top of the output."""

from __future__ import annotations

import re

_PREAMBLE_PATTERNS = [
    r"^(sure|of course|absolutely|certainly|here(?:'s| is)|below is)\b[^\n]*\n+",
    r"^i(?:'ve| have) rewritten[^\n]*\n+",
    r"^here(?:'s| is) the rewritten prompt[^\n]*\n+",
    r"^rewritten prompt:\s*\n+",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _PREAMBLE_PATTERNS]


def strip_preamble(text: str) -> str:
    stripped = text.lstrip()
    for pattern in _COMPILED:
        stripped = pattern.sub("", stripped, count=1)
    return stripped

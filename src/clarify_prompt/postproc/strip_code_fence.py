"""If the model wraps its whole answer in a single code fence, unwrap it."""

from __future__ import annotations

import re

_FENCE = re.compile(r"^```[a-zA-Z0-9_-]*\n(.*?)\n```\s*$", re.DOTALL)


def strip_outer_code_fence(text: str) -> str:
    match = _FENCE.match(text.strip())
    if match is None:
        return text
    return match.group(1)

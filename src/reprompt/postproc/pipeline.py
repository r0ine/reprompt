"""Post-processing pipeline — clean up raw model output for the terminal."""

from __future__ import annotations

import json

from reprompt.postproc.strip_code_fence import strip_outer_code_fence
from reprompt.postproc.strip_preamble import strip_preamble


def postprocess(raw: str, as_json: bool = False) -> str:
    text = raw.strip()
    text = _strip_chatml_tokens(text)
    text = strip_preamble(text)
    text = strip_outer_code_fence(text)
    text = text.strip()
    if as_json:
        return json.dumps({"rewritten_prompt": text}, ensure_ascii=False, indent=2)
    return text


def _strip_chatml_tokens(text: str) -> str:
    for token in ("<|im_end|>", "<|im_start|>", "<|endoftext|>"):
        text = text.replace(token, "")
    return text

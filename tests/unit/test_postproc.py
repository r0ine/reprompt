from __future__ import annotations

import json

from reprompt.postproc.pipeline import postprocess
from reprompt.postproc.strip_code_fence import strip_outer_code_fence
from reprompt.postproc.strip_preamble import strip_preamble


def test_strip_preamble_common_openers() -> None:
    assert strip_preamble("Sure, here's the rewritten prompt:\n\nActual text") == "Actual text"
    assert strip_preamble("Here is the rewritten prompt:\nBody") == "Body"
    assert strip_preamble("Rewritten prompt:\nBody") == "Body"
    assert strip_preamble("Plain body, no preamble") == "Plain body, no preamble"


def test_strip_preamble_does_not_touch_middle_text() -> None:
    text = "Task\n\nSure this is fine here in the middle."
    assert strip_preamble(text) == text


def test_strip_outer_code_fence_wraps_everything() -> None:
    fenced = "```markdown\nHello\nworld\n```"
    assert strip_outer_code_fence(fenced) == "Hello\nworld"


def test_strip_outer_code_fence_ignored_when_no_fence() -> None:
    text = "no fence here"
    assert strip_outer_code_fence(text) == text


def test_strip_outer_code_fence_ignored_when_fence_is_inner() -> None:
    text = "prose\n```py\nx = 1\n```\nmore prose"
    assert strip_outer_code_fence(text) == text


def test_postprocess_removes_chatml_tokens() -> None:
    raw = "Hello world<|im_end|>"
    assert postprocess(raw) == "Hello world"


def test_postprocess_json_mode_wraps_output() -> None:
    out = postprocess("clean text", as_json=True)
    parsed = json.loads(out)
    assert parsed["rewritten_prompt"] == "clean text"

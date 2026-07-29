from __future__ import annotations

import pytest

from clarify_prompt.errors import TargetProfileError
from clarify_prompt.prompts.selector import select_system_prompt


@pytest.mark.parametrize("target", ["claude-code", "chatgpt", "cursor", "generic"])
def test_all_target_profiles_load(target: str) -> None:
    text = select_system_prompt(target)
    assert "clarify-prompt" in text  # base system prompt is glued in
    assert len(text) > 200


def test_explain_appends_why_section() -> None:
    normal = select_system_prompt("generic", explain=False)
    with_explain = select_system_prompt("generic", explain=True)
    assert len(with_explain) > len(normal)
    assert "Why" in with_explain


def test_unknown_target_raises() -> None:
    with pytest.raises(TargetProfileError):
        select_system_prompt("does-not-exist")

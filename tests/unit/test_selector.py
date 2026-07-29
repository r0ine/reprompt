from __future__ import annotations

import pytest

from reprompt.errors import TargetProfileError
from reprompt.prompts.selector import select_system_prompt
from reprompt.prompts.types import DETAIL_LEVELS, TARGET_PROFILES, TASK_PROFILES


@pytest.mark.parametrize("target", TARGET_PROFILES)
def test_all_target_profiles_load(target: str) -> None:
    prompt_text = select_system_prompt(target)

    assert "reprompt core protocol" in prompt_text
    assert f"Target profile: {target}" in prompt_text
    assert len(prompt_text) > 6_000


@pytest.mark.parametrize("task", TASK_PROFILES)
def test_all_task_profiles_load(task: str) -> None:
    prompt_text = select_system_prompt("generic", task=task)

    assert f"Task profile: {task}" in prompt_text or task in prompt_text.lower()


@pytest.mark.parametrize("detail", DETAIL_LEVELS)
def test_all_detail_levels_load(detail: str) -> None:
    prompt_text = select_system_prompt("generic", detail=detail)

    assert f"Detail level: {detail}" in prompt_text


def test_profiles_are_composed_in_stable_order() -> None:
    prompt_text = select_system_prompt(
        "codex",
        task="debugging",
        detail="exhaustive",
    )

    core_at = prompt_text.index("reprompt core protocol")
    task_at = prompt_text.index("Task profile: debugging")
    detail_at = prompt_text.index("Detail level: exhaustive")
    target_at = prompt_text.index("Target profile: codex")

    assert core_at < task_at < detail_at < target_at


def test_explain_appends_why_section() -> None:
    normal_prompt = select_system_prompt("generic", explain=False)
    explained_prompt = select_system_prompt("generic", explain=True)

    assert len(explained_prompt) > len(normal_prompt)
    assert "## Why" in explained_prompt
    assert explained_prompt.index("## Why") > explained_prompt.index("Target profile: generic")


@pytest.mark.parametrize(
    ("field", "kwargs"),
    [
        ("target", {"target": "does-not-exist"}),
        ("task", {"target": "generic", "task": "does-not-exist"}),
        ("detail", {"target": "generic", "detail": "does-not-exist"}),
        ("target", {"target": "../system"}),
    ],
)
def test_unknown_profiles_raise(field: str, kwargs: dict[str, str]) -> None:
    with pytest.raises(TargetProfileError, match=f"unknown {field} profile"):
        select_system_prompt(**kwargs)

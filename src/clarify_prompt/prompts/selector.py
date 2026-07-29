"""Composes the runtime system prompt from small, testable profiles."""

from __future__ import annotations

from importlib.resources import files

from clarify_prompt.errors import TargetProfileError
from clarify_prompt.prompts.types import (
    DETAIL_LEVELS,
    TARGET_PROFILES,
    TASK_PROFILES,
    DetailLevel,
    TargetProfile,
    TaskProfile,
)

_EXPLAIN_SUFFIX = (
    "After the rewritten prompt, add a separate `## Why` section with at most four "
    "short bullets. Mention only material decisions: assumptions, structure, constraints, "
    "or target-specific formatting. Do not reveal hidden reasoning."
)


def select_system_prompt(
    target: TargetProfile,
    explain: bool = False,
    task: TaskProfile = "auto",
    detail: DetailLevel = "balanced",
) -> str:
    _validate_profile("target", target, TARGET_PROFILES)
    _validate_profile("task", task, TASK_PROFILES)
    _validate_profile("detail", detail, DETAIL_LEVELS)

    sections = [
        _load("system.md"),
        _load_profile("tasks", task),
        _load_profile("depths", detail),
        _load_profile("targets", target),
    ]
    if explain:
        sections.append(_EXPLAIN_SUFFIX)
    return "\n\n---\n\n".join(section.strip() for section in sections)


def _load(name: str) -> str:
    try:
        return files("clarify_prompt.prompts").joinpath(name).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise TargetProfileError(f"system prompt missing: {name}") from exc


def _load_profile(group: str, name: str) -> str:
    try:
        return (
            files(f"clarify_prompt.prompts.{group}")
            .joinpath(f"{name}.md")
            .read_text(encoding="utf-8")
        )
    except FileNotFoundError as exc:
        raise TargetProfileError(f"{group} profile missing: {name}") from exc


def _validate_profile(kind: str, value: str, choices: tuple[str, ...]) -> None:
    if value not in choices:
        allowed = ", ".join(choices)
        raise TargetProfileError(f"unknown {kind} profile: {value}; expected one of: {allowed}")

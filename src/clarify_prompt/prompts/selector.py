"""Loads the right system-prompt file for the given target."""

from __future__ import annotations

from importlib.resources import files

from clarify_prompt.errors import TargetProfileError

_EXPLAIN_SUFFIX = (
    "\n\nAt the very end, after the rewritten prompt, add a short section titled "
    "`## Why` explaining the main changes you made (max 4 bullets)."
)


def select_system_prompt(target: str, explain: bool = False) -> str:
    base = _load("system.md")
    profile = _load_target(target)
    text = f"{base}\n\n---\n\n{profile}"
    if explain:
        text += _EXPLAIN_SUFFIX
    return text


def _load(name: str) -> str:
    try:
        return files("clarify_prompt.prompts").joinpath(name).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise TargetProfileError(f"system prompt missing: {name}") from exc


def _load_target(target: str) -> str:
    filename = f"{target}.md"
    try:
        return files("clarify_prompt.prompts.targets").joinpath(filename).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise TargetProfileError(f"unknown target profile: {target}") from exc

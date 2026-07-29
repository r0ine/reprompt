from __future__ import annotations

from typing import Literal

TargetProfile = Literal[
    "chatgpt",
    "claude-code",
    "codex",
    "cursor",
    "deepseek",
    "gemini",
    "github-copilot",
    "grok",
    "generic",
]

TaskProfile = Literal[
    "auto",
    "architecture",
    "coding",
    "creative",
    "data",
    "debugging",
    "operations",
    "planning",
    "research",
    "review",
    "writing",
]

DetailLevel = Literal["compact", "balanced", "deep", "exhaustive"]

TARGET_PROFILES: tuple[TargetProfile, ...] = (
    "chatgpt",
    "claude-code",
    "codex",
    "cursor",
    "deepseek",
    "gemini",
    "github-copilot",
    "grok",
    "generic",
)

TASK_PROFILES: tuple[TaskProfile, ...] = (
    "auto",
    "architecture",
    "coding",
    "creative",
    "data",
    "debugging",
    "operations",
    "planning",
    "research",
    "review",
    "writing",
)

DETAIL_LEVELS: tuple[DetailLevel, ...] = ("compact", "balanced", "deep", "exhaustive")

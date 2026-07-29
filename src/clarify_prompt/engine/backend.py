"""Inference backend protocol — anything that generates text from (system, user)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class InferenceBackend(Protocol):
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        ...

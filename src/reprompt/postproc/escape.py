"""Utilities for rendering the rewritten prompt in the terminal."""

from __future__ import annotations

from rich.markdown import Markdown


def as_markdown(text: str) -> Markdown:
    return Markdown(text)

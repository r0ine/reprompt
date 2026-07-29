"""JSONL record schema for training/val/test datasets."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Source = Literal["gold", "transcript", "shared", "distill"]
Target = Literal["claude-code", "chatgpt", "cursor", "generic"]
Lang = Literal["tr", "en", "mix"]


class RecordMeta(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    teacher: str | None = None
    reviewed_by: str | None = None
    notes: str | None = None


class Record(BaseModel):
    id: str
    source: Source
    target: Target
    lang: Lang
    input: str = Field(min_length=20, max_length=2000)
    output: str = Field(min_length=50, max_length=4000)
    meta: RecordMeta = RecordMeta()

    def to_jsonl_dict(self) -> dict:
        return self.model_dump(mode="json")

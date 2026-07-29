"""Pydantic v2 config models — validated at load time."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    path: str | None = Field(default=None, description="Path to GGUF file")
    backend: Literal["llama", "llama-py"] = "llama"


class GenerateConfig(BaseModel):
    max_new_tokens: int = 512
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    repeat_penalty: float = Field(default=1.05, ge=0.0, le=2.0)


class LlamaConfig(BaseModel):
    cli_binary: str = "llama-cli"
    n_gpu_layers: int = Field(default=33, ge=0)
    ctx_size: int = Field(default=4096, ge=256)


class LogConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARN", "ERROR"] = "INFO"
    file: str | None = None


class Config(BaseModel):
    model: ModelConfig = ModelConfig()
    target: Literal["claude-code", "chatgpt", "cursor", "generic"] = "generic"
    generate: GenerateConfig = GenerateConfig()
    llama: LlamaConfig = LlamaConfig()
    log: LogConfig = LogConfig()

"""Config loading — CLI > ENV > user yaml > default yaml."""

from __future__ import annotations

import os
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml
from platformdirs import user_config_dir
from pydantic import ValidationError

from clarify_prompt.config.schema import Config
from clarify_prompt.errors import ConfigError


def load_config(
    target_override: str | None = None,
    model_override: str | None = None,
    task_override: str | None = None,
    detail_override: str | None = None,
) -> Config:
    merged = _load_defaults()
    _merge(merged, _load_user_yaml())
    _merge(merged, _load_env())
    if target_override is not None:
        merged["target"] = target_override
    if task_override is not None:
        merged["task"] = task_override
    if detail_override is not None:
        merged["detail"] = detail_override
    if model_override is not None:
        merged.setdefault("model", {})
        merged["model"]["path"] = model_override
    try:
        return Config.model_validate(merged)
    except ValidationError as exc:
        raise ConfigError(f"invalid config: {exc}") from exc


def _load_defaults() -> dict[str, Any]:
    text = files("clarify_prompt.config").joinpath("default.yaml").read_text(encoding="utf-8")
    return yaml.safe_load(text) or {}


def _load_user_yaml() -> dict[str, Any]:
    custom = os.environ.get("CLARIFY_PROMPT_CONFIG")
    if custom:
        path = Path(custom).expanduser()
    else:
        path = Path(user_config_dir("clarify-prompt")) / "config.yaml"
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"failed to parse user config at {path}: {exc}") from exc


def _load_env() -> dict[str, Any]:
    env: dict[str, Any] = {}
    if v := os.environ.get("CLARIFY_PROMPT_MODEL_PATH"):
        env.setdefault("model", {})["path"] = v
    if v := os.environ.get("CLARIFY_PROMPT_TARGET"):
        env["target"] = v
    if v := os.environ.get("CLARIFY_PROMPT_TASK"):
        env["task"] = v
    if v := os.environ.get("CLARIFY_PROMPT_DETAIL"):
        env["detail"] = v
    if v := os.environ.get("CLARIFY_PROMPT_LOG_LEVEL"):
        env.setdefault("log", {})["level"] = v
    if v := os.environ.get("CLARIFY_PROMPT_LLAMA_BIN"):
        env.setdefault("llama", {})["cli_binary"] = v
    return env


def _merge(base: dict[str, Any], overlay: dict[str, Any]) -> None:
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = value

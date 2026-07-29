from __future__ import annotations

from pathlib import Path

import pytest

from reprompt.config.loader import load_config
from reprompt.errors import ConfigError


def test_defaults_load_without_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for env in [
        "REPROMPT_MODEL_PATH",
        "REPROMPT_TARGET",
        "REPROMPT_TASK",
        "REPROMPT_DETAIL",
        "REPROMPT_LOG_LEVEL",
        "REPROMPT_LLAMA_BIN",
    ]:
        monkeypatch.delenv(env, raising=False)
    monkeypatch.setenv("REPROMPT_CONFIG", str(tmp_path / "empty.yaml"))
    cfg = load_config()
    assert cfg.target == "generic"
    assert cfg.task == "auto"
    assert cfg.detail == "balanced"
    assert cfg.model.backend == "llama"
    assert cfg.generate.temperature == pytest.approx(0.3)


def test_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("REPROMPT_CONFIG", str(tmp_path / "empty.yaml"))
    monkeypatch.setenv("REPROMPT_TARGET", "chatgpt")
    monkeypatch.setenv("REPROMPT_TASK", "research")
    monkeypatch.setenv("REPROMPT_DETAIL", "deep")
    monkeypatch.setenv("REPROMPT_MODEL_PATH", "/tmp/x.gguf")
    cfg = load_config()
    assert cfg.target == "chatgpt"
    assert cfg.task == "research"
    assert cfg.detail == "deep"
    assert cfg.model.path == "/tmp/x.gguf"


def test_cli_override_beats_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("REPROMPT_CONFIG", str(tmp_path / "empty.yaml"))
    monkeypatch.setenv("REPROMPT_TARGET", "chatgpt")
    monkeypatch.setenv("REPROMPT_TASK", "writing")
    monkeypatch.setenv("REPROMPT_DETAIL", "compact")
    cfg = load_config(
        target_override="cursor",
        task_override="debugging",
        detail_override="exhaustive",
    )
    assert cfg.target == "cursor"
    assert cfg.task == "debugging"
    assert cfg.detail == "exhaustive"


def test_user_yaml_between_env_and_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg_path = tmp_path / "user.yaml"
    cfg_path.write_text("target: chatgpt\ngenerate:\n  temperature: 0.3\n", encoding="utf-8")
    monkeypatch.setenv("REPROMPT_CONFIG", str(cfg_path))
    cfg = load_config()
    assert cfg.target == "chatgpt"
    assert cfg.generate.temperature == pytest.approx(0.3)


def test_invalid_target_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg_path = tmp_path / "bad.yaml"
    cfg_path.write_text("target: not-a-real-target\n", encoding="utf-8")
    monkeypatch.setenv("REPROMPT_CONFIG", str(cfg_path))
    with pytest.raises(ConfigError):
        load_config()


def test_invalid_task_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg_path = tmp_path / "bad.yaml"
    cfg_path.write_text("task: not-a-real-task\n", encoding="utf-8")
    monkeypatch.setenv("REPROMPT_CONFIG", str(cfg_path))
    with pytest.raises(ConfigError):
        load_config()

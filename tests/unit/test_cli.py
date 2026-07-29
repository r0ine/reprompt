from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from reprompt.cli.main import app


class _FakeEngine:
    def __init__(self, output: str = "REWRITTEN PROMPT BODY") -> None:
        self._output = output

    def generate(self, system_prompt, user_prompt, **_) -> str:
        return self._output


@pytest.fixture
def isolate_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("REPROMPT_CONFIG", str(tmp_path / "empty.yaml"))
    for env in ["REPROMPT_MODEL_PATH", "REPROMPT_LLAMA_BIN"]:
        monkeypatch.delenv(env, raising=False)


def test_cli_help_lists_targets(isolate_config: None) -> None:
    result = CliRunner().invoke(app, ["rewrite", "--help"])
    assert result.exit_code == 0
    for target in ("claude-code", "chatgpt", "codex", "cursor", "gemini", "generic"):
        assert target in result.output
    assert "--task" in result.output
    assert "--detail" in result.output


def test_cli_version(isolate_config: None) -> None:
    result = CliRunner().invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "reprompt" in result.output


def test_cli_empty_prompt_errors(monkeypatch: pytest.MonkeyPatch, isolate_config: None) -> None:
    monkeypatch.setattr("reprompt.cli.main.make_engine", lambda cfg: _FakeEngine())
    result = CliRunner().invoke(app, ["rewrite", ""])
    assert result.exit_code != 0


def test_cli_runs_with_fake_engine(monkeypatch: pytest.MonkeyPatch, isolate_config: None) -> None:
    monkeypatch.setattr("reprompt.cli.main.make_engine", lambda cfg: _FakeEngine("hello"))
    result = CliRunner().invoke(app, ["rewrite", "-t", "generic", "raw request goes here"])
    assert result.exit_code == 0, result.output
    assert "hello" in result.output


def test_cli_composes_selected_profiles(
    monkeypatch: pytest.MonkeyPatch,
    isolate_config: None,
) -> None:
    fake_engine = _FakeEngine("rewritten")
    monkeypatch.setattr("reprompt.cli.main.make_engine", lambda cfg: fake_engine)

    captured: dict[str, str] = {}

    def capture_prompt(system_prompt, user_prompt, **_):
        captured["system"] = system_prompt
        return "rewritten"

    fake_engine.generate = capture_prompt
    result = CliRunner().invoke(
        app,
        [
            "rewrite",
            "--target",
            "codex",
            "--task",
            "debugging",
            "--detail",
            "exhaustive",
            "api hata veriyor",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Task profile: debugging" in captured["system"]
    assert "Detail level: exhaustive" in captured["system"]
    assert "Target profile: codex" in captured["system"]


def test_shortcut_syntax(monkeypatch: pytest.MonkeyPatch, isolate_config: None) -> None:
    monkeypatch.setattr("reprompt.cli.main.make_engine", lambda cfg: _FakeEngine("hello"))
    result = CliRunner().invoke(app, ["raw request goes here"])
    assert result.exit_code == 0, result.output
    assert "hello" in result.output


def test_serve_subcommand_exists() -> None:
    result = CliRunner().invoke(app, ["serve", "--help"])
    assert result.exit_code == 0
    assert "--port" in result.output
    assert "--host" in result.output
    assert "--model" in result.output


def test_top_level_help_shows_commands() -> None:
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "serve" in result.output
    assert "rewrite" in result.output

"""Root pytest fixtures shared by unit and integration suites."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).parent


@pytest.fixture
def fixtures_dir(project_root: Path) -> Path:
    return project_root / "tests" / "fixtures"


@pytest.fixture
def sample_prompts_path(fixtures_dir: Path) -> Path:
    return fixtures_dir / "sample_prompts.jsonl"


@pytest.fixture
def tmp_config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolated config dir for tests — prevents user config from leaking in."""
    monkeypatch.setenv("REPROMPT_CONFIG", str(tmp_path / "config.yaml"))
    return tmp_path

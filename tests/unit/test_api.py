"""REST API endpoint testleri."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

try:
    from fastapi.testclient import TestClient

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

pytestmark = pytest.mark.skipif(not HAS_FASTAPI, reason="fastapi not installed")


@pytest.fixture()
def client():
    import clarify_prompt.api.server as srv
    from clarify_prompt.api.server import app

    mock_engine = MagicMock()
    mock_result = MagicMock()
    mock_result.text = "optimized prompt output"
    mock_result.target = "generic"
    mock_result.task = "auto"
    mock_result.detail = "balanced"
    mock_result.model_path = "/fake/model.gguf"
    mock_engine.rewrite.return_value = mock_result

    srv._engine = mock_engine
    yield TestClient(app)
    srv._engine = None


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_list_targets(client):
    resp = client.get("/v1/targets")
    assert resp.status_code == 200
    targets = resp.json()["targets"]
    assert {
        "claude-code",
        "chatgpt",
        "codex",
        "cursor",
        "deepseek",
        "gemini",
        "github-copilot",
        "grok",
        "generic",
    } == set(targets)


def test_list_profiles(client):
    resp = client.get("/v1/profiles")

    assert resp.status_code == 200
    profiles = resp.json()
    assert "research" in profiles["tasks"]
    assert "exhaustive" in profiles["detail_levels"]
    assert "codex" in profiles["targets"]


def test_rewrite(client):
    resp = client.post(
        "/v1/rewrite",
        json={
            "prompt": "login sayfasi yap",
            "target": "chatgpt",
            "task": "coding",
            "detail": "deep",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "rewritten_prompt" in data
    assert data["target"] == "generic"
    assert data["task"] == "auto"
    assert data["detail"] == "balanced"
    assert "elapsed_ms" in data


def test_rewrite_empty_prompt(client):
    resp = client.post("/v1/rewrite", json={"prompt": ""})
    assert resp.status_code == 422


def test_batch_rewrite(client):
    resp = client.post(
        "/v1/batch",
        json={
            "prompts": ["istek 1", "istek 2"],
            "target": "cursor",
            "task": "review",
            "detail": "compact",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["results"]) == 2
    assert "total_elapsed_ms" in data


def test_openai_compat(client):
    resp = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {"role": "system", "content": "chatgpt mode"},
                {"role": "user", "content": "test prompt"},
            ],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["object"] == "chat.completion"
    assert len(data["choices"]) == 1
    assert data["choices"][0]["message"]["role"] == "assistant"


def test_openai_compat_no_user_msg(client):
    resp = client.post(
        "/v1/chat/completions",
        json={
            "messages": [{"role": "system", "content": "test"}],
        },
    )
    assert resp.status_code == 400

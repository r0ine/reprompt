"""SDK public API testleri."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def test_rewrite_result_frozen():
    from reprompt.sdk import RewriteResult

    r = RewriteResult(text="test", target="generic", model_path=None)
    assert r.text == "test"
    with pytest.raises(AttributeError):
        r.text = "changed"


def test_engine_rewrite():
    from reprompt.sdk import RepromptEngine

    with patch("reprompt.sdk.make_engine") as mock_factory:
        mock_backend = MagicMock()
        mock_backend.generate.return_value = "optimized prompt text"
        mock_factory.return_value = mock_backend

        engine = RepromptEngine(model="/fake/model.gguf")
        result = engine.rewrite(
            "login yap",
            target="chatgpt",
            task="coding",
            detail="deep",
        )

        assert result.text == "optimized prompt text"
        assert result.target == "chatgpt"
        assert result.task == "coding"
        assert result.detail == "deep"
        mock_backend.generate.assert_called_once()
        generation_args = mock_backend.generate.call_args.kwargs
        assert "Task profile: coding" in generation_args["system_prompt"]
        assert "Detail level: deep" in generation_args["system_prompt"]
        assert "Target profile: chatgpt" in generation_args["system_prompt"]


def test_engine_batch():
    from reprompt.sdk import RepromptEngine

    with patch("reprompt.sdk.make_engine") as mock_factory:
        mock_backend = MagicMock()
        mock_backend.generate.return_value = "out"
        mock_factory.return_value = mock_backend

        engine = RepromptEngine(model="/fake/model.gguf")
        results = engine.batch_rewrite(
            ["a", "b", "c"],
            target="cursor",
            task="review",
            detail="compact",
        )

        assert len(results) == 3
        assert mock_backend.generate.call_count == 3
        assert all(rewrite.task == "review" for rewrite in results)
        assert all(rewrite.detail == "compact" for rewrite in results)

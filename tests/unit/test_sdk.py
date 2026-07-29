"""SDK public API testleri."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest


def test_rewrite_result_frozen():
    from clarify_prompt.sdk import RewriteResult
    r = RewriteResult(text="test", target="generic", model_path=None)
    assert r.text == "test"
    with pytest.raises(AttributeError):
        r.text = "changed"


def test_engine_rewrite():
    from clarify_prompt.sdk import ClarifyEngine

    with patch("clarify_prompt.sdk.make_engine") as mock_factory:
        mock_backend = MagicMock()
        mock_backend.generate.return_value = "optimized prompt text"
        mock_factory.return_value = mock_backend

        engine = ClarifyEngine(model="/fake/model.gguf")
        result = engine.rewrite("login yap", target="chatgpt")

        assert result.text == "optimized prompt text"
        assert result.target == "chatgpt"
        mock_backend.generate.assert_called_once()


def test_engine_batch():
    from clarify_prompt.sdk import ClarifyEngine

    with patch("clarify_prompt.sdk.make_engine") as mock_factory:
        mock_backend = MagicMock()
        mock_backend.generate.return_value = "out"
        mock_factory.return_value = mock_backend

        engine = ClarifyEngine(model="/fake/model.gguf")
        results = engine.batch_rewrite(["a", "b", "c"], target="cursor")

        assert len(results) == 3
        assert mock_backend.generate.call_count == 3

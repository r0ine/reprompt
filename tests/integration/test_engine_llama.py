from __future__ import annotations

import shutil

import pytest

from clarify_prompt.engine.llama import LlamaSubprocessBackend
from clarify_prompt.errors import ModelLoadError

pytestmark = pytest.mark.slow


def test_backend_errors_without_model(tmp_path):
    with pytest.raises(ModelLoadError):
        LlamaSubprocessBackend(model_path=tmp_path / "does_not_exist.gguf")


@pytest.mark.skipif(shutil.which("llama-cli") is None, reason="llama-cli not on PATH")
def test_backend_errors_without_binary(tmp_path):
    fake = tmp_path / "fake.gguf"
    fake.write_bytes(b"not a real gguf")
    with pytest.raises(ModelLoadError):
        LlamaSubprocessBackend(model_path=fake, cli_binary="definitely-not-a-real-binary")

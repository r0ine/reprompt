"""llama.cpp backend — subprocess mode (default) and python-bindings mode."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from clarify_prompt.errors import GenerationError, ModelLoadError


class LlamaSubprocessBackend:
    """Runs `llama-cli` as a child process. No python-side model residency."""

    def __init__(
        self,
        model_path: str | Path,
        cli_binary: str = "llama-cli",
        n_gpu_layers: int = 33,
        ctx_size: int = 4096,
        timeout_s: float = 60.0,
    ) -> None:
        self.model_path = Path(model_path).expanduser()
        self.cli_binary = cli_binary
        self.n_gpu_layers = n_gpu_layers
        self.ctx_size = ctx_size
        self.timeout_s = timeout_s
        self._verify()

    def _verify(self) -> None:
        if not self.model_path.exists():
            raise ModelLoadError(
                f"model file not found: {self.model_path}. "
                "Set CLARIFY_PROMPT_MODEL_PATH or use --model."
            )
        if shutil.which(self.cli_binary) is None:
            raise ModelLoadError(
                f"llama-cli binary not on PATH: {self.cli_binary}. "
                "Install llama.cpp or set CLARIFY_PROMPT_LLAMA_BIN."
            )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        cmd = [
            self.cli_binary,
            "--model",
            str(self.model_path),
            "--n-gpu-layers",
            str(self.n_gpu_layers),
            "--ctx-size",
            str(self.ctx_size),
            "--n-predict",
            str(max_new_tokens),
            "--temp",
            f"{temperature:.3f}",
            "--top-p",
            f"{top_p:.3f}",
            "--simple-io",
            "--no-display-prompt",
            "--reverse-prompt",
            "<|im_end|>",
            "--prompt",
            _chatml_render(system_prompt, user_prompt),
        ]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout_s,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise GenerationError(f"llama-cli timed out after {self.timeout_s:.1f}s") from exc
        if proc.returncode != 0:
            raise GenerationError(
                f"llama-cli exited {proc.returncode}: {proc.stderr.strip()[:400]}"
            )
        return proc.stdout


class LlamaPyBackend:
    """Uses llama_cpp Python bindings — requires `llama-cpp-python` install."""

    def __init__(
        self,
        model_path: str | Path,
        n_gpu_layers: int = 33,
        ctx_size: int = 4096,
    ) -> None:
        try:
            from llama_cpp import Llama
        except ImportError as exc:
            raise ModelLoadError(
                "llama_cpp Python binding not installed. "
                "Install with: pip install clarify-prompt[llama]"
            ) from exc
        self.model_path = Path(model_path).expanduser()
        if not self.model_path.exists():
            raise ModelLoadError(f"model file not found: {self.model_path}")
        self._llm = Llama(
            model_path=str(self.model_path),
            n_gpu_layers=n_gpu_layers,
            n_ctx=ctx_size,
            verbose=False,
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        out = self._llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        try:
            content = out["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GenerationError(f"unexpected llama_cpp response shape: {exc}") from exc
        if not isinstance(content, str):
            raise GenerationError("llama_cpp response content is not text")
        return content


def _chatml_render(system_prompt: str, user_prompt: str) -> str:
    return (
        "<|im_start|>system\n"
        f"{system_prompt}"
        "<|im_end|>\n"
        "<|im_start|>user\n"
        f"{user_prompt}"
        "<|im_end|>\n"
        "<|im_start|>assistant\n"
    )

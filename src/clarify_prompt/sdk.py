"""Public API for programmatic use.

    from clarify_prompt import ClarifyEngine

    engine = ClarifyEngine(model="path/to/model.gguf")
    result = engine.rewrite("login sayfası yap", target="claude-code")
    print(result.text)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from clarify_prompt.config.schema import Config, ModelConfig, LlamaConfig, GenerateConfig
from clarify_prompt.engine.factory import make_engine
from clarify_prompt.engine.backend import InferenceBackend
from clarify_prompt.postproc.pipeline import postprocess
from clarify_prompt.prompts.selector import select_system_prompt

TargetProfile = Literal["claude-code", "chatgpt", "cursor", "generic"]


@dataclass(frozen=True)
class RewriteResult:
    text: str
    target: TargetProfile
    model_path: str | None


class ClarifyEngine:
    """Stateful wrapper around the inference pipeline.

    Loads the model once, reuses across calls.
    """

    def __init__(
        self,
        model: str | Path | None = None,
        backend: str = "llama",
        n_gpu_layers: int = 33,
        ctx_size: int = 4096,
    ) -> None:
        model_path = str(model) if model else os.environ.get("CLARIFY_PROMPT_MODEL_PATH")
        self._model_path = model_path
        cfg = Config(
            model=ModelConfig(path=model_path, backend=backend),
            llama=LlamaConfig(n_gpu_layers=n_gpu_layers, ctx_size=ctx_size),
        )
        self._engine: InferenceBackend = make_engine(cfg)
        self._gen_cfg = cfg.generate

    def rewrite(
        self,
        prompt: str,
        target: TargetProfile = "generic",
        explain: bool = False,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> RewriteResult:
        sys_prompt = select_system_prompt(target, explain=explain)
        raw = self._engine.generate(
            system_prompt=sys_prompt,
            user_prompt=prompt.strip(),
            max_new_tokens=max_tokens or self._gen_cfg.max_new_tokens,
            temperature=temperature if temperature is not None else self._gen_cfg.temperature,
            top_p=self._gen_cfg.top_p,
        )
        cleaned = postprocess(raw)
        return RewriteResult(text=cleaned, target=target, model_path=self._model_path)

    def batch_rewrite(
        self,
        prompts: list[str],
        target: TargetProfile = "generic",
    ) -> list[RewriteResult]:
        return [self.rewrite(p, target=target) for p in prompts]

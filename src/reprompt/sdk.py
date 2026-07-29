"""Public API for programmatic use.

from reprompt import RepromptEngine

engine = RepromptEngine(model="path/to/model.gguf")
result = engine.rewrite("login sayfası yap", target="claude-code")
print(result.text)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from reprompt.config.schema import BackendName, Config, LlamaConfig, ModelConfig
from reprompt.engine.backend import InferenceBackend
from reprompt.engine.factory import make_engine
from reprompt.postproc.pipeline import postprocess
from reprompt.prompts.selector import select_system_prompt
from reprompt.prompts.types import DetailLevel, TargetProfile, TaskProfile


@dataclass(frozen=True)
class RewriteResult:
    text: str
    target: TargetProfile
    model_path: str | None
    task: TaskProfile = "auto"
    detail: DetailLevel = "balanced"


class RepromptEngine:
    """Stateful wrapper around the inference pipeline.

    Loads the model once, reuses across calls.
    """

    def __init__(
        self,
        model: str | Path | None = None,
        backend: BackendName = "llama",
        n_gpu_layers: int = 33,
        ctx_size: int = 8192,
    ) -> None:
        model_path = str(model) if model else os.environ.get("REPROMPT_MODEL_PATH")
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
        task: TaskProfile = "auto",
        detail: DetailLevel = "balanced",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> RewriteResult:
        sys_prompt = select_system_prompt(target, explain=explain, task=task, detail=detail)
        raw = self._engine.generate(
            system_prompt=sys_prompt,
            user_prompt=prompt.strip(),
            max_new_tokens=max_tokens or self._gen_cfg.max_new_tokens,
            temperature=temperature if temperature is not None else self._gen_cfg.temperature,
            top_p=self._gen_cfg.top_p,
        )
        cleaned = postprocess(raw)
        return RewriteResult(
            text=cleaned,
            target=target,
            model_path=self._model_path,
            task=task,
            detail=detail,
        )

    def batch_rewrite(
        self,
        prompts: list[str],
        target: TargetProfile = "generic",
        task: TaskProfile = "auto",
        detail: DetailLevel = "balanced",
    ) -> list[RewriteResult]:
        return [self.rewrite(prompt, target=target, task=task, detail=detail) for prompt in prompts]

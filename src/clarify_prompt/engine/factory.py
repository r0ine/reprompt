"""Backend factory — picks the right engine based on config."""

from __future__ import annotations

from clarify_prompt.config.schema import Config
from clarify_prompt.engine.backend import InferenceBackend
from clarify_prompt.engine.llama import LlamaPyBackend, LlamaSubprocessBackend
from clarify_prompt.errors import ConfigError


def make_engine(cfg: Config) -> InferenceBackend:
    backend = cfg.model.backend
    if backend == "llama":
        return LlamaSubprocessBackend(
            model_path=cfg.model.path,
            cli_binary=cfg.llama.cli_binary,
            n_gpu_layers=cfg.llama.n_gpu_layers,
            ctx_size=cfg.llama.ctx_size,
        )
    if backend == "llama-py":
        return LlamaPyBackend(
            model_path=cfg.model.path,
            n_gpu_layers=cfg.llama.n_gpu_layers,
            ctx_size=cfg.llama.ctx_size,
        )
    raise ConfigError(f"unknown backend: {backend!r}")

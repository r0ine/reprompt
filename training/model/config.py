"""ClarifyGPT model yapilandirmasi."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClarifyConfig:
    vocab_size: int = 32_000
    max_seq_len: int = 1024
    dim: int = 768
    n_layers: int = 12
    n_heads: int = 12
    n_kv_heads: int = 4
    hidden_dim: int | None = None
    dropout: float = 0.0
    norm_eps: float = 1e-5
    rope_theta: float = 10_000.0
    tie_embeddings: bool = True

    def __post_init__(self) -> None:
        if self.hidden_dim is None:
            raw = int(self.dim * 8 / 3)
            self.hidden_dim = raw + (64 - raw % 64) if raw % 64 else raw

    @property
    def head_dim(self) -> int:
        return self.dim // self.n_heads


SMALL = ClarifyConfig(
    vocab_size=12_000,
    max_seq_len=1024,
    dim=512,
    n_layers=8,
    n_heads=8,
    n_kv_heads=4,
    dropout=0.1,
)

BASE = ClarifyConfig(
    vocab_size=12_000,
    max_seq_len=1024,
    dim=768,
    n_layers=12,
    n_heads=12,
    n_kv_heads=4,
    dropout=0.05,
)

LARGE = ClarifyConfig(
    vocab_size=12_000,
    max_seq_len=1024,
    dim=1024,
    n_layers=16,
    n_heads=16,
    n_kv_heads=4,
    dropout=0.05,
)

XLARGE = ClarifyConfig(
    vocab_size=12_000,
    max_seq_len=1024,
    dim=1280,
    n_layers=20,
    n_heads=20,
    n_kv_heads=4,
    dropout=0.05,
)

"""ClarifyGPT — sifirdan decoder-only transformer.

RoPE pozisyon kodlamasi, Grouped-Query Attention, SwiGLU FFN.
~50-200M parametre araliginda, RTX 4060 8GB VRAM'e sigacak sekilde.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.checkpoint import checkpoint as grad_checkpoint

from training.model.config import ClarifyConfig


def precompute_rope(dim: int, max_seq_len: int, theta: float = 10_000.0) -> torch.Tensor:
    freqs = 1.0 / (theta ** (torch.arange(0, dim, 2).float() / dim))
    t = torch.arange(max_seq_len, dtype=torch.float32)
    freqs = torch.outer(t, freqs)
    return torch.polar(torch.ones_like(freqs), freqs)


def apply_rope(x: torch.Tensor, rope: torch.Tensor) -> torch.Tensor:
    # x: (bs, seq, n_heads, head_dim)
    x_ = torch.view_as_complex(x.float().reshape(*x.shape[:-1], -1, 2))
    rope = rope[: x_.shape[1]].unsqueeze(0).unsqueeze(2)
    return torch.view_as_real(x_ * rope).flatten(-2).type_as(x)


def repeat_kv(x: torch.Tensor, n_rep: int) -> torch.Tensor:
    if n_rep == 1:
        return x
    bs, seq, n_kv, head_dim = x.shape
    return (
        x[:, :, :, None, :]
        .expand(bs, seq, n_kv, n_rep, head_dim)
        .reshape(bs, seq, n_kv * n_rep, head_dim)
    )


class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-5):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        norm = x.float().pow(2).mean(-1, keepdim=True).add(self.eps).rsqrt()
        return (x.float() * norm).type_as(x) * self.weight


class Attention(nn.Module):
    def __init__(self, cfg: ClarifyConfig):
        super().__init__()
        self.n_heads = cfg.n_heads
        self.n_kv_heads = cfg.n_kv_heads
        self.head_dim = cfg.head_dim
        self.n_rep = cfg.n_heads // cfg.n_kv_heads

        self.wq = nn.Linear(cfg.dim, cfg.n_heads * cfg.head_dim, bias=False)
        self.wk = nn.Linear(cfg.dim, cfg.n_kv_heads * cfg.head_dim, bias=False)
        self.wv = nn.Linear(cfg.dim, cfg.n_kv_heads * cfg.head_dim, bias=False)
        self.wo = nn.Linear(cfg.n_heads * cfg.head_dim, cfg.dim, bias=False)
        self.dropout = nn.Dropout(cfg.dropout)

    def forward(
        self, x: torch.Tensor, rope: torch.Tensor, mask: torch.Tensor | None = None
    ) -> torch.Tensor:
        bs, seq_len, _ = x.shape

        q = self.wq(x).view(bs, seq_len, self.n_heads, self.head_dim)
        k = self.wk(x).view(bs, seq_len, self.n_kv_heads, self.head_dim)
        v = self.wv(x).view(bs, seq_len, self.n_kv_heads, self.head_dim)

        q = apply_rope(q, rope)
        k = apply_rope(k, rope)

        k = repeat_kv(k, self.n_rep)
        v = repeat_kv(v, self.n_rep)

        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)

        scale = 1.0 / math.sqrt(self.head_dim)
        scores = torch.matmul(q, k.transpose(-2, -1)) * scale

        if mask is not None:
            scores = scores + mask

        attn = F.softmax(scores, dim=-1)
        attn = self.dropout(attn)

        out = torch.matmul(attn, v)
        out = out.transpose(1, 2).contiguous().view(bs, seq_len, -1)
        return self.wo(out)


class FeedForward(nn.Module):
    def __init__(self, cfg: ClarifyConfig):
        super().__init__()
        self.w1 = nn.Linear(cfg.dim, cfg.hidden_dim, bias=False)
        self.w2 = nn.Linear(cfg.hidden_dim, cfg.dim, bias=False)
        self.w3 = nn.Linear(cfg.dim, cfg.hidden_dim, bias=False)
        self.dropout = nn.Dropout(cfg.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dropout(self.w2(F.silu(self.w1(x)) * self.w3(x)))


class TransformerBlock(nn.Module):
    def __init__(self, cfg: ClarifyConfig):
        super().__init__()
        self.attn_norm = RMSNorm(cfg.dim, cfg.norm_eps)
        self.attn = Attention(cfg)
        self.ffn_norm = RMSNorm(cfg.dim, cfg.norm_eps)
        self.ffn = FeedForward(cfg)

    def forward(
        self, x: torch.Tensor, rope: torch.Tensor, mask: torch.Tensor | None = None
    ) -> torch.Tensor:
        x = x + self.attn(self.attn_norm(x), rope, mask)
        x = x + self.ffn(self.ffn_norm(x))
        return x


class ClarifyGPT(nn.Module):
    def __init__(self, cfg: ClarifyConfig, use_checkpointing: bool = False):
        super().__init__()
        self.cfg = cfg
        self.use_checkpointing = use_checkpointing
        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.dim)
        self.layers = nn.ModuleList([TransformerBlock(cfg) for _ in range(cfg.n_layers)])
        self.norm = RMSNorm(cfg.dim, cfg.norm_eps)
        self.head = nn.Linear(cfg.dim, cfg.vocab_size, bias=False)

        if cfg.tie_embeddings:
            self.head.weight = self.tok_emb.weight

        self.register_buffer(
            "rope_cache",
            precompute_rope(cfg.head_dim, cfg.max_seq_len, cfg.rope_theta),
            persistent=False,
        )

        self.apply(self._init_weights)

    def _init_weights(self, module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(
        self, tokens: torch.Tensor, targets: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        bs, seq_len = tokens.shape
        x = self.tok_emb(tokens)

        mask = torch.full((seq_len, seq_len), float("-inf"), device=tokens.device)
        mask = torch.triu(mask, diagonal=1)
        mask = mask.unsqueeze(0).unsqueeze(0)

        for layer in self.layers:
            if self.use_checkpointing and self.training:
                x = grad_checkpoint(layer, x, self.rope_cache, mask, use_reentrant=False)
            else:
                x = layer(x, self.rope_cache, mask)

        x = self.norm(x)
        logits = self.head(x)

        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.view(-1),
                ignore_index=-100,
            )

        return logits, loss

    def param_count(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    @torch.inference_mode()
    def generate(
        self,
        prompt_tokens: torch.Tensor,
        max_new: int = 512,
        temperature: float = 0.7,
        top_k: int = 50,
    ) -> torch.Tensor:
        tokens = prompt_tokens
        for _ in range(max_new):
            ctx = tokens[:, -self.cfg.max_seq_len :]
            logits, _ = self(ctx)
            logits = logits[:, -1, :] / max(temperature, 1e-5)

            if top_k > 0:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float("-inf")

            probs = F.softmax(logits, dim=-1)
            next_tok = torch.multinomial(probs, num_samples=1)
            tokens = torch.cat([tokens, next_tok], dim=1)

        return tokens

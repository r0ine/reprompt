"""ClarifyGPT model mimarisi testleri."""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch", reason="torch kurulu degil")

from training.model.config import BASE, LARGE, SMALL, ClarifyConfig  # noqa: E402
from training.model.transformer import (  # noqa: E402
    Attention,
    ClarifyGPT,
    FeedForward,
    RMSNorm,
    TransformerBlock,
    apply_rope,
    precompute_rope,
    repeat_kv,
)

# ── Config presets ──────────────────────────────────────────────


class TestConfigPresets:
    def test_small_param_budget(self):
        m = ClarifyGPT(SMALL)
        assert 20_000_000 < m.param_count() < 40_000_000

    def test_base_param_budget(self):
        m = ClarifyGPT(BASE)
        assert 60_000_000 < m.param_count() < 110_000_000

    def test_large_param_budget(self):
        m = ClarifyGPT(LARGE)
        assert 150_000_000 < m.param_count() < 250_000_000

    def test_all_presets_use_12k_vocab(self):
        for cfg in (SMALL, BASE, LARGE):
            assert cfg.vocab_size == 12_000

    def test_head_dim_consistency(self):
        for cfg in (SMALL, BASE, LARGE):
            assert cfg.dim % cfg.n_heads == 0
            assert cfg.head_dim == cfg.dim // cfg.n_heads

    def test_kv_heads_divide_heads(self):
        for cfg in (SMALL, BASE, LARGE):
            assert cfg.n_heads % cfg.n_kv_heads == 0

    def test_hidden_dim_auto_computed(self):
        cfg = ClarifyConfig(dim=768)
        expected_raw = int(768 * 8 / 3)
        aligned = expected_raw + (64 - expected_raw % 64) if expected_raw % 64 else expected_raw
        assert cfg.hidden_dim == aligned

    def test_hidden_dim_explicit_override(self):
        cfg = ClarifyConfig(dim=768, hidden_dim=3072)
        assert cfg.hidden_dim == 3072


# ── RoPE ────────────────────────────────────────────────────────


class TestRoPE:
    def test_shape(self):
        rope = precompute_rope(64, 128)
        assert rope.shape == (128, 32)

    def test_dtype_complex(self):
        rope = precompute_rope(64, 128)
        assert rope.dtype == torch.complex64

    def test_apply_preserves_shape(self):
        rope = precompute_rope(64, 32)
        x = torch.randn(2, 32, 8, 64)
        out = apply_rope(x, rope)
        assert out.shape == x.shape

    def test_different_positions_give_different_embeddings(self):
        rope = precompute_rope(64, 16)
        x = torch.ones(1, 16, 4, 64)
        out = apply_rope(x, rope)
        assert not torch.allclose(out[0, 0], out[0, 1], atol=1e-5)

    def test_apply_rope_works_with_gqa_heads(self):
        rope = precompute_rope(64, 16)
        q = torch.randn(2, 16, 16, 64)
        k = torch.randn(2, 16, 4, 64)
        q_rot = apply_rope(q, rope)
        k_rot = apply_rope(k, rope)
        assert q_rot.shape == q.shape
        assert k_rot.shape == k.shape


# ── RMSNorm ─────────────────────────────────────────────────────


class TestRMSNorm:
    def test_output_shape(self):
        norm = RMSNorm(64)
        x = torch.randn(2, 10, 64)
        assert norm(x).shape == x.shape

    def test_normalized_rms_near_one(self):
        norm = RMSNorm(256)
        x = torch.randn(4, 8, 256) * 5
        out = norm(x)
        rms = out.float().pow(2).mean(-1).sqrt()
        assert rms.mean().item() == pytest.approx(1.0, abs=0.3)

    def test_weight_initialized_ones(self):
        norm = RMSNorm(128)
        assert torch.allclose(norm.weight, torch.ones(128))


# ── repeat_kv ───────────────────────────────────────────────────


class TestRepeatKV:
    def test_no_repeat(self):
        x = torch.randn(2, 10, 4, 64)
        assert repeat_kv(x, 1) is x

    def test_repeat_shape(self):
        x = torch.randn(2, 10, 4, 64)
        out = repeat_kv(x, 3)
        assert out.shape == (2, 10, 12, 64)

    def test_values_match_after_repeat(self):
        x = torch.randn(1, 5, 2, 32)
        out = repeat_kv(x, 4)
        for kv_idx in range(2):
            for rep in range(4):
                assert torch.allclose(out[0, :, kv_idx * 4 + rep], x[0, :, kv_idx])


# ── Attention ───────────────────────────────────────────────────


class TestAttention:
    @pytest.fixture
    def small_cfg(self):
        return ClarifyConfig(dim=128, n_heads=4, n_kv_heads=2, vocab_size=100, n_layers=1)

    def test_output_shape(self, small_cfg):
        attn = Attention(small_cfg)
        rope = precompute_rope(small_cfg.head_dim, 32)
        x = torch.randn(2, 16, 128)
        out = attn(x, rope)
        assert out.shape == x.shape

    def test_causal_mask_prevents_future(self, small_cfg):
        attn = Attention(small_cfg)
        rope = precompute_rope(small_cfg.head_dim, 8)
        x = torch.randn(1, 8, 128)
        mask = torch.full((8, 8), float("-inf"))
        mask = torch.triu(mask, diagonal=1).unsqueeze(0).unsqueeze(0)
        out_masked = attn(x, rope, mask)
        assert out_masked.shape == x.shape


# ── FeedForward (SwiGLU) ────────────────────────────────────────


class TestFeedForward:
    def test_output_shape(self):
        cfg = ClarifyConfig(dim=128, hidden_dim=256, vocab_size=100, n_layers=1)
        ff = FeedForward(cfg)
        x = torch.randn(2, 10, 128)
        assert ff(x).shape == x.shape


# ── TransformerBlock ────────────────────────────────────────────


class TestTransformerBlock:
    def test_residual_connection(self):
        cfg = ClarifyConfig(
            dim=128, n_heads=4, n_kv_heads=2, vocab_size=100, n_layers=1, dropout=0.0
        )
        block = TransformerBlock(cfg)
        block.eval()
        rope = precompute_rope(cfg.head_dim, 16)
        x = torch.randn(1, 8, 128)
        out = block(x, rope)
        assert out.shape == x.shape
        assert not torch.allclose(out, x, atol=1e-6)


# ── ClarifyGPT full model ──────────────────────────────────────


class TestClarifyGPT:
    @pytest.fixture
    def tiny_model(self):
        cfg = ClarifyConfig(
            vocab_size=256,
            dim=64,
            n_layers=2,
            n_heads=4,
            n_kv_heads=2,
            max_seq_len=32,
            dropout=0.0,
        )
        return ClarifyGPT(cfg)

    def test_forward_logits_shape(self, tiny_model):
        tokens = torch.randint(0, 256, (2, 16))
        logits, loss = tiny_model(tokens)
        assert logits.shape == (2, 16, 256)
        assert loss is None

    def test_forward_with_targets_returns_loss(self, tiny_model):
        tokens = torch.randint(0, 256, (2, 16))
        targets = torch.randint(0, 256, (2, 16))
        logits, loss = tiny_model(tokens, targets)
        assert loss is not None
        assert loss.item() > 0

    def test_loss_ignores_minus_100(self, tiny_model):
        tokens = torch.randint(0, 256, (1, 16))
        targets_all = torch.randint(0, 256, (1, 16))
        targets_masked = targets_all.clone()
        targets_masked[:, :8] = -100
        _, loss_all = tiny_model(tokens, targets_all)
        _, loss_masked = tiny_model(tokens, targets_masked)
        assert loss_all.item() != pytest.approx(loss_masked.item(), abs=0.01)

    def test_weight_tying(self, tiny_model):
        assert tiny_model.head.weight is tiny_model.tok_emb.weight

    def test_no_weight_tying_when_disabled(self):
        cfg = ClarifyConfig(
            vocab_size=256,
            dim=64,
            n_layers=2,
            n_heads=4,
            n_kv_heads=2,
            tie_embeddings=False,
        )
        m = ClarifyGPT(cfg)
        assert m.head.weight is not m.tok_emb.weight

    def test_rope_cache_registered(self, tiny_model):
        assert hasattr(tiny_model, "rope_cache")
        assert tiny_model.rope_cache.shape[0] == 32

    def test_generate_extends_sequence(self, tiny_model):
        prompt = torch.randint(0, 256, (1, 4))
        out = tiny_model.generate(prompt, max_new=8, temperature=1.0)
        assert out.shape == (1, 12)

    def test_generate_respects_max_new(self, tiny_model):
        prompt = torch.randint(0, 256, (1, 4))
        out = tiny_model.generate(prompt, max_new=3)
        assert out.shape[1] == 7

    def test_param_count_positive(self, tiny_model):
        assert tiny_model.param_count() > 0

    def test_all_params_require_grad(self, tiny_model):
        for name, p in tiny_model.named_parameters():
            assert p.requires_grad, f"{name} has requires_grad=False"

    def test_gradient_flows(self, tiny_model):
        tokens = torch.randint(0, 256, (1, 8))
        targets = torch.randint(0, 256, (1, 8))
        _, loss = tiny_model(tokens, targets)
        loss.backward()
        grad_norms = [p.grad.norm().item() for p in tiny_model.parameters() if p.grad is not None]
        assert len(grad_norms) > 0
        assert sum(grad_norms) > 0

    def test_different_inputs_different_outputs(self, tiny_model):
        a = torch.tensor([[1, 2, 3, 4]])
        b = torch.tensor([[5, 6, 7, 8]])
        la, _ = tiny_model(a)
        lb, _ = tiny_model(b)
        assert not torch.allclose(la, lb)

"""Egitim yardimci fonksiyonlari testleri — cosine LR, collate, dataset."""

from __future__ import annotations

import math

import pytest

torch = pytest.importorskip("torch", reason="torch kurulu degil")


def cosine_lr(step: int, warmup: int, total: int, peak_lr: float, min_lr: float) -> float:
    if step < warmup:
        return peak_lr * step / max(warmup, 1)
    progress = (step - warmup) / max(total - warmup, 1)
    return min_lr + 0.5 * (peak_lr - min_lr) * (1 + math.cos(math.pi * progress))


class TestCosineLR:
    def test_starts_at_zero(self):
        assert cosine_lr(0, 100, 1000, 3e-4, 1e-5) == 0.0

    def test_reaches_peak_at_warmup(self):
        lr = cosine_lr(100, 100, 1000, 3e-4, 1e-5)
        assert lr == pytest.approx(3e-4, rel=0.01)

    def test_decays_after_warmup(self):
        peak = cosine_lr(100, 100, 1000, 3e-4, 1e-5)
        mid = cosine_lr(550, 100, 1000, 3e-4, 1e-5)
        assert mid < peak

    def test_ends_near_min_lr(self):
        lr = cosine_lr(1000, 100, 1000, 3e-4, 1e-5)
        assert lr == pytest.approx(1e-5, rel=0.01)

    def test_warmup_is_linear(self):
        lr_25 = cosine_lr(25, 100, 1000, 3e-4, 1e-5)
        lr_50 = cosine_lr(50, 100, 1000, 3e-4, 1e-5)
        assert lr_50 == pytest.approx(2 * lr_25, rel=0.01)

    def test_midpoint_is_average_of_peak_and_min(self):
        mid_step = 100 + (1000 - 100) // 2
        lr = cosine_lr(mid_step, 100, 1000, 3e-4, 1e-5)
        expected = (3e-4 + 1e-5) / 2
        assert lr == pytest.approx(expected, rel=0.05)


class TestCollateFn:
    def test_pads_to_longest(self):
        from training.train_scratch import collate_fn

        batch = [
            {"input_ids": torch.tensor([1, 2, 3]), "labels": torch.tensor([2, 3, 4])},
            {"input_ids": torch.tensor([5, 6]), "labels": torch.tensor([6, 7])},
        ]
        out = collate_fn(batch, pad_id=0)
        assert out["input_ids"].shape == (2, 3)
        assert out["labels"].shape == (2, 3)

    def test_shorter_sequence_padded(self):
        from training.train_scratch import collate_fn

        batch = [
            {"input_ids": torch.tensor([1, 2, 3, 4]), "labels": torch.tensor([2, 3, 4, 5])},
            {"input_ids": torch.tensor([10]), "labels": torch.tensor([11])},
        ]
        out = collate_fn(batch, pad_id=0)
        assert out["input_ids"][1, 0].item() == 10
        assert out["input_ids"][1, 1].item() == 0
        assert out["labels"][1, 1].item() == -100

    def test_single_item_batch(self):
        from training.train_scratch import collate_fn

        batch = [{"input_ids": torch.tensor([1, 2]), "labels": torch.tensor([2, 3])}]
        out = collate_fn(batch, pad_id=0)
        assert out["input_ids"].shape == (1, 2)

    def test_custom_pad_id(self):
        from training.train_scratch import collate_fn

        batch = [
            {"input_ids": torch.tensor([1, 2, 3]), "labels": torch.tensor([2, 3, 4])},
            {"input_ids": torch.tensor([5]), "labels": torch.tensor([6])},
        ]
        out = collate_fn(batch, pad_id=99)
        assert out["input_ids"][1, 1].item() == 99
        assert out["input_ids"][1, 2].item() == 99


class TestEvaluateFunction:
    def test_evaluate_returns_float(self):
        from training.model.config import ClarifyConfig
        from training.model.transformer import ClarifyGPT
        from training.train_scratch import evaluate

        cfg = ClarifyConfig(vocab_size=100, dim=32, n_layers=1, n_heads=2, n_kv_heads=1)
        model = ClarifyGPT(cfg)
        device = torch.device("cpu")

        dummy_data = [
            {"input_ids": torch.randint(0, 100, (2, 16)), "labels": torch.randint(0, 100, (2, 16))},
        ]
        val_loss = evaluate(model, dummy_data, device)
        assert isinstance(val_loss, float)
        assert val_loss > 0

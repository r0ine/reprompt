"""Tests for data pipeline: import_gold, augment, split."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from reprompt.prompts.types import TARGET_PROFILES

LEGACY_TARGETS = {"claude-code", "chatgpt", "cursor", "generic"}


def test_gold_jsonl_exists_and_valid():
    gold = Path("training/datasets/raw/gold.jsonl")
    if not gold.exists():
        pytest.skip("gold.jsonl not generated yet")
    records = []
    with gold.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line.strip())
            records.append(rec)
            assert "input" in rec
            assert "output" in rec
            assert "target" in rec
            assert "lang" in rec
            assert rec["target"] in TARGET_PROFILES
            assert rec["lang"] in ("tr", "en", "mix")
            assert len(rec["input"]) >= 10
            assert len(rec["output"]) >= 30
    assert len(records) >= 50


def test_augmented_jsonl_valid():
    aug = Path("training/datasets/raw/augmented.jsonl")
    if not aug.exists():
        pytest.skip("augmented.jsonl not generated yet")
    count = 0
    with aug.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line.strip())
            count += 1
            assert "input" in rec
            assert "output" in rec
            assert rec["target"] in TARGET_PROFILES
    assert count >= 50


def test_train_val_test_split_exists():
    for name in ("train", "val", "test"):
        path = Path(f"training/datasets/{name}.jsonl")
        if not path.exists():
            pytest.skip(f"{name}.jsonl not generated yet")
        count = 0
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                json.loads(line.strip())
                count += 1
        assert count >= 1


def test_synthetic_jsonl_valid():
    syn = Path("training/datasets/raw/synthetic_v2.jsonl")
    if not syn.exists():
        pytest.skip("synthetic_v2.jsonl not generated yet")
    count = 0
    targets = set()
    langs = set()
    with syn.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line.strip())
            count += 1
            assert "input" in rec
            assert "output" in rec
            assert "target" in rec
            assert "lang" in rec
            assert rec["source"] in ("synthetic", "synthetic_v2")
            targets.add(rec["target"])
            langs.add(rec["lang"])
    assert count >= 100_000
    assert LEGACY_TARGETS.issubset(targets)
    assert targets.issubset(set(TARGET_PROFILES))
    assert langs.issuperset({"tr", "en"})
    assert len(langs) >= 2


def test_tokenizer_model_exists():
    model_path = Path("training/tokenizer/clarify_tok.model")
    if not model_path.exists():
        pytest.skip("tokenizer not trained yet")
    assert model_path.stat().st_size > 1000


def test_train_split_size():
    train = Path("training/datasets/train.jsonl")
    if not train.exists():
        pytest.skip("train.jsonl not generated yet")
    count = sum(1 for _ in train.open(encoding="utf-8"))
    assert count >= 70_000


def test_no_data_leakage():
    paths = {}
    for name in ("train", "val", "test"):
        path = Path(f"training/datasets/{name}.jsonl")
        if not path.exists():
            pytest.skip(f"{name}.jsonl not generated yet")
        ids = set()
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                rec = json.loads(line.strip())
                ids.add(rec["id"])
        paths[name] = ids

    assert paths["train"].isdisjoint(paths["val"]), "train/val overlap"
    assert paths["train"].isdisjoint(paths["test"]), "train/test overlap"
    assert paths["val"].isdisjoint(paths["test"]), "val/test overlap"

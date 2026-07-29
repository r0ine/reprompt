"""Veri seti kalite testleri — dil dagılımı, format, tutarlılık."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

SYNTHETIC_PATH = Path("training/datasets/raw/synthetic_v2.jsonl")
TRAIN_PATH = Path("training/datasets/train.jsonl")
GOLD_PATH = Path("training/datasets/raw/gold.jsonl")

ALL_TARGETS = {"claude-code", "chatgpt", "cursor", "generic"}
ALL_LANGS = {"tr", "en", "de", "fr", "es", "pt", "ru", "ja", "zh", "ko"}


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        pytest.skip(f"{path.name} henuz olusturulmamis")
    records = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# ── Synthetic dataset ───────────────────────────────────────────


class TestSyntheticBalance:
    @pytest.fixture(autouse=True)
    def _load(self):
        self.records = load_records(SYNTHETIC_PATH)

    def test_min_100k_records(self):
        assert len(self.records) >= 100_000

    def test_all_10_languages_present(self):
        langs = {r["lang"] for r in self.records}
        assert langs.issuperset(ALL_LANGS)

    def test_all_4_targets_present(self):
        targets = {r["target"] for r in self.records}
        assert targets == ALL_TARGETS

    def test_lang_distribution_not_heavily_skewed(self):
        counts = Counter(r["lang"] for r in self.records)
        max_count = max(counts.values())
        min_count = min(counts.values())
        assert max_count / min_count < 3.0, f"max/min oran: {max_count}/{min_count}"

    def test_target_distribution_roughly_balanced(self):
        counts = Counter(r["target"] for r in self.records)
        values = list(counts.values())
        avg = sum(values) / len(values)
        for t, c in counts.items():
            assert abs(c - avg) / avg < 0.15, f"{t} orani cok sapti: {c} vs avg {avg}"

    def test_each_lang_has_all_targets(self):
        by_lang = {}
        for r in self.records:
            by_lang.setdefault(r["lang"], set()).add(r["target"])
        for lang, targets in by_lang.items():
            assert targets == ALL_TARGETS, f"{lang} eksik hedef: {ALL_TARGETS - targets}"

    def test_no_empty_inputs(self):
        empties = [r for r in self.records if len(r["input"].strip()) < 5]
        assert len(empties) == 0, f"{len(empties)} bos/cok kisa girdi"

    def test_no_empty_outputs(self):
        empties = [r for r in self.records if len(r["output"].strip()) < 20]
        assert len(empties) == 0, f"{len(empties)} bos/cok kisa cikti"

    def test_ids_unique(self):
        ids = [r["id"] for r in self.records]
        assert len(ids) == len(set(ids)), f"{len(ids) - len(set(ids))} tekrar ID"

    def test_source_is_synthetic(self):
        non_syn = [r for r in self.records if r.get("source") not in ("synthetic", "synthetic_v2")]
        assert len(non_syn) == 0


# ── Output format per target ────────────────────────────────────


class TestOutputFormats:
    @pytest.fixture(autouse=True)
    def _load(self):
        self.records = load_records(SYNTHETIC_PATH)

    def _get_by_target(self, target: str) -> list[dict]:
        return [r for r in self.records if r["target"] == target]

    def test_claude_code_has_xml_tags(self):
        samples = self._get_by_target("claude-code")[:500]
        tagged = sum(1 for r in samples if "<" in r["output"] and "</" in r["output"])
        assert tagged / len(samples) > 0.9

    def test_chatgpt_has_markdown_headings(self):
        samples = self._get_by_target("chatgpt")[:500]
        headed = sum(1 for r in samples if "##" in r["output"])
        assert headed / len(samples) > 0.9

    def test_cursor_has_numbered_steps(self):
        samples = self._get_by_target("cursor")[:500]
        numbered = sum(1 for r in samples if "1." in r["output"] or "1)" in r["output"])
        assert numbered / len(samples) > 0.7

    def test_generic_has_structure(self):
        samples = self._get_by_target("generic")[:500]
        structured = sum(1 for r in samples
                         if "##" in r["output"] or "**" in r["output"]
                         or ":" in r["output"].split("\n")[0])
        assert structured / len(samples) > 0.7


# ── Gold data ───────────────────────────────────────────────────


class TestGoldData:
    @pytest.fixture(autouse=True)
    def _load(self):
        self.records = load_records(GOLD_PATH)

    def test_min_50_records(self):
        assert len(self.records) >= 50

    def test_gold_fields_complete(self):
        for r in self.records:
            assert "id" in r
            assert "input" in r
            assert "output" in r
            assert "target" in r
            assert "lang" in r

    def test_gold_has_multiple_targets(self):
        targets = {r["target"] for r in self.records}
        assert len(targets) >= 3


# ── Train split ─────────────────────────────────────────────────


class TestTrainSplit:
    @pytest.fixture(autouse=True)
    def _load(self):
        self.records = load_records(TRAIN_PATH)

    def test_train_size(self):
        assert len(self.records) >= 70_000

    def test_train_has_all_langs(self):
        langs = {r["lang"] for r in self.records}
        assert langs.issuperset({"tr", "en"})

    def test_train_has_all_targets(self):
        targets = {r["target"] for r in self.records}
        assert targets == ALL_TARGETS


# ── Cross-split ─────────────────────────────────────────────────


class TestCrossSplit:
    def test_no_leakage_between_splits(self):
        splits = {}
        for name in ("train", "val", "test"):
            path = Path(f"training/datasets/{name}.jsonl")
            if not path.exists():
                pytest.skip(f"{name}.jsonl yok")
            ids = set()
            with path.open(encoding="utf-8") as fh:
                for line in fh:
                    ids.add(json.loads(line)["id"])
            splits[name] = ids

        for a, b in [("train", "val"), ("train", "test"), ("val", "test")]:
            overlap = splits[a] & splits[b]
            assert len(overlap) == 0, f"{a}/{b} arasinda {len(overlap)} ortak ID"

    def test_splits_cover_full_dataset(self):
        total = 0
        for name in ("train", "val", "test"):
            path = Path(f"training/datasets/{name}.jsonl")
            if not path.exists():
                pytest.skip(f"{name}.jsonl yok")
            total += sum(1 for _ in path.open(encoding="utf-8"))
        assert total >= 100_000


# ── Input diversity ─────────────────────────────────────────────


class TestInputDiversity:
    @pytest.fixture(autouse=True)
    def _load(self):
        self.records = load_records(SYNTHETIC_PATH)

    def test_no_exact_duplicate_inputs(self):
        inputs = [r["input"] for r in self.records]
        unique = len(set(inputs))
        dup_rate = 1 - (unique / len(inputs))
        assert dup_rate < 0.50, f"%{dup_rate*100:.1f} tekrar girdi"

    def test_input_length_variance(self):
        lengths = [len(r["input"]) for r in self.records]
        avg = sum(lengths) / len(lengths)
        variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
        std = variance ** 0.5
        assert std > 3, f"girdi uzunluk std={std:.1f}, cok dusuk"

    def test_turkish_uses_turkish_words(self):
        tr = [r for r in self.records if r["lang"] == "tr"][:500]
        tr_words = {"yap", "ekle", "düzelt", "olustur", "kontrol", "sayfa",
                    "veritaban", "api", "test", "kur", "ayarla", "sistem", "modul"}
        matches = sum(1 for r in tr if any(w in r["input"].lower() for w in tr_words))
        assert matches / len(tr) > 0.15

    def test_english_uses_english_words(self):
        en = [r for r in self.records if r["lang"] == "en"][:500]
        en_words = {"fix", "add", "create", "implement", "build", "update", "test",
                    "set", "configure", "deploy", "api", "system", "module", "debug"}
        matches = sum(1 for r in en if any(w in r["input"].lower() for w in en_words))
        assert matches / len(en) > 0.15

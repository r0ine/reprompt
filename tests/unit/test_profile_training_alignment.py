from __future__ import annotations

import pytest

from reprompt.prompts.types import TARGET_PROFILES
from training.data.augment import CONVERTERS
from training.data.generate_v2 import FORMATTERS


def test_training_generators_cover_every_runtime_target() -> None:
    expected_targets = set(TARGET_PROFILES)

    assert set(CONVERTERS) == expected_targets
    assert set(FORMATTERS) == expected_targets


def test_llm_seed_rules_cover_every_runtime_target() -> None:
    pytest.importorskip("requests", reason="training bagimliliklari kurulu degil")
    from training.data.generate_llm_seeds import TARGET_RULES

    assert set(TARGET_RULES) == set(TARGET_PROFILES)


def test_tokenizer_declares_every_target_token() -> None:
    pytest.importorskip("sentencepiece", reason="sentencepiece kurulu degil")
    from training.tokenizer.train_tokenizer import SPECIAL_TOKENS

    for target in TARGET_PROFILES:
        assert f"<|{target}|>" in SPECIAL_TOKENS

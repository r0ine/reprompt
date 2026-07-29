"""Evaluation fonksiyonlari testleri — structure_score, length_ratio.

evaluate.py torch bagimliligi nedeniyle dogrudan import edilemiyor.
Fonksiyonlar burada bagimsiz olarak test ediliyor.
"""

from __future__ import annotations

import pytest


def structure_score(text: str, target: str) -> float:
    score = 0.0
    if target == "claude-code":
        tags = ["<task>", "<context>", "<constraints>", "<acceptance>"]
        found = sum(1 for t in tags if t in text)
        score = found / len(tags)
    elif target == "chatgpt":
        headings = ["## Hedef", "## Goal", "## Baglam", "## Context",
                     "## Kisitlar", "## Constraints"]
        found = sum(1 for h in headings if h in text)
        score = min(found / 3, 1.0)
    elif target == "cursor":
        has_numbered = any(f"{i}." in text for i in range(1, 6))
        has_donot = "Do not" in text or "not:" in text
        score = (0.5 if has_numbered else 0) + (0.5 if has_donot else 0)
    elif target == "generic":
        headings = ["## Hedef", "## Goal", "## Adimlar", "## Steps",
                     "## Kabul", "## Acceptance"]
        found = sum(1 for h in headings if h in text)
        score = min(found / 3, 1.0)
    return score


def length_ratio(generated: str, reference: str) -> float:
    if not reference:
        return 0.0
    ratio = len(generated) / len(reference)
    if 0.5 <= ratio <= 2.0:
        return 1.0
    elif 0.25 <= ratio <= 3.0:
        return 0.5
    return 0.0


class TestStructureScoreClaude:
    def test_all_tags_present(self):
        text = "<task>X</task>\n<context>Y</context>\n<constraints>Z</constraints>\n<acceptance>W</acceptance>"
        assert structure_score(text, "claude-code") == 1.0

    def test_half_tags(self):
        text = "<task>X</task>\n<context>Y</context>"
        assert structure_score(text, "claude-code") == 0.5

    def test_no_tags(self):
        text = "just plain text with no XML"
        assert structure_score(text, "claude-code") == 0.0

    def test_three_of_four(self):
        text = "<task>X</task>\n<context>Y</context>\n<constraints>Z</constraints>"
        assert structure_score(text, "claude-code") == 0.75


class TestStructureScoreChatGPT:
    def test_three_headings(self):
        text = "## Goal\nSomething\n## Context\nSome\n## Constraints\nStuff"
        assert structure_score(text, "chatgpt") == 1.0

    def test_turkish_headings(self):
        text = "## Hedef\nBir sey\n## Baglam\nBilgi\n## Kisitlar\nKural"
        assert structure_score(text, "chatgpt") == 1.0

    def test_no_headings(self):
        text = "plain text without markdown"
        assert structure_score(text, "chatgpt") == 0.0


class TestStructureScoreCursor:
    def test_numbered_and_donot(self):
        text = "1. First step\n2. Second step\nDo not break things"
        assert structure_score(text, "cursor") == 1.0

    def test_only_numbered(self):
        text = "1. Step one\n2. Step two"
        assert structure_score(text, "cursor") == 0.5

    def test_only_donot(self):
        text = "Do not modify the database"
        assert structure_score(text, "cursor") == 0.5

    def test_plain_text(self):
        text = "just do the thing"
        assert structure_score(text, "cursor") == 0.0


class TestStructureScoreGeneric:
    def test_with_headings(self):
        text = "## Goal\nX\n## Steps\nY\n## Acceptance\nZ"
        assert structure_score(text, "generic") == 1.0

    def test_turkish_headings(self):
        text = "## Hedef\nX\n## Adimlar\nY\n## Kabul\nZ"
        assert structure_score(text, "generic") == 1.0


class TestLengthRatio:
    def test_equal_length(self):
        assert length_ratio("abcde", "abcde") == 1.0

    def test_half_length(self):
        assert length_ratio("abc", "abcdef") == 1.0

    def test_double_length(self):
        assert length_ratio("a" * 200, "a" * 100) == 1.0

    def test_too_short(self):
        assert length_ratio("a" * 30, "a" * 100) == 0.5

    def test_way_too_short(self):
        assert length_ratio("a", "a" * 1000) == 0.0

    def test_way_too_long(self):
        assert length_ratio("a" * 10000, "a" * 100) == 0.0

    def test_empty_reference(self):
        assert length_ratio("abc", "") == 0.0

    def test_empty_both(self):
        assert length_ratio("", "") == 0.0

    def test_boundary_0_5_ratio(self):
        assert length_ratio("a" * 50, "a" * 100) == 1.0

    def test_boundary_2_0_ratio(self):
        assert length_ratio("a" * 200, "a" * 100) == 1.0

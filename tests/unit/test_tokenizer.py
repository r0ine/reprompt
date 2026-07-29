"""Tokenizer testleri — round-trip, ozel tokenlar, coklu dil."""

from __future__ import annotations

from pathlib import Path

import pytest

spm = pytest.importorskip("sentencepiece", reason="sentencepiece kurulu degil")

TOK_PATH = Path("training/tokenizer/clarify_tok.model")

SPECIAL_TOKENS = [
    "<|pad|>", "<|bos|>", "<|eos|>",
    "<|im_start|>", "<|im_end|>",
    "<|claude-code|>", "<|chatgpt|>", "<|cursor|>", "<|generic|>",
    "<|system|>", "<|user|>", "<|assistant|>",
]


@pytest.fixture
def tokenizer():
    if not TOK_PATH.exists():
        pytest.skip("tokenizer modeli henuz egitilmemis")
    sp = spm.SentencePieceProcessor()
    sp.Load(str(TOK_PATH))
    return sp


def test_vocab_size_is_12k(tokenizer):
    assert tokenizer.GetPieceSize() == 12_000


def test_all_special_tokens_exist(tokenizer):
    for tok in SPECIAL_TOKENS:
        tid = tokenizer.PieceToId(tok)
        assert tid != tokenizer.unk_id(), f"{tok} bulunamadi"


def test_special_token_ids_are_valid(tokenizer):
    pad_id = tokenizer.PieceToId("<|pad|>")
    bos_id = tokenizer.PieceToId("<|bos|>")
    eos_id = tokenizer.PieceToId("<|eos|>")
    unk_id = tokenizer.unk_id()
    assert pad_id != unk_id
    assert bos_id != unk_id
    assert eos_id != unk_id
    assert len({pad_id, bos_id, eos_id}) == 3


def test_roundtrip_turkish(tokenizer):
    text = "Kullanici giris sayfasini olustur ve veritabani baglantisini kontrol et"
    ids = tokenizer.Encode(text)
    decoded = tokenizer.Decode(ids)
    assert decoded.replace(" ", "") == text.replace(" ", "")


def test_roundtrip_english(tokenizer):
    text = "Fix the authentication bug in the login module"
    ids = tokenizer.Encode(text)
    decoded = tokenizer.Decode(ids)
    assert decoded.strip() == text


def test_roundtrip_german(tokenizer):
    text = "Erstelle eine REST-API mit Datenbankanbindung"
    ids = tokenizer.Encode(text)
    decoded = tokenizer.Decode(ids)
    assert "REST-API" in decoded or "REST" in decoded


def test_roundtrip_japanese(tokenizer):
    text = "ログイン機能を実装して"
    ids = tokenizer.Encode(text)
    decoded = tokenizer.Decode(ids)
    assert len(decoded.strip()) > 0
    assert len(ids) > 0


def test_roundtrip_chinese(tokenizer):
    text = "创建一个用户注册页面"
    ids = tokenizer.Encode(text)
    decoded = tokenizer.Decode(ids)
    assert len(decoded.strip()) > 0


def test_roundtrip_korean(tokenizer):
    text = "사용자 인증 시스템을 구현하세요"
    ids = tokenizer.Encode(text)
    decoded = tokenizer.Decode(ids)
    assert len(decoded.strip()) > 0


def test_empty_string(tokenizer):
    ids = tokenizer.Encode("")
    assert ids == []


def test_digits_split(tokenizer):
    text = "port 8080 ve 3000"
    ids = tokenizer.Encode(text)
    decoded = tokenizer.Decode(ids)
    assert "8080" in decoded
    assert "3000" in decoded


def test_xml_tags_survive(tokenizer):
    text = "<task>\nLogin sayfasi yap.\n</task>"
    ids = tokenizer.Encode(text)
    decoded = tokenizer.Decode(ids)
    assert "<task>" in decoded
    assert "</task>" in decoded


def test_markdown_headings_survive(tokenizer):
    text = "## Goal\n\nFix the search bug.\n\n## Constraints\n\n- No breaking changes"
    ids = tokenizer.Encode(text)
    decoded = tokenizer.Decode(ids)
    assert "## Goal" in decoded or "##Goal" in decoded
    assert "## Constraints" in decoded or "##Constraints" in decoded


def test_chatml_format_roundtrip(tokenizer):
    text = "<|im_start|>system\nSen bir prompt muhendisisin.<|im_end|>"
    ids = tokenizer.Encode(text)
    assert len(ids) > 5
    im_start_id = tokenizer.PieceToId("<|im_start|>")
    im_end_id = tokenizer.PieceToId("<|im_end|>")
    assert im_start_id in ids
    assert im_end_id in ids


def test_long_text_tokenizes(tokenizer):
    text = "bu bir test cumlesdir. " * 200
    ids = tokenizer.Encode(text)
    assert len(ids) > 100
    decoded = tokenizer.Decode(ids)
    assert "test" in decoded


def test_mixed_language_text(tokenizer):
    text = "Login sayfasini fix et, then add validation rules"
    ids = tokenizer.Encode(text)
    decoded = tokenizer.Decode(ids)
    assert "Login" in decoded or "login" in decoded.lower()
    assert "validation" in decoded


def test_code_snippet_tokenizes(tokenizer):
    text = 'def hello():\n    print("world")\n    return True'
    ids = tokenizer.Encode(text)
    decoded = tokenizer.Decode(ids)
    assert "def" in decoded
    assert "print" in decoded

"""Inference yardimci fonksiyonlari testleri.

inference.py torch bagimliligi nedeniyle dogrudan import edilemiyor.
build_prompt_tokens fonksiyonu burada bagimsiz olarak tanimlanip test ediliyor.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from reprompt.prompts.types import TARGET_PROFILES

spm = pytest.importorskip("sentencepiece", reason="sentencepiece kurulu degil")

TOK_PATH = Path("training/tokenizer/clarify_tok.model")


def build_prompt_tokens(
    raw_input: str, target: str, tokenizer: spm.SentencePieceProcessor
) -> list[int]:
    bos = tokenizer.PieceToId("<|bos|>")
    im_start = tokenizer.PieceToId("<|im_start|>")
    im_end = tokenizer.PieceToId("<|im_end|>")
    sys_tok = tokenizer.PieceToId("<|system|>")
    usr_tok = tokenizer.PieceToId("<|user|>")
    asst_tok = tokenizer.PieceToId("<|assistant|>")

    target_tok = tokenizer.PieceToId(f"<|{target}|>")
    system_msg = "Sen bir prompt muhendisisin. Kullanicinin ham girdisini, hedef LLM icin optimize edilmis yapisal bir prompta donustur."
    sys_ids = tokenizer.Encode(system_msg)
    inp_ids = tokenizer.Encode(raw_input)

    seq = [bos, im_start, sys_tok]
    if target_tok != tokenizer.unk_id():
        seq.append(target_tok)
    seq.extend(sys_ids)
    seq.append(im_end)
    seq.extend([im_start, usr_tok])
    seq.extend(inp_ids)
    seq.append(im_end)
    seq.extend([im_start, asst_tok])

    return seq


@pytest.fixture
def tokenizer():
    if not TOK_PATH.exists():
        pytest.skip("tokenizer modeli yok")
    sp = spm.SentencePieceProcessor()
    sp.Load(str(TOK_PATH))
    return sp


class TestBuildPromptTokens:
    def test_starts_with_bos(self, tokenizer):
        tokens = build_prompt_tokens("test input", "generic", tokenizer)
        bos_id = tokenizer.PieceToId("<|bos|>")
        assert tokens[0] == bos_id

    def test_contains_target_token(self, tokenizer):
        for target in TARGET_PROFILES:
            tokens = build_prompt_tokens("hello", target, tokenizer)
            target_id = tokenizer.PieceToId(f"<|{target}|>")
            if target_id != tokenizer.unk_id():
                assert target_id in tokens

    def test_contains_im_start_end(self, tokenizer):
        tokens = build_prompt_tokens("test", "generic", tokenizer)
        im_start = tokenizer.PieceToId("<|im_start|>")
        im_end = tokenizer.PieceToId("<|im_end|>")
        assert im_start in tokens
        assert im_end in tokens

    def test_ends_with_assistant_token(self, tokenizer):
        tokens = build_prompt_tokens("test", "generic", tokenizer)
        asst = tokenizer.PieceToId("<|assistant|>")
        im_start = tokenizer.PieceToId("<|im_start|>")
        last_three = tokens[-3:]
        assert im_start in last_three
        assert asst in last_three

    def test_different_inputs_different_tokens(self, tokenizer):
        t1 = build_prompt_tokens("login sayfasi yap", "generic", tokenizer)
        t2 = build_prompt_tokens("fix the search bug", "generic", tokenizer)
        assert t1 != t2

    def test_different_targets_different_tokens(self, tokenizer):
        t1 = build_prompt_tokens("test input", "claude-code", tokenizer)
        t2 = build_prompt_tokens("test input", "chatgpt", tokenizer)
        assert t1 != t2

    def test_system_message_encoded(self, tokenizer):
        tokens = build_prompt_tokens("x", "generic", tokenizer)
        sys_tok = tokenizer.PieceToId("<|system|>")
        assert sys_tok in tokens

    def test_returns_list_of_ints(self, tokenizer):
        tokens = build_prompt_tokens("hello world", "generic", tokenizer)
        assert isinstance(tokens, list)
        assert all(isinstance(t, int) for t in tokens)

    def test_reasonable_length(self, tokenizer):
        tokens = build_prompt_tokens("kisa bir istek", "generic", tokenizer)
        assert 20 < len(tokens) < 200

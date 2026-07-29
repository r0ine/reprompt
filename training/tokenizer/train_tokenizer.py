"""SentencePiece BPE tokenizer egitimi.

Sentetik veri setindeki tum metinlerden ozel tokenizer egitir.
Ozel tokenlar: <|pad|>, <|bos|>, <|eos|>, <|im_start|>, <|im_end|>
ve kayitli hedef profil tokenlari.

Kullanim:
    python -m training.tokenizer.train_tokenizer --vocab-size 32000
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import click
import sentencepiece as spm
from rich.console import Console

from reprompt.prompts.types import TARGET_PROFILES

console = Console()

RAW_DIR = Path("training/datasets/raw")
OUT_DIR = Path("training/tokenizer")

SPECIAL_TOKENS = (
    [
        "<|pad|>",
        "<|bos|>",
        "<|eos|>",
        "<|im_start|>",
        "<|im_end|>",
    ]
    + [f"<|{target}|>" for target in TARGET_PROFILES]
    + [
        "<|system|>",
        "<|user|>",
        "<|assistant|>",
    ]
)


@click.command()
@click.option("--vocab-size", "-v", default=32_000, help="Sozluk buyuklugu")
def main(vocab_size: int) -> None:
    corpus_lines = []
    for jl in sorted(RAW_DIR.glob("*.jsonl")):
        console.print(f"  Okunuyor: {jl.name}")
        with jl.open(encoding="utf-8") as fh:
            for line in fh:
                rec = json.loads(line)
                corpus_lines.append(rec["input"])
                corpus_lines.append(rec["output"])

    console.print(f"  Toplam metin parcasi: {len(corpus_lines):,}")

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8",
    ) as corpus_file:
        for text in corpus_lines:
            corpus_file.write(text + "\n")
        corpus_path = Path(corpus_file.name)

    model_prefix = str(OUT_DIR / "clarify_tok")

    try:
        spm.SentencePieceTrainer.Train(
            input=str(corpus_path),
            model_prefix=model_prefix,
            vocab_size=vocab_size,
            model_type="bpe",
            character_coverage=0.9999,
            num_threads=8,
            split_digits=True,
            byte_fallback=True,
            allow_whitespace_only_pieces=True,
            normalization_rule_name="identity",
            user_defined_symbols=SPECIAL_TOKENS,
            pad_id=0,
            bos_id=1,
            eos_id=2,
            unk_id=3,
        )
    finally:
        corpus_path.unlink(missing_ok=True)

    console.print(f"[green]Tokenizer egitildi: {model_prefix}.model ({vocab_size} token)[/green]")

    sp = spm.SentencePieceProcessor()
    sp.Load(f"{model_prefix}.model")

    test_inputs = [
        "login sayfasi yap",
        "fix the shopping cart bug",
        "<|im_start|>system\nSen bir prompt muhendisisin.<|im_end|>",
    ]
    for text in test_inputs:
        ids = sp.Encode(text)
        decoded = sp.Decode(ids)
        console.print(f"  [{len(ids)} token] {text[:50]} -> {decoded[:50]}")


if __name__ == "__main__":
    main()

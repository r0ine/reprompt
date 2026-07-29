"""Print token-length histograms for the split JSONL files."""

from __future__ import annotations

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()

FILES = [
    Path("training/datasets/train.jsonl"),
    Path("training/datasets/val.jsonl"),
    Path("training/datasets/test.jsonl"),
]


@click.command()
@click.option("--tokenizer", default="unsloth/Qwen2.5-7B-Instruct-bnb-4bit", show_default=True)
def cli(tokenizer: str) -> None:
    run(tokenizer)


def run(tokenizer: str = "unsloth/Qwen2.5-7B-Instruct-bnb-4bit") -> None:
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(tokenizer)
    table = Table(title="Token length stats")
    table.add_column("file")
    table.add_column("count")
    table.add_column("input p50")
    table.add_column("input p95")
    table.add_column("input max")
    table.add_column("output p50")
    table.add_column("output p95")
    table.add_column("output max")

    for path in FILES:
        if not path.exists():
            continue
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        in_lens = sorted(len(tok.encode(r["input"])) for r in rows)
        out_lens = sorted(len(tok.encode(r["output"])) for r in rows)
        if not in_lens:
            continue
        p50 = lambda xs: xs[len(xs) // 2]  # noqa: E731
        p95 = lambda xs: xs[int(len(xs) * 0.95)]  # noqa: E731
        table.add_row(
            path.name,
            str(len(rows)),
            str(p50(in_lens)),
            str(p95(in_lens)),
            str(in_lens[-1]),
            str(p50(out_lens)),
            str(p95(out_lens)),
            str(out_lens[-1]),
        )

    console.print(table)


if __name__ == "__main__":
    cli()

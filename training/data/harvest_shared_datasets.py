"""Sample raw user prompts from public instruction datasets on HF Hub."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import click
from rich.console import Console

from training.data.schema import Record, RecordMeta

console = Console()

OUT_PATH = Path("training/datasets/raw/shared.jsonl")

DEFAULT_SOURCES = [
    ("anon8231489123/ShareGPT_Vicuna_unfiltered", "train", 400),
    ("yahma/alpaca-cleaned", "train", 200),
    ("OpenAssistant/oasst1", "train", 200),
]


@click.command()
@click.option("--limit-per-source", type=int, default=None, help="Override sample count per source")
def cli(limit_per_source: int | None) -> None:
    run(limit_per_source)


def run(limit_per_source: int | None = None) -> None:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit("The `datasets` package is required. `pip install -e ./training`") from exc

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with OUT_PATH.open("w", encoding="utf-8") as fh:
        for name, split, count in DEFAULT_SOURCES:
            take = limit_per_source or count
            console.print(f"[cyan]streaming[/cyan] {name} split={split} take={take}")
            try:
                ds = load_dataset(name, split=split, streaming=True)
            except Exception as exc:  # noqa: BLE001
                console.print(f"[yellow]skip {name}: {exc}[/yellow]")
                continue
            picked = 0
            for row in ds:
                text = _extract_user_text(row)
                if not text or len(text) < 30 or len(text) > 1500:
                    continue
                rec = Record(
                    id=f"shared_{written:05d}",
                    source="shared",
                    target="generic",
                    lang="en",
                    input=text,
                    output="[TO BE DISTILLED]" + " " * 40,
                    meta=RecordMeta(
                        notes=name,
                        created_at=datetime.now(timezone.utc),
                    ),
                )
                fh.write(json.dumps(rec.to_jsonl_dict(), ensure_ascii=False) + "\n")
                written += 1
                picked += 1
                if picked >= take:
                    break
    console.print(f"[green]{written} shared ornek yazildi -> {OUT_PATH}[/green]")


def _extract_user_text(row: dict) -> str:
    for key in ("instruction", "prompt", "text", "input"):
        val = row.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    if isinstance(row.get("conversations"), list):
        for turn in row["conversations"]:
            if isinstance(turn, dict) and turn.get("from") in {"human", "user"}:
                return str(turn.get("value", "")).strip()
    if isinstance(row.get("messages"), list):
        for turn in row["messages"]:
            if isinstance(turn, dict) and turn.get("role") == "user":
                return str(turn.get("content", "")).strip()
    return ""


if __name__ == "__main__":
    cli()

"""Convert docs/gold_examples.md into JSONL records for the test set."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console

from training.data.schema import Record, RecordMeta

console = Console()

GOLD_MD = Path("docs/gold_examples.md")
OUT_PATH = Path("training/datasets/raw/gold.jsonl")

_ENTRY = re.compile(
    r"###\s+(?P<id>gold_\d+)\s*\|\s*target:\s*(?P<target>\S+)\s*\|\s*lang:\s*(?P<lang>\S+)\s*\n+"
    r"\*\*Input:\*\*\s*\n```[^\n]*\n(?P<input>.*?)\n```\s*\n+"
    r"\*\*Output:\*\*\s*\n```[^\n]*\n(?P<output>.*?)\n```",
    re.DOTALL,
)


def run() -> None:
    if not GOLD_MD.exists():
        console.print(f"[yellow]{GOLD_MD} yok — boş atlanıyor.[/yellow]")
        return
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    entries = list(_ENTRY.finditer(GOLD_MD.read_text(encoding="utf-8")))
    if not entries:
        console.print(f"[yellow]{GOLD_MD} icinde beklenen formatta ornek yok.[/yellow]")
        return
    written = 0
    with OUT_PATH.open("w", encoding="utf-8") as fh:
        for match in entries:
            rec = Record(
                id=match.group("id"),
                source="gold",
                target=match.group("target"),  # type: ignore[arg-type]
                lang=match.group("lang"),  # type: ignore[arg-type]
                input=match.group("input").strip(),
                output=match.group("output").strip(),
                meta=RecordMeta(
                    reviewed_by="kemal",
                    created_at=datetime.now(timezone.utc),
                ),
            )
            fh.write(json.dumps(rec.to_jsonl_dict(), ensure_ascii=False) + "\n")
            written += 1
    console.print(f"[green]{written} gold ornek yazildi -> {OUT_PATH}[/green]")


if __name__ == "__main__":
    run()

"""Combine all raw JSONL sources into one, drop near-duplicates by MinHash."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

console = Console()

SOURCES = [
    Path("training/datasets/raw/gold.jsonl"),
    Path("training/datasets/raw/transcripts.jsonl"),
    Path("training/datasets/raw/shared.jsonl"),
    Path("training/datasets/raw/distilled.jsonl"),
]
OUT_PATH = Path("training/datasets/raw/merged.jsonl")


def run(similarity_threshold: float = 0.85) -> None:
    try:
        from datasketch import MinHash, MinHashLSH
    except ImportError as exc:
        raise SystemExit("`pip install datasketch`") from exc

    records: list[dict] = []
    for path in SOURCES:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    console.print(f"[cyan]{len(records)} ham kayit yuklendi[/cyan]")

    lsh = MinHashLSH(threshold=similarity_threshold, num_perm=128)
    kept: list[dict] = []
    dropped = 0
    for rec in records:
        text = rec.get("input", "") + " " + rec.get("output", "")
        mh = MinHash(num_perm=128)
        for tok in text.lower().split():
            mh.update(tok.encode("utf-8"))
        if lsh.query(mh):
            dropped += 1
            continue
        lsh.insert(rec["id"], mh)
        kept.append(rec)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as fh:
        for rec in kept:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    console.print(f"[green]{len(kept)} tekil kayit, {dropped} yakin-duplicate atildi[/green]")
    console.print(f"[green]-> {OUT_PATH}[/green]")


if __name__ == "__main__":
    run()

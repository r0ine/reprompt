"""Split merged.jsonl into train/val/test. Gold records go to test only."""

from __future__ import annotations

import json
import random
from pathlib import Path

from rich.console import Console

console = Console()

MERGED = Path("training/datasets/raw/merged.jsonl")
TRAIN = Path("training/datasets/train.jsonl")
VAL = Path("training/datasets/val.jsonl")
TEST = Path("training/datasets/test.jsonl")

SEED = 3407
VAL_RATIO = 0.10
TEST_RATIO = 0.10


def run() -> None:
    if not MERGED.exists():
        raise SystemExit(f"{MERGED} yok. Once merge_dedup calistir.")
    records = [json.loads(line) for line in MERGED.read_text(encoding="utf-8").splitlines() if line]
    console.print(f"[cyan]{len(records)} kayit okundu[/cyan]")

    gold = [r for r in records if r.get("source") == "gold"]
    non_gold = [r for r in records if r.get("source") != "gold"]

    rng = random.Random(SEED)
    rng.shuffle(non_gold)

    n_val = int(len(non_gold) * VAL_RATIO)
    n_test_extra = max(0, int(len(non_gold) * TEST_RATIO) - len(gold))
    val = non_gold[:n_val]
    test_extra = non_gold[n_val : n_val + n_test_extra]
    train = non_gold[n_val + n_test_extra :]
    test = gold + test_extra

    _write(TRAIN, train)
    _write(VAL, val)
    _write(TEST, test)

    console.print(f"[green]train={len(train)}, val={len(val)}, test={len(test)}[/green]")


def _write(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    run()

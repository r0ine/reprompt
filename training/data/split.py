"""Split merged JSONL into train/val/test sets."""

from __future__ import annotations

import json
import random
from pathlib import Path

from rich.console import Console

console = Console()

RAW_DIR = Path("training/datasets/raw")
OUT_DIR = Path("training/datasets")

TRAIN_RATIO = 0.80
VAL_RATIO = 0.10


def run(seed: int = 3407) -> None:
    all_records: list[dict] = []
    for jsonl in sorted(RAW_DIR.glob("*.jsonl")):
        with jsonl.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    all_records.append(json.loads(line))

    if not all_records:
        console.print("[yellow]raw/ altinda JSONL dosyasi yok — atlanıyor.[/yellow]")
        return

    seen_ids: set[str] = set()
    unique: list[dict] = []
    for rec in all_records:
        rid = rec.get("id", "")
        if rid and rid in seen_ids:
            continue
        seen_ids.add(rid)
        unique.append(rec)

    if len(unique) < len(all_records):
        console.print(f"  {len(all_records) - len(unique)} tekrar kayit cikarildi")
    all_records = unique

    random.seed(seed)
    random.shuffle(all_records)

    n = len(all_records)
    n_train = max(1, int(n * TRAIN_RATIO))
    n_val = max(1, int(n * VAL_RATIO))

    train = all_records[:n_train]
    val = all_records[n_train : n_train + n_val]
    test = all_records[n_train + n_val :]

    if not test:
        test = [val.pop()]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, subset in [("train", train), ("val", val), ("test", test)]:
        out = OUT_DIR / f"{name}.jsonl"
        with out.open("w", encoding="utf-8") as fh:
            for rec in subset:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        console.print(f"  {name}: {len(subset)} ornek -> {out}")

    console.print(f"[green]Toplam {n} ornek bolundu: {len(train)}/{len(val)}/{len(test)}[/green]")


if __name__ == "__main__":
    run()

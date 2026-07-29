"""Veri seti istatistikleri ve kalite kontrolu.

Kullanim:
    python -m training.data.validate_dataset
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


def analyze_split(path: Path) -> dict:
    records = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            records.append(json.loads(line))

    targets = Counter(r["target"] for r in records)
    langs = Counter(r["lang"] for r in records)
    sources = Counter(r.get("source", "unknown") for r in records)

    input_lens = [len(r["input"]) for r in records]
    output_lens = [len(r["output"]) for r in records]

    ids = [r["id"] for r in records]
    unique_ids = len(set(ids))

    return {
        "count": len(records),
        "unique_ids": unique_ids,
        "duplicates": len(records) - unique_ids,
        "targets": dict(targets),
        "langs": dict(langs),
        "sources": dict(sources),
        "avg_input_len": sum(input_lens) / max(len(input_lens), 1),
        "avg_output_len": sum(output_lens) / max(len(output_lens), 1),
        "min_input": min(input_lens) if input_lens else 0,
        "max_input": max(input_lens) if input_lens else 0,
        "min_output": min(output_lens) if output_lens else 0,
        "max_output": max(output_lens) if output_lens else 0,
    }


def main() -> None:
    console.print("[bold]Veri Seti Dogrulama Raporu[/bold]\n")

    for name in ("train", "val", "test"):
        path = Path(f"training/datasets/{name}.jsonl")
        if not path.exists():
            console.print(f"  [yellow]{name}.jsonl bulunamadi[/yellow]")
            continue

        stats = analyze_split(path)

        tbl = Table(title=f"{name}.jsonl — {stats['count']:,} ornek")
        tbl.add_column("Metrik", style="cyan")
        tbl.add_column("Deger", style="green")

        tbl.add_row("Toplam", f"{stats['count']:,}")
        tbl.add_row("Benzersiz ID", f"{stats['unique_ids']:,}")
        tbl.add_row("Tekrar", f"{stats['duplicates']:,}")
        tbl.add_row("Hedefler", str(stats["targets"]))
        tbl.add_row("Diller", str(stats["langs"]))
        tbl.add_row("Kaynaklar", str(stats["sources"]))
        tbl.add_row("Ort. input uzunlugu", f"{stats['avg_input_len']:.0f} karakter")
        tbl.add_row("Ort. output uzunlugu", f"{stats['avg_output_len']:.0f} karakter")
        tbl.add_row("Input aralik", f"{stats['min_input']}–{stats['max_input']}")
        tbl.add_row("Output aralik", f"{stats['min_output']}–{stats['max_output']}")

        console.print(tbl)
        console.print()

    all_ids = set()
    overlap = False
    for name in ("train", "val", "test"):
        path = Path(f"training/datasets/{name}.jsonl")
        if not path.exists():
            continue
        ids = set()
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                ids.add(json.loads(line)["id"])
        inter = all_ids & ids
        if inter:
            console.print(f"  [red]SIZINTI: {name} ile onceki split arasinda {len(inter)} ortak ID[/red]")
            overlap = True
        all_ids |= ids

    if not overlap:
        console.print("[green]Veri sizintisi yok — split'ler tamamen ayrik.[/green]")


if __name__ == "__main__":
    main()

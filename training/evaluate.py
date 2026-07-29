"""Egitilmis modeli test seti uzerinde degerlendir.

Kullanim:
    python -m training.evaluate --checkpoint training/outputs/scratch-large/best.pt
"""

from __future__ import annotations

import json
from pathlib import Path

import click
import torch
import sentencepiece as spm
import yaml
from rich.console import Console
from rich.table import Table

console = Console()


def structure_score(text: str, target: str) -> float:
    score = 0.0
    if target == "claude-code":
        tags = ["<task>", "<context>", "<constraints>", "<acceptance>"]
        found = sum(1 for t in tags if t in text)
        score = found / len(tags)
    elif target == "chatgpt":
        headings = ["## Hedef", "## Goal", "## Baglam", "## Context",
                     "## Kisitlar", "## Constraints"]
        found = sum(1 for h in headings if h in text)
        score = min(found / 3, 1.0)
    elif target == "cursor":
        has_numbered = any(f"{i}." in text for i in range(1, 6))
        has_donot = "Do not" in text or "not:" in text
        score = (0.5 if has_numbered else 0) + (0.5 if has_donot else 0)
    elif target == "generic":
        headings = ["## Hedef", "## Goal", "## Adimlar", "## Steps",
                     "## Kabul", "## Acceptance"]
        found = sum(1 for h in headings if h in text)
        score = min(found / 3, 1.0)
    return score


def length_ratio(generated: str, reference: str) -> float:
    if not reference:
        return 0.0
    ratio = len(generated) / len(reference)
    if 0.5 <= ratio <= 2.0:
        return 1.0
    elif 0.25 <= ratio <= 3.0:
        return 0.5
    return 0.0


@click.command()
@click.option("--checkpoint", "-m", required=True)
@click.option("--config", "-c", default="training/configs/scratch-large.yaml")
@click.option("--split", "-s", default="test")
@click.option("--max-samples", "-n", default=200)
@click.option("--max-tokens", default=512)
@click.option("--temperature", default=0.7)
def main(checkpoint: str, config: str, split: str,
         max_samples: int, max_tokens: int, temperature: float) -> None:

    from training.inference import load_model, build_prompt_tokens

    console.print("[bold]ClarifyGPT Degerlendirme[/bold]")
    model, tokenizer, device = load_model(checkpoint, config)

    test_path = Path(f"training/datasets/{split}.jsonl")
    records = []
    with test_path.open(encoding="utf-8") as fh:
        for line in fh:
            records.append(json.loads(line))

    if len(records) > max_samples:
        import random
        random.seed(42)
        records = random.sample(records, max_samples)

    console.print(f"  {len(records)} ornek degerlendirilecek")

    eos_id = tokenizer.PieceToId("<|eos|>")
    results_by_target = {}

    for i, rec in enumerate(records):
        target = rec["target"]
        prompt_ids = build_prompt_tokens(rec["input"], target, tokenizer)
        tokens = torch.tensor([prompt_ids], dtype=torch.long, device=device)

        with torch.inference_mode():
            output = model.generate(tokens, max_new=max_tokens,
                                    temperature=temperature, top_k=50)

        generated_ids = output[0, len(prompt_ids):].tolist()
        if eos_id in generated_ids:
            generated_ids = generated_ids[:generated_ids.index(eos_id)]
        generated = tokenizer.Decode(generated_ids)

        s_score = structure_score(generated, target)
        l_score = length_ratio(generated, rec["output"])
        nonempty = 1.0 if len(generated.strip()) > 20 else 0.0

        if target not in results_by_target:
            results_by_target[target] = {"struct": [], "length": [], "nonempty": []}

        results_by_target[target]["struct"].append(s_score)
        results_by_target[target]["length"].append(l_score)
        results_by_target[target]["nonempty"].append(nonempty)

        if (i + 1) % 50 == 0:
            console.print(f"  {i+1}/{len(records)} tamamlandi")

    tbl = Table(title="Degerlendirme Sonuclari")
    tbl.add_column("Hedef", style="cyan")
    tbl.add_column("Ornek", style="white")
    tbl.add_column("Yapi Skoru", style="green")
    tbl.add_column("Uzunluk Skoru", style="green")
    tbl.add_column("Bos Olmayan", style="green")

    all_struct, all_length, all_ne = [], [], []
    for target in sorted(results_by_target):
        r = results_by_target[target]
        avg_s = sum(r["struct"]) / len(r["struct"])
        avg_l = sum(r["length"]) / len(r["length"])
        avg_n = sum(r["nonempty"]) / len(r["nonempty"])
        tbl.add_row(target, str(len(r["struct"])),
                     f"{avg_s:.2%}", f"{avg_l:.2%}", f"{avg_n:.2%}")
        all_struct.extend(r["struct"])
        all_length.extend(r["length"])
        all_ne.extend(r["nonempty"])

    avg_total_s = sum(all_struct) / max(len(all_struct), 1)
    avg_total_l = sum(all_length) / max(len(all_length), 1)
    avg_total_n = sum(all_ne) / max(len(all_ne), 1)
    tbl.add_row("[bold]TOPLAM[/bold]", str(len(all_struct)),
                f"[bold]{avg_total_s:.2%}[/bold]",
                f"[bold]{avg_total_l:.2%}[/bold]",
                f"[bold]{avg_total_n:.2%}[/bold]")

    console.print(tbl)

    report = {
        "checkpoint": checkpoint,
        "split": split,
        "samples": len(records),
        "avg_structure": round(avg_total_s, 4),
        "avg_length_ratio": round(avg_total_l, 4),
        "avg_nonempty": round(avg_total_n, 4),
        "by_target": {
            t: {
                "count": len(r["struct"]),
                "avg_structure": round(sum(r["struct"]) / len(r["struct"]), 4),
                "avg_length_ratio": round(sum(r["length"]) / len(r["length"]), 4),
                "avg_nonempty": round(sum(r["nonempty"]) / len(r["nonempty"]), 4),
            }
            for t, r in results_by_target.items()
        },
    }

    out_path = Path(checkpoint).parent / f"eval_{split}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    console.print(f"\n  Rapor: {out_path}")


if __name__ == "__main__":
    main()

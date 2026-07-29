"""Interactive spot-check CLI — show N test examples, capture Kemal's verdict."""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

console = Console()

REPORTS_DIR = Path("training/eval/reports")
SPOT_DIR = Path("training/eval/spotchecks")


@click.command()
@click.option("--report", type=click.Path(exists=True, path_type=Path), required=True,
              help="Path to a report-*.jsonl produced by eval/run.py")
@click.option("--n", type=int, default=30, show_default=True)
def cli(report: Path, n: int) -> None:
    run(report, n)


def run(report: Path, n: int) -> None:
    rows = [json.loads(line) for line in report.read_text(encoding="utf-8").splitlines() if line]
    sample = random.Random(3407).sample(rows, min(n, len(rows)))

    SPOT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = SPOT_DIR / f"spotcheck-{stamp}.jsonl"

    counts = {"g": 0, "o": 0, "k": 0}
    with out_path.open("w", encoding="utf-8") as fh:
        for i, row in enumerate(sample, 1):
            console.rule(f"[bold]#{i}/{len(sample)}  id={row['test_example_id']}")
            console.print(Panel(row["input"], title="[cyan]HAM PROMPT"))
            console.print(Panel(row["our_output"], title="[green]BIZIM CIKTI"))
            console.print(Panel(row.get("gold_output", ""), title="[yellow]GOLD"))
            verdict = console.input("Verdict [g]ood / [o]rta / [k]otu / [s]kip: ").strip().lower()
            if verdict == "s":
                continue
            if verdict not in counts:
                verdict = "o"
            counts[verdict] += 1
            fh.write(json.dumps({
                "run_id": stamp,
                "test_example_id": row["test_example_id"],
                "kemal_verdict": {"g": "good", "o": "orta", "k": "kotu"}[verdict],
            }, ensure_ascii=False) + "\n")

    total = sum(counts.values())
    console.print(f"\n[bold]good={counts['g']}  orta={counts['o']}  kotu={counts['k']}  total={total}")
    if total:
        console.print(f"[green]iyi/orta orani: {(counts['g']+counts['o'])/total:.1%}[/green]")


if __name__ == "__main__":
    cli()

"""Measure end-to-end latency of `clarify-prompt` on a small prompt set."""

from __future__ import annotations

import statistics
import subprocess
import time
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()

SAMPLE_PROMPTS = [
    "reflection kodu patliyor duzelt",
    "blog yazisi yaz seo hakkinda",
    "bu componenti temizle",
    "pandas dataframe deki bos degerleri sil",
    "npm build hata veriyor bak",
]


@click.command()
@click.option("--runs", type=int, default=20, show_default=True)
@click.option("--target", default="generic", show_default=True)
def cli(runs: int, target: str) -> None:
    run(runs, target)


def run(runs: int = 20, target: str = "generic") -> None:
    times: list[float] = []
    for i in range(runs):
        prompt = SAMPLE_PROMPTS[i % len(SAMPLE_PROMPTS)]
        start = time.perf_counter()
        proc = subprocess.run(
            ["clarify-prompt", "-t", target, prompt],
            capture_output=True,
            text=True,
            check=False,
        )
        elapsed = time.perf_counter() - start
        if proc.returncode != 0:
            console.print(f"[red]run {i + 1} failed: {proc.stderr.strip()[:200]}[/red]")
            continue
        times.append(elapsed)
        console.log(f"run {i + 1:2d}: {elapsed:.2f}s")

    if not times:
        console.print("[red]No successful runs.[/red]")
        raise SystemExit(1)

    times.sort()
    p50 = times[len(times) // 2]
    p95 = times[int(len(times) * 0.95)]
    p99 = times[int(len(times) * 0.99)]
    mean = statistics.mean(times)

    table = Table(title="clarify-prompt latency")
    table.add_column("metric")
    table.add_column("seconds")
    table.add_row("runs", str(len(times)))
    table.add_row("mean", f"{mean:.2f}")
    table.add_row("p50", f"{p50:.2f}")
    table.add_row("p95", f"{p95:.2f}")
    table.add_row("p99", f"{p99:.2f}")
    table.add_row("min", f"{min(times):.2f}")
    table.add_row("max", f"{max(times):.2f}")
    console.print(table)

    Path("bench/results").mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    (Path("bench/results") / f"latency-{stamp}.txt").write_text(
        f"runs={len(times)}\nmean={mean:.3f}\np50={p50:.3f}\np95={p95:.3f}\np99={p99:.3f}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    cli()

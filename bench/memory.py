"""Sample VRAM and RSS while `reprompt` is running."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.command()
@click.option("--prompt", default="reflection kodu patliyor duzelt")
@click.option("--target", default="generic")
@click.option("--interval", type=float, default=0.5, show_default=True)
def cli(prompt: str, target: str, interval: float) -> None:
    run(prompt, target, interval)


def run(prompt: str, target: str, interval: float) -> None:
    proc = subprocess.Popen(
        ["reprompt", "-t", target, prompt],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    peak_vram_mb = 0
    peak_rss_mb = 0
    samples = 0
    while proc.poll() is None:
        vram_mb = _snapshot_vram_mb()
        rss_mb = _snapshot_rss_mb(proc.pid)
        peak_vram_mb = max(peak_vram_mb, vram_mb)
        peak_rss_mb = max(peak_rss_mb, rss_mb)
        samples += 1
        time.sleep(interval)

    console.print(f"[bold]samples:[/bold] {samples}")
    console.print(f"[bold]peak VRAM:[/bold] {peak_vram_mb} MB")
    console.print(f"[bold]peak RSS:[/bold] {peak_rss_mb} MB")

    Path("bench/results").mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    (Path("bench/results") / f"memory-{stamp}.txt").write_text(
        f"peak_vram_mb={peak_vram_mb}\npeak_rss_mb={peak_rss_mb}\nsamples={samples}\n",
        encoding="utf-8",
    )


def _snapshot_vram_mb() -> int:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if out.returncode == 0:
            return int(out.stdout.strip().splitlines()[0])
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass
    return 0


def _snapshot_rss_mb(pid: int) -> int:
    try:
        import psutil

        return int(psutil.Process(pid).memory_info().rss / (1024 * 1024))
    except Exception:  # noqa: BLE001
        return 0


if __name__ == "__main__":
    cli()

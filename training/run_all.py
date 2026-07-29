"""Tam egitim pipeline'i: veri uretimi -> tokenizer -> egitim -> degerlendirme.

Kullanim:
    python -m training.run_all [--skip-data] [--skip-tokenizer] [--config CONFIG]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console

console = Console()
PY = sys.executable


def run_step(name: str, cmd: list[str]) -> bool:
    console.print(f"\n{'=' * 60}")
    console.print(f"[bold cyan]{name}[/bold cyan]")
    console.print(f"{'=' * 60}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    if result.returncode != 0:
        console.print(f"[red]{name} basarisiz (exit {result.returncode})[/red]")
        return False
    console.print(f"[green]{name} tamamlandi[/green]")
    return True


@click.command()
@click.option("--skip-data", is_flag=True, help="Veri uretimini atla")
@click.option("--skip-tokenizer", is_flag=True, help="Tokenizer egitimini atla")
@click.option("--config", "-c", default="training/configs/scratch-large.yaml")
@click.option("--count", "-n", default=100_000, help="Uretilecek sentetik ornek sayisi")
@click.option("--vocab-size", "-v", default=12_000)
def main(skip_data: bool, skip_tokenizer: bool, config: str, count: int, vocab_size: int) -> None:

    console.print("[bold]ClarifyGPT — Tam Egitim Pipeline[/bold]")

    if not skip_data:
        if not run_step(
            "1/5 Sentetik veri uretimi",
            [PY, "-m", "training.data.generate_synthetic", "--count", str(count)],
        ):
            return

        if not run_step("2/5 Veri bolme (train/val/test)", [PY, "-m", "training.data.split"]):
            return
    else:
        console.print("\n  [dim]Veri uretimi atlandi[/dim]")

    if not skip_tokenizer:
        if not run_step(
            "3/5 Tokenizer egitimi",
            [PY, "-m", "training.tokenizer.train_tokenizer", "--vocab-size", str(vocab_size)],
        ):
            return
    else:
        console.print("\n  [dim]Tokenizer atlandi[/dim]")

    if not run_step("4/5 Model egitimi", [PY, "-m", "training.train_scratch", "--config", config]):
        return

    import yaml

    with open(config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    output_dir = cfg.get("training", {}).get("output_dir", "training/outputs/scratch")
    best_ckpt = Path(output_dir) / "best.pt"

    if best_ckpt.exists():
        run_step(
            "5/5 Degerlendirme",
            [PY, "-m", "training.evaluate", "--checkpoint", str(best_ckpt), "--config", config],
        )
    else:
        console.print("[yellow]best.pt bulunamadi, degerlendirme atlandi[/yellow]")

    console.print("\n[bold green]Pipeline tamamlandi![/bold green]")


if __name__ == "__main__":
    main()

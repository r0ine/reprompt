"""Merge a trained LoRA adapter into the base model, save as fp16 safetensors."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.command()
@click.option("--adapter", type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--out", type=click.Path(path_type=Path), default=Path("training/outputs/merged"))
def cli(adapter: Path, out: Path) -> None:
    run(adapter, out)


def run(adapter: Path, out: Path) -> None:
    from unsloth import FastLanguageModel

    console.print(f"[cyan]loading adapter: {adapter}[/cyan]")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(adapter),
        max_seq_length=2048,
        load_in_4bit=False,
    )
    out.mkdir(parents=True, exist_ok=True)
    console.print(f"[cyan]saving merged fp16 -> {out}[/cyan]")
    model.save_pretrained_merged(str(out), tokenizer, save_method="merged_16bit")
    console.print(f"[green]merged model kaydedildi -> {out}[/green]")


if __name__ == "__main__":
    cli()

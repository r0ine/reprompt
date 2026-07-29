"""Convert a merged HF model to GGUF Q4_K_M via Unsloth's helper."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.command()
@click.option("--model", type=click.Path(exists=True, path_type=Path), required=True,
              help="Path to merged model dir")
@click.option("--quant", default="q4_k_m", show_default=True,
              help="GGUF quantization: q4_k_m | q5_k_m | q6_k | q8_0 | f16")
@click.option("--out", type=click.Path(path_type=Path),
              default=Path("training/outputs/gguf"))
def cli(model: Path, quant: str, out: Path) -> None:
    run(model, quant, out)


def run(model: Path, quant: str = "q4_k_m", out: Path = Path("training/outputs/gguf")) -> None:
    from unsloth import FastLanguageModel

    console.print(f"[cyan]loading merged model: {model}[/cyan]")
    mdl, tok = FastLanguageModel.from_pretrained(
        model_name=str(model), max_seq_length=2048, load_in_4bit=False,
    )
    out.mkdir(parents=True, exist_ok=True)
    console.print(f"[cyan]converting -> GGUF {quant} at {out}[/cyan]")
    mdl.save_pretrained_gguf(str(out), tok, quantization_method=quant)
    console.print(f"[green]GGUF kaydedildi -> {out}[/green]")


if __name__ == "__main__":
    cli()

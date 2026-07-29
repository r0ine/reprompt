"""Egitilmis ClarifyGPT ile prompt donusumu.

Kullanim:
    python -m training.inference --checkpoint training/outputs/scratch/best.pt
"""

from __future__ import annotations

import json
from pathlib import Path

import click
import torch
import sentencepiece as spm
import yaml
from rich.console import Console
from rich.panel import Panel

console = Console()


def load_model(checkpoint_path: str, config_path: str = "training/configs/scratch-base.yaml"):
    from training.model.config import ClarifyConfig
    from training.model.transformer import ClarifyGPT

    with open(config_path, encoding="utf-8") as f:
        cfg_dict = yaml.safe_load(f)

    tok_path = cfg_dict.get("tokenizer", "training/tokenizer/clarify_tok.model")
    tokenizer = spm.SentencePieceProcessor()
    tokenizer.Load(tok_path)

    model_cfg = ClarifyConfig(**cfg_dict.get("model", {}))
    model_cfg.vocab_size = tokenizer.GetPieceSize()

    model = ClarifyGPT(model_cfg)
    ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    model.load_state_dict(ckpt["model_state"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device).eval()

    return model, tokenizer, device


def build_prompt_tokens(raw_input: str, target: str,
                        tokenizer: spm.SentencePieceProcessor) -> list[int]:
    bos = tokenizer.PieceToId("<|bos|>")
    im_start = tokenizer.PieceToId("<|im_start|>")
    im_end = tokenizer.PieceToId("<|im_end|>")
    sys_tok = tokenizer.PieceToId("<|system|>")
    usr_tok = tokenizer.PieceToId("<|user|>")
    asst_tok = tokenizer.PieceToId("<|assistant|>")

    target_tok = tokenizer.PieceToId(f"<|{target}|>")
    system_msg = "Sen bir prompt muhendisisin. Kullanicinin ham girdisini, hedef LLM icin optimize edilmis yapisal bir prompta donustur."
    sys_ids = tokenizer.Encode(system_msg)
    inp_ids = tokenizer.Encode(raw_input)

    seq = [bos, im_start, sys_tok]
    if target_tok != tokenizer.unk_id():
        seq.append(target_tok)
    seq.extend(sys_ids)
    seq.append(im_end)
    seq.extend([im_start, usr_tok])
    seq.extend(inp_ids)
    seq.append(im_end)
    seq.extend([im_start, asst_tok])

    return seq


@click.command()
@click.option("--checkpoint", "-m", required=True, help="Model checkpoint yolu")
@click.option("--config", "-c", default="training/configs/scratch-base.yaml")
@click.option("--target", "-t", default="generic",
              type=click.Choice(["claude-code", "chatgpt", "cursor", "generic"]))
@click.option("--temperature", default=0.7, help="Uretim sicakligi")
@click.option("--max-tokens", default=512, help="Maksimum uretim token sayisi")
@click.option("--interactive/--no-interactive", default=True)
def main(checkpoint: str, config: str, target: str,
         temperature: float, max_tokens: int, interactive: bool) -> None:
    console.print("[bold]ClarifyGPT Inference[/bold]")
    model, tokenizer, device = load_model(checkpoint, config)
    console.print(f"  Model yuklendi: {checkpoint}")
    console.print(f"  Hedef profil: {target}")

    eos_id = tokenizer.PieceToId("<|eos|>")

    if interactive:
        console.print("\n  Ham promptunuzu girin (cikis: q)\n")
        while True:
            try:
                raw = console.input("[bold cyan]> [/bold cyan]")
            except (EOFError, KeyboardInterrupt):
                break
            if raw.strip().lower() in ("q", "quit", "exit"):
                break

            prompt_ids = build_prompt_tokens(raw.strip(), target, tokenizer)
            tokens = torch.tensor([prompt_ids], dtype=torch.long, device=device)

            output = model.generate(tokens, max_new=max_tokens,
                                    temperature=temperature, top_k=50)

            generated = output[0, len(prompt_ids):].tolist()
            if eos_id in generated:
                generated = generated[:generated.index(eos_id)]
            text = tokenizer.Decode(generated)

            console.print(Panel(text, title=f"[{target}]", border_style="green"))
    else:
        test_prompts = [
            "login sayfasi yap",
            "fix the search bug",
            "API dokumantasyonu hazirla",
            "optimize database queries",
        ]
        for raw in test_prompts:
            prompt_ids = build_prompt_tokens(raw, target, tokenizer)
            tokens = torch.tensor([prompt_ids], dtype=torch.long, device=device)
            output = model.generate(tokens, max_new=max_tokens,
                                    temperature=temperature, top_k=50)
            generated = output[0, len(prompt_ids):].tolist()
            if eos_id in generated:
                generated = generated[:generated.index(eos_id)]
            text = tokenizer.Decode(generated)

            console.print(Panel(f"[dim]{raw}[/dim]\n\n{text}",
                                title=f"[{target}]", border_style="green"))


if __name__ == "__main__":
    main()

"""Test a fine-tuned LoRA model against baseline on sample prompts."""

from __future__ import annotations

import json
from pathlib import Path

import click
import torch
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

SYSTEM_PROMPT = (
    "You are `clarify-prompt`, a rewriter that turns a raw user request "
    "into a well-structured prompt for a downstream large language model.\n\n"
    "Rules:\n"
    "- Preserve the user's intent exactly. Do not add features or scope.\n"
    "- Add missing structure: a clear goal, the context the target LLM needs, "
    "acceptance criteria, and the expected output format.\n"
    "- Do NOT answer the request yourself. Return the rewritten prompt, not the solution.\n"
    "- Reply in the same language as the input.\n"
    "- Format the rewritten prompt as a self-contained block."
)

TEST_PROMPTS = [
    {"input": "bu kodu düzelt çalışmıyor", "lang": "tr"},
    {"input": "add authentication to my app", "lang": "en"},
    {"input": "veritabanını optimize et", "lang": "tr"},
    {"input": "write a readme for this project", "lang": "en"},
    {"input": "api endpoint yavaş düzelt", "lang": "tr"},
    {"input": "refactor this messy code", "lang": "en"},
]


def generate(model, tokenizer, user_input: str, max_new_tokens: int = 512) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    generated = outputs[0][inputs["input_ids"].shape[1] :]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


@click.command()
@click.option("--adapter", "-a", type=click.Path(exists=True, path_type=Path), required=True,
              help="LoRA adapter dizini (training/outputs/.../final)")
@click.option("--base-model", "-b", type=str, default=None,
              help="Base model ismi (adapter config'den okunur)")
@click.option("--test-file", "-t", type=click.Path(exists=True, path_type=Path), default=None,
              help="JSONL test dosyasi (varsayilan: dahili test promptlari)")
@click.option("--compare/--no-compare", default=True,
              help="Baseline ile karsilastir")
def main(adapter: Path, base_model: str | None, test_file: Path | None, compare: bool) -> None:
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel

    adapter_config = json.loads((adapter / "adapter_config.json").read_text())
    if base_model is None:
        base_model = adapter_config["base_model_name_or_path"]
    console.rule(f"[bold]Test: {base_model} + LoRA")

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    console.print("Base model yukleniyor...")
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    base = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True,
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    prompts = TEST_PROMPTS
    if test_file:
        prompts = []
        with test_file.open(encoding="utf-8") as fh:
            for line in fh:
                rec = json.loads(line.strip())
                prompts.append({"input": rec["input"], "lang": rec.get("lang", "en")})
        prompts = prompts[:10]

    if compare:
        console.print("\n[dim]--- BASELINE (adaptorsuz) ---[/dim]")
        baseline_outputs = []
        for p in prompts:
            out = generate(base, tokenizer, p["input"])
            baseline_outputs.append(out)
            console.print(Panel(out[:300], title=f"Baseline | {p['input'][:40]}...", border_style="dim"))

    console.print("\nLoRA adapter yukleniyor...")
    model = PeftModel.from_pretrained(base, str(adapter))
    model.eval()

    console.print("\n[bold green]--- FINE-TUNED ---[/bold green]")
    finetuned_outputs = []
    for p in prompts:
        out = generate(model, tokenizer, p["input"])
        finetuned_outputs.append(out)
        console.print(Panel(out[:500], title=f"Fine-tuned | {p['input'][:40]}...", border_style="green"))

    if compare:
        table = Table(title="Karsilastirma Ozeti")
        table.add_column("Prompt", style="cyan", max_width=30)
        table.add_column("Baseline uzunluk", justify="right")
        table.add_column("Fine-tuned uzunluk", justify="right")
        table.add_column("Yapi var?", justify="center")

        structure_markers = ["##", "<task>", "Goal", "Hedef", "Context", "Acceptance", "Constraints", "1.", "2."]
        for i, p in enumerate(prompts):
            bl = baseline_outputs[i]
            ft = finetuned_outputs[i]
            has_structure = any(m in ft for m in structure_markers)
            table.add_row(
                p["input"][:30],
                str(len(bl)),
                str(len(ft)),
                "[green]Evet[/green]" if has_structure else "[red]Hayir[/red]",
            )
        console.print(table)

    results_dir = adapter.parent
    results_path = results_dir / "test_results.json"
    results = []
    for i, p in enumerate(prompts):
        entry = {"input": p["input"], "finetuned": finetuned_outputs[i]}
        if compare:
            entry["baseline"] = baseline_outputs[i]
        results.append(entry)
    with results_path.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    console.print(f"\n[green]Sonuclar kaydedildi: {results_path}[/green]")


if __name__ == "__main__":
    main()

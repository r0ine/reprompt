"""Run the test set through the fine-tuned model + baseline, score with judge."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import click
from rich.console import Console

console = Console()

TEST_PATH = Path("training/datasets/test.jsonl")
REPORTS_DIR = Path("training/eval/reports")


@click.command()
@click.option("--model", "-m", type=click.Path(exists=True, path_type=Path), required=True,
              help="Path to trained LoRA adapter or merged model")
@click.option("--baseline", is_flag=True, help="Also evaluate the base model with a generic prompt")
@click.option("--limit", type=int, default=None)
def cli(model: Path, baseline: bool, limit: int | None) -> None:
    run(model=model, baseline=baseline, limit=limit)


def run(model: Path, baseline: bool = True, limit: int | None = None) -> None:
    if not TEST_PATH.exists():
        raise SystemExit(f"{TEST_PATH} yok. Once veri seti hazirla.")

    from training.eval.judge_prometheus import load_judge, score_one
    from unsloth import FastLanguageModel  # noqa: F401

    records = [json.loads(line) for line in TEST_PATH.read_text(encoding="utf-8").splitlines()]
    if limit is not None:
        records = records[:limit]

    console.print(f"[cyan]{len(records)} test kayit yuklendi[/cyan]")

    ours = _generate_from_adapter(model, records)
    base = _generate_from_baseline(records) if baseline else [None] * len(records)

    judge_model, judge_tok = load_judge()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = REPORTS_DIR / f"report-{stamp}.jsonl"

    wins = 0
    with report_path.open("w", encoding="utf-8") as fh:
        for rec, our_out, base_out in zip(records, ours, base):
            our_score = score_one(judge_model, judge_tok, rec["input"], our_out, rec["output"])
            base_score = (
                score_one(judge_model, judge_tok, rec["input"], base_out, rec["output"])
                if base_out is not None else {"score": 0}
            )
            row = {
                "run_id": stamp,
                "test_example_id": rec["id"],
                "target": rec["target"],
                "input": rec["input"],
                "our_output": our_out,
                "baseline_output": base_out,
                "gold_output": rec["output"],
                "our_score": our_score.get("score"),
                "baseline_score": base_score.get("score"),
                "our_win": (our_score.get("score", 0) > base_score.get("score", 0)),
            }
            wins += int(row["our_win"])
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    total = len(records)
    console.print(f"[green]kazanma orani: {wins}/{total} = {wins/total:.1%}[/green]")
    console.print(f"[green]rapor: {report_path}[/green]")


def _generate_from_adapter(adapter_path: Path, records: list[dict]) -> list[str]:
    console.print("[cyan]bizim model (LoRA adapter) generate[/cyan]")
    return _generate(adapter_path, records, is_adapter=True)


def _generate_from_baseline(records: list[dict]) -> list[str]:
    console.print("[cyan]baseline (base model + generic sys prompt)[/cyan]")
    return _generate(Path("unsloth/Qwen2.5-7B-Instruct-bnb-4bit"), records, is_adapter=False)


def _generate(model_ref: Path, records: list[dict], is_adapter: bool) -> list[str]:
    from unsloth import FastLanguageModel

    if is_adapter:
        model, tok = FastLanguageModel.from_pretrained(
            model_name=str(model_ref), max_seq_length=2048, load_in_4bit=True,
        )
    else:
        model, tok = FastLanguageModel.from_pretrained(
            model_name=str(model_ref), max_seq_length=2048, load_in_4bit=True,
        )
    FastLanguageModel.for_inference(model)

    outputs: list[str] = []
    for rec in records:
        messages = [
            {"role": "system", "content": "Rewrite the user's raw request into an optimized prompt."},
            {"role": "user", "content": rec["input"]},
        ]
        prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tok(prompt, return_tensors="pt").to(model.device)
        out = model.generate(**inputs, max_new_tokens=512, temperature=0.7, top_p=0.9)
        text = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        outputs.append(text.strip())
    return outputs


if __name__ == "__main__":
    cli()

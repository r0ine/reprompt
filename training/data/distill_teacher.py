"""Teacher-distill raw prompts into (raw, optimized) pairs via Claude Opus."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import click
from rich.console import Console
from tenacity import retry, stop_after_attempt, wait_exponential

from training.data.schema import Record, RecordMeta

console = Console()

RAW_INPUTS = [
    Path("training/datasets/raw/transcripts.jsonl"),
    Path("training/datasets/raw/shared.jsonl"),
]
OUT_PATH = Path("training/datasets/raw/distilled.jsonl")

TEACHER_MODEL_DEFAULT = "claude-opus-4-7"
COST_PER_1K_OUTPUT_USD = 0.075  # rough — verify before running


SYSTEM_PROMPT = """You are a prompt engineer. Given a raw user request, rewrite it into an
optimized prompt for a downstream LLM. Preserve the user's intent exactly. Add missing
structure: goal, context, acceptance criteria, output format. Reply in the same language
as the input. Return ONLY the rewritten prompt — no preamble, no explanation.
"""


@click.command()
@click.option("--limit", type=int, default=None, help="Stop after N records (dry-run friendly)")
@click.option("--dry-run", is_flag=True, help="Estimate cost, no API calls")
@click.option("--teacher", default=TEACHER_MODEL_DEFAULT, show_default=True)
def cli(limit: int | None, dry_run: bool, teacher: str) -> None:
    run(limit=limit, dry_run=dry_run, teacher=teacher)


def run(limit: int | None = None, dry_run: bool = False, teacher: str = TEACHER_MODEL_DEFAULT) -> None:
    inputs = list(_load_pending())
    if limit is not None:
        inputs = inputs[:limit]
    est_output_tokens = 250 * len(inputs)
    est_cost = est_output_tokens / 1000.0 * COST_PER_1K_OUTPUT_USD
    console.print(
        f"[cyan]{len(inputs)} kayit, ~{est_output_tokens} out tok, ~${est_cost:.2f} USD tahmini[/cyan]"
    )
    if dry_run:
        return
    if est_cost > 50.0:
        console.print("[red]Butce kapagi $50 asildi. --limit ile kucult veya kapagi ac.[/red]")
        raise SystemExit(3)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY ortam degiskeni gerekli.")
    try:
        import anthropic
    except ImportError as exc:
        raise SystemExit("`pip install anthropic` gerekli.") from exc
    client = anthropic.Anthropic(api_key=api_key)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with OUT_PATH.open("w", encoding="utf-8") as fh:
        for i, raw_rec in enumerate(inputs, 1):
            try:
                optimized = _distill_one(client, teacher, raw_rec["input"])
            except Exception as exc:  # noqa: BLE001
                console.print(f"[red]#{i} fail: {exc}[/red]")
                continue
            new_rec = Record(
                id=f"distill_{written:05d}",
                source="distill",
                target=raw_rec.get("target", "generic"),
                lang=raw_rec.get("lang", "en"),
                input=raw_rec["input"],
                output=optimized,
                meta=RecordMeta(
                    teacher=teacher,
                    created_at=datetime.now(timezone.utc),
                    notes=f"seed:{raw_rec.get('source', '?')}",
                ),
            )
            fh.write(json.dumps(new_rec.to_jsonl_dict(), ensure_ascii=False) + "\n")
            written += 1
            if written % 25 == 0:
                console.print(f"  {written} tamam")
    console.print(f"[green]{written} distilled ornek -> {OUT_PATH}[/green]")


def _load_pending():
    for path in RAW_INPUTS:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("input") and "[TO BE DISTILLED]" in obj.get("output", ""):
                yield obj


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
def _distill_one(client, teacher: str, user_input: str) -> str:
    resp = client.messages.create(
        model=teacher,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_input}],
    )
    return "".join(block.text for block in resp.content if hasattr(block, "text")).strip()


if __name__ == "__main__":
    cli()

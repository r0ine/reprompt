"""Prometheus 2 based LLM-as-judge for the rewritten prompts."""

from __future__ import annotations

import json
import re
from pathlib import Path

from rich.console import Console

console = Console()

RUBRIC_PATH = Path("training/eval/rubric.md")


def load_judge(model_name: str = "prometheus-eval/prometheus-7b-v2.0"):
    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=4096,
        load_in_4bit=True,
    )
    FastLanguageModel.for_inference(model)
    return model, tokenizer


def score_one(model, tokenizer, user_input: str, our_output: str, gold_output: str) -> dict:
    rubric = RUBRIC_PATH.read_text(encoding="utf-8")
    prompt = (
        f"{rubric}\n\n"
        f"# Original user request\n{user_input}\n\n"
        f"# Reference (gold) rewrite\n{gold_output}\n\n"
        f"# Candidate rewrite (to score)\n{our_output}\n\n"
        f"# Your JSON response:\n"
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    out = model.generate(**inputs, max_new_tokens=200, temperature=0.0)
    text = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return _parse_json_score(text)


def _parse_json_score(text: str) -> dict:
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if not match:
        return {"score": 0, "rationale": "unparseable judge output"}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"score": 0, "rationale": "malformed judge JSON"}

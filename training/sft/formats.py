"""Dataset row formatters — ChatML default, Alpaca fallback."""

from __future__ import annotations

CHATML_TEMPLATE = "<|im_start|>user\n{input}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"

ALPACA_TEMPLATE = "### Instruction:\n{input}\n\n### Response:\n{output}"


def format_row(row: dict, fmt: str = "chatml") -> str:
    if fmt == "chatml":
        return CHATML_TEMPLATE.format(input=row["input"], output=row["output"])
    if fmt == "alpaca":
        return ALPACA_TEMPLATE.format(input=row["input"], output=row["output"])
    raise ValueError(f"unknown format: {fmt}")

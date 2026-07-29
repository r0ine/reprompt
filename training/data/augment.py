"""Augment the gold dataset by generating cross-target variants.

Takes existing gold examples and creates variants for other target profiles.
This multiplies the dataset roughly 3x without needing new raw examples.

Usage:
    python -m training.data.augment
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console

console = Console()

RAW_DIR = Path("training/datasets/raw")
GOLD_PATH = RAW_DIR / "gold.jsonl"
AUGMENTED_PATH = RAW_DIR / "augmented.jsonl"

TARGETS = ["claude-code", "chatgpt", "cursor", "generic"]

CLAUDE_CODE_TEMPLATE = """<task>
{goal}
</task>

<context>
{context}
</context>

<constraints>
{constraints}
</constraints>

<acceptance>
{acceptance}
</acceptance>

<output_format>
{output_format}
</output_format>"""

CHATGPT_TEMPLATE = """## Goal
{goal}

## Context
{context}

## Constraints
{constraints}

## Acceptance criteria
{acceptance}

## Output format
{output_format}"""

CURSOR_TEMPLATE = """{goal_short}

{numbered_steps}

Do not: {donot_list}"""

GENERIC_TEMPLATE = """## Goal
{goal}

## Context
{context}

## Steps
{steps}

## Acceptance criteria
{acceptance}

## Output format
{output_format}"""


def extract_sections(output: str) -> dict[str, str]:
    sections: dict[str, str] = {}

    for tag in ["task", "context", "constraints", "acceptance", "output_format"]:
        match = re.search(rf"<{tag}>\s*\n?(.*?)\n?\s*</{tag}>", output, re.DOTALL)
        if match:
            sections[tag] = match.group(1).strip()

    for heading in ["Goal", "Hedef", "Context", "Bağlam", "Constraints", "Kısıtlar",
                     "Acceptance", "Kabul", "Output format", "Çıktı formatı", "Steps"]:
        pattern = rf"##\s*{heading}[^\n]*\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, output, re.DOTALL)
        if match:
            key = heading.lower().replace("ı", "i").replace("ğ", "g")
            if "hedef" in key or "goal" in key:
                sections.setdefault("task", match.group(1).strip())
            elif "context" in key or "baglam" in key:
                sections.setdefault("context", match.group(1).strip())
            elif "constraint" in key or "kisitlar" in key:
                sections.setdefault("constraints", match.group(1).strip())
            elif "acceptance" in key or "kabul" in key:
                sections.setdefault("acceptance", match.group(1).strip())
            elif "output" in key or "cikti" in key:
                sections.setdefault("output_format", match.group(1).strip())
            elif "step" in key:
                sections.setdefault("steps", match.group(1).strip())

    numbered = re.findall(r"^\d+\.\s+.+", output, re.MULTILINE)
    if numbered:
        sections.setdefault("steps", "\n".join(numbered))

    do_not = re.search(r"Do not:?\s*(.+?)(?:\n\n|\Z)", output, re.DOTALL | re.IGNORECASE)
    if do_not:
        sections["donot"] = do_not.group(1).strip()

    return sections


def to_claude_code(sections: dict[str, str]) -> str | None:
    goal = sections.get("task", "")
    if not goal:
        return None
    return CLAUDE_CODE_TEMPLATE.format(
        goal=goal,
        context=sections.get("context", "- Proje dosyalarını incele."),
        constraints=sections.get("constraints", "- Mevcut testler geçmeli."),
        acceptance=sections.get("acceptance", "- İşlevsellik doğrulanmış."),
        output_format=sections.get("output_format", "- Değişen dosyaların diff'i."),
    )


def to_chatgpt(sections: dict[str, str]) -> str | None:
    goal = sections.get("task", "")
    if not goal:
        return None
    return CHATGPT_TEMPLATE.format(
        goal=goal,
        context=sections.get("context", "- Provide relevant context."),
        constraints=sections.get("constraints", "- Keep response focused."),
        acceptance=sections.get("acceptance", "1. Requirements met.\n2. No errors."),
        output_format=sections.get("output_format", "- Markdown format."),
    )


def to_cursor(sections: dict[str, str]) -> str | None:
    goal = sections.get("task", "")
    if not goal:
        return None
    steps = sections.get("steps", sections.get("constraints", ""))
    lines = [l.strip() for l in steps.split("\n") if l.strip()]
    if not lines:
        return None
    numbered = []
    for i, line in enumerate(lines[:6], 1):
        clean = re.sub(r"^[-•*\d.]+\s*", "", line)
        if clean:
            numbered.append(f"{i}. {clean}")
    donot = sections.get("donot", "change unrelated code or break existing tests")
    goal_short = goal.split(".")[0].strip() if "." in goal else goal[:80]
    return CURSOR_TEMPLATE.format(
        goal_short=goal_short,
        numbered_steps="\n".join(numbered),
        donot_list=donot,
    )


def to_generic(sections: dict[str, str]) -> str | None:
    goal = sections.get("task", "")
    if not goal:
        return None
    steps = sections.get("steps", sections.get("constraints", ""))
    return GENERIC_TEMPLATE.format(
        goal=goal,
        context=sections.get("context", "- Check the project structure."),
        steps=steps or "1. Analyze the current state.\n2. Apply changes.\n3. Verify.",
        acceptance=sections.get("acceptance", "1. All requirements met.\n2. Tests pass."),
        output_format=sections.get("output_format", "- Changed files with explanation."),
    )


CONVERTERS = {
    "claude-code": to_claude_code,
    "chatgpt": to_chatgpt,
    "cursor": to_cursor,
    "generic": to_generic,
}


def run() -> None:
    if not GOLD_PATH.exists():
        console.print("[yellow]gold.jsonl yok — once import_gold calistir.[/yellow]")
        return

    records = []
    with GOLD_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                records.append(json.loads(line))

    augmented = []
    for rec in records:
        sections = extract_sections(rec["output"])
        if not sections.get("task"):
            continue

        original_target = rec["target"]
        for target in TARGETS:
            if target == original_target:
                continue
            converter = CONVERTERS[target]
            new_output = converter(sections)
            if not new_output or len(new_output) < 50:
                continue

            new_id = f"{rec['id']}_aug_{target.replace('-', '')}"
            augmented.append({
                "id": new_id,
                "source": "gold",
                "target": target,
                "lang": rec["lang"],
                "input": rec["input"],
                "output": new_output,
                "meta": {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "reviewed_by": None,
                    "notes": f"augmented from {rec['id']}",
                },
            })

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with AUGMENTED_PATH.open("w", encoding="utf-8") as fh:
        for rec in augmented:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    console.print(f"[green]{len(augmented)} augmented ornek yazildi -> {AUGMENTED_PATH}[/green]")
    console.print(f"  Toplam: {len(records)} gold + {len(augmented)} augmented = {len(records) + len(augmented)}")


if __name__ == "__main__":
    run()

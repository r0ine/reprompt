"""Extract raw-prompt candidates from Kemal's Claude Code session logs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console

from training.data.anonymize import anonymize
from training.data.schema import Record, RecordMeta

console = Console()

SESSIONS_ROOT = Path.home() / ".claude" / "projects"
OUT_PATH = Path("training/datasets/raw/transcripts.jsonl")

MIN_LEN = 20
MAX_LEN = 2000


def iter_session_files() -> list[Path]:
    if not SESSIONS_ROOT.exists():
        return []
    return sorted(SESSIONS_ROOT.rglob("*.jsonl"))


def extract_user_prompts(file: Path) -> list[str]:
    prompts: list[str] = []
    for line in file.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = obj.get("role") or obj.get("type")
        if role != "user":
            continue
        content = obj.get("content") or obj.get("text") or ""
        if isinstance(content, list):
            content = " ".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        content = str(content).strip()
        if MIN_LEN <= len(content) <= MAX_LEN:
            prompts.append(content)
    return prompts


def run() -> None:
    sessions = iter_session_files()
    if not sessions:
        console.print(f"[yellow]Session dosyasi yok: {SESSIONS_ROOT}[/yellow]")
        return
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    seen: set[str] = set()
    with OUT_PATH.open("w", encoding="utf-8") as fh:
        for i, file in enumerate(sessions):
            for prompt in extract_user_prompts(file):
                clean = anonymize(prompt)
                if clean in seen:
                    continue
                seen.add(clean)
                # `output` field is filled by a later distillation step —
                # here we save the raw input side only, tagged as untrained.
                rec = Record(
                    id=f"transcript_{written:05d}",
                    source="transcript",
                    target="claude-code",
                    lang="mix",
                    input=clean,
                    output="[TO BE DISTILLED]" + " " * 40,  # placeholder length-safe
                    meta=RecordMeta(created_at=datetime.now(timezone.utc)),
                )
                try:
                    fh.write(json.dumps(rec.to_jsonl_dict(), ensure_ascii=False) + "\n")
                    written += 1
                except Exception as exc:  # noqa: BLE001
                    console.print(f"[red]skip: {exc}[/red]")
    console.print(f"[green]{written} transcript girisi yazildi -> {OUT_PATH}[/green]")


if __name__ == "__main__":
    run()

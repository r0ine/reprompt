"""Push adapter / merged / GGUF to Hugging Face Hub."""

from __future__ import annotations

import os
from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.command()
@click.option("--repo", required=True, help="e.g. clarify/clarify-prompt-qwen2.5-7b-v1")
@click.option("--path", type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--private/--public", default=True)
def cli(repo: str, path: Path, private: bool) -> None:
    run(repo, path, private)


def run(repo: str, path: Path, private: bool = True) -> None:
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit("HF_TOKEN ortam degiskeni gerekli (write scope).")
    os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "1")
    from huggingface_hub import HfApi

    api = HfApi(token=token)
    api.create_repo(repo_id=repo, private=private, exist_ok=True)
    console.print(f"[cyan]uploading {path} -> {repo}[/cyan]")
    api.upload_folder(
        repo_id=repo,
        folder_path=str(path),
        path_in_repo=".",
        commit_message="clarify-prompt release",
    )
    console.print(f"[green]done: https://huggingface.co/{repo}[/green]")


if __name__ == "__main__":
    cli()

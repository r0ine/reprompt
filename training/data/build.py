"""Top-level dataset orchestrator — chains harvest → distill → merge → split."""

from __future__ import annotations

import click
from rich.console import Console

console = Console()


@click.command()
@click.option("--from-transcripts", is_flag=True, help="Harvest from ~/.claude/projects/")
@click.option("--from-shared", is_flag=True, help="Sample raw prompts from ShareGPT/Alpaca")
@click.option("--distill", is_flag=True, help="Enrich raw prompts via teacher LLM")
@click.option("--gold", is_flag=True, help="Import handwritten examples from docs/gold_examples.md")
@click.option("--merge", is_flag=True, help="Merge sources + dedup")
@click.option("--split", is_flag=True, help="Split into train/val/test")
@click.option("--all", "run_all", is_flag=True, help="Run every stage in order")
def main(
    from_transcripts: bool,
    from_shared: bool,
    distill: bool,
    gold: bool,
    merge: bool,
    split: bool,
    run_all: bool,
) -> None:
    if run_all:
        from_transcripts = from_shared = distill = gold = merge = split = True

    if not any([from_transcripts, from_shared, distill, gold, merge, split]):
        console.print("[yellow]No stage flag given. Pass --all or one of the stage flags.[/yellow]")
        raise SystemExit(2)

    if gold:
        from training.data import import_gold
        console.rule("[bold]Import gold examples")
        import_gold.run()
    if from_transcripts:
        from training.data import harvest_transcripts
        console.rule("[bold]Harvest transcripts")
        harvest_transcripts.run()
    if from_shared:
        from training.data import harvest_shared_datasets
        console.rule("[bold]Harvest shared datasets")
        harvest_shared_datasets.run()
    if distill:
        from training.data import distill_teacher
        console.rule("[bold]Teacher distillation")
        distill_teacher.run()
    if merge:
        from training.data import merge_dedup
        console.rule("[bold]Merge + dedup")
        merge_dedup.run()
    if split:
        from training.data import split_train_val_test
        console.rule("[bold]Split train/val/test")
        split_train_val_test.run()

    console.print("[green]done.[/green]")


if __name__ == "__main__":
    main()

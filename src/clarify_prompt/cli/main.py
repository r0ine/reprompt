"""Command-line entry point for clarify-prompt."""

from __future__ import annotations

import sys

import click
from rich.console import Console

from clarify_prompt import __version__
from clarify_prompt.config.loader import load_config
from clarify_prompt.engine.factory import make_engine
from clarify_prompt.errors import ClarifyPromptError
from clarify_prompt.postproc.pipeline import postprocess
from clarify_prompt.prompts.selector import select_system_prompt
from clarify_prompt.prompts.types import DETAIL_LEVELS, TARGET_PROFILES, TASK_PROFILES

TARGET_CHOICES = list(TARGET_PROFILES)
TASK_CHOICES = list(TASK_PROFILES)
DETAIL_CHOICES = list(DETAIL_LEVELS)


class _DefaultGroup(click.Group):
    """Falls through to 'rewrite' when no recognized subcommand is given."""

    def parse_args(self, ctx, args):
        if args and args[0] not in self.commands and not args[0].startswith("-"):
            args = ["rewrite"] + args
        return super().parse_args(ctx, args)


@click.group(cls=_DefaultGroup, context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="clarify-prompt")
def app():
    """Rewrite raw prompts into optimized prompts for downstream LLMs.

    \b
    Examples:
      clarify-prompt "reflection kodu patliyor duzelt"
      clarify-prompt rewrite --target chatgpt "api rate limiting ekle"
      echo "long messy request" | clarify-prompt rewrite --stdin
      clarify-prompt serve --port 8741
    """


@app.command()
@click.argument("user_prompt", required=False)
@click.option(
    "--target", "-t", type=click.Choice(TARGET_CHOICES), default=None, help="Target LLM profile."
)
@click.option(
    "--task",
    type=click.Choice(TASK_CHOICES),
    default=None,
    help="Task profile; auto infers it from the request.",
)
@click.option(
    "--detail", "-d", type=click.Choice(DETAIL_CHOICES), default=None, help="Prompt detail level."
)
@click.option(
    "--model", "-m", type=click.Path(exists=False), default=None, help="Path to GGUF model file."
)
@click.option("--explain", is_flag=True, help="Also output a short 'why' explanation.")
@click.option("--json", "as_json", is_flag=True, help="JSON-formatted output.")
@click.option("--stdin", is_flag=True, help="Read prompt from stdin.")
def rewrite(user_prompt, target, task, detail, model, explain, as_json, stdin):
    """Rewrite a raw user prompt into an optimized prompt."""
    err_console = Console(stderr=True)
    try:
        cfg = load_config(
            target_override=target,
            model_override=model,
            task_override=task,
            detail_override=detail,
        )
        if stdin or user_prompt is None:
            user_prompt = sys.stdin.read()
        if not (user_prompt or "").strip():
            raise click.UsageError("empty prompt (nothing to rewrite)")
        sys_prompt = select_system_prompt(
            cfg.target,
            explain=explain,
            task=cfg.task,
            detail=cfg.detail,
        )
        engine = make_engine(cfg)
        raw = engine.generate(sys_prompt, user_prompt)
        result = postprocess(raw, as_json=as_json)
        click.echo(result)
    except ClarifyPromptError as exc:
        err_console.print(f"[bold red]clarify-prompt error:[/bold red] {exc}")
        sys.exit(exc.exit_code)
    except click.ClickException:
        raise
    except Exception as exc:
        err_console.print(f"[bold red]unexpected error:[/bold red] {exc}")
        sys.exit(1)


@app.command()
@click.option("--host", default="0.0.0.0", help="Bind address.")
@click.option("--port", "-p", default=8741, type=int, help="Port number.")
@click.option(
    "--model", "-m", type=click.Path(exists=False), default=None, help="Path to GGUF model file."
)
@click.option("--workers", "-w", default=1, type=int, help="Uvicorn worker count.")
@click.option("--reload", is_flag=True, help="Auto-reload on code changes (dev only).")
def serve(host, port, model, workers, reload):
    """Start the REST API server for remote prompt rewriting.

    \b
    Examples:
      clarify-prompt serve
      clarify-prompt serve --port 9000 --model ~/models/clarify.gguf
    """
    import os

    if model:
        os.environ["CLARIFY_PROMPT_MODEL_PATH"] = str(model)

    try:
        import uvicorn
    except ImportError:
        click.echo("uvicorn is required: pip install clarify-prompt[api]", err=True)
        sys.exit(1)

    click.echo(f"clarify-prompt v{__version__} — starting API on {host}:{port}")
    uvicorn.run(
        "clarify_prompt.api.server:app",
        host=host,
        port=port,
        workers=workers,
        reload=reload,
    )


if __name__ == "__main__":
    app()

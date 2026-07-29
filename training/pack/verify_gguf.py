from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import click

GIB = 1024**3
GGUF_MAGIC = b"GGUF"


@dataclass(frozen=True)
class GGUFReport:
    path: Path
    size_bytes: int
    target_gib: float
    tolerance_gib: float

    @property
    def size_gib(self) -> float:
        return self.size_bytes / GIB

    @property
    def is_target_size(self) -> bool:
        return abs(self.size_gib - self.target_gib) <= self.tolerance_gib


def inspect_gguf(
    model_path: Path,
    target_gib: float = 4.5,
    tolerance_gib: float = 0.75,
) -> GGUFReport:
    if target_gib <= 0:
        raise ValueError("target_gib must be greater than zero")
    if tolerance_gib < 0:
        raise ValueError("tolerance_gib cannot be negative")

    with model_path.open("rb") as model_file:
        if model_file.read(4) != GGUF_MAGIC:
            raise ValueError(f"not a GGUF artifact: {model_path}")

    return GGUFReport(
        path=model_path.resolve(),
        size_bytes=model_path.stat().st_size,
        target_gib=target_gib,
        tolerance_gib=tolerance_gib,
    )


@click.command()
@click.argument("model_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--target-gib", default=4.5, show_default=True, type=float)
@click.option("--tolerance-gib", default=0.75, show_default=True, type=float)
@click.option("--strict/--no-strict", default=True, show_default=True)
def cli(
    model_path: Path,
    target_gib: float,
    tolerance_gib: float,
    strict: bool,
) -> None:
    """GGUF başlığını ve üretim paketi boyutunu doğrula."""
    try:
        report = inspect_gguf(model_path, target_gib, tolerance_gib)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Dosya: {report.path}")
    click.echo(f"Boyut: {report.size_gib:.2f} GiB")
    click.echo(f"Hedef: {report.target_gib:.2f} ± {report.tolerance_gib:.2f} GiB")

    if report.is_target_size:
        click.echo("Durum: hedef aralıkta")
        return

    message = "GGUF geçerli, fakat üretim boyutu hedef aralığın dışında"
    if strict:
        raise click.ClickException(message)
    click.echo(f"Uyarı: {message}")


if __name__ == "__main__":
    cli()

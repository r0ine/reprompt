from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "markdown_library.py"
SPEC = importlib.util.spec_from_file_location("markdown_library", SCRIPT)
assert SPEC and SPEC.loader
markdown_library = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = markdown_library
SPEC.loader.exec_module(markdown_library)


def test_build_and_verify_small_library(tmp_path: Path) -> None:
    output = tmp_path / "library" / "corpus"
    manifest = tmp_path / "library" / "MANIFEST.md"

    records = markdown_library.build_library(
        output=output,
        manifest=manifest,
        target_bytes=48 * 1024,
        volume_bytes=16 * 1024,
        progress_every=10,
    )
    count, total = markdown_library.verify_library(output, manifest)

    assert count == len(records) == 3
    assert total >= 48 * 1024
    assert all(path.suffix == ".md" for path in output.rglob("*") if path.is_file())
    assert "SHA-256" in manifest.read_text(encoding="utf-8")


def test_verify_detects_changed_volume(tmp_path: Path) -> None:
    output = tmp_path / "library" / "corpus"
    manifest = tmp_path / "library" / "MANIFEST.md"
    markdown_library.build_library(
        output=output,
        manifest=manifest,
        target_bytes=8 * 1024,
        volume_bytes=8 * 1024,
    )
    volume = next(output.rglob("*.md"))
    volume.write_text(volume.read_text(encoding="utf-8") + "\nbozuldu\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Boyut uyuşmazlığı"):
        markdown_library.verify_library(output, manifest)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1GiB", 1024**3),
        ("1 GB", 1000**3),
        ("2MiB", 2 * 1024**2),
        ("4096", 4096),
    ],
)
def test_parse_size(value: str, expected: int) -> None:
    assert markdown_library.parse_size(value) == expected


def test_choice_combinations_do_not_fall_into_short_cycle() -> None:
    combinations = {
        (
            markdown_library.choose(markdown_library.SCENARIOS, seed, 5),
            markdown_library.choose(markdown_library.AUDIENCES, seed + 3, 3),
            markdown_library.choose(markdown_library.SCALES, seed + 7, 5),
            markdown_library.choose(markdown_library.CONSTRAINTS, seed + 11, 3),
            markdown_library.choose(markdown_library.OUTPUTS, seed + 19, 7),
            markdown_library.choose(markdown_library.RISKS, seed + 23, 3),
        )
        for seed in range(256)
    }

    assert len(combinations) >= 250

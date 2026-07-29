from __future__ import annotations

from pathlib import Path

import pytest

from training.pack.verify_gguf import GIB, inspect_gguf


def test_inspect_gguf_accepts_matching_artifact(tmp_path: Path) -> None:
    model_path = tmp_path / "clarify.gguf"
    model_path.write_bytes(b"GGUF" + bytes(1020))
    target_gib = model_path.stat().st_size / GIB

    report = inspect_gguf(model_path, target_gib=target_gib, tolerance_gib=0)

    assert report.size_bytes == 1024
    assert report.size_gib == pytest.approx(target_gib)
    assert report.is_target_size


def test_inspect_gguf_reports_size_mismatch(tmp_path: Path) -> None:
    model_path = tmp_path / "small.gguf"
    model_path.write_bytes(b"GGUF")

    report = inspect_gguf(model_path, target_gib=4.5, tolerance_gib=0.75)

    assert not report.is_target_size


def test_inspect_gguf_rejects_wrong_magic(tmp_path: Path) -> None:
    model_path = tmp_path / "weights.bin"
    model_path.write_bytes(b"NOPE")

    with pytest.raises(ValueError, match="not a GGUF artifact"):
        inspect_gguf(model_path)


@pytest.mark.parametrize(
    ("target_gib", "tolerance_gib", "message"),
    [
        (0, 0.5, "target_gib"),
        (4.5, -0.1, "tolerance_gib"),
    ],
)
def test_inspect_gguf_rejects_invalid_limits(
    tmp_path: Path,
    target_gib: float,
    tolerance_gib: float,
    message: str,
) -> None:
    model_path = tmp_path / "clarify.gguf"
    model_path.write_bytes(b"GGUF")

    with pytest.raises(ValueError, match=message):
        inspect_gguf(model_path, target_gib=target_gib, tolerance_gib=tolerance_gib)

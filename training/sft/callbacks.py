"""Optional TrainerCallbacks for VRAM logging and simple early-stop."""

from __future__ import annotations

import subprocess

from rich.console import Console
from transformers import TrainerCallback

console = Console()


class VramSnapshotCallback(TrainerCallback):
    def __init__(self, every_n_steps: int = 50) -> None:
        self.every_n_steps = every_n_steps

    def on_step_end(self, args, state, control, **kwargs):  # noqa: D401
        if state.global_step % self.every_n_steps != 0:
            return
        try:
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5, check=False,
            )
            if out.returncode == 0:
                console.log(f"[step {state.global_step}] VRAM: {out.stdout.strip()}")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

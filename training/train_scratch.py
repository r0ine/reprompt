"""ClarifyGPT sifirdan egitim dongusu.

100k sentetik veri ile ozel transformer modelini egitir.
Gradient checkpointing + mixed precision ile RTX 4060 8GB'a sigar.

Kullanim:
    python -m training.train_scratch --config training/configs/scratch-base.yaml
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any

import click
import sentencepiece as spm
import torch
import torch.nn as nn
import yaml
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from torch.amp import GradScaler, autocast
from torch.utils.data import DataLoader, Dataset

console = Console()


class PromptDataset(Dataset):
    def __init__(
        self, jsonl_path: Path, tokenizer: spm.SentencePieceProcessor, max_len: int = 1024
    ):
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.samples = []

        bos = tokenizer.PieceToId("<|bos|>")
        eos = tokenizer.PieceToId("<|eos|>")
        im_start = tokenizer.PieceToId("<|im_start|>")
        im_end = tokenizer.PieceToId("<|im_end|>")
        sys_tok = tokenizer.PieceToId("<|system|>")
        usr_tok = tokenizer.PieceToId("<|user|>")
        asst_tok = tokenizer.PieceToId("<|assistant|>")

        system_msg = "Sen bir prompt muhendisisin. Kullanicinin ham girdisini, hedef LLM icin optimize edilmis yapisal bir prompta donustur."

        with jsonl_path.open(encoding="utf-8") as fh:
            for line in fh:
                rec = json.loads(line)
                raw_input = rec["input"]
                structured_output = rec["output"]
                target = rec.get("target", "generic")

                target_tok_name = f"<|{target}|>"
                target_id = tokenizer.PieceToId(target_tok_name)
                if target_id == tokenizer.unk_id():
                    target_id = None

                sys_ids = tokenizer.Encode(system_msg)
                inp_ids = tokenizer.Encode(raw_input)
                out_ids = tokenizer.Encode(structured_output)

                seq = [bos, im_start, sys_tok]
                if target_id is not None:
                    seq.append(target_id)
                seq.extend(sys_ids)
                seq.append(im_end)
                seq.extend([im_start, usr_tok])
                seq.extend(inp_ids)
                seq.append(im_end)
                seq.extend([im_start, asst_tok])

                prompt_len = len(seq)
                seq.extend(out_ids)
                seq.append(eos)

                if len(seq) > max_len:
                    seq = seq[:max_len]

                self.samples.append((seq, prompt_len))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        seq, prompt_len = self.samples[idx]
        input_ids = torch.tensor(seq[:-1], dtype=torch.long)
        labels = torch.tensor(seq[1:], dtype=torch.long)
        labels[: prompt_len - 1] = -100
        return {"input_ids": input_ids, "labels": labels}


def collate_fn(batch: list[dict[str, torch.Tensor]], pad_id: int = 0):
    max_len = max(item["input_ids"].size(0) for item in batch)
    input_ids = torch.full((len(batch), max_len), pad_id, dtype=torch.long)
    labels = torch.full((len(batch), max_len), -100, dtype=torch.long)

    for i, item in enumerate(batch):
        seq_len = item["input_ids"].size(0)
        input_ids[i, :seq_len] = item["input_ids"]
        labels[i, :seq_len] = item["labels"]

    return {"input_ids": input_ids, "labels": labels}


def cosine_lr(step: int, warmup: int, total: int, peak_lr: float, min_lr: float) -> float:
    if step < warmup:
        return peak_lr * step / max(warmup, 1)
    progress = (step - warmup) / max(total - warmup, 1)
    return min_lr + 0.5 * (peak_lr - min_lr) * (1 + math.cos(math.pi * progress))


@click.command()
@click.option("--config", "-c", default="training/configs/scratch-base.yaml")
@click.option("--resume", "-r", default=None, help="Checkpoint dosyasindan devam et")
def main(config: str, resume: str | None) -> None:
    with open(config, encoding="utf-8") as f:
        cfg_dict: dict[str, Any] = yaml.safe_load(f)

    from training.model.config import ClarifyConfig
    from training.model.transformer import ClarifyGPT

    model_cfg = ClarifyConfig(**cfg_dict.get("model", {}))
    train_cfg = cfg_dict.get("training", {})

    lr = float(train_cfg.get("lr", 3e-4))
    min_lr = float(train_cfg.get("min_lr", 1e-5))
    warmup_steps = train_cfg.get("warmup_steps", 500)
    epochs = train_cfg.get("epochs", 3)
    batch_size = train_cfg.get("batch_size", 8)
    grad_accum = train_cfg.get("grad_accum", 4)
    max_grad_norm = float(train_cfg.get("max_grad_norm", 1.0))
    save_every = train_cfg.get("save_every", 1000)
    eval_every = train_cfg.get("eval_every", 500)
    output_dir = Path(train_cfg.get("output_dir", "training/outputs/scratch"))
    use_checkpointing = train_cfg.get("gradient_checkpointing", False)

    tok_path = cfg_dict.get("tokenizer", "training/tokenizer/clarify_tok.model")

    console.print("[bold]ClarifyGPT — Sifirdan Egitim[/bold]")
    console.print(f"  Config: {config}")

    tokenizer = spm.SentencePieceProcessor()
    tokenizer.Load(tok_path)
    model_cfg.vocab_size = tokenizer.GetPieceSize()
    console.print(f"  Tokenizer: {tok_path} ({model_cfg.vocab_size} token)")

    model = ClarifyGPT(model_cfg, use_checkpointing=use_checkpointing)
    console.print(f"  Parametre: {model.param_count():,}")
    console.print(f"  Mimari: {model_cfg.n_layers}L / {model_cfg.n_heads}H / dim={model_cfg.dim}")
    if use_checkpointing:
        console.print("  [yellow]Gradient checkpointing aktif[/yellow]")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    console.print(f"  Cihaz: {device}")

    if torch.cuda.is_available():
        mem_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        console.print(f"  GPU: {torch.cuda.get_device_name(0)} ({mem_gb:.1f} GB)")

    train_data = PromptDataset(
        Path("training/datasets/train.jsonl"),
        tokenizer,
        model_cfg.max_seq_len,
    )
    val_data = PromptDataset(
        Path("training/datasets/val.jsonl"),
        tokenizer,
        model_cfg.max_seq_len,
    )

    console.print(f"  Egitim: {len(train_data):,} ornek | Dogrulama: {len(val_data):,} ornek")

    pad_id = tokenizer.PieceToId("<|pad|>")
    train_loader = DataLoader(
        train_data,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=lambda b: collate_fn(b, pad_id),
        num_workers=0,
        pin_memory=True,
    )
    val_loader = DataLoader(
        val_data,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=lambda b: collate_fn(b, pad_id),
        num_workers=0,
    )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=lr,
        betas=(0.9, 0.95),
        weight_decay=0.1,
    )

    total_steps = len(train_loader) * epochs // grad_accum
    use_amp = device.type == "cuda"
    scaler = GradScaler(enabled=use_amp)
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"  Toplam adim: {total_steps:,} | Warmup: {warmup_steps}")
    console.print()

    global_step = 0
    start_epoch = 1
    best_val_loss = float("inf")
    log_file = output_dir / "train_log.jsonl"

    if resume:
        ckpt = torch.load(resume, map_location=device, weights_only=False)
        model.load_state_dict(ckpt["model_state"])
        optimizer.load_state_dict(ckpt["optimizer_state"])
        global_step = ckpt["step"]
        start_epoch = ckpt["epoch"]
        console.print(
            f"  [cyan]Checkpoint yuklendi: step={global_step}, epoch={start_epoch}[/cyan]"
        )

    train_start = time.time()
    last_hourly_report = train_start
    hourly_report_num = 0

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats()

    for epoch in range(start_epoch, epochs + 1):
        model.train()
        epoch_loss = 0.0
        epoch_steps = 0
        tokens_seen = 0

        with Progress(
            TextColumn(f"Epoch {epoch}/{epochs}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeRemainingColumn(),
            console=console,
        ) as pbar:
            task = pbar.add_task("train", total=len(train_loader))

            for step_in_epoch, batch in enumerate(train_loader):
                input_ids = batch["input_ids"].to(device)
                labels = batch["labels"].to(device)

                current_lr = cosine_lr(global_step, warmup_steps, total_steps, lr, min_lr)
                for pg in optimizer.param_groups:
                    pg["lr"] = current_lr

                with autocast(
                    device_type=device.type, dtype=torch.float16, enabled=device.type == "cuda"
                ):
                    _, loss = model(input_ids, labels)
                    loss = loss / grad_accum

                scaler.scale(loss).backward()

                if (step_in_epoch + 1) % grad_accum == 0:
                    scaler.unscale_(optimizer)
                    nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad(set_to_none=True)
                    global_step += 1

                    raw_loss = loss.item() * grad_accum
                    epoch_loss += raw_loss
                    epoch_steps += 1
                    tokens_seen += input_ids.numel()

                    if global_step % 100 == 0:
                        step_metrics = {
                            "step": global_step,
                            "loss": round(raw_loss, 4),
                            "lr": round(current_lr, 8),
                            "epoch": epoch,
                            "elapsed_min": round((time.time() - train_start) / 60, 1),
                        }
                        if device.type == "cuda":
                            step_metrics["vram_gib"] = round(
                                torch.cuda.memory_allocated() / (1024**3),
                                2,
                            )
                            step_metrics["peak_vram_gib"] = round(
                                torch.cuda.max_memory_allocated() / (1024**3),
                                2,
                            )
                        with log_file.open("a", encoding="utf-8") as lf:
                            lf.write(json.dumps(step_metrics) + "\n")

                    if global_step % eval_every == 0:
                        val_loss = evaluate(model, val_loader, device)
                        elapsed_min = (time.time() - train_start) / 60
                        gpu_info = ""
                        if device.type == "cuda":
                            used = torch.cuda.memory_allocated() / (1024**3)
                            gpu_info = f" vram={used:.1f}GB"
                        console.print(
                            f"\n  [step {global_step}] train_loss={raw_loss:.4f} "
                            f"val_loss={val_loss:.4f} lr={current_lr:.2e} "
                            f"t={elapsed_min:.0f}min{gpu_info}"
                        )
                        if val_loss < best_val_loss:
                            best_val_loss = val_loss
                            save_checkpoint(
                                model, optimizer, global_step, epoch, output_dir / "best.pt"
                            )
                            console.print(
                                f"  [green]En iyi model kaydedildi (val={val_loss:.4f})[/green]"
                            )
                        model.train()

                    if global_step % save_every == 0:
                        save_checkpoint(
                            model,
                            optimizer,
                            global_step,
                            epoch,
                            output_dir / f"step_{global_step}.pt",
                        )

                    now = time.time()
                    if now - last_hourly_report >= 3600:
                        hourly_report_num += 1
                        _write_hourly_report(
                            output_dir,
                            hourly_report_num,
                            global_step,
                            total_steps,
                            raw_loss,
                            best_val_loss,
                            current_lr,
                            now - train_start,
                            tokens_seen,
                            device,
                        )
                        last_hourly_report = now

                pbar.update(task, advance=1)

        avg_loss = epoch_loss / max(epoch_steps, 1)
        console.print(f"\n  Epoch {epoch} bitti — avg_loss={avg_loss:.4f}, tokens={tokens_seen:,}")

    total_time = time.time() - train_start
    save_checkpoint(model, optimizer, global_step, epochs, output_dir / "final.pt")
    console.print(
        f"\n[green bold]Egitim tamamlandi! Toplam {global_step:,} adim, "
        f"{total_time / 60:.1f} dakika.[/green bold]"
    )
    console.print(f"  En iyi val loss: {best_val_loss:.4f}")
    console.print(f"  Cikti: {output_dir}")

    _write_final_report(
        output_dir,
        global_step,
        total_steps,
        best_val_loss,
        total_time,
        epochs,
        model.param_count(),
        config,
        device,
    )


@torch.inference_mode()
def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> float:
    model.eval()
    total_loss = 0.0
    count = 0
    for batch in loader:
        input_ids = batch["input_ids"].to(device)
        labels = batch["labels"].to(device)
        with autocast(device_type=device.type, dtype=torch.float16, enabled=device.type == "cuda"):
            _, loss = model(input_ids, labels)
        total_loss += loss.item()
        count += 1
    return total_loss / max(count, 1)


def save_checkpoint(
    model: nn.Module, optimizer: torch.optim.Optimizer, step: int, epoch: int, path: Path
) -> None:
    torch.save(
        {
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "step": step,
            "epoch": epoch,
        },
        path,
    )


def _gpu_stats() -> dict[str, float]:
    if not torch.cuda.is_available():
        return {}
    return {
        "vram_used_gb": round(torch.cuda.memory_allocated() / (1024**3), 2),
        "vram_peak_gb": round(torch.cuda.max_memory_allocated() / (1024**3), 2),
        "vram_total_gb": round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2),
    }


def _write_hourly_report(
    output_dir: Path,
    report_num: int,
    step: int,
    total_steps: int,
    last_loss: float,
    best_val: float,
    lr: float,
    elapsed_sec: float,
    tokens_seen: int,
    device: torch.device,
) -> None:
    progress_pct = step / max(total_steps, 1) * 100
    eta_min = (elapsed_sec / max(step, 1) * (total_steps - step)) / 60
    report = {
        "report": report_num,
        "step": step,
        "total_steps": total_steps,
        "progress_pct": round(progress_pct, 1),
        "last_train_loss": round(last_loss, 4),
        "best_val_loss": round(best_val, 4),
        "lr": round(lr, 8),
        "elapsed_min": round(elapsed_sec / 60, 1),
        "eta_min": round(eta_min, 1),
        "tokens_seen": tokens_seen,
    }
    report.update(_gpu_stats())
    path = output_dir / f"hourly_report_{report_num}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    console.print(f"\n  [cyan]Saatlik rapor #{report_num} kaydedildi: {path}[/cyan]")


def _write_final_report(
    output_dir: Path,
    total_steps: int,
    planned_steps: int,
    best_val_loss: float,
    total_time: float,
    epochs: int,
    param_count: int,
    config_path: str,
    device: torch.device,
) -> None:
    steps_per_sec = total_steps / max(total_time, 1)
    log_path = output_dir / "train_log.jsonl"
    loss_history = []
    if log_path.exists():
        with log_path.open(encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                loss_history.append(entry.get("loss", 0))

    report = {
        "model": {
            "parameters": param_count,
            "config": config_path,
        },
        "training": {
            "total_steps": total_steps,
            "epochs": epochs,
            "total_time_min": round(total_time / 60, 1),
            "steps_per_sec": round(steps_per_sec, 2),
        },
        "results": {
            "best_val_loss": round(best_val_loss, 4),
            "final_train_loss": round(loss_history[-1], 4) if loss_history else None,
            "initial_train_loss": round(loss_history[0], 4) if loss_history else None,
        },
        "device": {
            "type": device.type,
            "name": torch.cuda.get_device_name(0) if device.type == "cuda" else "cpu",
        },
    }
    report["device"].update(_gpu_stats())

    path = output_dir / "training_report.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    console.print(f"\n  [bold green]Final rapor: {path}[/bold green]")


if __name__ == "__main__":
    main()

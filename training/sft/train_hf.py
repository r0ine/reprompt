"""SFT training loop — standard HuggingFace (transformers + peft + trl).

Unsloth Windows'ta sorun cikarirsa bu script fallback olarak calisir.
Kullanim:
    python -m training.sft.train_hf --config training/configs/qwen2.5-3b-r16.yaml
"""

from __future__ import annotations

import json
from pathlib import Path

import click
import torch
import yaml
from rich.console import Console

from clarify_prompt.prompts.selector import select_system_prompt

console = Console()


@click.command()
@click.option("--config", "-c", type=click.Path(exists=True, path_type=Path), required=True)
def main(config: Path) -> None:
    cfg = yaml.safe_load(config.read_text(encoding="utf-8"))
    console.rule(f"[bold]clarify-prompt SFT (HF) — {cfg['base_model']}")

    device_info = f"CUDA: {torch.cuda.is_available()}"
    if torch.cuda.is_available():
        device_info += (
            f" | {torch.cuda.get_device_name(0)} | {torch.cuda.mem_get_info()[1] / 1024**3:.1f} GB"
        )
    console.print(f"[dim]{device_info}[/dim]")

    _train(cfg)


def _load_jsonl(path: str) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _train(cfg: dict) -> None:
    from datasets import Dataset
    from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    base_model = cfg["base_model"]

    if base_model.startswith("unsloth/"):
        base_model = base_model.replace("unsloth/", "").replace("-bnb-4bit", "")
        console.print(f"[yellow]Unsloth prefix temizlendi: {base_model}[/yellow]")

    bnb_config = None
    if cfg.get("load_in_4bit", False):
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )

    console.print(f"Model yukleniyor: {base_model}")
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True,
    )

    if cfg.get("load_in_4bit", False):
        model = prepare_model_for_kbit_training(model)

    lora_cfg = cfg["lora"]
    peft_config = LoraConfig(
        r=lora_cfg["r"],
        lora_alpha=lora_cfg["alpha"],
        lora_dropout=lora_cfg["dropout"],
        target_modules=lora_cfg["target_modules"],
        bias=lora_cfg["bias"],
        use_rslora=lora_cfg.get("use_rslora", False),
        task_type=TaskType.CAUSAL_LM,
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_records = _load_jsonl(cfg["data"]["train"])
    val_records = _load_jsonl(cfg["data"]["val"])

    def to_chatml(records: list[dict]) -> list[str]:
        texts = []
        for rec in records:
            system_prompt = select_system_prompt(
                rec.get("target", "generic"),
                task=rec.get("task", "auto"),
                detail=rec.get("detail", "balanced"),
            )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": rec["input"]},
                {"role": "assistant", "content": rec["output"]},
            ]
            text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=False
            )
            texts.append(text)
        return texts

    train_texts = to_chatml(train_records)
    val_texts = to_chatml(val_records)

    train_ds = Dataset.from_dict({"text": train_texts})
    val_ds = Dataset.from_dict({"text": val_texts})

    console.print(f"Train: {len(train_ds)} ornek, Val: {len(val_ds)} ornek")

    output_dir = cfg["output"]["dir"]
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    tcfg = cfg["training"]
    training_args = SFTConfig(
        output_dir=output_dir,
        num_train_epochs=tcfg["num_train_epochs"],
        per_device_train_batch_size=tcfg["per_device_train_batch_size"],
        gradient_accumulation_steps=tcfg["gradient_accumulation_steps"],
        warmup_steps=tcfg["warmup_steps"],
        learning_rate=tcfg["learning_rate"],
        lr_scheduler_type=tcfg["lr_scheduler_type"],
        weight_decay=tcfg["weight_decay"],
        seed=tcfg["seed"],
        logging_steps=max(1, tcfg["logging_steps"]),
        eval_strategy="steps",
        eval_steps=tcfg["eval_steps"],
        save_steps=tcfg["save_steps"],
        save_total_limit=2,
        optim=tcfg["optim"],
        bf16=tcfg["bf16"],
        fp16=tcfg["fp16"],
        max_seq_length=cfg["max_seq_length"],
        packing=tcfg.get("packing", False),
        report_to=["none"],
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        args=training_args,
    )

    console.print("[bold green]Egitim basliyor...[/bold green]")
    train_result = trainer.train()

    final_dir = str(Path(output_dir) / "final")
    trainer.save_model(final_dir)
    tokenizer.save_pretrained(final_dir)

    console.print("\n[green]Egitim tamamlandi![/green]")
    console.print(f"  Train loss: {train_result.training_loss:.4f}")
    console.print(f"  LoRA adapter: {final_dir}")

    metrics = trainer.evaluate()
    console.print(f"  Val loss: {metrics['eval_loss']:.4f}")

    metrics_path = Path(output_dir) / "train_metrics.json"
    with metrics_path.open("w", encoding="utf-8") as fh:
        json.dump(
            {
                "train_loss": round(train_result.training_loss, 4),
                "eval_loss": round(metrics["eval_loss"], 4),
                "epochs": tcfg["num_train_epochs"],
                "train_samples": len(train_ds),
                "val_samples": len(val_ds),
            },
            fh,
            indent=2,
        )
    console.print(f"  Metrikler: {metrics_path}")


if __name__ == "__main__":
    main()

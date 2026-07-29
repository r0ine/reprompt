"""SFT training loop — Unsloth + TRL SFTTrainer on QLoRA."""

from __future__ import annotations

from pathlib import Path

import click
import yaml
from rich.console import Console

from reprompt.prompts.selector import select_system_prompt

console = Console()


@click.command()
@click.option("--config", "-c", type=click.Path(exists=True, path_type=Path), required=True)
def main(config: Path) -> None:
    cfg = yaml.safe_load(config.read_text(encoding="utf-8"))
    console.rule(f"[bold]reprompt SFT — {cfg['base_model']}")
    _train(cfg)


def _train(cfg: dict) -> None:
    from datasets import load_dataset
    from trl import SFTConfig, SFTTrainer
    from unsloth import FastLanguageModel  # imported lazily; heavy

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=cfg["base_model"],
        max_seq_length=cfg["max_seq_length"],
        dtype=cfg.get("dtype"),
        load_in_4bit=cfg["load_in_4bit"],
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=cfg["lora"]["r"],
        lora_alpha=cfg["lora"]["alpha"],
        lora_dropout=cfg["lora"]["dropout"],
        target_modules=cfg["lora"]["target_modules"],
        bias=cfg["lora"]["bias"],
        use_gradient_checkpointing=cfg["lora"]["use_gradient_checkpointing"],
        use_rslora=cfg["lora"].get("use_rslora", False),
        random_state=cfg["training"]["seed"],
    )

    train_ds = load_dataset("json", data_files=cfg["data"]["train"], split="train")
    val_ds = load_dataset("json", data_files=cfg["data"]["val"], split="train")

    def format_chatml(example: dict) -> dict:
        system_prompt = select_system_prompt(
            example.get("target", "generic"),
            task=example.get("task", "auto"),
            detail=example.get("detail", "balanced"),
        )
        chat = tokenizer.apply_chat_template(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": example["input"]},
                {"role": "assistant", "content": example["output"]},
            ],
            tokenize=False,
            add_generation_prompt=False,
        )
        return {"text": chat}

    train_ds = train_ds.map(format_chatml, remove_columns=train_ds.column_names)
    val_ds = val_ds.map(format_chatml, remove_columns=val_ds.column_names)

    output_dir = cfg["output"]["dir"]
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        dataset_text_field="text",
        max_seq_length=cfg["max_seq_length"],
        packing=cfg["training"].get("packing", False),
        args=SFTConfig(
            output_dir=output_dir,
            num_train_epochs=cfg["training"]["num_train_epochs"],
            per_device_train_batch_size=cfg["training"]["per_device_train_batch_size"],
            gradient_accumulation_steps=cfg["training"]["gradient_accumulation_steps"],
            warmup_steps=cfg["training"]["warmup_steps"],
            learning_rate=cfg["training"]["learning_rate"],
            lr_scheduler_type=cfg["training"]["lr_scheduler_type"],
            weight_decay=cfg["training"]["weight_decay"],
            seed=cfg["training"]["seed"],
            logging_steps=cfg["training"]["logging_steps"],
            eval_steps=cfg["training"]["eval_steps"],
            save_steps=cfg["training"]["save_steps"],
            optim=cfg["training"]["optim"],
            bf16=cfg["training"]["bf16"],
            fp16=cfg["training"]["fp16"],
            report_to=["none"],
        ),
    )

    trainer.train()
    trainer.save_model(str(Path(output_dir) / "final"))
    console.print(f"[green]LoRA adapter kaydedildi -> {output_dir}/final[/green]")


if __name__ == "__main__":
    main()

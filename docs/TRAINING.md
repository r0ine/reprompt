# Kendi clarify-prompt modelini eğit

Bu rehber, aynı pipeline'ı kendi verinle koşturmak isteyen geliştiriciler için.

## Donanım

- NVIDIA GPU, 8 GB+ VRAM. RTX 3060, 4060, 4070 laptop hepsi çalışır.
- 16 GB+ sistem RAM'i.
- 30 GB+ disk alanı.
- CUDA 12.4+ driver.

## Ortam

```bash
# Windows
.\training\scripts\setup_env.ps1
# WSL2 / Linux
bash training/scripts/setup_env.sh
```

## Veri seti oluşturma

```bash
# 1. El yapımı altın örnekleri import et
python -m training.data.import_gold

# 2. Kendi transkriptlerini süz
python -m training.data.harvest_transcripts

# 3. Açık kaynak datasetlerden seed al
python -m training.data.harvest_shared_datasets

# 4. Teacher distillation (Claude Opus 4.7 API — para ister)
python -m training.data.distill_teacher --dry-run   # önce maliyet göster
python -m training.data.distill_teacher --limit 100 # önce küçük test
python -m training.data.distill_teacher              # tümü

# 5. Birleştir + dedup + split
python -m training.data.merge_dedup
python -m training.data.split_train_val_test
python -m training.data.tokenize_stats               # uzunluk histogramı
```

Tek satırda:

```bash
python -m training.data.build --all
```

## Fine-tune

```bash
# Pilot (3B, 1 epoch) — 30-45 dk
python -m training.sft.train --config training/configs/qwen2.5-3b-r16.yaml

# Tam (7B, 3 epoch) — 2-3 saat, RTX 4060'ta sınırda
python -m training.sft.train --config training/configs/qwen2.5-7b-r16.yaml
```

`nvidia-smi -l 5` ile VRAM izle.

## Değerlendirme

```bash
python -m training.eval.run --model training/outputs/qwen2.5-7b-r16/final
python -m training.eval.spot_check --report training/eval/reports/report-XXXX.jsonl
```

## Paketleme

```bash
python -m training.pack.merge_lora --adapter training/outputs/qwen2.5-7b-r16/final
python -m training.pack.convert_to_gguf --model training/outputs/merged --quant q4_k_m
```

## Yayın (HF Hub)

```bash
python -m training.pack.push_hf --repo <ORG>/clarify-prompt-qwen2.5-7b-v1 \
    --path training/outputs/gguf
```

## Sorun giderme

- **OOM:** `training/configs/*.yaml` içinde `per_device_train_batch_size: 1`, `max_seq_length: 1024` yap.
- **Unsloth import hatası (Windows):** WSL2'ye geç, `bash training/scripts/setup_env.sh`.
- **CUDA sürüm uyumsuzluğu:** PyTorch'u driver sürümüne göre yeniden kur.
- **bitsandbytes çökmesi:** `pip install bitsandbytes-windows` fallback.

Detaylı hata katalogu: [../PLAN.md](../PLAN.md) §14.

# Kendi reprompt modelini eğit

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

# Üretim (7B, rank 32 rsLoRA, 4096 context)
python -m training.sft.train --config training/configs/qwen2.5-7b-production.yaml
```

Üretim profili RTX 4060 8 GB için batch size 1, gradient accumulation 8, 4-bit NF4 ve
gradient checkpointing kullanır. Süre veri seti boyutuna bağlıdır; tam koşudan önce
`training/configs/qwen2.5-3b-pilot.yaml` ile veri ve format kontrolü yap.

`nvidia-smi -l 5` ile VRAM izle. OOM durumunda ilk olarak `max_seq_length` değerini 3072'ye
indir; çekirdek sistem promptunu eski kısa kopyayla değiştirme. Eğitim ve çıkarım aynı
`select_system_prompt()` derleyicisini kullanmalıdır.

## Değerlendirme

```bash
python -m training.eval.run --model training/outputs/qwen2.5-7b-production/final
python -m training.eval.spot_check --report training/eval/reports/report-XXXX.jsonl
```

## Paketleme

```bash
python -m training.pack.merge_lora \
  --adapter training/outputs/qwen2.5-7b-production/final \
  --out training/outputs/qwen2.5-7b-merged

python -m training.pack.convert_to_gguf \
  --model training/outputs/qwen2.5-7b-merged \
  --quant q4_k_m \
  --out training/outputs/gguf

python -m training.pack.verify_gguf \
  training/outputs/gguf/reprompt-qwen2.5-7b-q4_k_m.gguf \
  --target-gib 4.5 \
  --tolerance-gib 0.75
```

Q4_K_M dosyası dönüştürücü sürümüne göre yaklaşık 4–5 GiB çıkar. `verify_gguf`, GGUF
başlığını ve boyut aralığını kontrol eder; model kalitesi için değerlendirme komutlarının
yerine geçmez.

## Yayın (HF Hub)

```bash
python -m training.pack.push_hf --repo <ORG>/reprompt-qwen2.5-7b-v1 \
    --path training/outputs/gguf
```

## Sorun giderme

- **OOM:** batch size zaten 1 ise `max_seq_length` değerini 3072 veya 2048'e indir.
- **Unsloth import hatası (Windows):** WSL2'ye geç, `bash training/scripts/setup_env.sh`.
- **CUDA sürüm uyumsuzluğu:** PyTorch'u driver sürümüne göre yeniden kur.
- **bitsandbytes çökmesi:** `pip install bitsandbytes-windows` fallback.

Detaylı hata katalogu: [../PLAN.md](../PLAN.md) §14.

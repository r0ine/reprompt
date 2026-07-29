# Hızlı Başlangıç

> **Not:** Şu an proje Faz 0'da. Model henüz eğitilmedi; aşağıdaki adımlar iskelet
> üzerinde çalışır ama gerçek çıkarım için Faz 4 sonrası GGUF dosyası gerekir.

## Ön koşullar

- Python 3.10-3.12 (3.12 önerilir)
- Windows 11 / Linux / WSL2
- NVIDIA GPU (isteğe bağlı — sadece inference için CPU da yeter, ama yavaş)

## Sadece kullanıcı (inference) tarafı

```bash
git clone https://github.com/clarify/clarify-prompt.git
cd clarify-prompt
python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
# Linux / WSL
source .venv/bin/activate

pip install -e .
```

Bu kadar. Test:

```bash
clarify-prompt --version
clarify-prompt --help
```

## Model dosyası

Model henüz release edilmedi. Faz 4 sonrası:

```bash
huggingface-cli download clarify/clarify-prompt-qwen2.5-7b-v1 \
    --include "*.gguf" \
    --local-dir ~/.clarify-prompt/models
export CLARIFY_PROMPT_MODEL_PATH=~/.clarify-prompt/models/clarify-prompt-qwen2.5-7b-q4_k_m.gguf
```

## Kullanım

```bash
clarify-prompt "reflection kodu patliyor duzelt"

clarify-prompt --target chatgpt "long messy request"

echo "uzun karışık istek" | clarify-prompt --stdin --target cursor

clarify-prompt --explain "..."   # değişikliklerin özetini de göster
clarify-prompt --json "..."      # JSON çıktı
```

## Geliştirici / eğitim tarafı

Sadece proje üzerinde çalışacaksan:

```bash
pip install -e ".[dev]"
pip install torch --index-url https://download.pytorch.org/whl/cu124
pip install -e "./training[unsloth-cu124]"
```

Windows kısayolu:

```powershell
.\training\scripts\setup_env.ps1
```

WSL / Linux:

```bash
bash training/scripts/setup_env.sh
```

## Faz akışı (uygulama sırası)

1. `make data` — Faz 1, veri seti oluşturma
2. `make train` — Faz 2, ilk fine-tune (Qwen 2.5 7B)
3. `make eval` — Faz 3, değerlendirme + spot-check
4. `make pack` — Faz 4, GGUF paketleme

Tam plan: [../PLAN.md](../PLAN.md).

## Test

```bash
make test          # birim testler
make test-slow     # entegrasyon testleri (llama.cpp gerekir)
```

## Sorun giderme

- `CLARIFY_PROMPT_MODEL_PATH` bulunamadı hatası: `.env`'i doldur veya `--model` bayrağını kullan.
- `llama-cli not on PATH`: `PROMPTSMITH_LLAMA_BIN` yerine `CLARIFY_PROMPT_LLAMA_BIN` kullan, yolu ver.
- Windows'ta Unsloth kurulumu başarısız: `bash training/scripts/setup_env.sh` (WSL2 fallback).

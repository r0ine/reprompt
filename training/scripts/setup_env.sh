#!/usr/bin/env bash
# WSL2 / Linux fallback. Windows'ta Unsloth kurulumu takilirsa bunu WSL'de calistir.
set -euo pipefail

echo "=== clarify-prompt: egitim ortami kurulumu (WSL2 / Linux) ==="

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 yok. Once python3.12 kur." >&2
    exit 1
fi

if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "nvidia-smi yok. WSL2'de NVIDIA CUDA driver kurulmali." >&2
    exit 1
fi
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

python -m pip install --upgrade pip

pip install -e .

pip install torch --index-url https://download.pytorch.org/whl/cu124

pip install -e "./training[unsloth-cu124]"

python -c "import torch; print('cuda:', torch.cuda.is_available()); print('device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'yok')"

echo "=== Kurulum tamam. Sonraki adim: make data ==="

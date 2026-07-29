# Windows PowerShell — clarify-prompt egitim ortami kurulumu.
# Kullanim: PowerShell'de yonetici degil, normal sekilde:  .\training\scripts\setup_env.ps1
$ErrorActionPreference = "Stop"

Write-Host "=== clarify-prompt: egitim ortami kurulumu (Windows) ===" -ForegroundColor Cyan

# 1) Python surumu kontrol
$py = python --version 2>$null
if (-not $py) {
    Write-Host "Python bulunamadi. Python 3.12 kurup PATH'e ekleyin." -ForegroundColor Red
    exit 1
}
Write-Host "Python: $py"

# 2) CUDA sürüm kontrol
try {
    $nvcc = nvcc --version 2>$null
    if ($nvcc) { Write-Host "CUDA nvcc bulundu." }
} catch {
    Write-Host "nvcc yok — CUDA Toolkit yuklu degil olabilir." -ForegroundColor Yellow
}

# 3) nvidia-smi ile GPU kontrol
try {
    $gpu = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    Write-Host "GPU: $gpu"
} catch {
    Write-Host "nvidia-smi calismadi. NVIDIA driver'i ve GPU kontrol edin." -ForegroundColor Red
    exit 1
}

# 4) venv olustur
if (-not (Test-Path .venv)) {
    Write-Host "venv olusturuluyor (.venv)..." -ForegroundColor Cyan
    python -m venv .venv
}
& .venv\Scripts\Activate.ps1

# 5) pip guncel
python -m pip install --upgrade pip

# 6) Inference (kucuk) bagimliliklar
Write-Host "Inference bagimliliklari yukleniyor..." -ForegroundColor Cyan
pip install -e .

# 7) PyTorch CUDA 12.4 wheel (Unsloth ile hizali)
Write-Host "PyTorch CUDA 12.4 wheel yukleniyor..." -ForegroundColor Cyan
pip install torch --index-url https://download.pytorch.org/whl/cu124

# 8) Training agir bagimliliklari (Unsloth ust wheel'i git+URL uzerinden)
Write-Host "Egitim bagimliliklari (unsloth dahil) yukleniyor..." -ForegroundColor Cyan
pip install -e "./training[unsloth-cu124]"

# 9) GPU / torch dogrulama
Write-Host "torch CUDA testi..." -ForegroundColor Cyan
python -c "import torch; print('cuda:', torch.cuda.is_available()); print('device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'yok')"

Write-Host "=== Kurulum tamam. Sonraki adim: make data ===" -ForegroundColor Green

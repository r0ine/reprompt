@echo off
echo ============================================
echo ClarifyGPT - Sifirdan Egitim Pipeline
echo ============================================
echo.

set VENV=.train-venv\Scripts\python.exe

echo [1/4] Veri seti kontrol...
%VENV% -c "from pathlib import Path; assert Path('training/datasets/train.jsonl').exists(), 'train.jsonl yok!'; print('OK')"
if errorlevel 1 (
    echo Veri seti bulunamadi. Once veri uretin:
    echo   %VENV% -m training.data.generate_synthetic --count 100000
    echo   %VENV% -m training.data.split
    exit /b 1
)

echo [2/4] Tokenizer kontrol...
%VENV% -c "from pathlib import Path; assert Path('training/tokenizer/clarify_tok.model').exists(), 'Tokenizer yok!'; print('OK')"
if errorlevel 1 (
    echo Tokenizer bulunamadi. Once egitim:
    echo   %VENV% -m training.tokenizer.train_tokenizer --vocab-size 12000
    exit /b 1
)

echo [3/4] PyTorch CUDA kontrol...
%VENV% -c "import torch; assert torch.cuda.is_available(), 'CUDA yok!'; print(f'GPU: {torch.cuda.get_device_name(0)}')"
if errorlevel 1 (
    echo CUDA bulunamadi! PyTorch CUDA yukleyin:
    echo   %VENV% -m pip install torch --index-url https://download.pytorch.org/whl/cu121
    exit /b 1
)

echo [4/4] Model egitimi basliyor...
echo Config: training/configs/scratch-large.yaml
echo.
%VENV% -m training.train_scratch --config training/configs/scratch-large.yaml

echo.
echo Egitim tamamlandi!
pause

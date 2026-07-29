@echo off
chcp 65001 >nul
title ClarifyGPT Egitim

echo ============================================
echo   ClarifyGPT XLARGE - Egitim Baslatici
echo ============================================
echo.

set VENV=.train-venv\Scripts\python.exe
set CONFIG=training/configs/scratch-xlarge.yaml
set CHECKPOINT=training/outputs/scratch-xlarge/best.pt

if not exist "%VENV%" (
    echo [HATA] Virtual environment bulunamadi: %VENV%
    echo Once venv kurulumu yapin.
    pause
    exit /b 1
)

echo [1] Sifirdan baslat
echo [2] Checkpoint'tan devam et (best.pt)
echo [3] Belirli checkpoint'tan devam et
echo.
set /p SECIM="Seciminiz (1/2/3): "

if "%SECIM%"=="1" (
    echo.
    echo Sifirdan egitim baslatiliyor...
    echo Durdurmak icin: Ctrl+C veya pencereyi kapat
    echo.
    "%VENV%" -m training.train_scratch -c %CONFIG%
) else if "%SECIM%"=="2" (
    if not exist "%CHECKPOINT%" (
        echo [HATA] best.pt bulunamadi. Once sifirdan baslatmaniz gerekiyor.
        pause
        exit /b 1
    )
    echo.
    echo Checkpoint'tan devam ediliyor: %CHECKPOINT%
    echo.
    "%VENV%" -m training.train_scratch -c %CONFIG% -r %CHECKPOINT%
) else if "%SECIM%"=="3" (
    set /p CKPT="Checkpoint dosya yolu: "
    echo.
    echo Devam ediliyor: %CKPT%
    echo.
    "%VENV%" -m training.train_scratch -c %CONFIG% -r %CKPT%
) else (
    echo Gecersiz secim.
)

echo.
echo Egitim tamamlandi veya durduruldu.
pause

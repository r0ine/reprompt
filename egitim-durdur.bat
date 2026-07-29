@echo off
chcp 65001 >nul
title ClarifyGPT Egitim - Durdur

echo Egitim sureci araniyor...
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /fi "windowtitle eq ClarifyGPT*" /fo list ^| findstr "PID"') do (
    echo Durduruluyor: PID %%a
    taskkill /pid %%a /f >nul 2>&1
)

REM Fallback: train_scratch calistiran python sureclerini bul
wmic process where "commandline like '%%train_scratch%%'" get processid 2>nul | findstr /r "[0-9]" >nul
if %errorlevel%==0 (
    for /f %%p in ('wmic process where "commandline like '%%train_scratch%%'" get processid ^| findstr /r "[0-9]"') do (
        echo Durduruluyor: PID %%p
        taskkill /pid %%p /f >nul 2>&1
    )
)

echo.
echo Egitim durduruldu. Checkpoint'lar training/outputs/scratch-xlarge/ altinda.
echo Devam ettirmek icin egitim-baslat.bat'i calistirip secim 2'yi secin.
pause

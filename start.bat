@echo off
title Image Craft AI
echo ===================================
echo     Starting Image Craft AI
echo ===================================
echo.
python -m src.ui.app
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to start. Make sure you have activated the conda environment:
    echo        conda activate imagecraft
    echo.
    pause
)

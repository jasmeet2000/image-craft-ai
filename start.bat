@echo off
title Image Craft AI
echo ===================================
echo     Starting Image Craft AI
echo ===================================
echo.

:: Attempt to activate the conda environment
call conda activate imagecraft 2>nul
if %ERRORLEVEL% NEQ 0 (
    :: Fallback to explicit path for the user
    if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
        call "%USERPROFILE%\anaconda3\Scripts\activate.bat" imagecraft
    ) else if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
        call "%USERPROFILE%\miniconda3\Scripts\activate.bat" imagecraft
    ) else (
        echo [ERROR] Could not find conda. Please open Anaconda Prompt,
        echo type 'conda activate imagecraft', and then run 'python -m src.ui.app'.
        pause
        exit /b 1
    )
)

:: Run the app
python -m src.ui.app
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] The application stopped unexpectedly.
    pause
)

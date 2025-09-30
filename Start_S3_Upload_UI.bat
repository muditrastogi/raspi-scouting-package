@echo off
title S3 Upload Manager
echo.
echo ========================================
echo    S3 Upload Manager - Starting...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if required Python packages are installed
echo Checking Python dependencies...
python -c "import boto3, tkinter" >nul 2>&1
if errorlevel 1 (
    echo Installing required Python packages...
    pip install boto3
    if errorlevel 1 (
        echo ERROR: Failed to install boto3
        pause
        exit /b 1
    )
)

REM Check if config file exists
if not exist "config.txt" (
    echo ERROR: config.txt file not found
    echo Please ensure config.txt exists in the same directory
    pause
    exit /b 1
)

REM Start the S3 Upload UI
echo Starting S3 Upload UI...
python s3_upload_ui.py

if errorlevel 1 (
    echo.
    echo ERROR: S3 Upload UI encountered an error
    pause
)

echo.
echo S3 Upload Manager closed.
pause

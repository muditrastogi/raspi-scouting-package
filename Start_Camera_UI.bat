@echo off
title Raspberry Pi Scouting Package - Windows UI
color 0A

echo ================================================================
echo          Raspberry Pi Scouting Package - Windows UI
echo ================================================================
echo.
echo [INFO] Starting camera interface...
echo [INFO] Make sure your USB cameras are connected
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    echo.
    pause
    exit /b 1
)

REM Check if main script exists
if not exist "simple_windows_ui.py" (
    echo [ERROR] simple_windows_ui.py not found
    echo Please ensure you're running this from the correct directory
    echo.
    pause
    exit /b 1
)

REM Check if cameras are configured
if not exist "config.txt" (
    echo [WARNING] config.txt not found
    echo [INFO] Run Configure_Cameras.bat first to set up camera positions
    echo.
    pause
)

REM Start the application
echo [INFO] Loading camera configuration...
echo [INFO] Only USB cameras from config.txt will be used
echo [INFO] Close the camera window to exit
echo.
python simple_windows_ui.py

echo.
echo [INFO] Camera UI has closed
pause

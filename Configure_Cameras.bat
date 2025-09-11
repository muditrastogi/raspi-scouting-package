@echo off
title Camera Configuration Tool
color 0B

echo ================================================================
echo            Camera Configuration Tool
echo         Raspberry Pi Scouting Package (Windows)
echo ================================================================
echo.
echo This tool will help you configure camera positions:
echo   • Bottom Camera
echo   • Middle Camera  
echo   • Top Camera
echo.
echo IMPORTANT: This tool only detects USB cameras.
echo           System/integrated webcams are ignored for safety.
echo.
echo Make sure all USB cameras are connected before proceeding.
echo.
pause

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

REM Check if configuration script exists
if not exist "windows_configure_cameras.py" (
    echo [ERROR] windows_configure_cameras.py not found
    echo Please ensure you're running this from the correct directory
    echo.
    pause
    exit /b 1
)

REM Run configuration tool
echo [INFO] Starting camera configuration tool...
python windows_configure_cameras.py

echo.
echo [INFO] Configuration complete!
echo [INFO] Device IDs have been saved to config.txt
echo [INFO] You can now run the camera UI using Start_Camera_UI.bat
echo.
pause

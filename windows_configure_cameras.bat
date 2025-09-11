@echo off
REM Windows Camera Configuration Script
REM Batch wrapper for the Python camera configuration tool

setlocal enabledelayedexpansion

echo ================================================================
echo             Windows Camera Configuration Tool
echo             Raspberry Pi Scouting Package (Windows)
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.6 or later from https://python.org
    echo.
    pause
    exit /b 1
)

REM Check if the Python script exists
if not exist "windows_configure_cameras.py" (
    echo [ERROR] windows_configure_cameras.py not found
    echo Please ensure you're running this from the correct directory
    echo.
    pause
    exit /b 1
)

echo [INFO] Starting Windows camera configuration...
echo [INFO] This tool will help you configure camera positions using Windows device IDs
echo.

REM Run the Python script
python windows_configure_cameras.py

echo.
echo [INFO] Camera configuration tool finished
pause

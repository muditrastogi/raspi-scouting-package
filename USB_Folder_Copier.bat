@echo off
title USB Folder Copier - Scout Videos Transfer
color 0B

echo ================================================================
echo              USB Folder Copier - Scout Videos Transfer
echo         Raspberry Pi Scouting Package (Windows)
echo ================================================================
echo.
echo This tool helps you copy scout video folders to USB drives.
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if PowerShell script exists
if not exist "USB_Folder_Copier_GUI.ps1" (
    echo [ERROR] USB_Folder_Copier_GUI.ps1 not found
    echo Please ensure you're running this from the correct directory
    echo.
    pause
    exit /b 1
)

echo [INFO] Starting USB Folder Copier GUI...
echo [INFO] This will open a graphical interface for folder selection and USB copying
echo.

REM Run the PowerShell GUI
powershell -ExecutionPolicy Bypass -File USB_Folder_Copier_GUI.ps1

echo.
echo [INFO] USB Folder Copier has closed
pause

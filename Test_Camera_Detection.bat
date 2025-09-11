@echo off
title Camera Detection Test
color 0E

echo ================================================================
echo              Camera Detection Test
echo         Raspberry Pi Scouting Package (Windows)
echo ================================================================
echo.
echo This tool will test:
echo   • Windows camera detection (wmic command)
echo   • OpenCV camera access
echo   • USB camera identification
echo   • System vs USB camera differentiation
echo.
echo This helps troubleshoot camera detection issues.
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

REM Check if test script exists
if not exist "test_windows_camera_detection.py" (
    echo [ERROR] test_windows_camera_detection.py not found
    echo Please ensure you're running this from the correct directory
    echo.
    pause
    exit /b 1
)

REM Run test script
echo [INFO] Starting camera detection test...
echo [INFO] This may take a few moments...
echo.
python test_windows_camera_detection.py

echo.
echo [INFO] Test complete
echo [INFO] If you found issues, check the troubleshooting section in PROJECT_SETUP_GUIDE.md
pause

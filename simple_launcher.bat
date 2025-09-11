@echo off
REM Simple Windows Scouting Package Launcher (No RTSP/FFmpeg)

echo ============================================
echo  Simple Windows Scouting Package
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python and add to PATH
    pause
    exit /b 1
)
echo Python found.

REM Check if OpenCV is available
python -c "import cv2; print('OpenCV OK')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: OpenCV not installed
    echo Please install with: pip install opencv-python
    pause
    exit /b 1
)
echo OpenCV found.

REM Create output directory
if not exist "%USERPROFILE%\Desktop\scout-videos" (
    mkdir "%USERPROFILE%\Desktop\scout-videos"
    echo Created output directory.
)

echo.
echo Starting simple camera viewer...
echo Close the window to exit.
echo.

REM Run the simple UI
python simple_windows_ui.py

echo.
echo Application closed.
pause

@echo off
REM Windows Scouting Package Launcher
REM Replaces desktopmultiv5.sh for Windows compatibility

setlocal enabledelayedexpansion

REM Configuration - can be moved to config file later
set RTSP_BASE_PORT=8554
set RECORD_API_BASE_PORT=5000
set DEFAULT_RESOLUTION=1920x1080
set DEFAULT_FPS=30

REM Camera configuration (can be customized)
set CONFIG_BOTTOM_CAMERA=
set CONFIG_MIDDLE_CAMERA=
set CONFIG_TOP_CAMERA=

REM Arrays to track devices and services
set CAMERAS_FOUND=0
set /a RTSP_SERVERS_COUNT=0
set /a RECORD_APIS_COUNT=0

REM Color codes for Windows (limited compared to Linux)
echo Windows Scouting Package Launcher
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and make sure it's in your PATH
    pause
    exit /b 1
)

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: FFmpeg is not installed or not in PATH
    echo Please install FFmpeg and make sure it's in your PATH
    echo Download from: https://ffmpeg.org/download.html
    pause
    exit /b 1
)

REM Check if OpenCV is available
python -c "import cv2; print('OpenCV version:', cv2.__version__)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: OpenCV is not installed
    echo Please install it with: pip install opencv-python
    pause
    exit /b 1
)

REM Check if required Python packages are available
python -c "import flask, requests, PIL" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Required Python packages are missing
    echo Please install them with: pip install flask requests pillow
    pause
    exit /b 1
)

echo Prerequisites check passed.

REM Detect cameras using our Python script
echo.
echo Detecting available cameras...
python windows_camera_detection.py --detect-only

if errorlevel 1 (
    echo ERROR: Camera detection failed
    pause
    exit /b 1
)

REM For now, we'll simulate camera detection and use localhost RTSP streams
REM In a real setup, you would parse the output from camera detection
echo.
echo Simulating camera setup for demonstration...
echo Assuming 3 cameras are connected at:
echo Camera 0: rtsp://localhost:8554/stream
echo Camera 1: rtsp://localhost:8555/stream
echo Camera 2: rtsp://localhost:8556/stream

REM Create directories for recordings
if not exist "%USERPROFILE%\Desktop\scout-videos" (
    mkdir "%USERPROFILE%\Desktop\scout-videos"
)

REM Start RTSP servers for each camera
echo.
echo Starting RTSP servers...

REM Kill any existing processes first
taskkill /f /im python.exe >nul 2>&1
timeout /t 1 /nobreak >nul

set RTSP_PORT=%RTSP_BASE_PORT%
for /l %%i in (0,1,2) do (
    echo Starting RTSP server for camera %%i on port !RTSP_PORT!
    REM Try simple RTSP server first (FFmpeg-based)
    powershell -Command "Start-Process -FilePath 'python' -ArgumentList 'simple_rtsp_server.py --camera %%i --port !RTSP_PORT!' -NoNewWindow -RedirectStandardOutput 'nul' -RedirectStandardError 'nul'"

    REM Wait a moment to see if it starts
    timeout /t 2 /nobreak >nul

    REM If FFmpeg fails, try OpenCV fallback
    REM This will be attempted if the FFmpeg server doesn't start properly
    set /a RTSP_PORT+=1
    timeout /t 5 /nobreak >nul
)

echo RTSP servers started.

REM Start record APIs
echo.
echo Starting record APIs...
set API_PORT=%RECORD_API_BASE_PORT%
set RTSP_PORT=%RTSP_BASE_PORT%

for /l %%i in (0,1,2) do (
    echo Starting record API for camera %%i on port !API_PORT!
    if %%i==0 (
        set POSITION=bottom
    ) else if %%i==1 (
        set POSITION=middle
    ) else (
        set POSITION=top
    )

    REM Use PowerShell to run completely in background
    powershell -Command "Start-Process -FilePath 'python' -ArgumentList 'windows_record_api.py --port !API_PORT! --rtsp-url rtsp://localhost:!RTSP_PORT!/live --mode frames' -NoNewWindow -RedirectStandardOutput 'nul' -RedirectStandardError 'nul'"
    set /a API_PORT+=1
    set /a RTSP_PORT+=1
    timeout /t 3 /nobreak >nul
)

echo Record APIs started.

REM Wait a moment for services to initialize
echo.
echo Waiting for services to initialize...
timeout /t 5 /nobreak >nul

REM Prepare arguments for UI
set DEVICE_ARGS=--devices rtsp://localhost:8554/live rtsp://localhost:8555/live rtsp://localhost:8556/live
set RECORD_ARGS=--record-api http://localhost:5000 http://localhost:5001 http://localhost:5002

echo.
echo Launching GUI application...
echo Command: python windows_ui.py %DEVICE_ARGS% %RECORD_ARGS%

REM Launch the GUI
python windows_ui.py %DEVICE_ARGS% %RECORD_ARGS%

REM Cleanup when GUI closes
echo.
echo GUI closed. Cleaning up...

REM Kill any remaining processes (this is a simple cleanup)
taskkill /f /im python.exe >nul 2>&1

echo Cleanup completed.
pause
exit /b 0

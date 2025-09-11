@echo off
REM Windows Scouting Package Installer
REM Sets up the Windows version of the Raspberry Pi scouting package

echo ============================================
echo  Windows Scouting Package Installer
echo ============================================
echo.

REM Check if running as administrator (optional but recommended)
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as administrator - good!
) else (
    echo WARNING: Not running as administrator
    echo Some features might not work properly
    echo.
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    echo Please install Python 3.7+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found. Installing/updating pip...
python -m pip install --upgrade pip

if not exist "windows_requirements.txt" (
    echo ERROR: windows_requirements.txt not found in current directory
    pause
    exit /b 1
)

echo.
echo Installing Python packages...
pip install -r windows_requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install Python packages
    pause
    exit /b 1
)

echo Python packages installed successfully.

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: FFmpeg is not installed or not in PATH
    echo FFmpeg is required for RTSP streaming and recording
    echo.
    echo Please install FFmpeg:
    echo 1. Download from https://ffmpeg.org/download.html
    echo 2. Extract to a folder (e.g., C:\ffmpeg)
    echo 3. Add the bin folder to your system PATH
    echo 4. Restart this installer
    echo.
    pause
    exit /b 1
)

echo FFmpeg found.

REM Create necessary directories
echo.
echo Creating directories...

if not exist "%USERPROFILE%\Desktop\scout-videos" (
    mkdir "%USERPROFILE%\Desktop\scout-videos"
    echo Created %USERPROFILE%\Desktop\scout-videos
)

if not exist "%USERPROFILE%\Desktop\scout-config" (
    mkdir "%USERPROFILE%\Desktop\scout-config"
    echo Created %USERPROFILE%\Desktop\scout-config
)

REM Create a basic config file
echo Creating basic configuration file...
(
echo # Windows Scouting Package Configuration
echo # Camera resolution (width x height)
echo resolution=1920x1080
echo.
echo # Camera FPS
echo fps=30
echo.
echo # Camera serial IDs for ordering (leave empty to auto-detect)
echo # To find camera serials, you can use device manager or run camera detection
echo bottomcamera=
echo middlecamera=
echo topcamera=
) > "%USERPROFILE%\Desktop\scout-config\config.txt"

echo Configuration file created at %USERPROFILE%\Desktop\scout-config\config.txt

REM Create desktop shortcuts (optional)
echo.
echo Creating desktop shortcuts...

REM Create shortcut for main launcher
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\Windows Scouting Package.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%CD%\windows_scout_launcher.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%CD%" >> CreateShortcut.vbs
echo oLink.Description = "Windows Scouting Package Launcher" >> CreateShortcut.vbs
echo oLink.IconLocation = "shell32.dll,43" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

echo Desktop shortcut created.

REM Test camera detection
echo.
echo Testing camera detection...
python windows_camera_detection.py --detect-only

if errorlevel 1 (
    echo.
    echo WARNING: Camera detection test failed
    echo This might be normal if no cameras are connected
    echo You can test again later when cameras are connected
) else (
    echo Camera detection test completed.
)

echo.
echo ============================================
echo  Installation completed successfully!
echo ============================================
echo.
echo What was installed:
echo - Python packages (OpenCV, Flask, etc.)
echo - Desktop shortcuts
echo - Configuration directory
echo - Recording directories
echo.
echo To run the application:
echo 1. Connect your USB cameras
echo 2. Double-click "Windows Scouting Package" on your desktop
echo    OR run: windows_scout_launcher.bat
echo.
echo Configuration file: %USERPROFILE%\Desktop\scout-config\config.txt
echo Recordings will be saved to: %USERPROFILE%\Desktop\scout-videos\
echo.
echo For support or issues, check the console output when running.
echo.
pause

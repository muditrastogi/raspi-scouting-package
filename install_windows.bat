@echo off
REM Windows Installation Script for Raspberry Pi Scouting Package
REM This script sets up the Windows-compatible version of the system

echo ========================================
echo Windows Raspberry Pi Scouting Package
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo pip found:
pip --version
echo.

REM Create necessary directories
echo Creating directories...
if not exist "%USERPROFILE%\Desktop\scout-videos" mkdir "%USERPROFILE%\Desktop\scout-videos"
if not exist "%USERPROFILE%\Desktop\systemlogs" mkdir "%USERPROFILE%\Desktop\systemlogs"
echo Directories created successfully.
echo.

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements_windows.txt
if errorlevel 1 (
    echo ERROR: Failed to install some dependencies
    echo Please check the error messages above
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg is not installed or not in PATH
    echo FFmpeg is required for video recording functionality
    echo.
    echo To install FFmpeg:
    echo 1. Download from https://ffmpeg.org/download.html
    echo 2. Extract to a folder (e.g., C:\ffmpeg)
    echo 3. Add C:\ffmpeg\bin to your PATH environment variable
    echo.
    echo After installing FFmpeg, restart this script
    echo.
    pause
    exit /b 1
)

echo FFmpeg found:
ffmpeg -version | findstr "ffmpeg version"
echo.

REM Check if VLC is installed
vlc --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: VLC is not installed or not in PATH
    echo VLC is required for video streaming functionality
    echo.
    echo To install VLC:
    echo 1. Download from https://www.videolan.org/vlc/
    echo 2. Install with default settings
    echo 3. Restart this script after installation
    echo.
    pause
    exit /b 1
)

echo VLC found:
vlc --version | findstr "VLC version"
echo.

REM Copy configuration file if it doesn't exist
if not exist "config.txt" (
    echo Creating configuration file...
    copy "config_windows.txt" "config.txt" >nul
    echo Configuration file created.
    echo.
)

REM Create desktop shortcuts
echo Creating desktop shortcuts...
echo @echo off > "%USERPROFILE%\Desktop\Start Scouting System.bat"
echo cd /d "%~dp0" >> "%USERPROFILE%\Desktop\Start Scouting System.bat"
echo python windows_launcher.py >> "%USERPROFILE%\Desktop\Start Scouting System.bat"
echo pause >> "%USERPROFILE%\Desktop\Start Scouting System.bat"

echo @echo off > "%USERPROFILE%\Desktop\Configure Cameras.bat"
echo cd /d "%~dp0" >> "%USERPROFILE%\Desktop\Configure Cameras.bat"
echo python configure_cameras_windows.py >> "%USERPROFILE%\Desktop\Configure Cameras.bat"
echo pause >> "%USERPROFILE%\Desktop\Configure Cameras.bat"

echo @echo off > "%USERPROFILE%\Desktop\Start FTP Server.bat"
echo cd /d "%~dp0" >> "%USERPROFILE%\Desktop\Start FTP Server.bat"
echo python ftpserver_windows.py >> "%USERPROFILE%\Desktop\Start FTP Server.bat"
echo pause >> "%USERPROFILE%\Desktop\Start FTP Server.bat"

echo @echo off > "%USERPROFILE%\Desktop\Start System Monitor.bat"
echo cd /d "%~dp0" >> "%USERPROFILE%\Desktop\Start System Monitor.bat"
echo python system_monitor_windows.py --daemon >> "%USERPROFILE%\Desktop\Start System Monitor.bat"
echo pause >> "%USERPROFILE%\Desktop\Start System Monitor.bat"

echo @echo off > "%USERPROFILE%\Desktop\Cleanup Old Files.bat"
echo cd /d "%~dp0" >> "%USERPROFILE%\Desktop\Start System Monitor.bat"
echo python delete_except_newest_windows.py --days 30 >> "%USERPROFILE%\Desktop\Cleanup Old Files.bat"
echo pause >> "%USERPROFILE%\Desktop\Cleanup Old Files.bat"

echo Desktop shortcuts created successfully.
echo.

REM Display installation summary
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo The following components have been installed:
echo - Python dependencies
echo - Configuration files
echo - Desktop shortcuts
echo.
echo Next steps:
echo 1. Connect your USB cameras
echo 2. Run "Configure Cameras.bat" to set up camera positions
echo 3. Run "Start Scouting System.bat" to launch the main system
echo.
echo Optional services:
echo - "Start FTP Server.bat" - For remote file access
echo - "Start System Monitor.bat" - For system monitoring
echo - "Cleanup Old Files.bat" - For disk space management
echo.
echo For help and documentation, see README_Windows.md
echo.
pause

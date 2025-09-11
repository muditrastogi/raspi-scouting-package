@echo off
REM Quick test batch file for Windows scouting package

echo ============================================
echo  Windows Scouting Package - Quick Test
echo ============================================
echo.

echo Testing Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)
echo.

echo Testing FFmpeg installation...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: FFmpeg not found in PATH
    echo Please install FFmpeg and add to PATH
    pause
    exit /b 1
)
echo FFmpeg found.
echo.

echo Running diagnostic tests...
python quick_diagnostic.py

if errorlevel 1 (
    echo.
    echo Diagnostic tests failed.
    echo Try running individual tests:
    echo python simple_rtsp_server.py --camera 0
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Diagnostics completed successfully!
echo ============================================
echo.
echo You can now run the main application:
echo windows_scout_launcher.bat
echo.
pause

@echo off
title Quick FTP Download for Scout Videos
color 0A

echo ================================================================
echo              Quick FTP Download for Scout Videos
echo         Raspberry Pi Scouting Package (Windows Client)
echo ================================================================
echo.
echo This is a quick launcher for the FTP Download Manager.
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if PowerShell script exists
if not exist "FTP_Download_Manager.ps1" (
    echo [ERROR] FTP_Download_Manager.ps1 not found
    echo Please ensure you're running this from the correct directory
    echo.
    pause
    exit /b 1
)

echo Options:
echo.
echo   1) Interactive FTP Download (Recommended)
echo   2) Quick Download All Videos
echo   3) Sync Mode (Download only new videos)
echo   4) Manual FTP Client Setup
echo   5) Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto interactive
if "%choice%"=="2" goto download_all
if "%choice%"=="3" goto sync_mode
if "%choice%"=="4" goto manual_setup
if "%choice%"=="5" goto end
goto invalid_choice

:interactive
echo.
echo [INFO] Starting Interactive FTP Download Manager...
echo [INFO] You will be prompted for server IP and settings
echo.
powershell -ExecutionPolicy Bypass -File FTP_Download_Manager.ps1
goto end

:download_all
echo.
set /p server_ip="Enter Raspberry Pi IP address (e.g., 192.168.1.100): "
if "%server_ip%"=="" (
    echo [ERROR] IP address is required
    pause
    goto menu
)

echo.
echo [INFO] Starting automatic download of all videos...
echo [INFO] Server: %server_ip%
echo.
powershell -ExecutionPolicy Bypass -File FTP_Download_Manager.ps1 -ServerIP "%server_ip%" -AutoDownload
goto end

:sync_mode
echo.
set /p server_ip="Enter Raspberry Pi IP address (e.g., 192.168.1.100): "
if "%server_ip%"=="" (
    echo [ERROR] IP address is required
    pause
    goto menu
)

echo.
echo [INFO] Starting sync mode (download only new videos)...
echo [INFO] Server: %server_ip%
echo.
powershell -ExecutionPolicy Bypass -File FTP_Download_Manager.ps1 -ServerIP "%server_ip%" -AutoDownload -SyncMode
goto end

:manual_setup
echo.
echo [INFO] Opening manual FTP client setup...
if exist "FTP_Client_Setup.bat" (
    call FTP_Client_Setup.bat
) else (
    echo [ERROR] FTP_Client_Setup.bat not found
    pause
)
goto end

:invalid_choice
echo.
echo [ERROR] Invalid choice. Please select 1-5.
pause
goto menu

:menu
cls
goto start

:start
echo ================================================================
echo              Quick FTP Download for Scout Videos
echo         Raspberry Pi Scouting Package (Windows Client)
echo ================================================================
echo.
echo This is a quick launcher for the FTP Download Manager.
echo.
echo Options:
echo.
echo   1) Interactive FTP Download (Recommended)
echo   2) Quick Download All Videos
echo   3) Sync Mode (Download only new videos)  
echo   4) Manual FTP Client Setup
echo   5) Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto interactive
if "%choice%"=="2" goto download_all
if "%choice%"=="3" goto sync_mode
if "%choice%"=="4" goto manual_setup
if "%choice%"=="5" goto end
goto invalid_choice

:end
echo.
echo ================================================================
echo                    FTP Download Complete
echo ================================================================
echo.
echo Videos are downloaded to:
echo   %USERPROFILE%\Desktop\scout-videos-downloaded
echo.
echo For more options, use:
echo   • FTP_Client_Setup.bat (Full FTP client setup)
echo   • FTP_Download_Manager.ps1 (Advanced PowerShell script)
echo.
pause

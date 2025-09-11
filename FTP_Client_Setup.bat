@echo off
title FTP Client Setup for Scout Videos
color 0D

echo ================================================================
echo              FTP Client Setup for Scout Videos
echo         Raspberry Pi Scouting Package (Windows Client)
echo ================================================================
echo.
echo This tool helps you connect to the Raspberry Pi FTP server
echo to download scout videos and recordings.
echo.
echo Default FTP Server Settings:
echo   • Port: 21
echo   • Username: pirecorder
echo   • Password: recorderpi
echo   • Directory: ~/Desktop/scout-videos
echo.

REM Change to script directory
cd /d "%~dp0"

REM Create downloads directory
set "DOWNLOAD_DIR=%USERPROFILE%\Desktop\scout-videos-downloaded"
if not exist "%DOWNLOAD_DIR%" (
    mkdir "%DOWNLOAD_DIR%"
    echo [INFO] Created download directory: %DOWNLOAD_DIR%
)

echo ================================================================
echo                    FTP Connection Options
echo ================================================================
echo.
echo Choose your connection method:
echo.
echo   1) Windows Built-in FTP Client (Command Line)
echo   2) FileZilla FTP Client (GUI - Recommended)
echo   3) PowerShell FTP Script (Automated Download)
echo   4) WinSCP Client (GUI Alternative)
echo   5) Configure Custom FTP Settings
echo   6) Test FTP Connection
echo   7) Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto builtin_ftp
if "%choice%"=="2" goto filezilla_setup
if "%choice%"=="3" goto powershell_ftp
if "%choice%"=="4" goto winscp_setup
if "%choice%"=="5" goto configure_settings
if "%choice%"=="6" goto test_connection
if "%choice%"=="7" goto end
goto invalid_choice

:builtin_ftp
echo.
echo ================================================================
echo             Windows Built-in FTP Client Setup
echo ================================================================
echo.
set /p server_ip="Enter Raspberry Pi IP address (e.g., 192.168.1.100): "
if "%server_ip%"=="" (
    echo [ERROR] IP address is required
    pause
    goto menu
)

echo.
echo [INFO] Starting FTP client connection...
echo [INFO] Use these credentials when prompted:
echo         Username: pirecorder
echo         Password: recorderpi
echo.
echo [INFO] Useful FTP commands:
echo         ls          - List files
echo         cd dirname  - Change directory
echo         get filename - Download file
echo         mget *      - Download all files
echo         binary      - Set binary mode (for videos)
echo         quit        - Exit FTP
echo.
pause

REM Create FTP script for automatic login
echo open %server_ip% > ftp_script.txt
echo pirecorder >> ftp_script.txt
echo recorderpi >> ftp_script.txt
echo binary >> ftp_script.txt
echo ls >> ftp_script.txt

echo.
echo Starting FTP session...
ftp -s:ftp_script.txt

del ftp_script.txt
goto menu

:filezilla_setup
echo.
echo ================================================================
echo                  FileZilla Client Setup
echo ================================================================
echo.
echo FileZilla is a free, professional FTP client with GUI.
echo.
echo Step 1: Download and Install FileZilla
echo   • Go to: https://filezilla-project.org/download.php?type=client
echo   • Download FileZilla Client (FREE version)
echo   • Install with default settings
echo.
echo Step 2: Configure Connection
set /p server_ip="Enter Raspberry Pi IP address (e.g., 192.168.1.100): "
if "%server_ip%"=="" (
    echo [ERROR] IP address is required
    pause
    goto menu
)

echo.
echo   In FileZilla, enter these settings:
echo     Host: %server_ip%
echo     Username: pirecorder
echo     Password: recorderpi
echo     Port: 21
echo.
echo Step 3: Connect and Download
echo   • Click "Quickconnect"
echo   • Navigate to scout-videos folder
echo   • Drag files from right panel to left panel to download
echo.

REM Create FileZilla site configuration file
set "FILEZILLA_CONFIG=%APPDATA%\FileZilla\sitemanager.xml"
if exist "%APPDATA%\FileZilla\" (
    echo.
    echo [INFO] Creating FileZilla site configuration...
    echo ^<?xml version="1.0" encoding="UTF-8"?^> > "%FILEZILLA_CONFIG%"
    echo ^<FileZilla3 version="3.0.0" platform="windows"^> >> "%FILEZILLA_CONFIG%"
    echo   ^<Servers^> >> "%FILEZILLA_CONFIG%"
    echo     ^<Server^> >> "%FILEZILLA_CONFIG%"
    echo       ^<Host^>%server_ip%^</Host^> >> "%FILEZILLA_CONFIG%"
    echo       ^<Port^>21^</Port^> >> "%FILEZILLA_CONFIG%"
    echo       ^<Protocol^>0^</Protocol^> >> "%FILEZILLA_CONFIG%"
    echo       ^<Type^>0^</Type^> >> "%FILEZILLA_CONFIG%"
    echo       ^<User^>pirecorder^</User^> >> "%FILEZILLA_CONFIG%"
    echo       ^<Pass encoding="base64"^>cmVjb3JkZXJwaQ==^</Pass^> >> "%FILEZILLA_CONFIG%"
    echo       ^<Name^>Raspberry Pi Scout Videos^</Name^> >> "%FILEZILLA_CONFIG%"
    echo     ^</Server^> >> "%FILEZILLA_CONFIG%"
    echo   ^</Servers^> >> "%FILEZILLA_CONFIG%"
    echo ^</FileZilla3^> >> "%FILEZILLA_CONFIG%"
    echo [SUCCESS] FileZilla configuration created!
)

echo.
echo Do you want to launch FileZilla now? (Y/N)
set /p launch_filezilla=
if /i "%launch_filezilla%"=="Y" (
    start filezilla
)

goto menu

:powershell_ftp
echo.
echo ================================================================
echo            PowerShell Automated FTP Download
echo ================================================================
echo.
set /p server_ip="Enter Raspberry Pi IP address (e.g., 192.168.1.100): "
if "%server_ip%"=="" (
    echo [ERROR] IP address is required
    pause
    goto menu
)

echo.
echo [INFO] Creating PowerShell FTP download script...

REM Create PowerShell FTP script
echo # PowerShell FTP Download Script for Scout Videos > ftp_download.ps1
echo $server = "%server_ip%" >> ftp_download.ps1
echo $username = "pirecorder" >> ftp_download.ps1
echo $password = "recorderpi" >> ftp_download.ps1
echo $localPath = "%DOWNLOAD_DIR%" >> ftp_download.ps1
echo. >> ftp_download.ps1
echo Write-Host "Connecting to FTP server: $server" -ForegroundColor Green >> ftp_download.ps1
echo. >> ftp_download.ps1
echo try { >> ftp_download.ps1
echo     # Create FTP request >> ftp_download.ps1
echo     $ftpUri = "ftp://$server/" >> ftp_download.ps1
echo     $ftpRequest = [System.Net.FtpWebRequest]::Create($ftpUri) >> ftp_download.ps1
echo     $ftpRequest.Credentials = New-Object System.Net.NetworkCredential($username, $password) >> ftp_download.ps1
echo     $ftpRequest.Method = [System.Net.WebRequestMethods+Ftp]::ListDirectory >> ftp_download.ps1
echo. >> ftp_download.ps1
echo     # Get directory listing >> ftp_download.ps1
echo     $response = $ftpRequest.GetResponse() >> ftp_download.ps1
echo     $responseStream = $response.GetResponseStream() >> ftp_download.ps1
echo     $reader = New-Object System.IO.StreamReader($responseStream) >> ftp_download.ps1
echo     $files = $reader.ReadToEnd().Split([Environment]::NewLine) >> ftp_download.ps1
echo     $reader.Close() >> ftp_download.ps1
echo     $response.Close() >> ftp_download.ps1
echo. >> ftp_download.ps1
echo     Write-Host "Files available on server:" -ForegroundColor Yellow >> ftp_download.ps1
echo     foreach ($file in $files) { >> ftp_download.ps1
echo         if ($file.Trim() -ne "") { >> ftp_download.ps1
echo             Write-Host "  $file" -ForegroundColor Cyan >> ftp_download.ps1
echo         } >> ftp_download.ps1
echo     } >> ftp_download.ps1
echo. >> ftp_download.ps1
echo     Write-Host "`nDownload all .avi files? (Y/N): " -NoNewline -ForegroundColor White >> ftp_download.ps1
echo     $choice = Read-Host >> ftp_download.ps1
echo. >> ftp_download.ps1
echo     if ($choice -eq 'Y' -or $choice -eq 'y') { >> ftp_download.ps1
echo         foreach ($file in $files) { >> ftp_download.ps1
echo             if ($file.EndsWith('.avi') -or $file.EndsWith('.mp4')) { >> ftp_download.ps1
echo                 $remoteUri = "ftp://$server/$file" >> ftp_download.ps1
echo                 $localFile = Join-Path $localPath $file >> ftp_download.ps1
echo. >> ftp_download.ps1
echo                 Write-Host "Downloading: $file" -ForegroundColor Green >> ftp_download.ps1
echo. >> ftp_download.ps1
echo                 $downloadRequest = [System.Net.FtpWebRequest]::Create($remoteUri) >> ftp_download.ps1
echo                 $downloadRequest.Credentials = New-Object System.Net.NetworkCredential($username, $password) >> ftp_download.ps1
echo                 $downloadRequest.Method = [System.Net.WebRequestMethods+Ftp]::DownloadFile >> ftp_download.ps1
echo. >> ftp_download.ps1
echo                 $downloadResponse = $downloadRequest.GetResponse() >> ftp_download.ps1
echo                 $downloadStream = $downloadResponse.GetResponseStream() >> ftp_download.ps1
echo. >> ftp_download.ps1
echo                 $fileStream = [System.IO.File]::Create($localFile) >> ftp_download.ps1
echo                 $downloadStream.CopyTo($fileStream) >> ftp_download.ps1
echo. >> ftp_download.ps1
echo                 $fileStream.Close() >> ftp_download.ps1
echo                 $downloadStream.Close() >> ftp_download.ps1
echo                 $downloadResponse.Close() >> ftp_download.ps1
echo. >> ftp_download.ps1
echo                 Write-Host "✓ Downloaded: $file" -ForegroundColor Green >> ftp_download.ps1
echo             } >> ftp_download.ps1
echo         } >> ftp_download.ps1
echo         Write-Host "`nDownload completed! Files saved to: $localPath" -ForegroundColor Green >> ftp_download.ps1
echo     } >> ftp_download.ps1
echo. >> ftp_download.ps1
echo } catch { >> ftp_download.ps1
echo     Write-Host "Error: $_" -ForegroundColor Red >> ftp_download.ps1
echo     Write-Host "Check server IP, credentials, and network connection." -ForegroundColor Yellow >> ftp_download.ps1
echo } >> ftp_download.ps1
echo. >> ftp_download.ps1
echo Write-Host "`nPress any key to continue..." -ForegroundColor White >> ftp_download.ps1
echo $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") >> ftp_download.ps1

echo [SUCCESS] PowerShell script created: ftp_download.ps1
echo.
echo Running PowerShell FTP download script...
powershell -ExecutionPolicy Bypass -File ftp_download.ps1

goto menu

:winscp_setup
echo.
echo ================================================================
echo                    WinSCP Client Setup
echo ================================================================
echo.
echo WinSCP is another excellent FTP/SFTP client with GUI.
echo.
echo Step 1: Download and Install WinSCP
echo   • Go to: https://winscp.net/eng/download.php
echo   • Download WinSCP (FREE)
echo   • Install with default settings
echo.
echo Step 2: Configure Connection
set /p server_ip="Enter Raspberry Pi IP address (e.g., 192.168.1.100): "
if "%server_ip%"=="" (
    echo [ERROR] IP address is required
    pause
    goto menu
)

echo.
echo   In WinSCP, create new session with:
echo     File protocol: FTP
echo     Host name: %server_ip%
echo     Port number: 21
echo     User name: pirecorder
echo     Password: recorderpi
echo.
echo Step 3: Connect and Download
echo   • Click "Login"
echo   • Navigate to scout-videos folder on right panel
echo   • Select files and drag to left panel (local) to download
echo.

echo Do you want to launch WinSCP now? (Y/N)
set /p launch_winscp=
if /i "%launch_winscp%"=="Y" (
    start winscp
)

goto menu

:configure_settings
echo.
echo ================================================================
echo                Configure Custom FTP Settings
echo ================================================================
echo.
echo Current default settings:
echo   Port: 21
echo   Username: pirecorder
echo   Password: recorderpi
echo.
echo Enter new settings (press Enter to keep current):
echo.

set /p new_port="FTP Port [21]: "
if "%new_port%"=="" set new_port=21

set /p new_username="Username [pirecorder]: "
if "%new_username%"=="" set new_username=pirecorder

set /p new_password="Password [recorderpi]: "
if "%new_password%"=="" set new_password=recorderpi

echo.
echo [INFO] New settings saved for this session:
echo   Port: %new_port%
echo   Username: %new_username%
echo   Password: %new_password%
echo.
echo Note: These settings are temporary for this session only.
echo       To make permanent changes, edit the ftpserver.py file.

pause
goto menu

:test_connection
echo.
echo ================================================================
echo                    Test FTP Connection
echo ================================================================
echo.
set /p server_ip="Enter Raspberry Pi IP address to test: "
if "%server_ip%"=="" (
    echo [ERROR] IP address is required
    pause
    goto menu
)

echo.
echo [INFO] Testing connection to %server_ip%:21...

REM Test basic connectivity
ping -n 3 %server_ip% >nul
if %errorlevel% neq 0 (
    echo [ERROR] Cannot ping %server_ip%
    echo         Check IP address and network connection
    pause
    goto menu
)

echo [SUCCESS] Ping test passed

REM Test FTP port
echo [INFO] Testing FTP port 21...
telnet %server_ip% 21 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Could not connect to FTP port 21
    echo           FTP server might not be running
) else (
    echo [SUCCESS] FTP port is accessible
)

REM Create test FTP script
echo [INFO] Testing FTP login...
echo open %server_ip% > test_ftp.txt
echo pirecorder >> test_ftp.txt
echo recorderpi >> test_ftp.txt
echo ls >> test_ftp.txt
echo quit >> test_ftp.txt

ftp -s:test_ftp.txt
del test_ftp.txt

pause
goto menu

:invalid_choice
echo.
echo [ERROR] Invalid choice. Please select 1-7.
pause
goto menu

:menu
echo.
goto begin

:begin
cls
goto start

:start
echo ================================================================
echo              FTP Client Setup for Scout Videos
echo         Raspberry Pi Scouting Package (Windows Client)  
echo ================================================================
echo.
echo This tool helps you connect to the Raspberry Pi FTP server
echo to download scout videos and recordings.
echo.
echo Default FTP Server Settings:
echo   • Port: 21
echo   • Username: pirecorder
echo   • Password: recorderpi
echo   • Directory: ~/Desktop/scout-videos
echo.
echo ================================================================
echo                    FTP Connection Options
echo ================================================================
echo.
echo Choose your connection method:
echo.
echo   1) Windows Built-in FTP Client (Command Line)
echo   2) FileZilla FTP Client (GUI - Recommended)
echo   3) PowerShell FTP Script (Automated Download)
echo   4) WinSCP Client (GUI Alternative)
echo   5) Configure Custom FTP Settings
echo   6) Test FTP Connection
echo   7) Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto builtin_ftp
if "%choice%"=="2" goto filezilla_setup
if "%choice%"=="3" goto powershell_ftp
if "%choice%"=="4" goto winscp_setup
if "%choice%"=="5" goto configure_settings
if "%choice%"=="6" goto test_connection
if "%choice%"=="7" goto end
goto invalid_choice

:end
echo.
echo ================================================================
echo                    FTP Client Setup Complete
echo ================================================================
echo.
echo Thank you for using the FTP Client Setup tool!
echo.
echo Your downloads will be saved to:
echo   %DOWNLOAD_DIR%
echo.
echo For support, see PROJECT_SETUP_GUIDE.md
echo.
pause

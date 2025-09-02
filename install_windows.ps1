# Windows PowerShell Installation Script for Raspberry Pi Scouting Package
# This script sets up the Windows-compatible version of the system

param(
    [switch]$Force,
    [switch]$SkipDependencies,
    [string]$PythonPath = "python"
)

# Set execution policy for current session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Windows Raspberry Pi Scouting Package" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command($CommandName) {
    try {
        Get-Command $CommandName -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Function to create directory if it doesn't exist
function New-DirectoryIfNotExists($Path) {
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "Created directory: $Path" -ForegroundColor Green
    } else {
        Write-Host "Directory exists: $Path" -ForegroundColor Yellow
    }
}

# Function to check Python installation
function Test-PythonInstallation {
    Write-Host "Checking Python installation..." -ForegroundColor Yellow
    
    if (Test-Command $PythonPath) {
        $pythonVersion = & $PythonPath --version 2>&1
        Write-Host "Python found: $pythonVersion" -ForegroundColor Green
        return $true
    } else {
        Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Red
        Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Red
        return $false
    }
}

# Function to check pip availability
function Test-PipAvailability {
    Write-Host "Checking pip availability..." -ForegroundColor Yellow
    
    if (Test-Command "pip") {
        $pipVersion = & pip --version 2>&1
        Write-Host "pip found: $pipVersion" -ForegroundColor Green
        return $true
    } else {
        Write-Host "ERROR: pip is not available" -ForegroundColor Red
        Write-Host "Please ensure pip is installed with Python" -ForegroundColor Red
        return $false
    }
}

# Function to install Python dependencies
function Install-PythonDependencies {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    
    try {
        & pip install -r requirements_windows.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Dependencies installed successfully." -ForegroundColor Green
            return $true
        } else {
            Write-Host "ERROR: Failed to install some dependencies" -ForegroundColor Red
            Write-Host "Please check the error messages above" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "ERROR: Exception during dependency installation: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to check FFmpeg installation
function Test-FFmpegInstallation {
    Write-Host "Checking FFmpeg installation..." -ForegroundColor Yellow
    
    if (Test-Command "ffmpeg") {
        $ffmpegVersion = & ffmpeg -version 2>&1 | Select-String "ffmpeg version"
        Write-Host "FFmpeg found: $ffmpegVersion" -ForegroundColor Green
        return $true
    } else {
        Write-Host "WARNING: FFmpeg is not installed or not in PATH" -ForegroundColor Yellow
        Write-Host "FFmpeg is required for video recording functionality" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To install FFmpeg:" -ForegroundColor Yellow
        Write-Host "1. Download from https://ffmpeg.org/download.html" -ForegroundColor Yellow
        Write-Host "2. Extract to a folder (e.g., C:\ffmpeg)" -ForegroundColor Yellow
        Write-Host "3. Add C:\ffmpeg\bin to your PATH environment variable" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "After installing FFmpeg, restart this script" -ForegroundColor Yellow
        Write-Host ""
        
        if (-not $Force) {
            $response = Read-Host "Continue without FFmpeg? (y/N)"
            if ($response -ne "y" -and $response -ne "Y") {
                return $false
            }
        }
        return $false
    }
}

# Function to check VLC installation
function Test-VLCInstallation {
    Write-Host "Checking VLC installation..." -ForegroundColor Yellow
    
    if (Test-Command "vlc") {
        $vlcVersion = & vlc --version 2>&1 | Select-String "VLC version"
        Write-Host "VLC found: $vlcVersion" -ForegroundColor Green
        return $true
    } else {
        Write-Host "WARNING: VLC is not installed or not in PATH" -ForegroundColor Yellow
        Write-Host "VLC is required for video streaming functionality" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To install VLC:" -ForegroundColor Yellow
        Write-Host "1. Download from https://www.videolan.org/vlc/" -ForegroundColor Yellow
        Write-Host "2. Install with default settings" -ForegroundColor Yellow
        Write-Host "3. Restart this script after installation" -ForegroundColor Yellow
        Write-Host ""
        
        if (-not $Force) {
            $response = Read-Host "Continue without VLC? (y/N)"
            if ($response -ne "y" -and $response -ne "Y") {
                return $false
            }
        }
        return $false
    }
}

# Function to create configuration file
function New-ConfigurationFile {
    Write-Host "Creating configuration file..." -ForegroundColor Yellow
    
    if (-not (Test-Path "config.txt")) {
        if (Test-Path "config_windows.txt") {
            Copy-Item "config_windows.txt" "config.txt"
            Write-Host "Configuration file created from config_windows.txt." -ForegroundColor Green
        } else {
            Write-Host "WARNING: config_windows.txt not found, creating basic config.txt" -ForegroundColor Yellow
            @"
[cameras]
resolution=1920x1080
fps=30
bottomcamera=
middlecamera=
topcamera=

[recording]
crf=23
format=mp4
audio=false

[network]
rtsp_base_port=8554
record_api_port=5000
ftp_port=21
ftp_username=pirecorder
ftp_password=recorderpi

[storage]
video_dir=scout-videos
log_dir=systemlogs
max_disk_usage=90
retention_days=30

[system]
monitor_interval=30
cpu_threshold=80
memory_threshold=80
auto_cleanup=true
cleanup_interval=24
"@ | Out-File -FilePath "config.txt" -Encoding UTF8
            Write-Host "Basic configuration file created." -ForegroundColor Green
        }
    } else {
        Write-Host "Configuration file already exists." -ForegroundColor Yellow
    }
}

# Function to create desktop shortcuts
function New-DesktopShortcuts {
    Write-Host "Creating desktop shortcuts..." -ForegroundColor Yellow
    
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $scriptPath = Get-Location
    
    # Start Scouting System
    $shortcutPath = Join-Path $desktopPath "Start Scouting System.bat"
    @"
@echo off
cd /d "$scriptPath"
python windows_launcher.py
pause
"@ | Out-File -FilePath $shortcutPath -Encoding ASCII
    Write-Host "Created: Start Scouting System.bat" -ForegroundColor Green
    
    # Configure Cameras
    $shortcutPath = Join-Path $desktopPath "Configure Cameras.bat"
    @"
@echo off
cd /d "$scriptPath"
python configure_cameras_windows.py
pause
"@ | Out-File -FilePath $shortcutPath -Encoding ASCII
    Write-Host "Created: Configure Cameras.bat" -ForegroundColor Green
    
    # Start FTP Server
    $shortcutPath = Join-Path $desktopPath "Start FTP Server.bat"
    @"
@echo off
cd /d "$scriptPath"
python ftpserver_windows.py
pause
"@ | Out-File -FilePath $shortcutPath -Encoding ASCII
    Write-Host "Created: Start FTP Server.bat" -ForegroundColor Green
    
    # Start System Monitor
    $shortcutPath = Join-Path $desktopPath "Start System Monitor.bat"
    @"
@echo off
cd /d "$scriptPath"
python system_monitor_windows.py --daemon
pause
"@ | Out-File -FilePath $shortcutPath -Encoding ASCII
    Write-Host "Created: Start System Monitor.bat" -ForegroundColor Green
    
    # Cleanup Old Files
    $shortcutPath = Join-Path $desktopPath "Cleanup Old Files.bat"
    @"
@echo off
cd /d "$scriptPath"
python delete_except_newest_windows.py --days 30
pause
"@ | Out-File -FilePath $shortcutPath -Encoding ASCII
    Write-Host "Created: Cleanup Old Files.bat" -ForegroundColor Green
    
    Write-Host "Desktop shortcuts created successfully." -ForegroundColor Green
}

# Function to display installation summary
function Show-InstallationSummary {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Installation Complete!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "The following components have been installed:" -ForegroundColor White
    Write-Host "- Python dependencies" -ForegroundColor White
    Write-Host "- Configuration files" -ForegroundColor White
    Write-Host "- Desktop shortcuts" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "1. Connect your USB cameras" -ForegroundColor White
    Write-Host "2. Run 'Configure Cameras.bat' to set up camera positions" -ForegroundColor White
    Write-Host "3. Run 'Start Scouting System.bat' to launch the main system" -ForegroundColor White
    Write-Host ""
    Write-Host "Optional services:" -ForegroundColor White
    Write-Host "- 'Start FTP Server.bat' - For remote file access" -ForegroundColor White
    Write-Host "- 'Start System Monitor.bat' - For system monitoring" -ForegroundColor White
    Write-Host "- 'Cleanup Old Files.bat' - For disk space management" -ForegroundColor White
    Write-Host ""
    Write-Host "For help and documentation, see README_Windows.md" -ForegroundColor White
    Write-Host ""
}

# Main installation process
function Start-Installation {
    Write-Host "Starting Windows Raspberry Pi Scouting Package installation..." -ForegroundColor Yellow
    Write-Host ""
    
    # Check Python
    if (-not (Test-PythonInstallation)) {
        return $false
    }
    Write-Host ""
    
    # Check pip
    if (-not (Test-PipAvailability)) {
        return $false
    }
    Write-Host ""
    
    # Create directories
    Write-Host "Creating directories..." -ForegroundColor Yellow
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    New-DirectoryIfNotExists (Join-Path $desktopPath "scout-videos")
    New-DirectoryIfNotExists (Join-Path $desktopPath "systemlogs")
    Write-Host "Directories created successfully." -ForegroundColor Green
    Write-Host ""
    
    # Install Python dependencies
    if (-not $SkipDependencies) {
        if (-not (Install-PythonDependencies)) {
            return $false
        }
        Write-Host ""
    } else {
        Write-Host "Skipping Python dependencies installation." -ForegroundColor Yellow
        Write-Host ""
    }
    
    # Check FFmpeg
    Test-FFmpegInstallation | Out-Null
    Write-Host ""
    
    # Check VLC
    Test-VLCInstallation | Out-Null
    Write-Host ""
    
    # Create configuration file
    New-ConfigurationFile
    Write-Host ""
    
    # Create desktop shortcuts
    New-DesktopShortcuts
    Write-Host ""
    
    # Show summary
    Show-InstallationSummary
    
    return $true
}

# Main execution
try {
    $success = Start-Installation
    if ($success) {
        Write-Host "Installation completed successfully!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "Installation failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERROR: Unexpected error during installation: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}

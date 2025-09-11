# Raspberry Pi Scouting Package - Windows Setup Guide

Complete step-by-step guide for setting up the Windows version of the Raspberry Pi Scouting Package with camera configuration and clickable UI files.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [GitHub Installation & Branch Setup](#github-installation--branch-setup)
3. [Python Environment Setup](#python-environment-setup)
4. [Camera Device ID Configuration](#camera-device-id-configuration)
5. [Creating Clickable UI Files](#creating-clickable-ui-files)
6. [Testing & Verification](#testing--verification)
7. [Troubleshooting](#troubleshooting)
8. [Project Structure](#project-structure)

---

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11 (64-bit recommended)
- **Python**: Version 3.7 or higher
- **Git**: Latest version
- **Hardware**: 3 USB cameras (recommended: identical models for consistency)
- **Permissions**: Administrator access for camera drivers and system commands

### Required Software Installation

#### 1. Install Git for Windows
1. Download from: https://git-scm.com/download/win
2. Run installer with default settings
3. Verify installation:
   ```cmd
   git --version
   ```

#### 2. Install Python
1. Download from: https://python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### 3. Install Required System Tools
- **Windows Management Instrumentation**: Usually pre-installed
- **Camera Drivers**: Ensure all USB cameras are properly detected in Device Manager

---

## GitHub Installation & Branch Setup

### Step 1: Clone the Repository

1. **Open Command Prompt or PowerShell**
   ```cmd
   # Navigate to desired directory (e.g., Downloads)
   cd C:\Users\%USERNAME%\Downloads
   
   # Create project directory
   mkdir grai_pune
   cd grai_pune
   ```

2. **Clone the Repository**
   ```cmd
   git clone https://github.com/your-username/raspi-scouting-package.git
   cd raspi-scouting-package
   ```

### Step 2: Switch to Windows Scripts Branch

1. **List Available Branches**
   ```cmd
   git branch -a
   ```

2. **Checkout to win-scripts Branch**
   ```cmd
   git checkout win-scripts
   ```

3. **Verify Current Branch**
   ```cmd
   git branch
   # Should show: * win-scripts
   ```

4. **Pull Latest Changes**
   ```cmd
   git pull origin win-scripts
   ```

### Step 3: Verify Project Structure

After checkout, you should see these key files:
```
raspi-scouting-package/
├── config.txt
├── simple_windows_ui.py
├── windows_configure_cameras.py
├── windows_configure_cameras.bat
├── test_windows_camera_detection.py
├── WINDOWS_CAMERA_CONFIG.md
├── windows_requirements.txt
└── ... (other files)
```

---

## Python Environment Setup

### Step 1: Install Python Dependencies

1. **Navigate to Project Directory**
   ```cmd
   cd C:\Users\%USERNAME%\Downloads\grai_pune\raspi-scouting-package
   ```

2. **Install Required Packages**
   ```cmd
   # Install from Windows requirements file
   pip install -r windows_requirements.txt
   
   # Or install manually:
   pip install opencv-python pillow tkinter subprocess32
   ```

### Step 2: Verify OpenCV Installation

1. **Test OpenCV**
   ```cmd
   python -c "import cv2; print('OpenCV version:', cv2.__version__)"
   ```

2. **Test Tkinter**
   ```cmd
   python -c "import tkinter; print('Tkinter working')"
   ```

### Step 3: Check Camera Access

1. **Run Camera Test**
   ```cmd
   python test_windows_camera_detection.py
   ```

This will:
- Test wmic command functionality
- Detect USB cameras
- Verify OpenCV camera access
- Show available camera device IDs

---

## Camera Device ID Configuration

### Step 1: Connect USB Cameras

1. **Connect all 3 USB cameras** to your computer
2. **Use different USB ports** (preferably USB 3.0)
3. **Avoid USB hubs** if possible for better stability

### Step 2: Verify Camera Detection

1. **Check Device Manager**
   - Open Device Manager (Win + X, then M)
   - Expand "Cameras" or "Imaging devices"
   - Ensure all cameras are listed without errors

2. **Test Camera Detection**
   ```cmd
   python test_windows_camera_detection.py
   ```

### Step 3: Configure Camera Positions

#### Method 1: Using Batch Script (Recommended)
1. **Double-click** `windows_configure_cameras.bat`
2. Follow the interactive menu

#### Method 2: Using Python Script
1. **Open Command Prompt in project directory**
   ```cmd
   python windows_configure_cameras.py
   ```

#### Configuration Process:
1. **Select camera position** (Bottom, Middle, Top)
2. **Choose corresponding camera** from detected list
3. **Confirm selection**
4. **Repeat for all positions**

### Step 4: Verify Configuration

1. **Check config.txt file**
   ```cmd
   type config.txt
   ```

2. **Should contain device IDs like:**
   ```ini
   resolution=1920x1080
   fps=15
   bottomcamera=2430AP0JP9R8
   middlecamera=2430AP0JP398
   topcamera=2431AP03VQV8
   # Windows camera device IDs (for Windows systems)
   bottomcamera_deviceid=USB\VID_046D&PID_0825\42359210
   middlecamera_deviceid=USB\VID_046D&PID_0825\42359210
   topcamera_deviceid=USB\VID_046D&PID_0825\42359210
   ```

### Step 5: Test Camera Configuration

1. **Run the main UI**
   ```cmd
   python simple_windows_ui.py
   ```

2. **Verify camera order**
   - Left panel: "bottom (first)"
   - Middle panel: "middle (second)"
   - Right panel: "top (third)"

---

## Creating Clickable UI Files

### Step 1: Create Enhanced Batch Scripts

#### Main UI Launcher
Create `Start_Camera_UI.bat`:

```cmd
@echo off
title Raspberry Pi Scouting Package - Windows UI
color 0A

echo ================================================================
echo          Raspberry Pi Scouting Package - Windows UI
echo ================================================================
echo.
echo [INFO] Starting camera interface...
echo [INFO] Make sure your USB cameras are connected
echo.

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

REM Check if main script exists
if not exist "simple_windows_ui.py" (
    echo [ERROR] simple_windows_ui.py not found
    echo Please ensure you're running this from the correct directory
    echo.
    pause
    exit /b 1
)

REM Start the application
echo [INFO] Loading camera configuration...
python simple_windows_ui.py

echo.
echo [INFO] Camera UI has closed
pause
```

#### Camera Configuration Launcher
Create `Configure_Cameras.bat`:

```cmd
@echo off
title Camera Configuration Tool
color 0B

echo ================================================================
echo            Camera Configuration Tool
echo         Raspberry Pi Scouting Package (Windows)
echo ================================================================
echo.
echo This tool will help you configure camera positions:
echo   • Bottom Camera
echo   • Middle Camera  
echo   • Top Camera
echo.
echo Make sure all USB cameras are connected before proceeding.
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

REM Run configuration tool
python windows_configure_cameras.py

echo.
echo [INFO] Configuration complete
echo You can now run the camera UI using Start_Camera_UI.bat
pause
```

#### Camera Test Script
Create `Test_Camera_Detection.bat`:

```cmd
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

REM Run test script
python test_windows_camera_detection.py

echo.
echo [INFO] Test complete
pause
```

### Step 2: Create Desktop Shortcuts

#### Using PowerShell Script
Create `Create_Desktop_Shortcuts.ps1`:

```powershell
# PowerShell script to create desktop shortcuts
$WshShell = New-Object -comObject WScript.Shell

# Get current directory
$CurrentDir = Get-Location

# Create shortcut for Main UI
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\Scouting Camera UI.lnk")
$Shortcut.TargetPath = "$CurrentDir\Start_Camera_UI.bat"
$Shortcut.WorkingDirectory = $CurrentDir
$Shortcut.IconLocation = "shell32.dll,23"
$Shortcut.Description = "Raspberry Pi Scouting Package - Camera UI"
$Shortcut.Save()

# Create shortcut for Camera Configuration
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\Configure Cameras.lnk")
$Shortcut.TargetPath = "$CurrentDir\Configure_Cameras.bat"
$Shortcut.WorkingDirectory = $CurrentDir
$Shortcut.IconLocation = "shell32.dll,176"
$Shortcut.Description = "Configure Camera Positions"
$Shortcut.Save()

# Create shortcut for Camera Test
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\Test Cameras.lnk")
$Shortcut.TargetPath = "$CurrentDir\Test_Camera_Detection.bat"
$Shortcut.WorkingDirectory = $CurrentDir
$Shortcut.IconLocation = "shell32.dll,22"
$Shortcut.Description = "Test Camera Detection"
$Shortcut.Save()

Write-Host "Desktop shortcuts created successfully!" -ForegroundColor Green
Write-Host "Check your desktop for:" -ForegroundColor Yellow
Write-Host "  • Scouting Camera UI.lnk" -ForegroundColor Cyan
Write-Host "  • Configure Cameras.lnk" -ForegroundColor Cyan  
Write-Host "  • Test Cameras.lnk" -ForegroundColor Cyan
```

#### Run Shortcut Creation
```cmd
powershell -ExecutionPolicy Bypass -File Create_Desktop_Shortcuts.ps1
```

### Step 3: Create Start Menu Entries (Optional)

Create `Install_Start_Menu.bat`:

```cmd
@echo off
title Install to Start Menu
echo Installing Scouting Package to Start Menu...

REM Create Start Menu folder
set StartMenuPath=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Scouting Package
mkdir "%StartMenuPath%" 2>nul

REM Create shortcuts in Start Menu
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%StartMenuPath%\Scouting Camera UI.lnk'); $Shortcut.TargetPath = '%~dp0Start_Camera_UI.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()}"

powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%StartMenuPath%\Configure Cameras.lnk'); $Shortcut.TargetPath = '%~dp0Configure_Cameras.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()}"

echo Start Menu entries created successfully!
echo Check: Start Menu ^> Programs ^> Scouting Package
pause
```

---

## Testing & Verification

### Step 1: Complete System Test

1. **Test Camera Detection**
   ```cmd
   # Double-click Test_Camera_Detection.bat
   # OR run manually:
   python test_windows_camera_detection.py
   ```

2. **Configure Cameras**
   ```cmd
   # Double-click Configure_Cameras.bat
   # OR run manually:
   python windows_configure_cameras.py
   ```

3. **Launch Main UI**
   ```cmd
   # Double-click Start_Camera_UI.bat
   # OR run manually:
   python simple_windows_ui.py
   ```

### Step 2: Verify Camera Functionality

1. **In the UI, check:**
   - All 3 camera panels are visible
   - Labels show correct positions (bottom, middle, top)
   - "Start All Streams" button works
   - Individual camera controls work
   - Recording functionality works

2. **Test Recording:**
   - Click "Start All Streams"
   - Click "Start Recording All"
   - Navigate through grids (A-1-A, A-1-B, etc.)
   - Check that videos are saved to Desktop

### Step 3: Performance Verification

1. **Check FPS and Quality:**
   - Verify smooth video streaming
   - Check for frame drops or delays
   - Monitor CPU usage

2. **Test Multi-Camera Stability:**
   - Run all cameras simultaneously
   - Test for extended periods
   - Check for NVIDIA driver conflicts

---

## Troubleshooting

### Common Issues & Solutions

#### 1. "Python not found" Error
```cmd
# Check Python installation
python --version

# If not found, reinstall Python with "Add to PATH" checked
# Or manually add Python to PATH
```

#### 2. "No USB cameras found" Error
```cmd
# Check Device Manager for camera status
# Try different USB ports
# Update camera drivers
# Run as Administrator
```

#### 3. Camera Access Denied
```cmd
# Close other applications using cameras
# Restart computer
# Check antivirus software settings
# Run as Administrator
```

#### 4. wmic Command Fails
```cmd
# Run Command Prompt as Administrator
# Check Windows Management Instrumentation service
# Try: net start winmgmt
```

#### 5. OpenCV Import Error
```cmd
# Reinstall OpenCV
pip uninstall opencv-python
pip install opencv-python

# Try alternative version
pip install opencv-python==4.5.5.64
```

### Advanced Troubleshooting

#### Enable Verbose Logging
Add to `simple_windows_ui.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Check Camera Backends
```python
# Test different OpenCV backends
import cv2
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # DirectShow
cap = cv2.VideoCapture(0, cv2.CAP_MSMF)   # Media Foundation
```

#### Manual Device ID Lookup
```cmd
# Get detailed camera information
wmic path Win32_PnPEntity where "Description like '%Camera%'" get Name,DeviceID,Status
```

---

## Project Structure

### Final Project Layout
```
raspi-scouting-package/
├── 📁 Core Application Files
│   ├── simple_windows_ui.py           # Main camera UI application
│   ├── config.txt                     # Camera configuration file
│   └── windows_requirements.txt       # Python dependencies
│
├── 📁 Configuration Tools
│   ├── windows_configure_cameras.py   # Camera configuration script
│   ├── windows_configure_cameras.bat  # Basic config launcher
│   └── test_windows_camera_detection.py # Camera detection test
│
├── 📁 Enhanced UI Launchers
│   ├── Start_Camera_UI.bat           # Main UI launcher
│   ├── Configure_Cameras.bat         # Configuration launcher
│   ├── Test_Camera_Detection.bat     # Test launcher
│   └── Install_Start_Menu.bat        # Start menu installer
│
├── 📁 Desktop Integration
│   ├── Create_Desktop_Shortcuts.ps1  # Desktop shortcut creator
│   └── 🔗 Desktop Shortcuts (created)
│       ├── Scouting Camera UI.lnk
│       ├── Configure Cameras.lnk
│       └── Test Cameras.lnk
│
├── 📁 Documentation
│   ├── PROJECT_SETUP_GUIDE.md        # This guide
│   ├── WINDOWS_CAMERA_CONFIG.md      # Camera configuration guide
│   └── README.md                     # General project info
│
└── 📁 Additional Files
    ├── ... (other project files)
    └── videos/                       # Recorded videos folder
```

### Configuration Files

#### config.txt Structure
```ini
# Video settings
resolution=1920x1080
fps=15

# Linux camera serials (for Raspberry Pi compatibility)
bottomcamera=2430AP0JP9R8
middlecamera=2430AP0JP398
topcamera=2431AP03VQV8

# Windows camera device IDs (for Windows systems)
bottomcamera_deviceid=USB\VID_046D&PID_0825\42359210
middlecamera_deviceid=USB\VID_046D&PID_0825\42359210
topcamera_deviceid=USB\VID_046D&PID_0825\42359210
```

---

## Quick Start Summary

For users who want to get started quickly:

1. **Clone and setup:**
   ```cmd
   git clone https://github.com/your-repo/raspi-scouting-package.git
   cd raspi-scouting-package
   git checkout win-scripts
   pip install -r windows_requirements.txt
   ```

2. **Configure cameras:**
   ```cmd
   # Double-click: Configure_Cameras.bat
   ```

3. **Start application:**
   ```cmd
   # Double-click: Start_Camera_UI.bat
   ```

That's it! The application should now be running with your configured USB cameras.

---

## Support & Resources

- **GitHub Repository**: Link to your repository
- **Issues/Bug Reports**: GitHub Issues section
- **Documentation**: This guide and WINDOWS_CAMERA_CONFIG.md
- **Dependencies**: See windows_requirements.txt

For additional help, refer to the troubleshooting section or create an issue on the GitHub repository.

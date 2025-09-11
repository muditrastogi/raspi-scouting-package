@echo off
title Raspberry Pi Scouting Package - Complete Setup
color 0F

echo ================================================================
echo        Raspberry Pi Scouting Package - Complete Setup
echo ================================================================
echo.
echo This script will help you set up the entire project:
echo   1. Check Python installation
echo   2. Install required packages
echo   3. Test camera detection
echo   4. Configure cameras
echo   5. Create desktop shortcuts
echo   6. Install Start Menu entries
echo.
echo Make sure you have:
echo   • Python 3.7+ installed
echo   • USB cameras connected
echo   • Internet connection (for package installation)
echo.
pause

REM Change to script directory
cd /d "%~dp0"

echo.
echo ================================================================
echo STEP 1: Checking Python Installation
echo ================================================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please:
    echo   1. Download Python from https://python.org/downloads/
    echo   2. Install with "Add Python to PATH" checked
    echo   3. Restart this script
    echo.
    pause
    exit /b 1
) else (
    echo [SUCCESS] Python is installed
    python --version
)

echo.
echo ================================================================
echo STEP 2: Installing Required Packages
echo ================================================================

echo Installing Python packages...
if exist "windows_requirements.txt" (
    pip install -r windows_requirements.txt
) else (
    echo Installing packages manually...
    pip install opencv-python pillow
)

if %errorlevel% neq 0 (
    echo [WARNING] Some packages may have failed to install
    echo [INFO] The application might still work, try continuing
) else (
    echo [SUCCESS] Packages installed successfully
)

echo.
echo ================================================================
echo STEP 3: Testing Camera Detection
echo ================================================================

echo Running camera detection test...
if exist "test_windows_camera_detection.py" (
    python test_windows_camera_detection.py
) else (
    echo [WARNING] Test script not found, skipping...
)

echo.
echo ================================================================
echo STEP 4: Camera Configuration
echo ================================================================

echo.
echo Do you want to configure camera positions now? (Y/N)
set /p configure_choice=
if /i "%configure_choice%"=="Y" (
    if exist "windows_configure_cameras.py" (
        echo Running camera configuration...
        python windows_configure_cameras.py
    ) else (
        echo [WARNING] Configuration script not found
    )
) else (
    echo [INFO] Skipping camera configuration
    echo [INFO] You can run Configure_Cameras.bat later
)

echo.
echo ================================================================
echo STEP 5: Creating Desktop Shortcuts
echo ================================================================

echo.
echo Do you want to create desktop shortcuts? (Y/N)
set /p desktop_choice=
if /i "%desktop_choice%"=="Y" (
    if exist "Create_Desktop_Shortcuts.ps1" (
        echo Creating desktop shortcuts...
        powershell -ExecutionPolicy Bypass -File Create_Desktop_Shortcuts.ps1
    ) else (
        echo [WARNING] Shortcut script not found
    )
) else (
    echo [INFO] Skipping desktop shortcuts
)

echo.
echo ================================================================
echo STEP 6: Start Menu Installation
echo ================================================================

echo.
echo Do you want to install Start Menu entries? (Y/N)
set /p startmenu_choice=
if /i "%startmenu_choice%"=="Y" (
    if exist "Install_Start_Menu.bat" (
        call Install_Start_Menu.bat
    ) else (
        echo [WARNING] Start Menu installer not found
    )
) else (
    echo [INFO] Skipping Start Menu installation
)

echo.
echo ================================================================
echo SETUP COMPLETE!
echo ================================================================
echo.
echo The Raspberry Pi Scouting Package is now set up.
echo.
echo Next steps:
if /i "%configure_choice%"=="Y" (
    echo   ✓ Cameras are configured
    echo   → Double-click "Start_Camera_UI.bat" to start the application
) else (
    echo   → Run "Configure_Cameras.bat" to set up camera positions
    echo   → Then run "Start_Camera_UI.bat" to start the application
)
echo.
echo Available launchers:
echo   • Start_Camera_UI.bat       - Main application
echo   • Configure_Cameras.bat     - Camera setup
echo   • Test_Camera_Detection.bat - Troubleshooting
echo.
echo For help, see PROJECT_SETUP_GUIDE.md
echo.
pause

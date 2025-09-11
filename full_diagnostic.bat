@echo off
REM Complete diagnostic suite for camera issues

echo ============================================
echo  Windows Camera Diagnostic Suite
echo ============================================
echo.

echo Step 1: Basic camera test
python test_simple_camera.py
echo.
echo Press any key to continue to troubleshooting...
pause >nul

echo.
echo ============================================
echo Step 2: Advanced troubleshooting
python camera_troubleshoot.py
echo.
echo Press any key to continue...
pause >nul

echo.
echo ============================================
echo Step 3: Quick diagnostic
python quick_diagnostic.py
echo.
echo Press any key to finish...
pause >nul

echo.
echo ============================================
echo  Diagnostic complete!
echo ============================================
echo.
echo If issues persist, try:
echo 1. Restart your computer
echo 2. Update camera drivers
echo 3. Try different USB ports
echo 4. Test with Windows Camera app
echo.
pause

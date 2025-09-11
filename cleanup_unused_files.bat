@echo off
title Project Cleanup - Remove Unused Files
color 0E

echo ================================================================
echo              Project Cleanup - Remove Unused Files
echo         Raspberry Pi Scouting Package (Windows)
echo ================================================================
echo.
echo This script will remove unused/redundant files to clean up the project.
echo.
echo Files to be removed:
echo   • Old UI versions (windows_ui.py, etc.)
echo   • Duplicate scripts and launchers
echo   • Linux-specific scripts
echo   • RTSP/complex streaming files (replaced by simple OpenCV)
echo   • Development/test scripts
echo   • Duplicate documentation
echo   • Legacy directories
echo.
echo Files to KEEP (core functionality):
echo   • simple_windows_ui.py (main app)
echo   • Camera configuration tools
echo   • Enhanced UI launchers
echo   • FTP client system
echo   • Core documentation
echo.
echo WARNING: This will permanently delete files!
echo Make sure you have a backup if needed.
echo.
set /p confirm="Continue with cleanup? (Y/N): "
if /i not "%confirm%"=="Y" goto cancel

echo.
echo ================================================================
echo                    Starting Cleanup Process
echo ================================================================

REM Old/Duplicate UIs
echo [1/8] Removing old UI versions...
if exist "windows_ui.py" del "windows_ui.py" && echo   ✓ Removed windows_ui.py
if exist "simple_launcher.bat" del "simple_launcher.bat" && echo   ✓ Removed simple_launcher.bat
if exist "windows_scout_launcher.bat" del "windows_scout_launcher.bat" && echo   ✓ Removed windows_scout_launcher.bat

REM Duplicate Configuration Scripts
echo [2/8] Removing duplicate configuration scripts...
if exist "windows_configure_cameras.bat" del "windows_configure_cameras.bat" && echo   ✓ Removed windows_configure_cameras.bat
if exist "configure_cameras.sh" del "configure_cameras.sh" && echo   ✓ Removed configure_cameras.sh

REM Outdated Installation Scripts
echo [3/8] Removing outdated installation scripts...
if exist "windows_install.bat" del "windows_install.bat" && echo   ✓ Removed windows_install.bat
if exist "install.sh" del "install.sh" && echo   ✓ Removed install.sh

REM Linux/Raspberry Pi Scripts
echo [4/8] Removing Linux-specific scripts...
if exist "desktopmultiv5.sh" del "desktopmultiv5.sh" && echo   ✓ Removed desktopmultiv5.sh
if exist "delete_except_newest.sh" del "delete_except_newest.sh" && echo   ✓ Removed delete_except_newest.sh

REM RTSP/Complex Streaming Files
echo [5/8] Removing RTSP/complex streaming files...
if exist "opencv_rtsp_server.py" del "opencv_rtsp_server.py" && echo   ✓ Removed opencv_rtsp_server.py
if exist "simple_rtsp_server.py" del "simple_rtsp_server.py" && echo   ✓ Removed simple_rtsp_server.py
if exist "windows_camera_detection.py" del "windows_camera_detection.py" && echo   ✓ Removed windows_camera_detection.py
if exist "rtsp_record_api.py" del "rtsp_record_api.py" && echo   ✓ Removed rtsp_record_api.py
if exist "windows_record_api.py" del "windows_record_api.py" && echo   ✓ Removed windows_record_api.py

REM Test/Development Scripts
echo [6/8] Removing test/development scripts...
if exist "camera_troubleshoot.py" del "camera_troubleshoot.py" && echo   ✓ Removed camera_troubleshoot.py
if exist "quick_diagnostic.py" del "quick_diagnostic.py" && echo   ✓ Removed quick_diagnostic.py
if exist "manual_test.py" del "manual_test.py" && echo   ✓ Removed manual_test.py
if exist "test_complete_setup.py" del "test_complete_setup.py" && echo   ✓ Removed test_complete_setup.py
if exist "test_simple_camera.py" del "test_simple_camera.py" && echo   ✓ Removed test_simple_camera.py
if exist "test_threading_fix.py" del "test_threading_fix.py" && echo   ✓ Removed test_threading_fix.py
if exist "test_rtsp_stream.py" del "test_rtsp_stream.py" && echo   ✓ Removed test_rtsp_stream.py
if exist "test_setup.bat" del "test_setup.bat" && echo   ✓ Removed test_setup.bat
if exist "try_all_methods.bat" del "try_all_methods.bat" && echo   ✓ Removed try_all_methods.bat
if exist "full_diagnostic.bat" del "full_diagnostic.bat" && echo   ✓ Removed full_diagnostic.bat
if exist "list_ffmpeg_devices.py" del "list_ffmpeg_devices.py" && echo   ✓ Removed list_ffmpeg_devices.py
if exist "system_monitor.py" del "system_monitor.py" && echo   ✓ Removed system_monitor.py

REM Duplicate Documentation
echo [7/8] Removing duplicate documentation...
if exist "SIMPLE_README.md" del "SIMPLE_README.md" && echo   ✓ Removed SIMPLE_README.md
if exist "INSTRUCTIONS.md" del "INSTRUCTIONS.md" && echo   ✓ Removed INSTRUCTIONS.md
if exist "README.md" del "README.md" && echo   ✓ Removed README.md
if exist "WINDOWS_README.md" del "WINDOWS_README.md" && echo   ✓ Removed WINDOWS_README.md
if exist "WINDOWS_TROUBLESHOOTING.md" del "WINDOWS_TROUBLESHOOTING.md" && echo   ✓ Removed WINDOWS_TROUBLESHOOTING.md
if exist "requirements.txt" del "requirements.txt" && echo   ✓ Removed requirements.txt

REM Legacy Directories
echo [8/8] Removing legacy directories...
if exist "frames" rmdir /s /q "frames" && echo   ✓ Removed frames/ directory
if exist "videos" rmdir /s /q "videos" && echo   ✓ Removed videos/ directory
if exist "v4l2rtspserver" rmdir /s /q "v4l2rtspserver" && echo   ✓ Removed v4l2rtspserver directory

echo.
echo ================================================================
echo                      Cleanup Complete!
echo ================================================================
echo.
echo Cleanup Summary:
echo   ✓ Removed old/duplicate UI files
echo   ✓ Removed Linux-specific scripts
echo   ✓ Removed RTSP/complex streaming files
echo   ✓ Removed development/test scripts
echo   ✓ Removed duplicate documentation
echo   ✓ Removed legacy directories
echo.
echo Core files retained:
echo   ✓ simple_windows_ui.py (main application)
echo   ✓ Camera configuration tools
echo   ✓ Enhanced UI launchers
echo   ✓ FTP client system
echo   ✓ Core documentation
echo.
echo The project is now cleaner and more focused!
echo.
goto end

:cancel
echo.
echo [INFO] Cleanup cancelled by user.
echo No files were removed.

:end
pause

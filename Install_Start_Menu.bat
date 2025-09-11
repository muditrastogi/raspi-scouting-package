@echo off
title Install to Start Menu
color 0C

echo ================================================================
echo          Install Scouting Package to Start Menu
echo ================================================================
echo.
echo This will create Start Menu entries for:
echo   • Scouting Camera UI
echo   • Configure Cameras
echo   • Test Camera Detection
echo.
echo Continue? (Y/N)
set /p choice=
if /i not "%choice%"=="Y" goto :end

echo.
echo Installing Scouting Package to Start Menu...

REM Create Start Menu folder
set "StartMenuPath=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Scouting Package"
mkdir "%StartMenuPath%" 2>nul

echo Created folder: %StartMenuPath%

REM Create shortcuts in Start Menu using PowerShell
echo Creating shortcuts...

REM Main UI shortcut
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%StartMenuPath%\Scouting Camera UI.lnk'); $Shortcut.TargetPath = '%~dp0Start_Camera_UI.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = 'shell32.dll,23'; $Shortcut.Description = 'Main Camera UI Application'; $Shortcut.Save()}"

REM Configuration shortcut
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%StartMenuPath%\Configure Cameras.lnk'); $Shortcut.TargetPath = '%~dp0Configure_Cameras.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = 'shell32.dll,176'; $Shortcut.Description = 'Configure Camera Positions'; $Shortcut.Save()}"

REM Test shortcut
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%StartMenuPath%\Test Camera Detection.lnk'); $Shortcut.TargetPath = '%~dp0Test_Camera_Detection.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = 'shell32.dll,22'; $Shortcut.Description = 'Test Camera Detection'; $Shortcut.Save()}"

echo.
echo ================================================================
echo SUCCESS: Start Menu entries created successfully!
echo ================================================================
echo.
echo You can now access the Scouting Package from:
echo   Start Menu ^> All Programs ^> Scouting Package
echo.
echo Or search for:
echo   • "Scouting Camera"
echo   • "Configure Cameras"  
echo   • "Test Camera"
echo.

:end
pause

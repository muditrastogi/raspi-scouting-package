# PowerShell script to create desktop shortcuts for Scouting Package
# Run this script to create convenient desktop shortcuts

Write-Host "Creating Desktop Shortcuts for Raspberry Pi Scouting Package..." -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan

$WshShell = New-Object -comObject WScript.Shell

# Get current directory
$CurrentDir = (Get-Location).Path
Write-Host "Project Directory: $CurrentDir" -ForegroundColor Yellow

# Desktop path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
Write-Host "Desktop Path: $DesktopPath" -ForegroundColor Yellow

try {
    # Create shortcut for Main UI
    Write-Host "`nCreating shortcut: Scouting Camera UI..." -ForegroundColor White
    $Shortcut = $WshShell.CreateShortcut("$DesktopPath\Scouting Camera UI.lnk")
    $Shortcut.TargetPath = "$CurrentDir\Start_Camera_UI.bat"
    $Shortcut.WorkingDirectory = $CurrentDir
    $Shortcut.IconLocation = "shell32.dll,23"  # Camera icon
    $Shortcut.Description = "Raspberry Pi Scouting Package - Main Camera UI"
    $Shortcut.Save()
    Write-Host "✓ Created: Scouting Camera UI.lnk" -ForegroundColor Green

    # Create shortcut for Camera Configuration
    Write-Host "Creating shortcut: Configure Cameras..." -ForegroundColor White
    $Shortcut = $WshShell.CreateShortcut("$DesktopPath\Configure Cameras.lnk")
    $Shortcut.TargetPath = "$CurrentDir\Configure_Cameras.bat"
    $Shortcut.WorkingDirectory = $CurrentDir
    $Shortcut.IconLocation = "shell32.dll,176"  # Settings icon
    $Shortcut.Description = "Configure Camera Positions (Bottom, Middle, Top)"
    $Shortcut.Save()
    Write-Host "✓ Created: Configure Cameras.lnk" -ForegroundColor Green

    # Create shortcut for Camera Test
    Write-Host "Creating shortcut: Test Cameras..." -ForegroundColor White
    $Shortcut = $WshShell.CreateShortcut("$DesktopPath\Test Cameras.lnk")
    $Shortcut.TargetPath = "$CurrentDir\Test_Camera_Detection.bat"
    $Shortcut.WorkingDirectory = $CurrentDir
    $Shortcut.IconLocation = "shell32.dll,22"  # Search icon
    $Shortcut.Description = "Test Camera Detection and Troubleshoot Issues"
    $Shortcut.Save()
    Write-Host "✓ Created: Test Cameras.lnk" -ForegroundColor Green

    Write-Host "`n================================================================" -ForegroundColor Cyan
    Write-Host "SUCCESS: Desktop shortcuts created successfully!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Cyan
    
    Write-Host "`nCheck your desktop for these shortcuts:" -ForegroundColor Yellow
    Write-Host "  📹 Scouting Camera UI.lnk    - Main application" -ForegroundColor Cyan
    Write-Host "  ⚙️  Configure Cameras.lnk    - Set up camera positions" -ForegroundColor Cyan  
    Write-Host "  🔍 Test Cameras.lnk          - Test camera detection" -ForegroundColor Cyan

    Write-Host "`nQuick Start:" -ForegroundColor Yellow
    Write-Host "  1. Double-click 'Configure Cameras' to set up your cameras" -ForegroundColor White
    Write-Host "  2. Double-click 'Scouting Camera UI' to start the application" -ForegroundColor White

} catch {
    Write-Host "`nERROR: Failed to create shortcuts" -ForegroundColor Red
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nTry running PowerShell as Administrator" -ForegroundColor Yellow
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

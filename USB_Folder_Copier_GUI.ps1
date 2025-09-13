# USB Folder Copier GUI - Scout Videos Transfer
# PowerShell script with Windows Forms GUI for copying folders to USB drives

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Configuration
$RootDirectory = "$env:USERPROFILE\Desktop\scout-videos"
$DefaultSourcePath = $RootDirectory

# Create main form
$form = New-Object System.Windows.Forms.Form
$form.Text = "USB Folder Copier - Scout Videos Transfer"
$form.Size = New-Object System.Drawing.Size(800, 600)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.MinimizeBox = $false

# Set form icon (if available)
try {
    $form.Icon = [System.Drawing.SystemIcons]::Application
} catch {
    # Icon not available, continue without
}

# Create main panel
$mainPanel = New-Object System.Windows.Forms.Panel
$mainPanel.Dock = "Fill"
$mainPanel.Padding = New-Object System.Windows.Forms.Padding(10)
$form.Controls.Add($mainPanel)

# Title label
$titleLabel = New-Object System.Windows.Forms.Label
$titleLabel.Text = "USB Folder Copier - Scout Videos Transfer"
$titleLabel.Font = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Bold)
$titleLabel.ForeColor = [System.Drawing.Color]::DarkBlue
$titleLabel.AutoSize = $true
$titleLabel.Location = New-Object System.Drawing.Point(10, 10)
$mainPanel.Controls.Add($titleLabel)

# Description label
$descLabel = New-Object System.Windows.Forms.Label
$descLabel.Text = "Select a folder from the scout videos directory and copy it to any attached USB drive."
$descLabel.Font = New-Object System.Drawing.Font("Arial", 9)
$descLabel.ForeColor = [System.Drawing.Color]::DarkGray
$descLabel.AutoSize = $true
$descLabel.Location = New-Object System.Drawing.Point(10, 40)
$mainPanel.Controls.Add($descLabel)

# Source directory group
$sourceGroup = New-Object System.Windows.Forms.GroupBox
$sourceGroup.Text = "Source Directory"
$sourceGroup.Location = New-Object System.Drawing.Point(10, 70)
$sourceGroup.Size = New-Object System.Drawing.Size(760, 80)
$mainPanel.Controls.Add($sourceGroup)

# Source path textbox
$sourceTextBox = New-Object System.Windows.Forms.TextBox
$sourceTextBox.Text = $DefaultSourcePath
$sourceTextBox.Location = New-Object System.Drawing.Point(10, 25)
$sourceTextBox.Size = New-Object System.Drawing.Size(600, 20)
$sourceGroup.Controls.Add($sourceTextBox)

# Browse source button
$browseSourceButton = New-Object System.Windows.Forms.Button
$browseSourceButton.Text = "Browse..."
$browseSourceButton.Location = New-Object System.Drawing.Point(620, 23)
$browseSourceButton.Size = New-Object System.Drawing.Size(80, 25)
$browseSourceButton.Add_Click({
    $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
    $folderBrowser.Description = "Select source directory containing scout videos"
    $folderBrowser.SelectedPath = $sourceTextBox.Text
    $folderBrowser.ShowNewFolderButton = $false
    
    if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $sourceTextBox.Text = $folderBrowser.SelectedPath
        UpdateFolderList
    }
})
$sourceGroup.Controls.Add($browseSourceButton)

# Folder list group
$folderGroup = New-Object System.Windows.Forms.GroupBox
$folderGroup.Text = "Available Folders"
$folderGroup.Location = New-Object System.Drawing.Point(10, 160)
$folderGroup.Size = New-Object System.Drawing.Size(760, 200)
$mainPanel.Controls.Add($folderGroup)

# Folder listbox
$folderListBox = New-Object System.Windows.Forms.ListBox
$folderListBox.Location = New-Object System.Drawing.Point(10, 25)
$folderListBox.Size = New-Object System.Drawing.Size(740, 165)
$folderListBox.SelectionMode = "One"
$folderGroup.Controls.Add($folderListBox)

# Refresh folders button
$refreshButton = New-Object System.Windows.Forms.Button
$refreshButton.Text = "Refresh Folders"
$refreshButton.Location = New-Object System.Drawing.Point(10, 200)
$refreshButton.Size = New-Object System.Drawing.Size(100, 25)
$refreshButton.Add_Click({ UpdateFolderList })
$folderGroup.Controls.Add($refreshButton)

# USB drives group
$usbGroup = New-Object System.Windows.Forms.GroupBox
$usbGroup.Text = "Destination USB Drive"
$usbGroup.Location = New-Object System.Drawing.Point(10, 370)
$usbGroup.Size = New-Object System.Drawing.Size(760, 80)
$mainPanel.Controls.Add($usbGroup)

# USB drive combobox
$usbComboBox = New-Object System.Windows.Forms.ComboBox
$usbComboBox.DropDownStyle = "DropDownList"
$usbComboBox.Location = New-Object System.Drawing.Point(10, 25)
$usbComboBox.Size = New-Object System.Drawing.Size(600, 20)
$usbGroup.Controls.Add($usbComboBox)

# Refresh USB button
$refreshUsbButton = New-Object System.Windows.Forms.Button
$refreshUsbButton.Text = "Refresh USB"
$refreshUsbButton.Location = New-Object System.Drawing.Point(620, 23)
$refreshUsbButton.Size = New-Object System.Drawing.Size(80, 25)
$refreshUsbButton.Add_Click({ 
    UpdateUsbDrives
    # Also refresh folder list to update copy button state
    UpdateFolderList
})
$usbGroup.Controls.Add($refreshUsbButton)

# Troubleshoot USB button
$troubleshootUsbButton = New-Object System.Windows.Forms.Button
$troubleshootUsbButton.Text = "Troubleshoot"
$troubleshootUsbButton.Location = New-Object System.Drawing.Point(520, 23)
$troubleshootUsbButton.Size = New-Object System.Drawing.Size(90, 25)
$troubleshootUsbButton.Add_Click({
    $troubleshootMessage = @"
USB Drive Troubleshooting:

1. PHYSICAL CONNECTION:
   - Ensure USB drive is properly connected
   - Try different USB ports (USB 2.0 and USB 3.0)
   - Check if USB drive lights up or makes noise
   - Try a different USB cable if possible

2. DRIVE FORMAT:
   - USB drive must be formatted (FAT32, NTFS, or exFAT)
   - Open Disk Management (diskmgmt.msc) to check/format

3. DRIVE LETTER:
   - Drive may not have assigned letter
   - In Disk Management, right-click drive and assign letter

4. PERMISSIONS:
   - Run this program as Administrator
   - Check Windows security settings

5. ANTIVIRUS:
   - Some antivirus software blocks USB access
   - Temporarily disable real-time protection

Click OK to open Disk Management for manual checking.
"@
    
    $result = [System.Windows.Forms.MessageBox]::Show($troubleshootMessage, "USB Troubleshooting Guide", "OKCancel", "Information")
    if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
        Start-Process "diskmgmt.msc"
    }
})
$usbGroup.Controls.Add($troubleshootUsbButton)

# Progress group
$progressGroup = New-Object System.Windows.Forms.GroupBox
$progressGroup.Text = "Copy Progress"
$progressGroup.Location = New-Object System.Drawing.Point(10, 460)
$progressGroup.Size = New-Object System.Drawing.Size(760, 60)
$mainPanel.Controls.Add($progressGroup)

# Progress bar
$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.Location = New-Object System.Drawing.Point(10, 25)
$progressBar.Size = New-Object System.Drawing.Size(600, 20)
$progressBar.Style = "Continuous"
$progressGroup.Controls.Add($progressBar)

# Status label
$statusLabel = New-Object System.Windows.Forms.Label
$statusLabel.Text = "Ready to copy folders"
$statusLabel.Location = New-Object System.Drawing.Point(10, 50)
$statusLabel.Size = New-Object System.Drawing.Size(600, 15)
$statusLabel.ForeColor = [System.Drawing.Color]::DarkGreen
$progressGroup.Controls.Add($statusLabel)

# Action buttons
$copyButton = New-Object System.Windows.Forms.Button
$copyButton.Text = "Copy Selected Folder"
$copyButton.Location = New-Object System.Drawing.Point(620, 25)
$copyButton.Size = New-Object System.Drawing.Size(120, 30)
$copyButton.Enabled = $false
$copyButton.Add_Click({ CopySelectedFolder })
$progressGroup.Controls.Add($copyButton)

# Function to update folder list
function UpdateFolderList {
    $folderListBox.Items.Clear()
    $statusLabel.Text = "Scanning folders..."
    $statusLabel.ForeColor = [System.Drawing.Color]::Blue
    $form.Refresh()
    
    try {
        if (Test-Path $sourceTextBox.Text) {
            $folders = Get-ChildItem -Path $sourceTextBox.Text -Directory | Sort-Object Name
            foreach ($folder in $folders) {
                $folderInfo = "$($folder.Name) (Modified: $($folder.LastWriteTime.ToString('yyyy-MM-dd HH:mm')))"
                $folderListBox.Items.Add($folderInfo)
            }
            $statusLabel.Text = "Found $($folders.Count) folders"
            $statusLabel.ForeColor = [System.Drawing.Color]::DarkGreen
        } else {
            $statusLabel.Text = "Source directory not found: $($sourceTextBox.Text)"
            $statusLabel.ForeColor = [System.Drawing.Color]::Red
        }
    } catch {
        $statusLabel.Text = "Error scanning folders: $($_.Exception.Message)"
        $statusLabel.ForeColor = [System.Drawing.Color]::Red
    }
    
    $copyButton.Enabled = ($folderListBox.SelectedIndex -ge 0 -and $usbComboBox.SelectedIndex -ge 0)
}

# Function to update USB drives
function UpdateUsbDrives {
    $usbComboBox.Items.Clear()
    $statusLabel.Text = "Scanning USB drives..."
    $statusLabel.ForeColor = [System.Drawing.Color]::Blue
    $form.Refresh()
    
    try {
        # Method 1: Try WMI with DriveType=2 (USB drives)
        $drives = @()
        try {
            $drives = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DriveType -eq 2 -and $_.Size -gt 0 }
        } catch {
            Write-Host "WMI method failed, trying alternative methods..."
        }
        
        # Method 2: If WMI fails, try Get-PSDrive
        if ($drives.Count -eq 0) {
            try {
                $psDrives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -gt 0 -and $_.Name -match '^[E-Z]$' }
                foreach ($psDrive in $psDrives) {
                    $drive = New-Object PSObject
                    $drive | Add-Member -NotePropertyName "DeviceID" -NotePropertyValue "$($psDrive.Name):"
                    $drive | Add-Member -NotePropertyName "VolumeName" -NotePropertyValue "USB Drive"
                    $drive | Add-Member -NotePropertyName "FreeSpace" -NotePropertyValue ($psDrive.Free * 1GB)
                    $drive | Add-Member -NotePropertyName "Size" -NotePropertyValue (($psDrive.Used + $psDrive.Free) * 1GB)
                    $drives += $drive
                }
            } catch {
                Write-Host "Get-PSDrive method failed, trying direct drive check..."
            }
        }
        
        # Method 3: Direct drive letter check
        if ($drives.Count -eq 0) {
            $driveLetters = @('E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')
            foreach ($letter in $driveLetters) {
                if (Test-Path "$letter`:\") {
                    try {
                        $driveInfo = Get-ItemProperty -Path "$letter`:\" -ErrorAction SilentlyContinue
                        if ($driveInfo) {
                            $drive = New-Object PSObject
                            $drive | Add-Member -NotePropertyName "DeviceID" -NotePropertyValue "$letter`:"
                            $drive | Add-Member -NotePropertyName "VolumeName" -NotePropertyValue "USB Drive"
                            $drive | Add-Member -NotePropertyName "FreeSpace" -NotePropertyValue 0
                            $drive | Add-Member -NotePropertyName "Size" -NotePropertyValue 0
                            $drives += $drive
                        }
                    } catch {
                        # Continue to next drive
                    }
                }
            }
        }
        
        # Add drives to combobox
        foreach ($drive in $drives) {
            $driveLetter = $drive.DeviceID
            $driveLabel = if ($drive.VolumeName -and $drive.VolumeName -ne "USB Drive") { $drive.VolumeName } else { "USB Drive" }
            
            if ($drive.Size -gt 0) {
                $freeSpace = [math]::Round($drive.FreeSpace / 1GB, 2)
                $totalSpace = [math]::Round($drive.Size / 1GB, 2)
                $driveInfo = "$driveLetter - $driveLabel (Free: $freeSpace GB / $totalSpace GB)"
            } else {
                $driveInfo = "$driveLetter - $driveLabel"
            }
            
            $usbComboBox.Items.Add($driveInfo)
        }
        
        if ($drives.Count -eq 0) {
            $usbComboBox.Items.Add("No USB drives found - Check connections and try again")
            $statusLabel.Text = "No USB drives detected. Please check:"
            $statusLabel.ForeColor = [System.Drawing.Color]::Orange
            
            # Add troubleshooting info
            $troubleshootInfo = @"
Troubleshooting:
1. Ensure USB drive is connected
2. Check if drive is formatted
3. Try different USB port
4. Check Disk Management (diskmgmt.msc)
5. Assign drive letter if needed
"@
            $usbComboBox.Items.Add($troubleshootInfo)
        } else {
            $statusLabel.Text = "Found $($drives.Count) USB drive(s)"
            $statusLabel.ForeColor = [System.Drawing.Color]::DarkGreen
        }
    } catch {
        $statusLabel.Text = "Error scanning USB drives: $($_.Exception.Message)"
        $statusLabel.ForeColor = [System.Drawing.Color]::Red
        $usbComboBox.Items.Add("Error: $($_.Exception.Message)")
    }
    
    $copyButton.Enabled = ($folderListBox.SelectedIndex -ge 0 -and $usbComboBox.SelectedIndex -ge 0 -and $usbComboBox.SelectedItem -notlike "*No USB drives found*" -and $usbComboBox.SelectedItem -notlike "*Troubleshooting*" -and $usbComboBox.SelectedItem -notlike "*Error*")
}

# Function to copy selected folder
function CopySelectedFolder {
    if ($folderListBox.SelectedIndex -lt 0) {
        [System.Windows.Forms.MessageBox]::Show("Please select a folder to copy.", "No Folder Selected", "OK", "Warning")
        return
    }
    
    if ($usbComboBox.SelectedIndex -lt 0) {
        [System.Windows.Forms.MessageBox]::Show("Please select a USB drive.", "No USB Drive Selected", "OK", "Warning")
        return
    }
    
    # Get selected folder name
    $selectedFolderInfo = $folderListBox.SelectedItem.ToString()
    $folderName = $selectedFolderInfo.Split(' ')[0]
    $sourceFolder = Join-Path $sourceTextBox.Text $folderName
    
    # Get selected USB drive
    $selectedUsbInfo = $usbComboBox.SelectedItem.ToString()
    
    # Check if it's an error or troubleshooting message
    if ($selectedUsbInfo -like "*No USB drives found*" -or $selectedUsbInfo -like "*Troubleshooting*" -or $selectedUsbInfo -like "*Error*") {
        [System.Windows.Forms.MessageBox]::Show("Please select a valid USB drive from the list. If no drives are shown, click 'Troubleshoot' for help.", "Invalid USB Drive Selection", "OK", "Warning")
        return
    }
    
    $usbDrive = $selectedUsbInfo.Split(' ')[0]
    
    # Verify USB drive is accessible
    if (!(Test-Path "$usbDrive\")) {
        [System.Windows.Forms.MessageBox]::Show("Selected USB drive '$usbDrive' is not accessible. Please check the connection and try refreshing the USB list.", "USB Drive Not Accessible", "OK", "Error")
        UpdateUsbDrives
        return
    }
    
    $destinationPath = Join-Path $usbDrive "scout-videos"
    
    # Confirm copy operation
    $confirmMessage = "Copy folder '$folderName' to USB drive $usbDrive`n`nSource: $sourceFolder`nDestination: $destinationPath`n`nContinue?"
    $result = [System.Windows.Forms.MessageBox]::Show($confirmMessage, "Confirm Copy Operation", "YesNo", "Question")
    
    if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
        try {
            $statusLabel.Text = "Starting copy operation..."
            $statusLabel.ForeColor = [System.Drawing.Color]::Blue
            $progressBar.Value = 0
            $form.Refresh()
            
            # Create destination directory if it doesn't exist
            if (!(Test-Path $destinationPath)) {
                New-Item -ItemType Directory -Path $destinationPath -Force | Out-Null
            }
            
            # Calculate total size for progress
            $sourceSize = (Get-ChildItem -Path $sourceFolder -Recurse -File | Measure-Object -Property Length -Sum).Sum
            $copiedSize = 0
            
            # Copy folder with progress
            $destinationFolder = Join-Path $destinationPath $folderName
            if (Test-Path $destinationFolder) {
                $overwrite = [System.Windows.Forms.MessageBox]::Show("Folder already exists on USB drive. Overwrite?", "Folder Exists", "YesNo", "Question")
                if ($overwrite -eq [System.Windows.Forms.DialogResult]::No) {
                    $statusLabel.Text = "Copy operation cancelled"
                    $statusLabel.ForeColor = [System.Drawing.Color]::Orange
                    return
                }
                Remove-Item -Path $destinationFolder -Recurse -Force
            }
            
            # Copy files with progress tracking
            $files = Get-ChildItem -Path $sourceFolder -Recurse -File
            $fileCount = $files.Count
            $currentFile = 0
            
            foreach ($file in $files) {
                $relativePath = $file.FullName.Substring($sourceFolder.Length + 1)
                $destFile = Join-Path $destinationFolder $relativePath
                $destDir = Split-Path $destFile -Parent
                
                if (!(Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                
                Copy-Item -Path $file.FullName -Destination $destFile -Force
                $copiedSize += $file.Length
                $currentFile++
                
                $progress = [math]::Round(($copiedSize / $sourceSize) * 100)
                $progressBar.Value = [math]::Min($progress, 100)
                $statusLabel.Text = "Copying file $currentFile of $fileCount - $($file.Name)"
                $form.Refresh()
            }
            
            $progressBar.Value = 100
            $statusLabel.Text = "Copy completed successfully! Copied $fileCount files to $usbDrive"
            $statusLabel.ForeColor = [System.Drawing.Color]::DarkGreen
            
            # Show completion message
            [System.Windows.Forms.MessageBox]::Show("Folder copied successfully!`n`nFiles copied: $fileCount`nDestination: $destinationFolder", "Copy Complete", "OK", "Information")
            
        } catch {
            $statusLabel.Text = "Copy failed: $($_.Exception.Message)"
            $statusLabel.ForeColor = [System.Drawing.Color]::Red
            $progressBar.Value = 0
            
            $errorMessage = "Copy operation failed: $($_.Exception.Message)`n`n"
            
            # Add specific error guidance
            if ($_.Exception.Message -like "*Access denied*" -or $_.Exception.Message -like "*Permission*") {
                $errorMessage += "SOLUTION: Try running as Administrator or check USB drive permissions."
            } elseif ($_.Exception.Message -like "*not found*" -or $_.Exception.Message -like "*path*") {
                $errorMessage += "SOLUTION: USB drive may have been disconnected. Check connection and refresh USB list."
            } elseif ($_.Exception.Message -like "*space*" -or $_.Exception.Message -like "*full*") {
                $errorMessage += "SOLUTION: USB drive is full. Free up space or use a different drive."
            } elseif ($_.Exception.Message -like "*write*" -or $_.Exception.Message -like "*protected*") {
                $errorMessage += "SOLUTION: USB drive is write-protected. Remove write protection or use a different drive."
            } else {
                $errorMessage += "SOLUTION: Check USB drive connection and try refreshing the USB list."
            }
            
            [System.Windows.Forms.MessageBox]::Show($errorMessage, "Copy Failed", "OK", "Error")
        }
    }
}

# Event handlers for enabling/disabling copy button
$folderListBox.Add_SelectedIndexChanged({
    $copyButton.Enabled = ($folderListBox.SelectedIndex -ge 0 -and $usbComboBox.SelectedIndex -ge 0)
})

$usbComboBox.Add_SelectedIndexChanged({
    $copyButton.Enabled = ($folderListBox.SelectedIndex -ge 0 -and $usbComboBox.SelectedIndex -ge 0)
})

# Initialize the form
$form.Add_Load({
    UpdateFolderList
    UpdateUsbDrives
})

# Show the form
$form.ShowDialog() | Out-Null

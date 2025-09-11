# Advanced FTP Download Manager for Scout Videos
# PowerShell script for automated video downloading and management

param(
    [string]$ServerIP = "",
    [string]$Username = "pirecorder",
    [string]$Password = "recorderpi",
    [int]$Port = 21,
    [string]$LocalPath = "$env:USERPROFILE\Desktop\scout-videos-downloaded",
    [switch]$AutoDownload,
    [switch]$SyncMode,
    [switch]$Help
)

# Color output functions
function Write-ColorOutput {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Write-Success { param([string]$Text) Write-ColorOutput $Text "Green" }
function Write-Error { param([string]$Text) Write-ColorOutput $Text "Red" }
function Write-Warning { param([string]$Text) Write-ColorOutput $Text "Yellow" }
function Write-Info { param([string]$Text) Write-ColorOutput $Text "Cyan" }

# Help function
function Show-Help {
    Write-ColorOutput "
FTP Download Manager for Scout Videos
=====================================

Usage:
  .\FTP_Download_Manager.ps1 [parameters]

Parameters:
  -ServerIP <IP>        Raspberry Pi IP address (required)
  -Username <user>      FTP username (default: pirecorder)
  -Password <pass>      FTP password (default: recorderpi)
  -Port <port>          FTP port (default: 21)
  -LocalPath <path>     Local download directory
  -AutoDownload         Download all videos automatically
  -SyncMode             Only download new/missing files
  -Help                 Show this help

Examples:
  .\FTP_Download_Manager.ps1 -ServerIP 192.168.1.100
  .\FTP_Download_Manager.ps1 -ServerIP 192.168.1.100 -AutoDownload
  .\FTP_Download_Manager.ps1 -ServerIP 192.168.1.100 -SyncMode

Interactive Mode:
  Just run the script without parameters for interactive setup.
" "White"
}

# FTP Connection Test
function Test-FTPConnection {
    param([string]$Server, [string]$User, [string]$Pass, [int]$FTPPort)
    
    try {
        Write-Info "Testing connection to $Server`:$FTPPort..."
        
        # Test basic connectivity
        if (!(Test-Connection -ComputerName $Server -Count 2 -Quiet)) {
            throw "Cannot ping server $Server"
        }
        Write-Success "✓ Ping test successful"
        
        # Test FTP connection
        $ftpUri = "ftp://$Server`:$FTPPort/"
        $ftpRequest = [System.Net.FtpWebRequest]::Create($ftpUri)
        $ftpRequest.Credentials = New-Object System.Net.NetworkCredential($User, $Pass)
        $ftpRequest.Method = [System.Net.WebRequestMethods+Ftp]::ListDirectory
        $ftpRequest.Timeout = 10000
        
        $response = $ftpRequest.GetResponse()
        $response.Close()
        
        Write-Success "✓ FTP connection successful"
        return $true
        
    } catch {
        Write-Error "✗ Connection failed: $($_.Exception.Message)"
        return $false
    }
}

# Get FTP Directory Listing
function Get-FTPFiles {
    param([string]$Server, [string]$User, [string]$Pass, [int]$FTPPort, [string]$RemotePath = "")
    
    try {
        $ftpUri = "ftp://$Server`:$FTPPort/$RemotePath"
        $ftpRequest = [System.Net.FtpWebRequest]::Create($ftpUri)
        $ftpRequest.Credentials = New-Object System.Net.NetworkCredential($User, $Pass)
        $ftpRequest.Method = [System.Net.WebRequestMethods+Ftp]::ListDirectoryDetails
        
        $response = $ftpRequest.GetResponse()
        $responseStream = $response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($responseStream)
        $content = $reader.ReadToEnd()
        $reader.Close()
        $response.Close()
        
        $files = @()
        foreach ($line in $content.Split([Environment]::NewLine)) {
            if ($line.Trim() -ne "" -and !$line.StartsWith("total")) {
                # Parse directory listing (Unix format)
                $parts = $line -split '\s+', 9
                if ($parts.Count -ge 9) {
                    $filename = $parts[8]
                    $isDirectory = $line.StartsWith("d")
                    $size = $parts[4]
                    $date = "$($parts[5]) $($parts[6]) $($parts[7])"
                    
                    $files += [PSCustomObject]@{
                        Name = $filename
                        IsDirectory = $isDirectory
                        Size = $size
                        Date = $date
                        FullPath = if ($RemotePath) { "$RemotePath/$filename" } else { $filename }
                    }
                }
            }
        }
        
        return $files
        
    } catch {
        Write-Error "Error listing FTP directory: $($_.Exception.Message)"
        return @()
    }
}

# Download FTP File
function Download-FTPFile {
    param([string]$Server, [string]$User, [string]$Pass, [int]$FTPPort, [string]$RemoteFile, [string]$LocalFile)
    
    try {
        $ftpUri = "ftp://$Server`:$FTPPort/$RemoteFile"
        $ftpRequest = [System.Net.FtpWebRequest]::Create($ftpUri)
        $ftpRequest.Credentials = New-Object System.Net.NetworkCredential($User, $Pass)
        $ftpRequest.Method = [System.Net.WebRequestMethods+Ftp]::DownloadFile
        $ftpRequest.UseBinary = $true
        
        # Ensure local directory exists
        $localDir = [System.IO.Path]::GetDirectoryName($LocalFile)
        if (!(Test-Path $localDir)) {
            New-Item -ItemType Directory -Path $localDir -Force | Out-Null
        }
        
        Write-Info "Downloading: $RemoteFile"
        
        $response = $ftpRequest.GetResponse()
        $responseStream = $response.GetResponseStream()
        $fileStream = [System.IO.File]::Create($LocalFile)
        
        # Copy with progress (for large files)
        $buffer = New-Object byte[] 8192
        $totalBytes = 0
        
        do {
            $bytesRead = $responseStream.Read($buffer, 0, $buffer.Length)
            if ($bytesRead -gt 0) {
                $fileStream.Write($buffer, 0, $bytesRead)
                $totalBytes += $bytesRead
            }
        } while ($bytesRead -gt 0)
        
        $fileStream.Close()
        $responseStream.Close()
        $response.Close()
        
        Write-Success "✓ Downloaded: $RemoteFile ($totalBytes bytes)"
        return $true
        
    } catch {
        Write-Error "✗ Download failed: $RemoteFile - $($_.Exception.Message)"
        return $false
    }
}

# Interactive Server Setup
function Get-ServerInfo {
    if ($ServerIP -eq "") {
        Write-ColorOutput "`nFTP Server Configuration" "Yellow"
        Write-ColorOutput "=========================" "Yellow"
        
        do {
            $ServerIP = Read-Host "Enter Raspberry Pi IP address (e.g., 192.168.1.100)"
        } while ($ServerIP -eq "")
        
        $userInput = Read-Host "Enter FTP username [$Username]"
        if ($userInput -ne "") { $Username = $userInput }
        
        $passInput = Read-Host "Enter FTP password [$Password]"
        if ($passInput -ne "") { $Password = $passInput }
        
        $portInput = Read-Host "Enter FTP port [$Port]"
        if ($portInput -ne "" -and $portInput -match '^\d+$') { $Port = [int]$portInput }
        
        $pathInput = Read-Host "Enter local download path [$LocalPath]"
        if ($pathInput -ne "") { $LocalPath = $pathInput }
    }
    
    return @{
        ServerIP = $ServerIP
        Username = $Username 
        Password = $Password
        Port = $Port
        LocalPath = $LocalPath
    }
}

# Main Function
function Main {
    Write-ColorOutput "
╔══════════════════════════════════════════════════════════════╗
║                FTP Download Manager for Scout Videos         ║
║              Raspberry Pi Scouting Package                   ║
╚══════════════════════════════════════════════════════════════╝
" "Cyan"

    if ($Help) {
        Show-Help
        return
    }
    
    # Get server configuration
    $config = Get-ServerInfo
    
    # Test connection
    if (!(Test-FTPConnection -Server $config.ServerIP -User $config.Username -Pass $config.Password -FTPPort $config.Port)) {
        Write-Error "Cannot connect to FTP server. Please check your settings."
        return
    }
    
    # Create local directory
    if (!(Test-Path $config.LocalPath)) {
        New-Item -ItemType Directory -Path $config.LocalPath -Force | Out-Null
        Write-Info "Created local directory: $($config.LocalPath)"
    }
    
    # Get file listing
    Write-Info "Getting file listing from server..."
    $remoteFiles = Get-FTPFiles -Server $config.ServerIP -User $config.Username -Pass $config.Password -FTPPort $config.Port
    
    if ($remoteFiles.Count -eq 0) {
        Write-Warning "No files found on server"
        return
    }
    
    # Filter video files
    $videoFiles = $remoteFiles | Where-Object { 
        !$_.IsDirectory -and ($_.Name -like "*.avi" -or $_.Name -like "*.mp4" -or $_.Name -like "*.mov")
    }
    
    Write-Success "Found $($videoFiles.Count) video file(s) on server:"
    foreach ($file in $videoFiles) {
        Write-ColorOutput "  $($file.Name) ($($file.Size) bytes) - $($file.Date)" "White"
    }
    
    if ($AutoDownload) {
        # Automatic download mode
        Write-Info "`nStarting automatic download..."
        $downloaded = 0
        $skipped = 0
        
        foreach ($file in $videoFiles) {
            $localFile = Join-Path $config.LocalPath $file.Name
            
            if ($SyncMode -and (Test-Path $localFile)) {
                Write-Warning "Skipping existing file: $($file.Name)"
                $skipped++
                continue
            }
            
            if (Download-FTPFile -Server $config.ServerIP -User $config.Username -Pass $config.Password -FTPPort $config.Port -RemoteFile $file.Name -LocalFile $localFile) {
                $downloaded++
            }
        }
        
        Write-Success "`nDownload Summary:"
        Write-Success "  Downloaded: $downloaded files"
        Write-Warning "  Skipped: $skipped files"
        Write-Info "  Local directory: $($config.LocalPath)"
        
    } else {
        # Interactive download mode
        Write-ColorOutput "`nDownload Options:" "Yellow"
        Write-ColorOutput "1) Download all video files" "White"
        Write-ColorOutput "2) Select specific files to download" "White"
        Write-ColorOutput "3) Sync mode (download only new files)" "White"
        Write-ColorOutput "4) Exit" "White"
        
        $choice = Read-Host "`nEnter your choice (1-4)"
        
        switch ($choice) {
            "1" {
                # Download all
                foreach ($file in $videoFiles) {
                    $localFile = Join-Path $config.LocalPath $file.Name
                    Download-FTPFile -Server $config.ServerIP -User $config.Username -Pass $config.Password -FTPPort $config.Port -RemoteFile $file.Name -LocalFile $localFile
                }
            }
            "2" {
                # Select specific files
                Write-ColorOutput "`nAvailable files:" "Yellow"
                for ($i = 0; $i -lt $videoFiles.Count; $i++) {
                    Write-ColorOutput "$($i + 1)) $($videoFiles[$i].Name)" "White"
                }
                
                $selection = Read-Host "`nEnter file numbers to download (comma-separated, e.g., 1,3,5)"
                $indices = $selection -split ',' | ForEach-Object { [int]$_.Trim() - 1 }
                
                foreach ($index in $indices) {
                    if ($index -ge 0 -and $index -lt $videoFiles.Count) {
                        $file = $videoFiles[$index]
                        $localFile = Join-Path $config.LocalPath $file.Name
                        Download-FTPFile -Server $config.ServerIP -User $config.Username -Pass $config.Password -FTPPort $config.Port -RemoteFile $file.Name -LocalFile $localFile
                    }
                }
            }
            "3" {
                # Sync mode
                foreach ($file in $videoFiles) {
                    $localFile = Join-Path $config.LocalPath $file.Name
                    
                    if (!(Test-Path $localFile)) {
                        Download-FTPFile -Server $config.ServerIP -User $config.Username -Pass $config.Password -FTPPort $config.Port -RemoteFile $file.Name -LocalFile $localFile
                    } else {
                        Write-Warning "Skipping existing file: $($file.Name)"
                    }
                }
            }
            "4" {
                Write-Info "Exiting..."
                return
            }
            default {
                Write-Error "Invalid choice"
                return
            }
        }
    }
    
    Write-Success "`nDownload process completed!"
    Write-Info "Files saved to: $($config.LocalPath)"
    
    # Open download folder
    $openFolder = Read-Host "`nOpen download folder? (Y/N)"
    if ($openFolder -eq 'Y' -or $openFolder -eq 'y') {
        Start-Process explorer.exe -ArgumentList $config.LocalPath
    }
}

# Run main function
try {
    Main
} catch {
    Write-Error "Unexpected error: $($_.Exception.Message)"
    Write-Error "Stack trace: $($_.ScriptStackTrace)"
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

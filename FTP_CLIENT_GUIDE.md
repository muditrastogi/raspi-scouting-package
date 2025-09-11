# FTP Client Guide for Scout Videos

Complete guide for connecting to the Raspberry Pi FTP server and downloading scout videos using various FTP clients.

## Table of Contents

1. [Overview](#overview)
2. [FTP Server Configuration](#ftp-server-configuration)
3. [Windows FTP Client Options](#windows-ftp-client-options)
4. [Quick Start Methods](#quick-start-methods)
5. [GUI FTP Clients](#gui-ftp-clients)
6. [Command Line Methods](#command-line-methods)
7. [Automated Download Scripts](#automated-download-scripts)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Raspberry Pi runs an FTP server (`ftpserver.py`) that provides access to recorded scout videos. This guide covers multiple ways to connect and download these videos from Windows computers.

### Default FTP Server Settings
- **Protocol**: FTP
- **Port**: 21
- **Username**: `pirecorder`
- **Password**: `recorderpi`
- **Root Directory**: `~/Desktop/scout-videos/`
- **Access**: Read/Write permissions

---

## FTP Server Configuration

### Server Details (from ftpserver.py)
```python
FTP_PORT = 21
FTP_USERNAME = "pirecorder"
FTP_PASSWORD = "recorderpi"
MAC_ADDRESS = "14:98:77:7c:8f:08"  # Target device MAC
FALLBACK_IP = "192.168.1.3"        # Fallback IP
PING_INTERVAL = 10                  # Network keep-alive interval
```

### Video Storage Location
Videos are stored in: `/home/pi/Desktop/scout-videos/`
Organized by date and grid: `recordings_2024-01-15/A-1-A-bottom/`

---

## Windows FTP Client Options

### Available Tools

| Tool | Type | Ease of Use | Features | Best For |
|------|------|-------------|----------|----------|
| `FTP_Client_Setup.bat` | Launcher | ⭐⭐⭐⭐⭐ | All-in-one setup | Beginners |
| `Quick_FTP_Download.bat` | Launcher | ⭐⭐⭐⭐⭐ | Quick downloads | Regular use |
| `FTP_Download_Manager.ps1` | PowerShell | ⭐⭐⭐⭐ | Advanced features | Power users |
| FileZilla | GUI Client | ⭐⭐⭐⭐ | Professional | File management |
| WinSCP | GUI Client | ⭐⭐⭐⭐ | Secure protocols | IT professionals |
| Windows FTP | Command Line | ⭐⭐ | Basic operations | Quick tasks |

---

## Quick Start Methods

### Method 1: One-Click Setup (Recommended for Beginners)
1. **Double-click**: `FTP_Client_Setup.bat`
2. **Choose option 2**: FileZilla FTP Client (GUI)
3. **Enter Raspberry Pi IP** when prompted
4. **Download and install** FileZilla when prompted
5. **Connect and download** videos using the GUI

### Method 2: Quick Download (Recommended for Regular Use)
1. **Double-click**: `Quick_FTP_Download.bat`
2. **Choose option 1**: Interactive FTP Download
3. **Enter Raspberry Pi IP** when prompted
4. **Select download option** (all files, specific files, or sync)
5. **Videos download automatically**

### Method 3: Advanced PowerShell (Power Users)
```powershell
.\FTP_Download_Manager.ps1 -ServerIP 192.168.1.100 -AutoDownload
```

---

## GUI FTP Clients

### FileZilla Client Setup

#### Installation
1. **Download**: https://filezilla-project.org/download.php?type=client
2. **Install**: Run installer with default settings
3. **Launch**: Start FileZilla

#### Connection Setup
1. **Host**: Enter Raspberry Pi IP (e.g., `192.168.1.100`)
2. **Username**: `pirecorder`
3. **Password**: `recorderpi`
4. **Port**: `21`
5. **Click**: "Quickconnect"

#### Using FileZilla
- **Left Panel**: Your computer (local files)
- **Right Panel**: Raspberry Pi (remote files)
- **Navigate**: Double-click folders to browse
- **Download**: Drag files from right to left panel
- **Upload**: Drag files from left to right panel

#### FileZilla Features
- ✅ Resume interrupted downloads
- ✅ Queue multiple file transfers
- ✅ Directory synchronization
- ✅ Site manager for saved connections
- ✅ Transfer speed limiting

### WinSCP Client Setup

#### Installation
1. **Download**: https://winscp.net/eng/download.php
2. **Install**: Run installer with default settings
3. **Launch**: Start WinSCP

#### Connection Setup
1. **File protocol**: FTP
2. **Host name**: Raspberry Pi IP
3. **Port number**: `21`
4. **User name**: `pirecorder`
5. **Password**: `recorderpi`
6. **Click**: "Login"

#### WinSCP Features
- ✅ Dual-pane interface
- ✅ Built-in editor
- ✅ Synchronization wizard
- ✅ Command line interface
- ✅ Integration with PuTTY

---

## Command Line Methods

### Windows Built-in FTP Client

#### Basic Connection
```cmd
ftp 192.168.1.100
# Enter username: pirecorder
# Enter password: recorderpi
```

#### Useful Commands
```ftp
ls                    # List files
cd directory_name     # Change directory
get filename          # Download single file
mget *.avi           # Download all .avi files
binary               # Set binary mode (for videos)
put filename         # Upload file
quit                 # Exit FTP
```

#### Scripted FTP Session
```cmd
echo open 192.168.1.100 > ftp_script.txt
echo pirecorder >> ftp_script.txt
echo recorderpi >> ftp_script.txt
echo binary >> ftp_script.txt
echo mget *.avi >> ftp_script.txt
echo quit >> ftp_script.txt

ftp -s:ftp_script.txt
```

### PowerShell FTP Commands

#### Basic Download
```powershell
$webclient = New-Object System.Net.WebClient
$webclient.Credentials = New-Object System.Net.NetworkCredential("pirecorder", "recorderpi")
$webclient.DownloadFile("ftp://192.168.1.100/video.avi", "C:\Downloads\video.avi")
```

---

## Automated Download Scripts

### FTP_Download_Manager.ps1 Features

#### Command Line Usage
```powershell
# Interactive mode
.\FTP_Download_Manager.ps1

# Automatic download all
.\FTP_Download_Manager.ps1 -ServerIP 192.168.1.100 -AutoDownload

# Sync mode (only new files)
.\FTP_Download_Manager.ps1 -ServerIP 192.168.1.100 -AutoDownload -SyncMode

# Custom settings
.\FTP_Download_Manager.ps1 -ServerIP 192.168.1.100 -Username myuser -Password mypass -Port 2121
```

#### Features
- ✅ **Connection Testing**: Verifies server accessibility
- ✅ **File Filtering**: Only downloads video files (.avi, .mp4, .mov)
- ✅ **Progress Tracking**: Shows download progress and statistics
- ✅ **Sync Mode**: Downloads only new/missing files
- ✅ **Error Handling**: Robust error recovery and reporting
- ✅ **Interactive Mode**: User-friendly prompts and menus
- ✅ **Batch Mode**: Fully automated downloads
- ✅ **Resume Support**: Can resume interrupted downloads

#### Download Modes
1. **Interactive**: User selects files to download
2. **Auto Download**: Downloads all video files automatically
3. **Sync Mode**: Downloads only new files not already present locally
4. **Selective**: User chooses specific files from a list

---

## Troubleshooting

### Common Issues

#### "Cannot connect to server"
**Symptoms**: Connection timeout or refused
**Solutions**:
1. **Check IP address**: Verify Raspberry Pi IP
   ```cmd
   ping 192.168.1.100
   ```
2. **Check FTP server**: Ensure `ftpserver.py` is running on Raspberry Pi
3. **Check firewall**: Verify port 21 is not blocked
4. **Check network**: Ensure both devices on same network

#### "Login failed" or "Authentication error"
**Symptoms**: Wrong username/password error
**Solutions**:
1. **Verify credentials**: Username: `pirecorder`, Password: `recorderpi`
2. **Check server config**: Verify `ftpserver.py` settings
3. **Case sensitivity**: Ensure exact case for username/password

#### "No files found" or "Empty directory"
**Symptoms**: FTP connects but shows no files
**Solutions**:
1. **Check directory**: Verify videos exist in `~/Desktop/scout-videos/`
2. **Check permissions**: Ensure FTP user has read access
3. **Check path**: Navigate to correct directory in FTP client

#### "Download fails" or "Transfer interrupted"
**Symptoms**: Downloads start but fail partway
**Solutions**:
1. **Use binary mode**: Essential for video files
   ```ftp
   binary
   ```
2. **Check disk space**: Ensure enough local storage
3. **Check network stability**: Use wired connection if possible
4. **Use resume**: FileZilla and PowerShell script support resume

#### "Permission denied"
**Symptoms**: Cannot write to local directory
**Solutions**:
1. **Check local permissions**: Ensure write access to download directory
2. **Run as administrator**: May need elevated privileges
3. **Change download location**: Use different local directory

### Advanced Troubleshooting

#### Network Diagnostics
```cmd
# Test basic connectivity
ping 192.168.1.100

# Test FTP port
telnet 192.168.1.100 21

# Check network route
tracert 192.168.1.100

# Check DNS resolution
nslookup raspberrypi.local
```

#### FTP Server Diagnostics
```bash
# On Raspberry Pi, check if FTP server is running
ps aux | grep python
netstat -ln | grep :21

# Check FTP logs
tail -f /var/log/ftp.log

# Test local FTP connection
ftp localhost
```

#### PowerShell Debugging
```powershell
# Enable detailed error messages
$ErrorActionPreference = "Stop"

# Test FTP connection manually
$ftpRequest = [System.Net.FtpWebRequest]::Create("ftp://192.168.1.100/")
$ftpRequest.Credentials = New-Object System.Net.NetworkCredential("pirecorder", "recorderpi")
$ftpRequest.Method = [System.Net.WebRequestMethods+Ftp]::ListDirectory
$response = $ftpRequest.GetResponse()
```

### Performance Optimization

#### Download Speed
- **Use wired connection**: Ethernet faster than WiFi
- **Close other applications**: Free up bandwidth
- **Use binary mode**: Essential for video files
- **Multiple connections**: Some clients support parallel downloads

#### Reliability
- **Stable network**: Avoid WiFi interference
- **Resume capability**: Use clients that support resume
- **Batch processing**: Download in smaller batches
- **Error retry**: Implement automatic retry logic

---

## File Organization

### Local Download Structure
```
%USERPROFILE%\Desktop\scout-videos-downloaded\
├── ABC_GRID_A-1-A_1_recording_20240115_120000_bottom.avi
├── ABC_GRID_A-1-A_1_recording_20240115_120000_middle.avi
├── ABC_GRID_A-1-A_1_recording_20240115_120000_top.avi
├── ABC_GRID_A-1-B_2_recording_20240115_120530_bottom.avi
└── ...
```

### File Naming Convention
```
ABC_GRID_{grid}_{counter}_recording_{timestamp}_{position}.avi

Where:
- grid: A-1-A, A-1-B, A-2-A, etc.
- counter: Sequential recording number
- timestamp: YYYYMMDD_HHMMSS
- position: bottom, middle, top
```

---

## Security Considerations

### FTP Limitations
- **Unencrypted**: FTP transmits passwords in plain text
- **Local network**: Only use on trusted local networks
- **Default credentials**: Consider changing default username/password

### Best Practices
1. **Local network only**: Never expose FTP server to internet
2. **Change credentials**: Modify default username/password in `ftpserver.py`
3. **Regular updates**: Keep FTP server software updated
4. **Monitor access**: Check FTP logs for unauthorized access
5. **Backup videos**: Maintain local backups of important recordings

---

## Integration with Scouting Workflow

### Typical Workflow
1. **Record videos**: Use `Start_Camera_UI.bat` to record scout videos
2. **Start FTP server**: Run `ftpserver.py` on Raspberry Pi
3. **Download videos**: Use any FTP client method to download
4. **Organize locally**: Sort videos by date, team, or grid
5. **Analysis**: Use video analysis software on downloaded files

### Automation Options
- **Scheduled downloads**: Use Windows Task Scheduler with PowerShell script
- **Real-time sync**: Monitor for new files and auto-download
- **Batch processing**: Download all videos at end of day
- **Cloud backup**: Upload downloaded videos to cloud storage

---

## Support and Resources

### Quick Reference
- **Default IP**: Usually `192.168.1.x` (check with `ipconfig`)
- **Default Port**: 21
- **Username**: `pirecorder`
- **Password**: `recorderpi`
- **Local Downloads**: `%USERPROFILE%\Desktop\scout-videos-downloaded\`

### Files
- **`FTP_Client_Setup.bat`**: Main FTP client setup tool
- **`Quick_FTP_Download.bat`**: Quick download launcher
- **`FTP_Download_Manager.ps1`**: Advanced PowerShell script
- **`ftpserver.py`**: Raspberry Pi FTP server

### Documentation
- **`PROJECT_SETUP_GUIDE.md`**: Complete project setup
- **`WINDOWS_CAMERA_CONFIG.md`**: Camera configuration
- **`FTP_CLIENT_GUIDE.md`**: This guide

For additional help, refer to the troubleshooting sections or create an issue on the GitHub repository.

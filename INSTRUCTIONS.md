# Raspberry Pi Scouting Package - Installation & Usage Instructions

This guide provides complete instructions for installing, configuring, and using the Raspberry Pi Scouting Package for multi-camera video recording and streaming.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Hardware Setup](#hardware-setup)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the System](#running-the-system)
6. [Using the Interface](#using-the-interface)
7. [Remote Access](#remote-access)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)
10. [Advanced Usage](#advanced-usage)

## 🔧 Prerequisites

### Hardware Requirements
- **Raspberry Pi 4** (recommended) or Raspberry Pi 3B+
- **MicroSD Card**: 32GB or larger (Class 10 recommended)
- **USB Cameras**: Up to 3 USB cameras (UVC compatible)
- **Power Supply**: Official Raspberry Pi power supply (5V/3A for Pi 4)
- **Network Connection**: Ethernet or WiFi
- **Display**: HDMI monitor/TV for initial setup and GUI usage

### Software Requirements
- **Raspberry Pi OS**: Latest version (Bullseye or newer)
- **Python 3.7+**: Usually pre-installed
- **Git**: For cloning the repository
- **Internet Connection**: For downloading dependencies

### Camera Compatibility
- **UVC (USB Video Class) cameras** are recommended
- **Webcams**: Most standard USB webcams work
- **Avoid**: Cameras requiring proprietary drivers
- **Test**: Check camera compatibility with `lsusb` and `v4l2-ctl --list-devices`

## 🔌 Hardware Setup

### 1. Prepare Your Raspberry Pi
```bash
# Update your system first
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git python3-pip python3-venv v4l-utils ffmpeg curl lsof
```

### 2. Connect Your Cameras
1. **Power off** your Raspberry Pi
2. **Connect USB cameras** to available USB ports
3. **Use a powered USB hub** if connecting multiple cameras
4. **Power on** the Raspberry Pi
5. **Verify camera detection**:
   ```bash
   # List connected cameras
   v4l2-ctl --list-devices
   
   # Check camera capabilities
   v4l2-ctl --device=/dev/video0 --list-formats-ext
   ```

### 3. Network Setup
- **Ethernet**: Connect network cable for best performance
- **WiFi**: Configure through `raspi-config` if needed
- **Static IP**: Consider setting a static IP for consistent access

## 🚀 Installation

### Method 1: Automated Installation (Recommended)

1. **Clone the Repository**
   ```bash
   cd ~
   git clone https://github.com/greenprem/raspi-scouting-package.git
   cd raspi-scouting-package
   ```

2. **Run the Installer**
   ```bash
   # Make installer executable
   chmod +x install.sh
   
   # Run installation (DO NOT use sudo)
   ./install.sh
   ```

3. **Wait for Completion**
   - The installer will show progress bars
   - Installation takes 5-15 minutes depending on your Pi
   - The script will create all necessary directories and services

### Method 2: Manual Installation

If the automated installer fails, follow these manual steps:

1. **Create Directory Structure**
   ```bash
   mkdir -p ~/Desktop/usb_raspi_package
   mkdir -p ~/Desktop/usb_raspi_package_camerafixed_frame
   mkdir -p ~/Desktop/gr-robo
   mkdir -p ~/Desktop/scout-videos
   mkdir -p ~/Desktop/systemlogs
   ```

2. **Copy Files**
   ```bash
   # For video recording version
   cp videos/* ~/Desktop/usb_raspi_package/
   cp v4l2rtspserver ~/Desktop/usb_raspi_package/
   
   # For frame recording version
   cp frames/* ~/Desktop/usb_raspi_package_camerafixed_frame/
   cp v4l2rtspserver ~/Desktop/usb_raspi_package_camerafixed_frame/
   cp config.txt ~/Desktop/usb_raspi_package_camerafixed_frame/
   
   # Copy utility scripts
   cp delete_except_newest.sh ~/Desktop/
   cp ftpserver.py system_monitor.py requirements.txt ~/
   ```

3. **Make Scripts Executable**
   ```bash
   chmod +x ~/Desktop/usb_raspi_package/desktopmultiv5.sh
   chmod +x ~/Desktop/usb_raspi_package_camerafixed_frame/desktopmultiv5.sh
   chmod +x ~/Desktop/usb_raspi_package/v4l2rtspserver
   chmod +x ~/Desktop/usb_raspi_package_camerafixed_frame/v4l2rtspserver
   chmod +x ~/Desktop/delete_except_newest.sh
   ```

4. **Setup Python Environment**
   ```bash
   python3 -m venv ~/Desktop/gr-robo/venv
   source ~/Desktop/gr-robo/venv/bin/activate
   pip install --upgrade pip
   pip install -r ~/requirements.txt
   deactivate
   ```

5. **Install System Packages**
   ```bash
   sudo apt install -y python3-pyftpdlib
   ```

## ⚙️ Configuration

### 1. Camera Configuration

#### Method A: Interactive Camera Configuration (Recommended)

Use the provided camera configuration script for easy setup:

```bash
# Make the script executable
chmod +x configure_cameras.sh

# Run the configuration script
./configure_cameras.sh
```

**What the script does:**
- Provides an interactive menu to configure each camera position
- Automatically detects camera serial IDs when you connect them one by one
- Updates `config.txt` with the correct serial numbers for automatic camera ordering
- Allows you to test camera detection and reset configurations

**Usage workflow:**
1. **Select camera position** (Bottom, Middle, or Top)
2. **Remove all cameras** from the Raspberry Pi
3. **Connect only the camera** you want to assign to that position
4. **Press Enter** to detect and save the camera serial ID
5. **Repeat** for each camera position
6. **Exit** when all cameras are configured

#### Method B: Manual Camera Configuration

Edit the camera configuration file manually:
```bash
nano ~/Desktop/usb_raspi_package_camerafixed_frame/config.txt
```

**Configuration Options:**
```ini
# Video resolution (width x height)
resolution=1920x1080

# Frame rate (frames per second)
fps=30

# Camera serial numbers (leave empty if not configuring automatic order)
bottomcamera=
middlecamera=
topcamera=
```

**Finding Camera Serial Numbers manually:**
```bash
# List cameras with serial information (connect one camera at a time)
udevadm info --query=all --name=/dev/video0 | awk -F= '/ID_SERIAL_SHORT/ {print $2}'

# Or use this command to see all cameras and their serials:
for dev in /dev/video*; do
    if [ -e "$dev" ]; then
        echo "Device: $dev"
        udevadm info --query=all --name="$dev" | grep ID_SERIAL_SHORT
        echo "---"
    fi
done
```

### 2. Network Configuration

**FTP Server Settings** (in `ftpserver.py`):
```python
# Default settings (modify if needed)
FTP_USERNAME = "pirecorder"
FTP_PASSWORD = "recorderpi"
FTP_PORT = 21

# Target device MAC address for keep-alive
MAC_ADDRESS = "14:98:77:7c:8f:08"  # Update this
FALLBACK_IP = "192.168.1.3"        # Update this
```

### 3. Service Configuration

The system monitor service is automatically configured during installation. Check its status:
```bash
# Check service status
sudo systemctl status system-monitor.service

# View service logs
sudo journalctl -u system-monitor.service -f
```

## 🏃 Running the System

### Option 1: Video Recording Version (Recommended for most users)

```bash
cd ~/Desktop/usb_raspi_package
./desktopmultiv5.sh
```

### Option 2: Frame Recording Version (For specific use cases)

```bash
cd ~/Desktop/usb_raspi_package_camerafixed_frame
./desktopmultiv5.sh
```

### What Happens During Startup:

1. **Camera Detection**: System scans for USB cameras
2. **Camera Ordering**: Orders cameras based on config.txt serial IDs
3. **RTSP Server Startup**: Starts streaming servers for each camera
4. **API Server Startup**: Starts recording control APIs
5. **GUI Launch**: Opens the main interface window

**Expected Output:**
```
[INFO] Starting local USB camera RTSP setup...
[INFO] Reading configuration from config.txt
[INFO] Config: bottomcamera=ABC123
[INFO] Config: middlecamera=DEF456
[INFO] Config: topcamera=GHI789
[INFO] Detecting available USB cameras...
[SUCCESS] Found playable camera: /dev/video0 (Serial: ABC123)
[SUCCESS] Found playable camera: /dev/video2 (Serial: DEF456)
[INFO] Added camera /dev/video0 (Serial: ABC123) in configured order
[INFO] Added camera /dev/video2 (Serial: DEF456) in configured order
[INFO] Starting v4l2rtspserver for /dev/video0 on port 8554...
[SUCCESS] v4l2rtspserver started for /dev/video0 on port 8554 (PID: 1234)
[INFO] Starting record API on port 5000...
[SUCCESS] Record API started on port 5000 (PID: 5678)
[INFO] Launching Python UI application...
``` 
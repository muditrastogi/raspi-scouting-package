# Windows Raspberry Pi Scouting Package

A Windows-compatible version of the Raspberry Pi Scouting Package for capturing video or image frames from USB cameras via RTSP. This system offers two modes: continuous video recording or single-frame image capture, with a modern GUI built using Tkinter and Python.

> ✅ This Windows version is designed for robotics, surveillance, or remote monitoring where quick setup, local streaming, and flexible capture modes are essential on Windows systems.

---

## 📦 Features

- 🎥 Live RTSP stream preview using VLC and OpenCV
- 🧪 Two operational modes:
  - **Video Mode** – continuous video recording
  - **Frame Mode** – saves images frame by frame
- 🧠 Modern Tkinter-based GUI with Start/Stop controls
- 🚀 Fast setup via one-click Windows installer
- 🔌 Auto-detection of USB cameras using DirectShow
- 🔧 Lightweight Flask API to trigger recording
- 📈 Background system monitoring
- 📤 FTP server included (for remote file access)
- 🖥️ Full Windows compatibility

---

## 🗂️ Folder Structure (Post Install)

```text
C:\Users\[Username]\Desktop\
├── scout-videos\                    # Video recordings
│   └── recordings_[DATE]\          # Daily recording folders
├── systemlogs\                      # System and application logs
│   ├── launcher_[DATE].log         # Launcher logs
│   ├── system_metrics_[DATE].json  # System performance data
│   ├── ftp_server.log              # FTP server logs
│   └── cleanup_script.log          # Cleanup operation logs
│
├── Start Scouting System.bat        # Main launcher shortcut
├── Configure Cameras.bat            # Camera setup shortcut
├── Start FTP Server.bat             # FTP server shortcut
├── Start System Monitor.bat         # System monitoring shortcut
└── Cleanup Old Files.bat            # File cleanup shortcut
```

---

## 🚀 Installation

### Prerequisites

- **Windows 10/11** (64-bit recommended)
- **Python 3.8+** with pip
- **FFmpeg** for video processing
- **VLC Media Player** for video streaming
- **USB Cameras** (UVC compatible)

### 🧠 One-Click Setup (Recommended)

1. **Download and Extract**
   - Download the Windows package
   - Extract to a folder (e.g., `C:\raspi-scouting-package`)

2. **Run the Installer**
   - Double-click `install_windows.bat`
   - Follow the on-screen instructions
   - The installer will check dependencies and create shortcuts

3. **Install Missing Dependencies**
   - If FFmpeg is missing, download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - If VLC is missing, download from [videolan.org](https://www.videolan.org/vlc/)

### 🔧 Manual Installation

If the automated installer fails, follow these manual steps:

1. **Install Python Dependencies**
   ```cmd
   pip install -r requirements_windows.txt
   ```

2. **Create Directories**
   ```cmd
   mkdir "%USERPROFILE%\Desktop\scout-videos"
   mkdir "%USERPROFILE%\Desktop\systemlogs"
   ```

3. **Copy Configuration**
   ```cmd
   copy config_windows.txt config.txt
   ```

---

## 🖥️ Usage

### 📽️ Launch the System

1. **Connect USB Cameras**
   - Connect your cameras to available USB ports
   - Ensure cameras are recognized by Windows

2. **Configure Cameras** (First time only)
   - Double-click `Configure Cameras.bat`
   - Follow the interactive setup to assign camera positions
   - Save configuration when complete

3. **Start the System**
   - Double-click `Start Scouting System.bat`
   - The system will detect cameras and launch the GUI

### 🎮 GUI Controls

- **Start Stream**: Begins RTSP preview via OpenCV
- **Start Record**: Calls the internal Flask API → triggers FFmpeg → saves video or frames
- **Stop**: Ends stream or recording

### 🔧 Optional Services

- **FTP Server**: Run `Start FTP Server.bat` for remote file access
- **System Monitor**: Run `Start System Monitor.bat` for performance monitoring
- **File Cleanup**: Run `Cleanup Old Files.bat` to manage disk space

---

## ⚙️ Configuration

### Camera Configuration

The system automatically detects and configures cameras. Use the camera configuration script to:

- Assign cameras to specific positions (bottom, middle, top)
- Test camera accessibility
- Save camera IDs for automatic ordering

### System Configuration

Edit `config.txt` to customize:

- Video resolution and frame rate
- Recording quality and format
- Network ports and FTP settings
- Storage directories and cleanup policies
- System monitoring thresholds

---

## 🔧 Troubleshooting

### Common Issues

1. **Cameras Not Detected**
   - Ensure cameras are UVC compatible
   - Check Windows Device Manager
   - Try different USB ports
   - Restart the system

2. **FFmpeg Not Found**
   - Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Extract to `C:\ffmpeg`
   - Add `C:\ffmpeg\bin` to PATH environment variable

3. **VLC Not Found**
   - Download VLC from [videolan.org](https://www.videolan.org/vlc/)
   - Install with default settings
   - Restart the system

4. **Permission Errors**
   - Run as Administrator if needed
   - Check antivirus software settings
   - Ensure write permissions to Desktop folders

5. **Port Conflicts**
   - Check if ports 8554, 5000, or 21 are in use
   - Modify `config.txt` to use different ports
   - Restart the system

### Log Files

Check these log files for detailed error information:

- `%USERPROFILE%\Desktop\systemlogs\launcher_[DATE].log`
- `%USERPROFILE%\Desktop\systemlogs\ftp_server.log`
- `%USERPROFILE%\Desktop\systemlogs\cleanup_script.log`

---

## 🔄 Updating

To update the system:

1. **Backup Configuration**
   - Copy your `config.txt` to a safe location

2. **Download New Version**
   - Download the latest Windows package
   - Extract to a new folder

3. **Reinstall**
   - Run `install_windows.bat` in the new folder
   - Restore your `config.txt`

---

## 📚 API Reference

### Recording API Endpoints

- `POST /start_record` - Start recording for a specific grid
- `POST /stop_record` - Stop recording (all or specific grid)
- `GET /status` - Get current recording status
- `GET /health` - Health check endpoint

### Example API Usage

```bash
# Start recording
curl -X POST http://localhost:5000/start_record \
  -H "Content-Type: application/json" \
  -d '{"grid_name": "A1", "counter": 1}'

# Stop recording
curl -X POST http://localhost:5000/stop_record \
  -H "Content-Type: application/json" \
  -d '{"grid_name": "A1"}'

# Get status
curl http://localhost:5000/status
```

---

## 🛠️ Development

### Project Structure

- `windows_launcher.py` - Main system launcher
- `rtsp_record_api_windows.py` - Recording API server
- `configure_cameras_windows.py` - Camera configuration utility
- `system_monitor_windows.py` - System monitoring service
- `ftpserver_windows.py` - FTP server
- `delete_except_newest_windows.py` - File cleanup utility

### Building from Source

1. **Clone Repository**
   ```cmd
   git clone [repository-url]
   cd raspi-scouting-package
   ```

2. **Install Development Dependencies**
   ```cmd
   pip install -r requirements_windows.txt
   ```

3. **Run Tests**
   ```cmd
   python -m pytest tests/
   ```

---

## 📞 Support

### Getting Help

1. **Check Log Files** - Most issues are logged with details
2. **Review Configuration** - Ensure `config.txt` is properly set
3. **Test Components** - Run individual scripts to isolate issues
4. **Check Dependencies** - Verify FFmpeg, VLC, and Python versions

### System Requirements

- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space minimum
- **Network**: Ethernet or WiFi for remote access

---

## 📄 License

This project is licensed under the same terms as the original Raspberry Pi Scouting Package.

---

## 🤝 Contributing

Contributions are welcome! Please ensure all changes maintain Windows compatibility and include appropriate error handling.

---

*Last updated: December 2024*

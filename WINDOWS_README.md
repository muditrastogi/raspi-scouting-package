# Windows Scouting Package

A Windows-compatible version of the Raspberry Pi scouting package for capturing video or image frames from USB cameras via RTSP. This version replaces VLC with OpenCV and v4l2rtspserver with native Windows/OpenCV RTSP streaming.

> ✅ This project is designed for robotics, surveillance, or remote monitoring on Windows systems where quick setup, local streaming, and flexible capture modes are essential.

---

## 📦 Features

- 🎥 Live RTSP stream preview using OpenCV (no VLC dependency)
- 🧪 Two operational modes:
  - **Frame Mode** – saves images frame by frame
  - **Video Mode** – continuous video recording
- 🧠 Simple Tkinter-based GUI with Start/Stop controls
- 🚀 Fast setup via one-click installer
- 🔌 Auto-detection of USB cameras using OpenCV
- 🔧 Lightweight Flask API to trigger recording
- 📈 Background system monitoring (optional)
- 📤 FTP server included (for remote file access)

---

## 🗂️ Installation Structure (Post Install)

```
%USERPROFILE%\Desktop\
├── scout-config\                    # Configuration files
│   └── config.txt                   # Camera and recording settings
│
├── scout-videos\                    # Recording output directory
│   └── recordings_YYYY-MM-DD\       # Daily recording folders
│
└── Windows Scouting Package.lnk     # Desktop shortcut
```

---

## 🚀 Installation

### Minimum Requirements
- Windows 10/11
- Python 3.7+
- FFmpeg (for RTSP streaming)
- USB cameras (webcams or industrial cameras)

### 🧠 One-Click Setup (Recommended)

1. **Install Python** (if not already installed):
   - Download from [python.org](https://python.org)
   - Make sure to check "Add Python to PATH"

2. **Install FFmpeg**:
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Extract to `C:\ffmpeg` (or any folder)
   - Add `C:\ffmpeg\bin` to your system PATH

3. **Run the installer**:
   ```batch
   windows_install.bat
   ```

The installer will:
- ✅ Check system requirements
- ✅ Install Python packages
- ✅ Create necessary directories
- ✅ Set up desktop shortcuts
- ✅ Test camera detection

---

## 🖥️ Usage

### 📽️ Launch the Application

**Option 1: Desktop Shortcut**
- Double-click "Windows Scouting Package" on your desktop

**Option 2: Command Line**
```batch
windows_scout_launcher.bat
```

### 🎮 GUI Controls

- **Start All Streams**: Begins RTSP preview for all cameras using OpenCV
- **Stop All Streams**: Ends all video streams
- **Start Recording All**: Calls the internal Flask API → triggers OpenCV/FFmpeg → saves video or frames
- **Stop Recording All**: Ends recording
- **Navigation**: Use Back/Forward buttons or Toggle A/B for grid navigation
- **Individual Camera Control**: Click "Start" on third camera for individual control

---

## 🔧 Configuration

### Config File Location
```
%USERPROFILE%\Desktop\scout-config\config.txt
```

### Configuration Options

```ini
# Camera resolution (width x height)
resolution=1920x1080

# Camera FPS
fps=30

# Camera serial IDs for ordering (leave empty to auto-detect)
bottomcamera=
middlecamera=
topcamera=
```

### Finding Camera Serial IDs

1. Open Device Manager
2. Expand "Cameras" or "Imaging devices"
3. Right-click camera → Properties → Details tab
4. Select "Device instance path" from Property dropdown
5. The serial number is usually at the end of the path

---

## 🔧 System Architecture

### Components

1. **Camera Detection** (`windows_camera_detection.py`)
   - Uses OpenCV to enumerate cameras
   - Tests camera accessibility
   - Provides camera information (resolution, FPS)

2. **RTSP Streaming** (`windows_camera_detection.py`)
   - OpenCV camera capture
   - FFmpeg RTSP server
   - Multi-threaded streaming

3. **GUI Application** (`windows_ui.py`)
   - Tkinter interface
   - OpenCV video display
   - Stream and recording controls

4. **Recording API** (`windows_record_api.py`)
   - Flask web API
   - OpenCV-based recording
   - Supports both frame and video modes

5. **Launcher Script** (`windows_scout_launcher.bat`)
   - Coordinates all components
   - Manages process lifecycle
   - Handles Windows-specific setup

### Data Flow

```
Camera → OpenCV Capture → FFmpeg RTSP Server → OpenCV Display (GUI)
                                      ↓
Recording API ← Flask API ← GUI Controls
                                      ↓
OpenCV Recording → File System (Frames/Video)
```

---

## 🧪 Recording Modes

### Frame Mode (Default)
- Captures individual JPEG images
- One frame every 0.7 seconds
- Files named with timestamp
- Useful for detailed analysis

### Video Mode
- Continuous MP4 video recording
- Configurable FPS and resolution
- Single video file per recording session
- Useful for continuous monitoring

To switch modes, modify the launcher script or API parameters.

---

## 🔧 Troubleshooting

### Common Issues

**"No cameras detected"**
- Check camera connections
- Try different USB ports
- Test cameras in other applications
- Run: `python windows_camera_detection.py --detect-only`

**"Failed to start RTSP stream"**
- Check FFmpeg installation and PATH
- Verify camera permissions
- Try different resolution/FPS settings

**"Recording not working"**
- Check write permissions to Desktop
- Verify Flask API is running
- Check available disk space

**"GUI not displaying video"**
- Install missing dependencies: `pip install pillow`
- Check Tkinter installation
- Try different camera resolutions

### Debug Mode

Run components individually for debugging:

```batch
# Test camera detection only
python windows_camera_detection.py --detect-only

# Test RTSP streaming for camera 0
python windows_camera_detection.py --start-stream 0

# Test recording API
python windows_record_api.py --port 5000 --rtsp-url rtsp://localhost:8554/stream
```

---

## 🔄 Updating

1. Download the latest version
2. Run `windows_install.bat` again
3. Restart the application

The installer will update Python packages and recreate necessary files.

---

## 📋 System Requirements Details

### Hardware
- Windows 10/11 (64-bit)
- USB cameras (DirectShow compatible)
- 4GB RAM minimum, 8GB recommended
- 10GB free disk space for recordings

### Software
- Python 3.7+ with pip
- FFmpeg 4.0+
- OpenCV-compatible camera drivers

### Network
- Local network access (for RTSP streaming)
- Optional: Internet access (for package installation)

---

## 🎯 Performance Tips

1. **Resolution**: Lower resolution = better performance
   - Try 1280x720 for better FPS
   - Use 640x480 for maximum performance

2. **FPS**: Match camera capabilities
   - 30 FPS is usually optimal
   - Higher FPS increases CPU usage

3. **Multiple Cameras**: Limit to 3 cameras maximum
   - Each camera uses significant CPU
   - Test with fewer cameras first

4. **Recording**: Choose appropriate mode
   - Frame mode: Better for analysis, higher storage
   - Video mode: Better for streaming, lower storage

---

## 📞 Support

For issues or questions:

1. Check the console output for error messages
2. Test components individually (see Troubleshooting)
3. Verify all requirements are met
4. Check camera compatibility with OpenCV

---

## 🔧 Troubleshooting

### Quick Diagnosis

If you're experiencing issues, run these diagnostic commands:

```batch
# 1. Test camera detection
python windows_camera_detection.py --detect-only

# 2. Test RTSP streaming
python windows_camera_detection.py --start-stream 0

# 3. Test RTSP connection
python windows_camera_detection.py --test-connection rtsp://localhost:8554/live
```

### Common Issues

| Problem | Solution |
|---------|----------|
| No video feed in GUI | Check FFmpeg installation and RTSP streaming |
| Multiple terminal windows | Launcher should hide them automatically |
| Recording not working | Test API endpoints with curl |
| Laggy video | Reduce resolution/FPS or check system resources |
| Camera not detected | Update camera drivers or try different index |

### Debug Mode

For detailed troubleshooting, see: `WINDOWS_TROUBLESHOOTING.md`

---

## 🔄 Migration from Raspberry Pi Version

### Key Differences

| Feature | Raspberry Pi | Windows |
|---------|--------------|---------|
| Camera Detection | `/dev/video*` + udev | OpenCV enumeration |
| RTSP Server | v4l2rtspserver | FFmpeg + OpenCV |
| Video Display | VLC | OpenCV + Tkinter |
| Recording | FFmpeg | OpenCV + FFmpeg |
| Process Management | systemd | Windows batch |
| Dependencies | Linux-specific | Cross-platform |

### Configuration Migration

1. Copy `config.txt` settings to Windows version
2. Update camera serial IDs (different format)
3. Adjust paths for Windows (use `%USERPROFILE%`)
4. Test with single camera first

The GUI and workflow remain largely identical, making migration straightforward.

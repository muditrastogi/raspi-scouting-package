# Raspberry Pi Scouting Package - Windows Edition

Windows-compatible version of the Raspberry Pi Scouting Package with USB camera support and automated setup.

## 🎯 What This Is

A Windows application for multi-camera recording and streaming, specifically designed for scouting applications. Features:

- **3-camera simultaneous recording** (bottom, middle, top)
- **USB camera support only** (no system webcams for safety)
- **Grid-based navigation** (A-1-A, A-1-B, etc.)
- **Automatic camera ordering** based on device IDs
- **Click-to-run interface** with batch files and shortcuts

## 🚀 Quick Start

### Method 1: Complete Automated Setup
1. **Clone and checkout:**
   ```cmd
   git clone https://github.com/your-repo/raspi-scouting-package.git
   cd raspi-scouting-package
   git checkout win-scripts
   ```

2. **Run complete setup:**
   ```cmd
   Setup_Project.bat
   ```

3. **Start application:**
   ```cmd
   Start_Camera_UI.bat
   ```

### Method 2: Step-by-Step Setup
1. **Install dependencies:** `pip install -r windows_requirements.txt`
2. **Test cameras:** Double-click `Test_Camera_Detection.bat`
3. **Configure cameras:** Double-click `Configure_Cameras.bat`
4. **Create shortcuts:** Run `Create_Desktop_Shortcuts.ps1`
5. **Launch app:** Double-click `Start_Camera_UI.bat`

## 📁 Key Files

| File | Purpose |
|------|---------|
| `Start_Camera_UI.bat` | 🎬 Main application launcher |
| `Configure_Cameras.bat` | ⚙️ Camera position setup |
| `Test_Camera_Detection.bat` | 🔍 Troubleshooting tool |
| `Setup_Project.bat` | 🛠️ Complete automated setup |
| `simple_windows_ui.py` | 💻 Main Python application |
| `config.txt` | 📄 Camera configuration file |

## 🎥 Camera Requirements

- **USB cameras only** (integrated webcams ignored)
- **3 cameras recommended** for full functionality
- **Identical models preferred** for consistency
- **USB 3.0 ports recommended** for performance

## 📋 Supported Camera Models

Tested with:
- Logitech USB cameras (C920, C922, etc.)
- Generic USB Video Class (UVC) cameras
- Most standard USB webcams

**Note:** Integrated laptop cameras and system webcams are intentionally ignored for security and consistency.

## 🔧 Configuration

### Camera Device IDs
The system uses Windows device IDs to identify cameras:
```
USB\VID_046D&PID_0825\42359210  # Example Logitech camera
```

### Configuration File (config.txt)
```ini
resolution=1920x1080
fps=15
# Windows camera device IDs
bottomcamera_deviceid=USB\VID_046D&PID_0825\42359210
middlecamera_deviceid=USB\VID_046D&PID_0825\42359210  
topcamera_deviceid=USB\VID_046D&PID_0825\42359210
```

## 🎮 Usage

1. **Launch:** Double-click `Start_Camera_UI.bat`
2. **Start cameras:** Click "Start All Streams"
3. **Begin recording:** Click "Start Recording All"
4. **Navigate:** Use Forward/Back buttons for grids
5. **Switch modes:** Use "Toggle A/B" button
6. **Individual control:** Use "Start/Stop" on third camera

### Camera Layout
- **Left:** Bottom camera (first)
- **Center:** Middle camera (second)  
- **Right:** Top camera (third)

### Recording Output
Videos saved to: `C:\Users\{username}\Desktop\scout-videos\`
Format: `ABC_GRID_{grid}_{counter}_recording_{timestamp}_{position}.avi`

## 🛠️ Troubleshooting

### Common Issues

**"No cameras found"**
- Run `Test_Camera_Detection.bat`
- Check USB connections
- Update camera drivers

**"Python not found"**
- Install Python 3.7+ with "Add to PATH" 
- Restart Command Prompt

**"Permission denied"**
- Close other camera applications
- Run as Administrator
- Check antivirus settings

**"Camera order wrong"**
- Run `Configure_Cameras.bat`
- Check `config.txt` device IDs

### Advanced Troubleshooting
- See `PROJECT_SETUP_GUIDE.md` for detailed troubleshooting
- Run `test_windows_camera_detection.py` for diagnostic info
- Check Windows Device Manager for camera status

## 📚 Documentation

- **`PROJECT_SETUP_GUIDE.md`** - Complete setup instructions
- **`WINDOWS_CAMERA_CONFIG.md`** - Camera configuration details  
- **`QUICK_START.md`** - Quick reference guide

## 🔄 Compatibility

### Original vs Windows Version
- **Original:** Raspberry Pi + Linux + v4l2rtspserver
- **Windows:** Windows + OpenCV + DirectShow/MSMF
- **Config:** Compatible config.txt format
- **Features:** Same UI and recording functionality

### Requirements
- **OS:** Windows 10/11 (64-bit recommended)
- **Python:** 3.7 or higher
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 10GB+ for video recordings
- **Cameras:** USB Video Class (UVC) compatible

## 🆘 Support

### Documentation
- Full setup guide in `PROJECT_SETUP_GUIDE.md`
- Camera troubleshooting in `WINDOWS_CAMERA_CONFIG.md`
- Quick reference in `QUICK_START.md`

### Getting Help
1. Check troubleshooting sections in documentation
2. Run `Test_Camera_Detection.bat` for diagnostics
3. Create GitHub issue with diagnostic output
4. Include `config.txt` and error messages

## 🔐 Security & Safety

- **USB cameras only:** System webcams ignored
- **Explicit configuration:** Only uses configured cameras
- **No network access:** Offline operation
- **Local storage:** Videos saved locally only

## 🎯 Development

### Project Structure
```
raspi-scouting-package/
├── 🎬 UI Launchers (*.bat)
├── 🔧 Configuration Tools
├── 🐍 Python Scripts
├── 📄 Documentation
└── ⚙️ Config Files
```

### Key Technologies
- **OpenCV:** Camera access and video processing
- **Tkinter:** User interface
- **Windows WMI:** Device detection
- **DirectShow/MSMF:** Camera backends

## 📜 License

Same license as the original Raspberry Pi Scouting Package.

---

**Ready to start?** Run `Setup_Project.bat` and follow the prompts!

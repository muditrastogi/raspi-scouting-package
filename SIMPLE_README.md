# Simple Windows Scouting Package

A **completely simplified** Windows camera viewing and recording application that removes all RTSP and FFmpeg complexity. Uses only OpenCV for direct camera access and recording.

## 🚀 Quick Start

1. **Install dependencies:**
   ```batch
   pip install opencv-python Pillow
   ```

2. **Run the application:**
   ```batch
   simple_launcher.bat
   ```

That's it! No complex setup, no RTSP servers, no FFmpeg configuration.

## 📋 What This Does

- ✅ **Direct camera streaming** to GUI (no RTSP protocol)
- ✅ **Simple AVI recording** using OpenCV VideoWriter
- ✅ **Multi-camera support** (automatically detects available cameras)
- ✅ **Real-time video display** in Tkinter windows
- ✅ **Grid-based navigation** (same as original UI)
- ✅ **Individual camera controls**

## 🗂️ Files Created

- **`simple_windows_ui.py`** - Main application with direct OpenCV streaming
- **`simple_launcher.bat`** - Simple launcher script
- **`windows_requirements.txt`** - Minimal dependencies (OpenCV + Pillow only)

## 🎯 Key Simplifications

| Feature | Before (Complex) | Now (Simple) |
|---------|------------------|--------------|
| **Protocol** | RTSP over network | Direct camera access |
| **Streaming** | FFmpeg RTSP server | OpenCV VideoCapture |
| **Recording** | Flask API + FFmpeg | Direct OpenCV VideoWriter |
| **Dependencies** | 20+ packages | 2 packages |
| **Setup** | Multiple services | Single Python script |
| **Debugging** | Complex network issues | Simple camera access |

## 📁 File Structure

```
C:\Users\[username]\Desktop\
├── scout-videos\
│   └── recordings_YYYY-MM-DD\
│       └── [grid]-[camera]\
│           └── ABC_GRID_[grid]_[timestamp]_[camera].avi
```

## 🎮 Usage

1. **Start Application:**
   ```batch
   simple_launcher.bat
   ```

2. **Camera Controls:**
   - **Start All Streams** - Start all detected cameras
   - **Individual buttons** - Control each camera separately
   - **Grid Navigation** - Use A/B and Forward/Back buttons

3. **Recording:**
   - **Start Recording All** - Records all active cameras to AVI files
   - **Grid-based naming** - Files named by current grid position

## 🔧 Requirements

- **Python 3.7+** (with tkinter)
- **OpenCV** (`pip install opencv-python`)
- **Pillow** (`pip install Pillow`)
- **Windows camera** (webcam or USB camera)

## 🚫 Removed Complexity

- ❌ **No RTSP protocol**
- ❌ **No FFmpeg dependency**
- ❌ **No Flask web server**
- ❌ **No network configuration**
- ❌ **No complex device enumeration**
- ❌ **No multiple background processes**

## 💡 Benefits

- **Reliable**: Direct camera access, no network issues
- **Simple**: One Python script, minimal dependencies
- **Fast**: No encoding/decoding overhead
- **Compatible**: Works with any DirectShow camera
- **Easy**: No complex setup or configuration

## 🐛 Troubleshooting

### Camera Access Issues

If you see "Failed to open camera" or NVIDIA-related warnings:

**Run diagnostics:**
```batch
# Complete diagnostic
full_diagnostic.bat

# Individual tests
python camera_troubleshoot.py
python test_simple_camera.py
```

**Common Issues:**

1. **NVIDIA Driver Conflicts:**
   - NVIDIA graphics drivers can block camera access
   - Update NVIDIA drivers or use integrated graphics
   - Restart computer after driver updates

2. **DirectShow Backend Issues:**
   - App tries multiple backends automatically
   - DirectShow, Media Foundation, Video for Windows
   - Some cameras only work with specific backends

3. **USB/Port Issues:**
   - Try different USB ports
   - Use USB 2.0 ports if 3.0 causes problems
   - Check USB power management settings

4. **Driver Problems:**
   - Update camera drivers from manufacturer website
   - Check Device Manager for camera status
   - Look for error codes (Code 10, etc.)

### Application Issues

**Application won't start:**
- Install OpenCV: `pip install opencv-python`
- Install Pillow: `pip install Pillow`
- Verify tkinter is available (usually included with Python)

**No video feed:**
- Run diagnostics first to verify camera access
- Test camera in Windows Camera app
- Try different resolution/FPS settings

**Recording fails:**
- Check write permissions to Desktop folder
- Ensure camera is streaming before recording
- Verify available disk space
- Check that output directory can be created

## 🔄 From Complex to Simple

This simplified version maintains the same UI and workflow as the original Raspberry Pi version, but removes all the complex networking and server components. It's perfect for:

- **Quick testing** and development
- **Simple camera monitoring** tasks
- **Educational purposes**
- **Basic recording** needs
- **Reliable operation** on various Windows systems

The complex RTSP/FFmpeg version is still available in the other files if you need advanced features like remote streaming or multiple simultaneous recordings.

# Windows Scouting Package Troubleshooting Guide

## RTSP Streaming Issues

### Problem: "Streams are starting in terminal but no feed in UI"

#### Solution 1: Test RTSP Streaming
```batch
# Test camera detection
python windows_camera_detection.py --detect-only

# Test RTSP streaming for camera 0
python windows_camera_detection.py --start-stream 0

# Test RTSP connection
python windows_camera_detection.py --test-connection rtsp://localhost:8554/live
```

#### Solution 2: Check FFmpeg Installation
```batch
# Verify FFmpeg is installed and in PATH
ffmpeg -version

# If not found, add FFmpeg to PATH or reinstall
# Download from: https://ffmpeg.org/download.html
```

#### Solution 3: Test with Simple RTSP Command
```batch
# Test basic FFmpeg RTSP streaming
ffmpeg -f dshow -i video=0 -f rtsp -rtsp_transport tcp rtsp://localhost:8554/test

# Test connection in another terminal
python windows_camera_detection.py --test-connection rtsp://localhost:8554/test
```

## Camera Detection Issues

### Problem: "No cameras detected"

#### Solution 1: Check Camera Permissions
1. Open Device Manager
2. Expand "Cameras" or "Imaging devices"
3. Right-click camera → Properties
4. Check if camera is enabled and working

#### Solution 2: Test DirectShow Access
```batch
# List available DirectShow devices
ffmpeg -f dshow -list_devices true -i dummy
```

#### Solution 3: Test with Different Camera Index
```batch
# Test different camera indices
python -c "import cv2; [print(f'Camera {i}:', cv2.VideoCapture(i, cv2.CAP_DSHOW).isOpened()) for i in range(5)]"
```

## GUI Issues

### Problem: "GUI shows black screen or no video"

#### Solution 1: Check OpenCV Installation
```batch
# Verify OpenCV can display video
python -c "import cv2; cap = cv2.VideoCapture(0, cv2.CAP_DSHOW); print('Camera opened:', cap.isOpened()); cap.release()"
```

#### Solution 2: Test RTSP Connection in GUI
```python
# Test RTSP connection manually
import cv2
cap = cv2.VideoCapture('rtsp://localhost:8554/live', cv2.CAP_FFMPEG)
if cap.isOpened():
    ret, frame = cap.read()
    print("RTSP connection successful:", ret)
else:
    print("RTSP connection failed")
cap.release()
```

## Process Issues

### Problem: "Multiple terminal windows still appear"

#### Solution: Check Launcher Script
The launcher uses `start /B` to run processes in background:
```batch
# Check if processes are running
tasklist | findstr python

# Kill background processes
taskkill /f /im python.exe
```

#### Alternative: Use Windows Task Scheduler
Create a scheduled task to run the services without visible windows.

## Recording Issues

### Problem: "Recording API not responding"

#### Solution 1: Test API Endpoints
```batch
# Test record API
curl http://localhost:5000/status

# Test recording start
curl "http://localhost:5000/record/start?counter=test&grid_name=A1"
```

#### Solution 2: Check Flask Logs
The API should show debug information in the terminal where it was started.

## Performance Issues

### Problem: "Video streaming is laggy or choppy"

#### Solution 1: Reduce Resolution/FPS
```batch
# Use lower settings
python windows_camera_detection.py --start-stream 0 --width 1280 --height 720 --fps 15
```

#### Solution 2: Adjust FFmpeg Parameters
Modify the FFmpeg command in `windows_camera_detection.py`:
- Reduce bitrate: `-b:v 1000k`
- Change preset: `-preset veryfast`
- Adjust GOP size: `-g 15`

## Common Error Messages

### "dshow: Could not enumerate video devices"
- Camera drivers not installed or incompatible
- Try updating camera drivers
- Test with different camera software

### "rtsp: Connection refused"
- RTSP server not started
- Wrong port number
- Firewall blocking connection
- FFmpeg DirectShow driver issues

### FFmpeg RTSP Issues

#### Problem: "Failed to start RTSP with H264 codec"
**Solution**: This is expected with OpenCV's VideoWriter. The system now uses FFmpeg directly.

#### Problem: FFmpeg DirectShow not working / "Video devices found: 0"
**Root Causes**:
1. FFmpeg build lacks DirectShow support
2. Camera drivers not compatible with DirectShow
3. Windows permissions issues
4. Camera using different capture API

**Solutions**:
1. **List all available devices (comprehensive)**:
   ```batch
   python list_ffmpeg_devices.py
   ```
   This tries multiple methods: DirectShow, VFW, AVFoundation

2. **Check FFmpeg capabilities**:
   ```batch
   ffmpeg -version | findstr dshow
   ```

3. **Test OpenCV fallback**:
   ```batch
   python opencv_rtsp_server.py --camera 0
   ```

4. **Update camera drivers** from manufacturer's website

#### Problem: "Could not find video device with name [0]"
**Solution**: FFmpeg expects device names, not indices. Use:
```batch
python list_ffmpeg_devices.py
```
Then use the correct device name instead of just the number.

#### Problem: RTSP server has fallback mechanism
**Good News**: The system now automatically tries:
1. FFmpeg DirectShow (fastest)
2. OpenCV VideoWriter fallback (more compatible)

If FFmpeg fails, it will automatically try the OpenCV method.

#### Problem: RTSP server starts but no stream
**Debug steps**:
1. Check if FFmpeg process is running:
   ```batch
   tasklist | findstr ffmpeg
   ```

2. Test RTSP manually:
   ```batch
   ffmpeg -i rtsp://localhost:8554/live -t 3 -f null -
   ```

3. Check FFmpeg logs (if available)

#### Problem: Camera opens but RTSP fails
**Check camera compatibility**:
- Some cameras may not work with DirectShow
- Try different camera resolutions/FPS
- Test with built-in webcam vs USB cameras

### "Failed to open RTSP stream"
- FFmpeg not in PATH
- Incorrect RTSP URL format
- Stream not yet available (wait a few seconds)

## Debug Mode

### Enable Detailed Logging
```python
# Add to any Python script for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or run with debug flag
python -c "import cv2; cv2.setLogLevel(0)"  # Enable OpenCV debug
```

### Check System Resources
```batch
# Monitor CPU/Memory usage
taskmgr

# Check port usage
netstat -ano | findstr :8554
```

## Quick Test Commands

```batch
# 1. Test camera access
python -c "import cv2; print(cv2.VideoCapture(0, cv2.CAP_DSHOW).isOpened())"

# 2. Test FFmpeg DirectShow
ffmpeg -f dshow -list_devices true -i dummy

# 3. Test FFmpeg camera capture
ffmpeg -f dshow -i video=0 -t 5 -f null -

# 4. Test RTSP server manually
python simple_rtsp_server.py --camera 0

# 5. Test RTSP connection (in another terminal)
ffmpeg -i rtsp://localhost:8554/live -t 3 -f null -

# 6. Run diagnostic
python quick_diagnostic.py

# 7. Test full system
windows_scout_launcher.bat
```

## Advanced Debugging

### FFmpeg Debug Output
```batch
# Enable FFmpeg debug logging
ffmpeg -f dshow -i video=0 -f rtsp -rtsp_transport tcp -v debug rtsp://localhost:8554/debug
```

### OpenCV Debug Information
```python
import cv2
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print("Backend:", cap.getBackendName())
print("Properties:", cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap.release()
```

If issues persist, check:
1. Windows version and updates
2. Camera drivers and firmware
3. Antivirus/firewall settings
4. Available system resources

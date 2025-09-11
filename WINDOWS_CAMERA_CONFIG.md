# Windows Camera Configuration Guide

This guide explains how to configure camera positions (bottom, middle, top) for the Windows version of the Raspberry Pi Scouting Package using Windows device IDs.

## Overview

The Windows camera configuration system uses the `wmic` command to get unique device IDs for each camera, which are then mapped to specific positions (bottom, middle, top) in the `config.txt` file.

### Key Command

The core command used to get camera device IDs is:
```cmd
wmic path Win32_PnPEntity where "Description like '%Camera%'" get DeviceID
```

This command queries Windows Management Interface (WMI) to get all camera devices and their unique device identifiers.

## Quick Start

### Method 1: Using the Batch Script (Easiest)
1. Double-click `windows_configure_cameras.bat`
2. Follow the interactive menu to configure each camera position
3. Run `simple_windows_ui.py` to use your configured cameras

### Method 2: Using Python Script Directly
1. Open Command Prompt or PowerShell
2. Navigate to the project directory
3. Run: `python windows_configure_cameras.py`
4. Follow the interactive menu

### Method 3: Test Detection First
1. Run: `python test_windows_camera_detection.py`
2. This will show you what cameras are detected and verify the wmic command works
3. Then proceed with configuration

## How It Works

### 1. Device ID Detection
The system uses the Windows `wmic` command to detect all camera devices:

```cmd
wmic path Win32_PnPEntity where "Description like '%Camera%'" get DeviceID
```

This returns device IDs like:
```
USB\VID_046D&PID_085B&MI_00\7&1A2B3C4D&0&0000
USB\VID_0BDA&PID_58B0&MI_00\6&2E3F4A5B&0&0000
USB\VID_1BCF&PID_2C99\5&6C7D8E9F&0&0000
```

### 2. Camera Mapping
Each detected camera gets assigned an index (0, 1, 2, etc.) based on detection order.

### 3. Position Configuration
You assign specific device IDs to camera positions:
- `bottomcamera_deviceid` - Bottom camera device ID
- `middlecamera_deviceid` - Middle camera device ID  
- `topcamera_deviceid` - Top camera device ID

### 4. Automatic Ordering
When you run `simple_windows_ui.py`, it:
1. Reads the device IDs from `config.txt`
2. Maps them to current camera indices
3. Uses cameras in the configured bottom → middle → top order

## Configuration File Format

The `config.txt` file includes both Linux and Windows camera identifiers:

```ini
# General settings
resolution=1920x1080
fps=15

# Linux camera serials (for Raspberry Pi)
bottomcamera=2430AP0JP9R8
middlecamera=2430AP0JP398
topcamera=2431AP03VQV8

# Windows camera device IDs (for Windows systems)
bottomcamera_deviceid=USB\VID_046D&PID_085B&MI_00\7&1A2B3C4D&0&0000
middlecamera_deviceid=USB\VID_0BDA&PID_58B0&MI_00\6&2E3F4A5B&0&0000
topcamera_deviceid=USB\VID_1BCF&PID_2C99\5&6C7D8E9F&0&0000
```

## Interactive Configuration Process

### Step 1: Start Configuration Tool
Run the configuration script:
```cmd
windows_configure_cameras.bat
```

### Step 2: Configure Each Position
The tool will show you a menu:
```
Select camera position to configure:

  1) Configure Bottom Camera
  2) Configure Middle Camera  
  3) Configure Top Camera
  4) Show Current Configuration
  5) Test Camera Detection
  6) Reset Windows Device ID Configuration
  7) Exit
```

### Step 3: Select Cameras
For each position, you'll see detected cameras:
```
Found 3 camera device(s):

  1) USB Video Device
      Device ID: USB\VID_046D&PID_085B&MI_00\7&1A2B3C4D&0&0000

  2) HD Webcam
      Device ID: USB\VID_0BDA&PID_58B0&MI_00\6&2E3F4A5B&0&0000

  3) Integrated Camera
      Device ID: USB\VID_1BCF&PID_2C99\5&6C7D8E9F&0&0000

Select camera for bottom position (1-3, or 'c' to cancel):
```

### Step 4: Verify Configuration
Use option 4 to check your configuration:
```
=== Current Configuration ===

General Settings:
  resolution     : 1920x1080
  fps            : 15

Windows Camera Device IDs:
  bottomcamera_deviceid : USB\VID_046D&PID_085B&MI_00\7&1A2B3C4D&0&0000
  middlecamera_deviceid : USB\VID_0BDA&PID_58B0&MI_00\6&2E3F4A5B&0&0000
  topcamera_deviceid    : USB\VID_1BCF&PID_2C99\5&6C7D8E9F&0&0000
```

## Troubleshooting

### Camera Not Detected by wmic
If cameras aren't showing up in wmic:

1. **Check Device Manager**: 
   - Open Device Manager
   - Look under "Cameras" or "Imaging devices"
   - Ensure cameras are installed without errors

2. **Update Drivers**:
   - Right-click camera in Device Manager
   - Select "Update driver"

3. **Try Different USB Ports**: 
   - USB 3.0 ports often work better
   - Avoid USB hubs if possible

4. **Run as Administrator**:
   - Right-click Command Prompt
   - Select "Run as administrator"
   - Try the wmic command again

### Camera Opens in OpenCV but Not in wmic
This can happen with some cameras. The test script will help identify this:
```cmd
python test_windows_camera_detection.py
```

### Multiple Cameras with Same Name
If you have identical cameras, the device IDs will still be unique. Use the device ID to distinguish them.

### Camera Order Changes
If you unplug and reconnect cameras, their indices might change, but the device IDs remain the same. This is why using device IDs for configuration is more reliable.

## Manual Configuration

If you prefer to edit `config.txt` manually:

1. **Get Device IDs**: Run the wmic command:
   ```cmd
   wmic path Win32_PnPEntity where "Description like '%Camera%'" get DeviceID
   ```

2. **Identify Your Cameras**: You may need to unplug/reconnect cameras one at a time to identify which device ID corresponds to which physical camera.

3. **Edit config.txt**: Add the device IDs to the appropriate lines:
   ```ini
   bottomcamera_deviceid=YOUR_BOTTOM_CAMERA_DEVICE_ID
   middlecamera_deviceid=YOUR_MIDDLE_CAMERA_DEVICE_ID
   topcamera_deviceid=YOUR_TOP_CAMERA_DEVICE_ID
   ```

## Testing Your Configuration

After configuration, test it:

1. **Run the UI**: 
   ```cmd
   python simple_windows_ui.py
   ```

2. **Check Console Output**: Look for messages like:
   ```
   🔍 Attempting to map cameras based on config.txt...
   ✅ Bottom camera: Device ID USB\VID_046D... -> Camera 0
   ✅ Middle camera: Device ID USB\VID_0BDA... -> Camera 1
   ✅ Top camera: Device ID USB\VID_1BCF... -> Camera 2
   🎬 Final camera order: [0, 1, 2]
   ```

3. **Verify Camera Labels**: In the UI, check that:
   - Left panel shows "bottom (first)"
   - Middle panel shows "middle (second)"  
   - Right panel shows "top (third)"

## Fallback Behavior

If configuration fails, the system automatically falls back to:
1. Auto-detection using OpenCV
2. Default camera indices [0, 1, 2]

This ensures the application still works even without proper configuration.

## Integration with Existing Scripts

The Windows camera configuration is compatible with:
- `simple_windows_ui.py` - Main camera viewer
- `windows_record_api.py` - Recording functionality
- All existing scouting package features

The Linux configuration (`bottomcamera`, `middlecamera`, `topcamera`) remains unchanged for Raspberry Pi compatibility.

## Files Overview

| File | Purpose |
|------|---------|
| `windows_configure_cameras.py` | Main configuration script |
| `windows_configure_cameras.bat` | Batch wrapper for easy execution |
| `test_windows_camera_detection.py` | Test script to verify wmic functionality |
| `config.txt` | Configuration file with camera mappings |
| `simple_windows_ui.py` | Main UI (updated to read config) |

## Command Reference

### wmic Command
```cmd
wmic path Win32_PnPEntity where "Description like '%Camera%'" get DeviceID
```

### Get Camera Names Too
```cmd
wmic path Win32_PnPEntity where "Description like '%Camera%'" get Name,DeviceID
```

### Test Configuration
```cmd
python test_windows_camera_detection.py
```

### Run Configuration Tool
```cmd
python windows_configure_cameras.py
```

### Start Camera Viewer
```cmd
python simple_windows_ui.py
```

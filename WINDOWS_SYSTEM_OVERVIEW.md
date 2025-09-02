# Windows Raspberry Pi Scouting Package - System Overview

This document provides a comprehensive overview of the Windows-compatible version of the Raspberry Pi Scouting Package, explaining how it works, what components are included, and how they interact with each other.

## 🎯 System Purpose

The Windows Raspberry Pi Scouting Package is a complete video recording and streaming system designed for:
- **Robotics competitions** - Recording robot movements and strategies
- **Surveillance applications** - Monitoring areas with multiple camera angles
- **Remote monitoring** - Capturing video from multiple locations
- **Research and development** - Recording experiments and prototypes

## 🏗️ System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Windows System                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   USB Cameras   │  │  Windows GUI    │  │  File I/O   │ │
│  │   (DirectShow)  │  │   (Tkinter)     │  │  (Desktop)  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  RTSP Streams   │  │  Recording API  │  │  System     │ │
│  │   (FFmpeg)      │  │   (Flask)       │  │  Monitor    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  FTP Server     │  │  File Cleanup   │  │  Logging    │ │
│  │  (pyftpdlib)    │  │  (Python)       │  │  System     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Camera Input** → USB cameras provide video streams
2. **RTSP Processing** → FFmpeg converts camera streams to RTSP
3. **API Control** → Flask API manages recording operations
4. **File Storage** → Videos saved to Desktop/scout-videos
5. **Remote Access** → FTP server provides file access
6. **System Monitoring** → Background monitoring of system health

## 📁 File Structure

### Core Python Scripts

| File | Purpose | Dependencies |
|------|---------|--------------|
| `windows_launcher.py` | Main system launcher | OpenCV, Flask, FFmpeg |
| `rtsp_record_api_windows.py` | Recording API server | Flask, FFmpeg |
| `configure_cameras_windows.py` | Camera setup utility | OpenCV, PowerShell |
| `system_monitor_windows.py` | System monitoring | psutil, logging |
| `ftpserver_windows.py` | FTP server | pyftpdlib |
| `delete_except_newest_windows.py` | File cleanup | pathlib, glob |

### Configuration Files

| File | Purpose | Format |
|------|---------|--------|
| `config_windows.txt` | Windows configuration template | INI |
| `config.txt` | Active configuration (created during install) | INI |
| `requirements_windows.txt` | Python dependencies | pip format |

### Installation Scripts

| File | Purpose | Platform |
|------|---------|----------|
| `install_windows.bat` | Batch file installer | Windows CMD |
| `install_windows.ps1` | PowerShell installer | Windows PowerShell |

### Documentation

| File | Purpose | Audience |
|------|---------|----------|
| `README_Windows.md` | User guide and installation | End users |
| `WINDOWS_SYSTEM_OVERVIEW.md` | Technical overview | Developers |

## 🔧 Key Technologies

### Python Libraries

- **Flask** - Web API framework for recording control
- **OpenCV** - Computer vision and camera access
- **psutil** - System monitoring and process management
- **pyftpdlib** - FTP server implementation
- **pathlib** - Modern file path handling

### External Dependencies

- **FFmpeg** - Video processing and RTSP streaming
- **VLC** - Video streaming and playback
- **Python 3.8+** - Runtime environment

### Windows-Specific Features

- **DirectShow** - Camera detection and enumeration
- **PowerShell** - System information gathering
- **Windows Services** - Background process management
- **Desktop Integration** - Shortcuts and file organization

## 🚀 System Operation

### Startup Sequence

1. **Launcher Initialization**
   - Load configuration from `config.txt`
   - Detect available USB cameras
   - Create necessary directories

2. **Camera Detection**
   - Use PowerShell to enumerate DirectShow devices
   - Test camera accessibility with OpenCV
   - Map cameras to configured positions

3. **Service Startup**
   - Start RTSP streaming servers (FFmpeg)
   - Launch recording API server (Flask)
   - Initialize system monitoring

4. **GUI Launch**
   - Start Tkinter-based user interface
   - Display camera streams
   - Provide recording controls

### Recording Workflow

1. **User Initiates Recording**
   - Click "Start Record" in GUI
   - GUI sends HTTP request to API

2. **API Processing**
   - Flask API receives recording request
   - Validates parameters (grid name, counter)
   - Creates recording thread

3. **Video Capture**
   - FFmpeg process starts recording from RTSP stream
   - Video saved to daily folder with timestamp
   - Recording continues until stopped

4. **File Management**
   - Videos organized by date and grid location
   - Automatic cleanup of old files
   - FTP access for remote retrieval

## ⚙️ Configuration System

### Configuration Categories

#### Cameras
```ini
[cameras]
resolution=1920x1080    # Video resolution
fps=30                  # Frame rate
bottomcamera=           # Camera ID for bottom position
middlecamera=           # Camera ID for middle position
topcamera=              # Camera ID for top position
```

#### Recording
```ini
[recording]
crf=23                  # Video quality (18-28, lower=better)
format=mp4              # Output format
audio=false             # Audio recording enabled
```

#### Network
```ini
[network]
rtsp_base_port=8554     # Base port for RTSP streams
record_api_port=5000    # Recording API port
ftp_port=21             # FTP server port
ftp_username=pirecorder # FTP username
ftp_password=recorderpi # FTP password
```

#### Storage
```ini
[storage]
video_dir=scout-videos  # Video storage directory
log_dir=systemlogs      # Log storage directory
max_disk_usage=90       # Disk usage threshold
retention_days=30       # Days to keep old files
```

#### System
```ini
[system]
monitor_interval=30     # System monitoring interval
cpu_threshold=80        # CPU usage warning threshold
memory_threshold=80     # Memory usage warning threshold
auto_cleanup=true       # Enable automatic cleanup
cleanup_interval=24     # Cleanup interval in hours
```

## 🔍 Monitoring and Logging

### System Monitoring

- **CPU Usage** - Real-time CPU utilization tracking
- **Memory Usage** - RAM usage monitoring
- **Disk Usage** - Storage space monitoring
- **Network Activity** - Data transfer monitoring
- **Process Health** - Service status monitoring

### Logging System

- **Launcher Logs** - System startup and camera detection
- **API Logs** - Recording operations and errors
- **FTP Logs** - File transfer activities
- **System Logs** - Performance metrics and warnings
- **Cleanup Logs** - File management operations

### Alert System

- **Threshold Warnings** - CPU/Memory/Disk usage alerts
- **Error Logging** - Detailed error information
- **Performance Tracking** - Historical performance data
- **Health Checks** - Service availability monitoring

## 🛡️ Security Features

### Access Control

- **FTP Authentication** - Username/password protection
- **API Security** - Local network access only
- **File Permissions** - Windows file system security
- **Process Isolation** - Separate processes for services

### Data Protection

- **Local Storage** - Files stored on local machine
- **No Cloud Upload** - All data remains local
- **Secure Logging** - Sensitive data not logged
- **Access Logging** - All operations logged for audit

## 🔄 Maintenance and Updates

### Regular Maintenance

- **File Cleanup** - Automatic removal of old recordings
- **Log Rotation** - Management of log file sizes
- **Performance Monitoring** - System health tracking
- **Error Resolution** - Automated error detection and logging

### Update Process

1. **Backup Configuration** - Save current `config.txt`
2. **Download Updates** - Get latest Windows package
3. **Reinstall System** - Run installation script
4. **Restore Configuration** - Apply saved settings
5. **Test System** - Verify all components work

### Troubleshooting

- **Log Analysis** - Check log files for error details
- **Component Testing** - Test individual services
- **Dependency Verification** - Ensure all software is installed
- **Configuration Validation** - Verify settings are correct

## 📊 Performance Characteristics

### Resource Requirements

- **CPU** - 2+ cores recommended for multi-camera operation
- **Memory** - 4GB minimum, 8GB recommended
- **Storage** - 10GB+ free space for video storage
- **Network** - Ethernet recommended for stable streaming

### Scalability

- **Camera Support** - Up to 3 cameras (expandable)
- **Recording Quality** - Configurable from 720p to 4K
- **Storage Management** - Automatic cleanup and organization
- **Performance Tuning** - Adjustable monitoring thresholds

### Limitations

- **Windows Only** - No cross-platform support
- **USB Cameras** - Requires UVC-compatible devices
- **Local Storage** - No cloud integration
- **Single Machine** - No distributed recording support

## 🚀 Future Enhancements

### Planned Features

- **Cloud Integration** - AWS S3 upload support
- **Web Interface** - Browser-based control panel
- **Mobile App** - Smartphone control application
- **AI Analysis** - Automated video analysis
- **Multi-Machine** - Distributed recording support

### Extension Points

- **Plugin System** - Modular architecture for custom features
- **API Extensions** - Additional REST endpoints
- **Custom Formats** - Support for additional video formats
- **Integration APIs** - Third-party system integration

## 📚 Development Guidelines

### Code Standards

- **Python 3.8+** - Modern Python features and syntax
- **Type Hints** - Optional type annotations for clarity
- **Error Handling** - Comprehensive exception handling
- **Logging** - Structured logging throughout the system
- **Documentation** - Inline code documentation

### Testing Strategy

- **Unit Tests** - Individual component testing
- **Integration Tests** - Service interaction testing
- **System Tests** - End-to-end functionality testing
- **Performance Tests** - Resource usage validation

### Deployment

- **Installation Scripts** - Automated setup process
- **Configuration Management** - Flexible configuration system
- **Dependency Management** - Clear dependency requirements
- **Error Recovery** - Graceful error handling and recovery

---

This Windows-compatible system provides a robust, scalable solution for multi-camera video recording and streaming, with comprehensive monitoring, logging, and management capabilities. The modular architecture allows for easy maintenance and future enhancements while maintaining the core functionality of the original Raspberry Pi system.

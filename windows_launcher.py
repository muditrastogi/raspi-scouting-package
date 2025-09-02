#!/usr/bin/env python3
"""
Windows Launcher for Raspberry Pi Scouting Package
A Windows-compatible version of the desktopmultiv5.sh script
"""

import os
import sys
import subprocess
import time
import threading
import json
import configparser
from pathlib import Path
import psutil
import requests
from datetime import datetime

class WindowsScoutingLauncher:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.rtsp_base_port = 8554
        self.record_api_base_port = 5000
        self.rtsp_check_timeout = 5
        
        # Default configuration values
        self.default_resolution = "1920x1080"
        self.default_fps = 15
        self.default_bottom_camera = ""
        self.default_middle_camera = ""
        self.default_top_camera = ""
        
        # Configuration variables
        self.config_resolution = self.default_resolution
        self.config_fps = self.default_fps
        self.config_bottom_camera = self.default_bottom_camera
        self.config_middle_camera = self.default_middle_camera
        self.config_top_camera = self.default_top_camera
        
        # Arrays to track devices and services
        self.playable_devices = []
        self.device_serials = []
        self.rtsp_servers = []
        self.record_apis = []
        self.rtsp_processes = []
        self.record_api_processes = []
        
        # Working directories
        self.video_dir = Path.home() / "Desktop" / "scout-videos"
        self.system_logs_dir = Path.home() / "Desktop" / "systemlogs"
        
        # Create necessary directories
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.system_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.read_config()
        
    def log_message(self, message, level="INFO"):
        """Log messages with timestamp and level"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        # Also save to log file
        log_file = self.system_logs_dir / f"launcher_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def read_config(self):
        """Read configuration from config.txt"""
        config_file = self.script_dir / "config.txt"
        
        if config_file.exists():
            self.log_message(f"Reading configuration from {config_file}")
            
            config = configparser.ConfigParser()
            config.read(config_file)
            
            # Read camera configuration
            if 'cameras' in config:
                camera_config = config['cameras']
                self.config_resolution = camera_config.get('resolution', self.default_resolution)
                self.config_fps = int(camera_config.get('fps', self.default_fps))
                self.config_bottom_camera = camera_config.get('bottomcamera', self.default_bottom_camera)
                self.config_middle_camera = camera_config.get('middlecamera', self.default_middle_camera)
                self.config_top_camera = camera_config.get('topcamera', self.default_top_camera)
                
                self.log_message(f"Config: resolution={self.config_resolution}")
                self.log_message(f"Config: fps={self.config_fps}")
                self.log_message(f"Config: bottomcamera={self.config_bottom_camera}")
                self.log_message(f"Config: middlecamera={self.config_middle_camera}")
                self.log_message(f"Config: topcamera={self.config_top_camera}")
        else:
            self.log_message("No config.txt found, using default values", "WARNING")
    
    def detect_windows_cameras(self):
        """Detect available cameras on Windows using DirectShow"""
        self.log_message("Detecting available Windows cameras...")
        
        try:
            # Use PowerShell to enumerate DirectShow video devices
            ps_command = """
            Add-Type -AssemblyName System.Management
            $devices = Get-WmiObject -Class Win32_PnPEntity | Where-Object {$_.Name -like "*camera*" -or $_.Name -like "*webcam*" -or $_.Name -like "*USB Video*"}
            $devices | ForEach-Object {
                $device = $_
                $deviceInfo = @{
                    Name = $device.Name
                    DeviceID = $device.DeviceID
                    Status = $device.Status
                }
                [PSCustomObject]$deviceInfo
            } | ConvertTo-Json
            """
            
            result = subprocess.run([
                'powershell', '-Command', ps_command
            ], capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                devices = json.loads(result.stdout)
                if not isinstance(devices, list):
                    devices = [devices]
                
                for device in devices:
                    if device.get('Status') == 'OK':
                        device_name = device.get('Name', 'Unknown Camera')
                        device_id = device.get('DeviceID', 'Unknown')
                        
                        # Check if camera is accessible using OpenCV
                        if self.test_camera_access(device_name):
                            self.playable_devices.append(device_name)
                            self.device_serials.append(device_id)
                            self.log_message(f"Found playable camera: {device_name} (ID: {device_id})", "SUCCESS")
                
                if not self.playable_devices:
                    self.log_message("No accessible cameras found", "WARNING")
                    return False
                    
                return True
                
        except subprocess.CalledProcessError as e:
            self.log_message(f"Error detecting cameras: {e}", "ERROR")
            return False
        except json.JSONDecodeError as e:
            self.log_message(f"Error parsing camera data: {e}", "ERROR")
            return False
    
    def test_camera_access(self, camera_name):
        """Test if a camera can be accessed using OpenCV"""
        try:
            import cv2
            
            # Try to open camera by index (0, 1, 2, etc.)
            for i in range(5):  # Test first 5 camera indices
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    # Try to read a frame
                    ret, frame = cap.read()
                    cap.release()
                    if ret:
                        self.log_message(f"Camera {camera_name} accessible at index {i}")
                        return True
                        
        except ImportError:
            self.log_message("OpenCV not available, skipping camera test", "WARNING")
            return True  # Assume camera is accessible if OpenCV not available
        except Exception as e:
            self.log_message(f"Error testing camera {camera_name}: {e}", "WARNING")
            
        return False
    
    def start_rtsp_server(self, camera_index, port):
        """Start RTSP server for a camera using FFmpeg"""
        try:
            # Use FFmpeg to create RTSP stream
            rtsp_url = f"rtsp://localhost:{port}/camera{camera_index}"
            
            ffmpeg_cmd = [
                'ffmpeg',
                '-f', 'dshow',
                '-i', f'video=USB Camera {camera_index}',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-tune', 'zerolatency',
                '-f', 'rtsp',
                '-rtsp_transport', 'tcp',
                rtsp_url
            ]
            
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            self.rtsp_processes.append({
                'camera_index': camera_index,
                'port': port,
                'process': process,
                'url': rtsp_url
            })
            
            self.log_message(f"Started RTSP server for camera {camera_index} on port {port} (PID: {process.pid})", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_message(f"Error starting RTSP server for camera {camera_index}: {e}", "ERROR")
            return False
    
    def start_record_api(self, port):
        """Start the recording API server"""
        try:
            api_script = self.script_dir / "rtsp_record_api.py"
            if not api_script.exists():
                self.log_message(f"API script not found: {api_script}", "ERROR")
                return False
            
            # Start the API server
            process = subprocess.Popen([
                sys.executable, str(api_script), '--port', str(port)
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            
            self.record_api_processes.append({
                'port': port,
                'process': process
            })
            
            self.log_message(f"Started record API on port {port} (PID: {process.pid})", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_message(f"Error starting record API: {e}", "ERROR")
            return False
    
    def launch_ui(self):
        """Launch the Python UI application"""
        try:
            ui_script = self.script_dir / "UI-May17-v16.py"
            if not ui_script.exists():
                self.log_message(f"UI script not found: {ui_script}", "ERROR")
                return False
            
            self.log_message("Launching Python UI application...")
            
            # Launch UI in a new process
            subprocess.Popen([
                sys.executable, str(ui_script)
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            return True
            
        except Exception as e:
            self.log_message(f"Error launching UI: {e}", "ERROR")
            return False
    
    def cleanup(self):
        """Clean up all running processes"""
        self.log_message("Cleaning up processes...")
        
        # Stop RTSP servers
        for rtsp_info in self.rtsp_processes:
            try:
                if rtsp_info['process'].poll() is None:
                    rtsp_info['process'].terminate()
                    rtsp_info['process'].wait(timeout=5)
            except Exception as e:
                self.log_message(f"Error stopping RTSP server: {e}", "WARNING")
        
        # Stop record APIs
        for api_info in self.record_api_processes:
            try:
                if api_info['process'].poll() is None:
                    api_info['process'].terminate()
                    api_info['process'].wait(timeout=5)
            except Exception as e:
                self.log_message(f"Error stopping record API: {e}", "WARNING")
        
        self.log_message("Cleanup completed")
    
    def run(self):
        """Main execution method"""
        try:
            self.log_message("Starting Windows USB camera RTSP setup...")
            
            # Detect cameras
            if not self.detect_windows_cameras():
                self.log_message("No cameras detected, exiting", "ERROR")
                return False
            
            # Start RTSP servers for each camera
            for i, device in enumerate(self.playable_devices):
                port = self.rtsp_base_port + i
                if not self.start_rtsp_server(i, port):
                    self.log_message(f"Failed to start RTSP server for camera {i}", "ERROR")
                    continue
            
            # Start record API
            if not self.start_record_api(self.record_api_base_port):
                self.log_message("Failed to start record API", "ERROR")
                return False
            
            # Wait a moment for services to start
            time.sleep(2)
            
            # Launch UI
            if not self.launch_ui():
                self.log_message("Failed to launch UI", "ERROR")
                return False
            
            self.log_message("Setup completed successfully", "SUCCESS")
            
            # Keep the launcher running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.log_message("Received interrupt signal, shutting down...")
            
        except Exception as e:
            self.log_message(f"Unexpected error: {e}", "ERROR")
            return False
        finally:
            self.cleanup()
        
        return True

def main():
    """Main entry point"""
    launcher = WindowsScoutingLauncher()
    
    try:
        success = launcher.run()
        if success:
            print("Launcher completed successfully")
        else:
            print("Launcher failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nLauncher interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Launcher error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

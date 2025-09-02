#!/usr/bin/env python3
"""
Windows Camera Configuration Script
A Windows-compatible version of configure_cameras.sh for the Raspberry Pi Scouting Package
"""

import os
import sys
import subprocess
import json
import configparser
from pathlib import Path
import cv2
import time

class WindowsCameraConfigurator:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.config_file = self.script_dir / "config.txt"
        self.cameras = {}
        
        # Camera positions
        self.positions = ['bottomcamera', 'middlecamera', 'topcamera']
        
        # Load existing configuration
        self.load_config()
    
    def load_config(self):
        """Load existing configuration from config.txt"""
        if self.config_file.exists():
            config = configparser.ConfigParser()
            config.read(self.config_file)
            
            if 'cameras' in config:
                camera_config = config['cameras']
                for position in self.positions:
                    self.cameras[position] = camera_config.get(position, '')
        else:
            # Initialize with empty values
            for position in self.positions:
                self.cameras[position] = ''
    
    def save_config(self):
        """Save configuration to config.txt"""
        config = configparser.ConfigParser()
        config['cameras'] = {
            'resolution': '1920x1080',
            'fps': '30'
        }
        
        # Add camera configurations
        for position in self.positions:
            config['cameras'][position] = self.cameras[position]
        
        with open(self.config_file, 'w') as f:
            config.write(f)
        
        print(f"Configuration saved to {self.config_file}")
    
    def detect_windows_cameras(self):
        """Detect all available cameras on Windows"""
        print("Detecting available Windows cameras...")
        
        available_cameras = []
        
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
                        
                        # Test camera accessibility
                        if self.test_camera_access(device_name):
                            available_cameras.append({
                                'name': device_name,
                                'id': device_id,
                                'index': len(available_cameras)
                            })
                            print(f"✓ Found accessible camera: {device_name}")
                        else:
                            print(f"✗ Camera not accessible: {device_name}")
            
            return available_cameras
            
        except subprocess.CalledProcessError as e:
            print(f"Error detecting cameras: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing camera data: {e}")
            return []
    
    def test_camera_access(self, camera_name):
        """Test if a camera can be accessed using OpenCV"""
        try:
            # Try to open camera by index (0, 1, 2, etc.)
            for i in range(5):  # Test first 5 camera indices
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    # Try to read a frame
                    ret, frame = cap.read()
                    cap.release()
                    if ret:
                        return True
                        
        except ImportError:
            print("OpenCV not available, assuming camera is accessible")
            return True
        except Exception as e:
            print(f"Error testing camera {camera_name}: {e}")
            
        return False
    
    def get_camera_serial(self, camera_name):
        """Get camera serial/ID from Windows device manager"""
        try:
            # Use PowerShell to get device ID
            ps_command = f"""
            $device = Get-WmiObject -Class Win32_PnPEntity | Where-Object {{$_.Name -eq "{camera_name}"}}
            $device.DeviceID
            """
            
            result = subprocess.run([
                'powershell', '-Command', ps_command
            ], capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                return result.stdout.strip()
                
        except subprocess.CalledProcessError:
            pass
        
        return camera_name  # Fallback to camera name if device ID not found
    
    def configure_camera_position(self, position, available_cameras):
        """Configure a specific camera position"""
        print(f"\n=== Configuring {position.replace('camera', '').title()} Camera ===")
        
        if not available_cameras:
            print("No cameras available for configuration")
            return False
        
        # Show available cameras
        print("\nAvailable cameras:")
        for i, camera in enumerate(available_cameras):
            print(f"  {i+1}. {camera['name']}")
        
        # Get user selection
        while True:
            try:
                choice = input(f"\nSelect camera for {position.replace('camera', '').title()} position (1-{len(available_cameras)}) or 'skip': ").strip()
                
                if choice.lower() == 'skip':
                    print(f"Skipping {position}")
                    return True
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(available_cameras):
                    selected_camera = available_cameras[choice_num - 1]
                    
                    # Get camera serial/ID
                    camera_id = self.get_camera_serial(selected_camera['name'])
                    
                    # Update configuration
                    self.cameras[position] = camera_id
                    
                    print(f"✓ Configured {position} as: {selected_camera['name']} (ID: {camera_id})")
                    return True
                else:
                    print("Invalid selection. Please choose a valid number.")
                    
            except ValueError:
                print("Invalid input. Please enter a number or 'skip'.")
            except KeyboardInterrupt:
                print("\nConfiguration cancelled.")
                return False
        
        return False
    
    def show_current_config(self):
        """Display current camera configuration"""
        print("\n=== Current Camera Configuration ===")
        
        if self.config_file.exists():
            print(f"Configuration file: {self.config_file}")
        else:
            print("No configuration file found. Will create new one.")
        
        print("\nCamera assignments:")
        for position in self.positions:
            camera_name = self.cameras[position]
            if camera_name:
                print(f"  {position.replace('camera', '').title()}: {camera_name}")
            else:
                print(f"  {position.replace('camera', '').title()}: Not configured")
    
    def reset_configuration(self):
        """Reset all camera configurations"""
        print("\n=== Resetting Camera Configuration ===")
        
        for position in self.positions:
            self.cameras[position] = ''
        
        print("All camera configurations have been reset.")
    
    def test_camera_detection(self):
        """Test camera detection and ordering"""
        print("\n=== Testing Camera Detection ===")
        
        available_cameras = self.detect_windows_cameras()
        
        if not available_cameras:
            print("No cameras detected.")
            return
        
        print(f"\nDetected {len(available_cameras)} camera(s):")
        for camera in available_cameras:
            print(f"  - {camera['name']} (Index: {camera['index']})")
        
        # Test camera ordering based on configuration
        print("\nCamera ordering test:")
        ordered_cameras = []
        
        for position in self.positions:
            camera_id = self.cameras[position]
            if camera_id:
                # Find camera with matching ID
                for camera in available_cameras:
                    if camera['id'] == camera_id or camera['name'] == camera_id:
                        ordered_cameras.append({
                            'position': position,
                            'camera': camera,
                            'index': camera['index']
                        })
                        print(f"  {position.replace('camera', '').title()}: {camera['name']} (Index: {camera['index']})")
                        break
        
        if not ordered_cameras:
            print("  No cameras configured for automatic ordering.")
    
    def run_interactive_configuration(self):
        """Run the interactive camera configuration"""
        print("=== Windows Camera Configuration ===")
        print("This script will help you configure camera positions for automatic ordering.")
        print("Follow the prompts to assign cameras to bottom, middle, and top positions.")
        
        while True:
            print("\n=== Main Menu ===")
            print("1. Configure camera positions")
            print("2. Show current configuration")
            print("3. Test camera detection")
            print("4. Reset configuration")
            print("5. Save and exit")
            print("6. Exit without saving")
            
            try:
                choice = input("\nSelect an option (1-6): ").strip()
                
                if choice == '1':
                    # Configure camera positions
                    available_cameras = self.detect_windows_cameras()
                    
                    if not available_cameras:
                        print("No cameras detected. Please connect cameras and try again.")
                        continue
                    
                    for position in self.positions:
                        if not self.configure_camera_position(position, available_cameras):
                            print("Configuration cancelled.")
                            return False
                    
                    print("\n✓ All camera positions configured successfully!")
                    
                elif choice == '2':
                    self.show_current_config()
                    
                elif choice == '3':
                    self.test_camera_detection()
                    
                elif choice == '4':
                    self.reset_configuration()
                    
                elif choice == '5':
                    self.save_config()
                    print("\n✓ Configuration saved successfully!")
                    return True
                    
                elif choice == '6':
                    print("\nExiting without saving changes.")
                    return False
                    
                else:
                    print("Invalid option. Please choose 1-6.")
                    
            except KeyboardInterrupt:
                print("\n\nConfiguration interrupted.")
                return False
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        return False

def main():
    """Main entry point"""
    try:
        configurator = WindowsCameraConfigurator()
        
        # Check if OpenCV is available
        try:
            import cv2
            print("OpenCV detected - camera testing enabled")
        except ImportError:
            print("OpenCV not available - camera testing will be limited")
            print("Install OpenCV with: pip install opencv-python")
        
        success = configurator.run_interactive_configuration()
        
        if success:
            print("\nCamera configuration completed successfully!")
            print("You can now run the Windows launcher with your configured cameras.")
        else:
            print("\nCamera configuration was not completed.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during configuration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

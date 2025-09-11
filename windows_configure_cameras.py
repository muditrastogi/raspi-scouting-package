#!/usr/bin/env python3
"""
Windows Camera Configuration Script for Raspberry Pi Scouting Package
Uses wmic command to get camera device IDs and configure camera positions in config.txt
"""

import os
import sys
import subprocess
import time
import getpass
from datetime import datetime

# Color codes for console output
class Colors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    RESET = '\033[0m'
    
    @staticmethod
    def supports_color():
        """Check if console supports ANSI color codes"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

def print_colored(text, color=Colors.RESET):
    """Print colored text if console supports it"""
    if Colors.supports_color():
        print(f"{color}{text}{Colors.RESET}")
    else:
        print(text)

def print_info(text):
    print_colored(f"[INFO] {text}", Colors.BLUE)

def print_success(text):
    print_colored(f"[SUCCESS] {text}", Colors.GREEN)

def print_warning(text):
    print_colored(f"[WARNING] {text}", Colors.YELLOW)

def print_error(text):
    print_colored(f"[ERROR] {text}", Colors.RED)

def print_header(text):
    print_colored(text, Colors.CYAN)

class WindowsCameraConfig:
    """Windows Camera Configuration Manager"""
    
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.script_dir, "config.txt")
        
    def get_camera_devices(self):
        """Get USB camera device IDs using wmic command"""
        print_info("Scanning for USB camera devices using Windows Management Interface...")
        
        try:
            # Only get USB cameras to avoid system/integrated webcams
            cmd = ['wmic', 'path', 'Win32_PnPEntity', 'where', 'Description like "%Camera%" AND DeviceID like "USB%"', 'get', 'DeviceID']
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode != 0:
                print_error(f"wmic command failed: {result.stderr}")
                return []
            
            devices = []
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                # Skip header and empty lines
                if line and not line.startswith('DeviceID') and not line.startswith('---'):
                    # Clean up the device ID and ensure it's a USB device
                    device_id = line.strip()
                    if device_id and device_id.startswith('USB\\'):
                        devices.append(device_id)
                        print_success(f"Found USB camera device: {device_id}")
            
            if not devices:
                print_warning("No USB camera devices found!")
                print_info("Note: This tool only shows USB cameras, not integrated/system webcams")
            
            return devices
            
        except Exception as e:
            print_error(f"Error detecting cameras: {e}")
            return []
    
    def get_camera_friendly_names(self):
        """Get USB camera friendly names for better identification"""
        print_info("Getting USB camera friendly names...")
        
        try:
            # Only get USB cameras
            cmd = ['wmic', 'path', 'Win32_PnPEntity', 'where', 'Description like "%Camera%" AND DeviceID like "USB%"', 'get', 'Name,DeviceID']
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode != 0:
                return {}
            
            camera_names = {}
            lines = result.stdout.strip().split('\n')
            
            # Skip header line
            header_found = False
            for line in lines:
                line = line.strip()
                if not header_found:
                    if 'DeviceID' in line and 'Name' in line:
                        header_found = True
                    continue
                
                if line and not line.startswith('---'):
                    # Split by multiple spaces to separate DeviceID and Name
                    parts = line.split()
                    if len(parts) >= 2:
                        # DeviceID is typically the last part, Name is everything else
                        device_id = parts[-1] if parts[-1].startswith('USB\\') else None
                        name = ' '.join(parts[:-1]) if device_id else line
                        
                        if device_id and device_id.startswith('USB\\'):
                            camera_names[device_id] = name
            
            return camera_names
            
        except Exception as e:
            print_warning(f"Could not get USB camera names: {e}")
            return {}
    
    def create_default_config(self):
        """Create default config.txt if it doesn't exist"""
        if not os.path.exists(self.config_file):
            print_info("Creating default config.txt file...")
            
            default_config = """resolution=1920x1080
fps=15
bottomcamera=
middlecamera=
topcamera=
# Windows camera device IDs (for Windows systems)
bottomcamera_deviceid=
middlecamera_deviceid=
topcamera_deviceid=
"""
            
            try:
                with open(self.config_file, 'w') as f:
                    f.write(default_config)
                print_success(f"Default config.txt created at {self.config_file}")
            except Exception as e:
                print_error(f"Failed to create config file: {e}")
                return False
        
        return True
    
    def read_config(self):
        """Read current configuration"""
        config = {}
        
        if not os.path.exists(self.config_file):
            return config
        
        try:
            with open(self.config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        except Exception as e:
            print_error(f"Error reading config file: {e}")
        
        return config
    
    def update_config(self, position, device_id):
        """Update config.txt with camera device ID"""
        if not self.create_default_config():
            return False
        
        config = self.read_config()
        
        # Update the Windows device ID field
        device_id_key = f"{position}camera_deviceid"
        config[device_id_key] = device_id
        
        # Write updated config
        try:
            lines = []
            config_keys = set(config.keys())
            
            # Read existing file to preserve order and comments
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    for line in f:
                        original_line = line.rstrip()
                        stripped = line.strip()
                        
                        if stripped and not stripped.startswith('#') and '=' in stripped:
                            key, _ = stripped.split('=', 1)
                            key = key.strip()
                            
                            if key in config:
                                lines.append(f"{key}={config[key]}")
                                config_keys.remove(key)
                            else:
                                lines.append(original_line)
                        else:
                            lines.append(original_line)
            
            # Add any new keys that weren't in the original file
            for key in config_keys:
                lines.append(f"{key}={config[key]}")
            
            # Write updated file
            with open(self.config_file, 'w') as f:
                for line in lines:
                    f.write(line + '\n')
            
            print_success(f"Updated {device_id_key}={device_id}")
            return True
            
        except Exception as e:
            print_error(f"Failed to update config file: {e}")
            return False
    
    def show_current_config(self):
        """Display current configuration"""
        print_header("=== Current Configuration ===")
        
        config = self.read_config()
        
        if not config:
            print_warning("Config file not found or empty")
            return
        
        # Show general settings
        print("\nGeneral Settings:")
        for key in ['resolution', 'fps']:
            value = config.get(key, 'Not set')
            print(f"  {key:15}: {value}")
        
        # Show Linux camera serials
        print("\nLinux Camera Serials:")
        for position in ['bottom', 'middle', 'top']:
            key = f"{position}camera"
            value = config.get(key, 'Not set')
            print(f"  {key:15}: {value}")
        
        # Show Windows device IDs
        print("\nWindows Camera Device IDs:")
        for position in ['bottom', 'middle', 'top']:
            key = f"{position}camera_deviceid"
            value = config.get(key, 'Not set')
            if len(value) > 50:  # Truncate long device IDs for display
                value = value[:47] + "..."
            print(f"  {key:20}: {value}")
        
        print()
    
    def wait_for_camera_selection(self, position):
        """Interactive camera selection for a position"""
        print_header(f"=== Configuring {position.title()} Camera ===")
        print()
        
        # Get all available cameras
        devices = self.get_camera_devices()
        
        if not devices:
            print_error("No camera devices found!")
            print_info("Troubleshooting:")
            print("  - Check camera connections")
            print("  - Ensure cameras are properly installed")
            print("  - Try different USB ports")
            print("  - Check Device Manager for camera status")
            return False
        
        # Get friendly names
        camera_names = self.get_camera_friendly_names()
        
        print_info(f"Found {len(devices)} camera device(s):")
        print()
        
        # Show numbered list of cameras
        for i, device_id in enumerate(devices):
            name = camera_names.get(device_id, "Unknown Camera")
            print(f"  {i + 1}) {name}")
            print(f"      Device ID: {device_id}")
            print()
        
        # Ask user to select
        while True:
            try:
                choice = input(f"Select camera for {position} position (1-{len(devices)}, or 'c' to cancel): ").strip()
                
                if choice.lower() == 'c':
                    print_info("Configuration cancelled")
                    return False
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(devices):
                    selected_device = devices[choice_num - 1]
                    selected_name = camera_names.get(selected_device, "Unknown Camera")
                    
                    print()
                    print_success(f"Selected: {selected_name}")
                    print_info(f"Device ID: {selected_device}")
                    
                    # Confirm selection
                    confirm = input("Confirm this selection? (y/N): ").strip().lower()
                    if confirm == 'y':
                        if self.update_config(position, selected_device):
                            print_success(f"{position.title()} camera configuration completed!")
                            return True
                        else:
                            print_error("Failed to update configuration")
                            return False
                    else:
                        print_info("Selection cancelled, please choose again")
                        continue
                else:
                    print_error(f"Invalid choice. Please enter 1-{len(devices)}")
                    
            except ValueError:
                print_error("Invalid input. Please enter a number or 'c' to cancel")
            except KeyboardInterrupt:
                print("\nOperation cancelled")
                return False
    
    def test_camera_detection(self):
        """Test camera detection functionality"""
        print_header("=== Camera Detection Test ===")
        print()
        
        devices = self.get_camera_devices()
        
        if not devices:
            print_warning("No camera devices detected")
            print_info("Troubleshooting tips:")
            print("  - Check camera connections")
            print("  - Ensure cameras are installed properly")
            print("  - Try different USB ports")
            print("  - Check Windows Device Manager")
            print("  - Try running as Administrator")
        else:
            print_success(f"Found {len(devices)} camera device(s)")
            
            # Get friendly names
            camera_names = self.get_camera_friendly_names()
            
            for i, device_id in enumerate(devices):
                name = camera_names.get(device_id, "Unknown Camera")
                print(f"  {i + 1}. {name}")
                print(f"     Device ID: {device_id}")
        
        print()
        input("Press Enter to continue...")
    
    def reset_config(self):
        """Reset camera configurations"""
        print_warning("This will reset all Windows camera device ID configurations!")
        confirm = input("Are you sure? (y/N): ").strip().lower()
        
        if confirm == 'y':
            for position in ['bottom', 'middle', 'top']:
                self.update_config(position, "")
            print_success("All Windows camera device IDs reset to empty")
        else:
            print_info("Reset cancelled")
        
        print()
        input("Press Enter to continue...")
    
    def show_menu(self):
        """Show main menu"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print_header("╔══════════════════════════════════════════════════════════════╗")
        print_header("║              Windows Camera Configuration Menu               ║")
        print_header("║            Raspberry Pi Scouting Package (Windows)          ║")
        print_header("╚══════════════════════════════════════════════════════════════╝")
        print()
        
        self.show_current_config()
        
        print("Select camera position to configure:")
        print()
        print("  1) Configure Bottom Camera")
        print("  2) Configure Middle Camera")
        print("  3) Configure Top Camera")
        print("  4) Show Current Configuration")
        print("  5) Test Camera Detection")
        print("  6) Reset Windows Device ID Configuration")
        print("  7) Exit")
        print()
    
    def run(self):
        """Main menu loop"""
        # Ensure config file exists
        self.create_default_config()
        
        while True:
            self.show_menu()
            
            try:
                choice = input("Enter your choice (1-7): ").strip()
                
                if choice == '1':
                    self.wait_for_camera_selection('bottom')
                    input("Press Enter to continue...")
                elif choice == '2':
                    self.wait_for_camera_selection('middle')
                    input("Press Enter to continue...")
                elif choice == '3':
                    self.wait_for_camera_selection('top')
                    input("Press Enter to continue...")
                elif choice == '4':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.show_current_config()
                    input("Press Enter to continue...")
                elif choice == '5':
                    self.test_camera_detection()
                elif choice == '6':
                    self.reset_config()
                elif choice == '7':
                    print_success("Configuration completed!")
                    print_info(f"Config file saved at: {self.config_file}")
                    print()
                    print_info("You can now run the Windows UI with:")
                    print_info("  python simple_windows_ui.py")
                    print()
                    break
                else:
                    print_error("Invalid choice. Please enter 1-7.")
                    time.sleep(2)
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print_error(f"Unexpected error: {e}")
                time.sleep(2)

def main():
    """Main function"""
    print_info("Windows Camera Configuration Tool")
    print_info("Using wmic to detect camera device IDs")
    print()
    
    # Check if we're on Windows
    if os.name != 'nt':
        print_warning("This script is designed for Windows. Current OS may not support wmic command.")
    
    # Create and run configuration manager
    config_manager = WindowsCameraConfig()
    config_manager.run()

if __name__ == "__main__":
    main()

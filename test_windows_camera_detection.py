#!/usr/bin/env python3
"""
Test script for Windows camera detection using wmic command
This verifies that the wmic command works and can detect camera devices
"""

import subprocess
import sys
import cv2

def test_wmic_camera_detection():
    """Test the wmic command for USB camera detection"""
    print("🔍 Testing Windows USB camera detection using wmic command")
    print("=" * 60)
    
    try:
        # Test USB cameras only (as required by the application)
        cmd = ['wmic', 'path', 'Win32_PnPEntity', 'where', 'Description like "%Camera%" AND DeviceID like "USB%"', 'get', 'DeviceID']
        
        cmd = [
            'wmic', 'path', 'Win32_PnPEntity',
            'where', '(Name like "%B525%" OR Name like "%Logi%") AND PNPClass="MEDIA"',
            'get', 'DeviceID,Name,PNPClass'
        ]


        print(f"📋 Running USB camera command: {' '.join(cmd)}")
        print()
        
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode != 0:
            print(f"❌ Command failed with return code: {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False
        
        print("✅ Command executed successfully!")
        print()
        print("📄 Raw output:")
        print("-" * 40)
        print(result.stdout)
        print("-" * 40)
        print()
        
        # Parse the output
        usb_devices = []
        all_devices = []
        lines = result.stdout.strip().split('\n')
        
        print("🔍 Parsing USB camera devices:")
        for i, line in enumerate(lines):
            line = line.strip()
            print(f"  Line {i:2d}: '{line}'")
            
            # Skip header and empty lines
            if line and not line.startswith('DeviceID') and not line.startswith('---'):
                device_id = line.strip()
                if device_id:
                    all_devices.append(device_id)
                    if device_id.startswith('USB\\'):
                        usb_devices.append(device_id)
                        print(f"    ✅ Found USB camera device: {device_id}")
                    else:
                        print(f"    ⚠️ Non-USB camera device: {device_id}")
        
        print()
        print(f"📊 Summary: Found {len(usb_devices)} USB camera device(s) out of {len(all_devices)} total")
        
        if usb_devices:
            print("\n📋 USB Camera Device IDs:")
            for i, device_id in enumerate(usb_devices):
                print(f"  {i + 1}. {device_id}")
        else:
            print("\n⚠️ No USB camera devices found!")
            print("Possible reasons:")
            print("  - No USB cameras connected")
            print("  - USB cameras not properly installed")
            print("  - Permission issues")
            print("  - Camera drivers not installed")
            print("  - Only integrated/system webcams available")
        
        # Also test all cameras for comparison
        print("\n" + "=" * 60)
        print("🔍 Testing ALL camera detection for comparison:")
        
        try:
            cmd_all = ['wmic', 'path', 'Win32_PnPEntity', 'where', 'Description like "%Camera%"', 'get', 'DeviceID']
            result_all = subprocess.run(cmd_all, capture_output=True, text=True, shell=True)
            
            if result_all.returncode == 0:
                all_camera_devices = []
                lines_all = result_all.stdout.strip().split('\n')
                
                for line in lines_all:
                    line = line.strip()
                    if line and not line.startswith('DeviceID') and not line.startswith('---'):
                        device_id = line.strip()
                        if device_id:
                            all_camera_devices.append(device_id)
                
                print(f"📊 Total cameras (including system/integrated): {len(all_camera_devices)}")
                
                non_usb_cameras = [d for d in all_camera_devices if not d.startswith('USB\\')]
                if non_usb_cameras:
                    print("\n📋 Non-USB cameras (ignored by application):")
                    for i, device_id in enumerate(non_usb_cameras):
                        print(f"  {i + 1}. {device_id}")
            
        except Exception as e:
            print(f"⚠️ Could not test all cameras: {e}")
        
        return len(usb_devices) > 0
        
    except Exception as e:
        print(f"❌ Error running wmic command: {e}")
        return False

def test_opencv_camera_access():
    """Test OpenCV camera access for comparison"""
    print("\n🎥 Testing OpenCV camera access for comparison")
    print("=" * 60)
    
    found_cameras = []
    
    for i in range(5):  # Test first 5 camera indices
        try:
            print(f"Testing camera index {i}...")
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    
                    found_cameras.append((i, width, height, fps))
                    print(f"  ✅ Camera {i}: {width}x{height} @ {fps:.1f} FPS")
                else:
                    print(f"  ⚠️ Camera {i}: Opened but cannot read frames")
            else:
                print(f"  ❌ Camera {i}: Cannot open")
            
            cap.release()
            
        except Exception as e:
            print(f"  ❌ Camera {i}: Error - {e}")
    
    print(f"\n📊 OpenCV found {len(found_cameras)} working camera(s)")
    return found_cameras

def main():
    """Main test function"""
    print("🧪 Windows Camera Detection Test")
    print("Testing the wmic command for camera device ID detection")
    print()
    
    # Test wmic detection
    wmic_success = test_wmic_camera_detection()
    
    # Test OpenCV detection
    opencv_cameras = test_opencv_camera_access()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    print(f"wmic detection:    {'✅ SUCCESS' if wmic_success else '❌ FAILED'}")
    print(f"OpenCV detection:  {'✅ SUCCESS' if opencv_cameras else '❌ FAILED'} ({len(opencv_cameras)} cameras)")
    
    if wmic_success and opencv_cameras:
        print("\n🎉 Both detection methods working!")
        print("✅ Camera configuration script should work properly")
    elif wmic_success:
        print("\n⚠️ wmic works but OpenCV has issues")
        print("💡 Check camera drivers and OpenCV installation")
    elif opencv_cameras:
        print("\n⚠️ OpenCV works but wmic has issues")
        print("💡 Check Windows permissions and wmic availability")
    else:
        print("\n❌ Both detection methods failed")
        print("💡 Check camera connections and drivers")
    
    print("\n🔧 Next steps:")
    if wmic_success:
        print("  • Run 'python windows_configure_cameras.py' to configure camera positions")
        print("  • Or run 'windows_configure_cameras.bat' for easier access")
    print("  • Run 'python simple_windows_ui.py' to start the camera viewer")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()

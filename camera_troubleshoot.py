#!/usr/bin/env python3
"""
Camera Troubleshooting Script for Windows
Addresses NVIDIA and DirectShow camera access issues
"""

import cv2
import subprocess
import sys
import os

def check_nvidia_issues():
    """Check for NVIDIA-related camera issues"""
    print("🔍 Checking for NVIDIA camera issues...")

    try:
        # Check if NVIDIA drivers are present
        result = subprocess.run(['driverquery'], capture_output=True, text=True, timeout=10)
        nvidia_drivers = [line for line in result.stdout.split('\n') if 'nvidia' in line.lower()]

        if nvidia_drivers:
            print("⚠️ NVIDIA drivers detected - this can cause camera conflicts")
            print("   NVIDIA drivers may interfere with DirectShow cameras")
            return True
        else:
            print("✅ No NVIDIA drivers detected")
            return False
    except:
        print("ℹ️ Could not check driver status")
        return False

def test_different_backends():
    """Test camera access with different OpenCV backends"""
    print("\n🔧 Testing different OpenCV backends...")

    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_VFW, "Video for Windows"),
        (cv2.CAP_ANY, "Default")
    ]

    working_backends = {}

    for camera_idx in range(3):  # Test first 3 cameras
        print(f"\nCamera {camera_idx}:")
        camera_working = False

        for backend, name in backends:
            try:
                cap = cv2.VideoCapture(camera_idx, backend)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        height, width = frame.shape[:2]
                        print(f"  ✅ {name}: {width}x{height}")
                        working_backends[f"Camera {camera_idx}"] = name
                        camera_working = True
                    else:
                        print(f"  ⚠️ {name}: Opened but no frames")
                else:
                    print(f"  ❌ {name}: Failed to open")
                cap.release()
            except Exception as e:
                print(f"  ❌ {name}: {str(e)[:50]}...")

        if not camera_working:
            print(f"  💥 Camera {camera_idx}: No working backend found")

    return working_backends

def suggest_solutions():
    """Provide specific solutions based on findings"""
    print("\n🔧 TROUBLESHOOTING SOLUTIONS:")
    print("=" * 40)

    print("\n📋 Quick Fixes to Try:")
    print("1. 🔄 Restart your computer")
    print("2. 🔌 Unplug and replug your camera")
    print("3. 🔗 Try a different USB port")
    print("4. 📷 Test camera in Windows Camera app")

    print("\n🛠️ Advanced Solutions:")

    # NVIDIA-specific issues
    if check_nvidia_issues():
        print("\n🎮 NVIDIA Graphics Card Detected:")
        print("   • NVIDIA drivers can interfere with camera access")
        print("   • Try updating NVIDIA drivers to latest version")
        print("   • Or temporarily disable NVIDIA graphics for camera app")
        print("   • Use integrated graphics for camera applications")

    print("\n📹 Camera Driver Issues:")
    print("   • Update camera drivers from manufacturer's website")
    print("   • Try generic USB camera drivers")
    print("   • Check Device Manager for camera status")

    print("\n⚙️ Windows Settings:")
    print("   • Open Device Manager → Cameras")
    print("   • Right-click camera → Update driver")
    print("   • Check for 'Code 10' or other error codes")

    print("\n🖥️ Alternative Applications:")
    print("   • Test with Windows Camera app")
    print("   • Try third-party camera software")
    print("   • Use different camera/webcam")

    print("\n💻 System Restart:")
    print("   • Sometimes a full system restart resolves issues")
    print("   • Especially after driver updates")

def main():
    """Main troubleshooting function"""
    print("🔧 Windows Camera Troubleshooting Tool")
    print("=" * 45)
    print("This tool diagnoses camera access issues on Windows")

    # Check OpenCV installation
    print("\n🔍 Checking OpenCV installation...")
    try:
        print(f"   OpenCV version: {cv2.__version__}")
        print("   ✅ OpenCV installed")
    except Exception as e:
        print(f"   ❌ OpenCV error: {e}")
        print("   Install with: pip install opencv-python")
        return

    # Check for NVIDIA issues
    has_nvidia = check_nvidia_issues()

    # Test different backends
    working_backends = test_different_backends()

    # Provide solutions
    suggest_solutions()

    print("
📊 SUMMARY:"    print("=" * 20)

    if working_backends:
        print(f"✅ Found {len(working_backends)} working camera(s):")
        for camera, backend in working_backends.items():
            print(f"   • {camera}: {backend}")

        print("\n🎯 RECOMMENDATION:")
        print("   Your cameras should work with the simple application!")
        print("   Try: python simple_windows_ui.py")
    else:
        print("❌ No cameras found with any backend")
        print("\n🎯 RECOMMENDATION:")
        print("   Try the troubleshooting steps above")
        print("   Check camera connections and drivers")

    print("
🔄 After fixing issues, test with:"    print("   python test_simple_camera.py")
    print("   simple_launcher.bat")

if __name__ == "__main__":
    main()

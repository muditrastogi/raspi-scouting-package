#!/usr/bin/env python3
"""
Quick diagnostic script for Windows scouting package
Run this to identify and fix common issues
"""

import cv2
import subprocess
import sys
import os

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible"""
    print("🔧 Checking FFmpeg installation...")
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg is installed and working")
            return True
        else:
            print("❌ FFmpeg is not working properly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg is not found in PATH")
        print("   Please install FFmpeg and add it to your PATH")
        print("   Download from: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"❌ FFmpeg check failed: {e}")
        return False

def check_opencv():
    """Check OpenCV installation"""
    print("\n📷 Checking OpenCV installation...")
    try:
        print(f"   OpenCV version: {cv2.__version__}")
        print("✅ OpenCV is installed")
        return True
    except Exception as e:
        print(f"❌ OpenCV check failed: {e}")
        return False

def check_cameras():
    """Check camera access"""
    print("\n📹 Checking camera access...")
    cameras_found = []

    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                cameras_found.append((i, width, height))
                print(f"   Camera {i}: {width}x{height}")
            cap.release()

    if cameras_found:
        print(f"✅ Found {len(cameras_found)} camera(s)")

        # Also check FFmpeg device enumeration
        try:
            import subprocess
            result = subprocess.run([
                'ffmpeg', '-f', 'dshow', '-list_devices', 'true', '-i', 'dummy'
            ], capture_output=True, text=True, timeout=10)

            if 'DirectShow video devices' in result.stderr:
                print("✅ FFmpeg DirectShow device enumeration working")
            else:
                print("⚠️  FFmpeg DirectShow device enumeration may have issues")
        except Exception as e:
            print(f"⚠️  FFmpeg DirectShow check failed: {e}")

        return True
    else:
        print("❌ No cameras detected")
        print("   Make sure your cameras are connected and drivers are installed")
        return False

def check_network():
    """Check network connectivity for RTSP"""
    print("\n🌐 Checking network connectivity...")
    try:
        import socket
        # Try to bind to RTSP port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 8554))
        sock.close()
        print("✅ Port 8554 is available")
        return True
    except OSError as e:
        print(f"❌ Port 8554 is in use: {e}")
        return False
    except Exception as e:
        print(f"❌ Network check failed: {e}")
        return False

def run_quick_test():
    """Run a quick test of RTSP streaming using FFmpeg"""
    print("\n🧪 Running quick RTSP test...")

    # Start simple RTSP server
    print("   Starting RTSP server...")
    proc = subprocess.Popen([
        sys.executable, 'simple_rtsp_server.py',
        '--camera', '0',
        '--port', '8554'
    ])

    # Wait for server to start
    import time
    time.sleep(5)  # Give more time for FFmpeg to start

    # Test connection using FFmpeg
    rtsp_url = "rtsp://localhost:8554/live"

    try:
        test_cmd = [
            'ffmpeg',
            '-i', rtsp_url,
            '-t', '2',  # Test for 2 seconds
            '-f', 'null',  # Null output
            '-'
        ]

        result = subprocess.run(
            test_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10
        )

        if result.returncode == 0:
            print("✅ RTSP test successful")
            success = True
        else:
            print("❌ RTSP stream test failed")
            success = False
    except subprocess.TimeoutExpired:
        print("❌ RTSP connection test timed out")
        success = False
    except FileNotFoundError:
        print("❌ FFmpeg not found in PATH")
        success = False
    except Exception as e:
        print(f"❌ RTSP test error: {e}")
        success = False

    # Cleanup
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()

    return success

def main():
    """Main diagnostic function"""
    print("🔍 Windows Scouting Package - Quick Diagnostic")
    print("=" * 50)

    all_good = True

    # Run checks
    checks = [
        check_ffmpeg,
        check_opencv,
        check_cameras,
        check_network
    ]

    for check in checks:
        if not check():
            all_good = False

    # If basic checks pass, run RTSP test
    if all_good:
        if run_quick_test():
            print("\n🎉 All diagnostics passed!")
            print("   Your Windows scouting package should work correctly.")
            print("   Run: windows_scout_launcher.bat")
        else:
            print("\n⚠️  Basic checks passed but RTSP test failed")
            print("   Check camera drivers or try a different camera index")
    else:
        print("\n❌ Some diagnostics failed")
        print("   Please fix the issues above before running the application")

    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())

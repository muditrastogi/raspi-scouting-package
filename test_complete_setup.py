#!/usr/bin/env python3
"""
Complete test script for Windows scouting package
Tests all components: camera detection, RTSP streaming, and API
"""

import subprocess
import time
import sys
import os
import requests
import cv2

def test_camera_detection():
    """Test camera detection"""
    print("🔍 Testing camera detection...")

    try:
        result = subprocess.run([
            sys.executable, 'windows_camera_detection.py', '--detect-only'
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ Camera detection successful")
            return True
        else:
            print(f"❌ Camera detection failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Camera detection error: {e}")
        return False

def test_rtsp_server():
    """Test RTSP server startup using FFmpeg"""
    print("\n🎥 Testing RTSP server...")

    try:
        # Start RTSP server in background
        proc = subprocess.Popen([
            sys.executable, 'simple_rtsp_server.py',
            '--camera', '0',
            '--port', '8554'
        ])

        # Wait for server to start
        time.sleep(5)

        # Test RTSP connection using FFmpeg
        rtsp_url = "rtsp://localhost:8554/live"

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
            print("✅ RTSP server working correctly")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
            return True
        else:
            print("❌ RTSP server test failed")

    except subprocess.TimeoutExpired:
        print("❌ RTSP server test timed out")
    except FileNotFoundError:
        print("❌ FFmpeg not found")
    except Exception as e:
        print(f"❌ RTSP server test error: {e}")

    # Cleanup
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()

    return False

def test_record_api():
    """Test record API"""
    print("\n📡 Testing record API...")

    try:
        # Start API server
        proc = subprocess.Popen([
            sys.executable, 'windows_record_api.py',
            '--port', '5000',
            '--rtsp-url', 'rtsp://localhost:8554/live'
        ])

        # Wait for server to start
        time.sleep(3)

        # Test API endpoints
        try:
            response = requests.get('http://localhost:5000/status', timeout=5)
            if response.status_code == 200:
                print("✅ Record API status endpoint working")
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                return True
            else:
                print(f"❌ Record API status failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Record API connection failed: {e}")

        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        return False

    except Exception as e:
        print(f"❌ Record API test error: {e}")
        return False

def main():
    """Run complete test suite"""
    print("🚀 Windows Scouting Package - Complete Test Suite")
    print("=" * 50)

    all_passed = True

    # Test camera detection
    if not test_camera_detection():
        all_passed = False

    # Test RTSP server
    if not test_rtsp_server():
        all_passed = False

    # Test record API
    if not test_record_api():
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your Windows scouting package is ready.")
        print("\nTo run the full application:")
        print("  windows_scout_launcher.bat")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\nTroubleshooting:")
        print("1. Make sure cameras are connected and accessible")
        print("2. Check that FFmpeg is installed and in PATH")
        print("3. Try running components individually:")
        print("   python simple_rtsp_server.py --camera 0")
        print("   python windows_record_api.py --port 5000")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

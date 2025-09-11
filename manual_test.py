#!/usr/bin/env python3
"""
Manual test script for RTSP streaming
Run this to manually test each component
"""

import subprocess
import sys
import time

def test_camera_access():
    """Test basic camera access"""
    print("Testing camera access...")
    try:
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                height, width = frame.shape[:2]
                print(f"✅ Camera 0: {width}x{height}")
                cap.release()
                return True
            else:
                print("❌ Camera opened but no frames")
        else:
            print("❌ Camera not accessible")
        cap.release()
    except Exception as e:
        print(f"❌ Camera test error: {e}")
    return False

def test_ffmpeg_direct():
    """Test FFmpeg direct camera access"""
    print("\nTesting FFmpeg direct camera access...")
    try:
        # List DirectShow devices
        result = subprocess.run([
            'ffmpeg', '-f', 'dshow', '-list_devices', 'true', '-i', 'dummy'
        ], capture_output=True, text=True, timeout=10)

        if 'DirectShow video devices' in result.stderr:
            print("✅ FFmpeg can access DirectShow devices")
            return True
        else:
            print("❌ FFmpeg DirectShow access failed")
            print("FFmpeg stderr:", result.stderr[:500])
    except Exception as e:
        print(f"❌ FFmpeg DirectShow test error: {e}")
    return False

def test_manual_rtsp():
    """Manual RTSP server test"""
    print("\nStarting manual RTSP server test...")
    print("This will start an RTSP server. In another terminal, run:")
    print("ffmpeg -i rtsp://localhost:8554/live -t 5 -f null -")
    print("Press Ctrl+C to stop the server")

    try:
        proc = subprocess.Popen([
            sys.executable, 'simple_rtsp_server.py',
            '--camera', '0'
        ])

        proc.wait()
    except KeyboardInterrupt:
        print("\nStopping RTSP server...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()

def main():
    """Main test function"""
    print("🔧 Manual RTSP Test Suite")
    print("=" * 30)

    # Test camera access
    if not test_camera_access():
        print("❌ Basic camera access failed. Cannot proceed.")
        return

    # Test FFmpeg DirectShow
    if not test_ffmpeg_direct():
        print("❌ FFmpeg DirectShow failed. Cannot proceed.")
        return

    # Manual RTSP test
    test_manual_rtsp()

if __name__ == "__main__":
    main()

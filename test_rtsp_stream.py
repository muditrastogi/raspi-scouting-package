#!/usr/bin/env python3
"""
Simple test script to debug RTSP streaming issues
"""

import cv2
import time
import subprocess
import sys

def test_camera_access():
    """Test if cameras are accessible"""
    print("Testing camera access...")

    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                print(f"✓ Camera {i}: {width}x{height}")
                cap.release()
                return i
            cap.release()

    print("✗ No accessible cameras found")
    return None

def test_ffmpeg_rtsp(camera_index):
    """Test FFmpeg RTSP streaming"""
    print(f"\nTesting FFmpeg RTSP streaming for camera {camera_index}...")

    rtsp_url = "rtsp://localhost:8554/live"

    ffmpeg_cmd = [
        'ffmpeg',
        '-f', 'dshow',
        '-i', f'video={camera_index}',
        '-f', 'rtsp',
        '-rtsp_transport', 'tcp',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-g', '30',
        '-b:v', '2000k',
        '-maxrate', '2000k',
        '-bufsize', '4000k',
        '-vf', 'scale=1920:1080',
        '-r', '30',
        rtsp_url
    ]

    print(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")

    try:
        proc = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        print(f"FFmpeg started. RTSP stream should be available at: {rtsp_url}")
        print("Press Ctrl+C to stop...")

        # Let it run for a few seconds
        time.sleep(5)

        # Test if we can connect to the RTSP stream
        print("\nTesting RTSP connection...")
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)

        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✓ Successfully connected to RTSP stream!")
                height, width = frame.shape[:2]
                print(f"✓ Stream resolution: {width}x{height}")
            else:
                print("✗ Failed to read frame from RTSP stream")
            cap.release()
        else:
            print("✗ Failed to open RTSP stream")

        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    except Exception as e:
        print(f"✗ Error testing FFmpeg: {e}")

def main():
    print("Windows RTSP Streaming Test")
    print("=" * 30)

    camera_index = test_camera_access()
    if camera_index is not None:
        test_ffmpeg_rtsp(camera_index)
    else:
        print("Cannot proceed without camera access")

if __name__ == "__main__":
    main()

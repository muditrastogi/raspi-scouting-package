#!/usr/bin/env python3
"""
Simple camera test for the simplified Windows scouting package
"""

import cv2
import sys

def test_camera_access():
    """Test camera access with multiple backends"""
    print("🔍 Testing camera access with multiple backends...")
    print("=" * 50)

    cameras_found = []

    for camera_idx in range(5):
        print(f"\nTesting camera {camera_idx}:")

        # Try different OpenCV backends
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_VFW, "Video for Windows"),
            (cv2.CAP_ANY, "Default")
        ]

        working_backend = None
        camera_info = None

        for backend, name in backends:
            try:
                print(f"  Trying {name}...")
                cap = cv2.VideoCapture(camera_idx, backend)

                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        height, width = frame.shape[:2]
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        print(f"  ✅ {name}: {width}x{height} @ {fps:.1f} FPS")
                        working_backend = backend
                        camera_info = (camera_idx, width, height, fps, name)
                        cap.release()
                        break
                    else:
                        print(f"  ⚠️ {name}: Opened but no frames")
                else:
                    print(f"  ❌ {name}: Failed to open")

                cap.release()

            except Exception as e:
                print(f"  ❌ {name}: Error - {e}")

        if working_backend:
            cameras_found.append(camera_info)
            print(f"  🎯 Camera {camera_idx} works with {camera_info[4]}")
        else:
            print(f"  ❌ Camera {camera_idx}: No working backend")

    print(f"\n📊 Results: {len(cameras_found)} camera(s) found")

    if cameras_found:
        print("\n🎯 Available cameras:")
        for idx, width, height, fps, backend in cameras_found:
            print(f"  Camera {idx}: {width}x{height} @ {fps:.1f} FPS ({backend})")

        print("\n🚀 You can now run:")
        print("  simple_launcher.bat")
        print("  python simple_windows_ui.py")
        return True
    else:
        print("\n❌ No cameras found!")
        print("\n🔧 Troubleshooting:")
        print("  1. Check camera connections")
        print("  2. Try different USB ports")
        print("  3. Update camera drivers")
        print("  4. Restart computer")
        print("  5. Check Device Manager for camera status")
        print("  6. Try different camera applications")
        return False

def test_opencv_installation():
    """Test OpenCV installation"""
    print("\n🔧 Testing OpenCV installation...")

    try:
        print(f"  OpenCV version: {cv2.__version__}")
        print("  ✅ OpenCV installed")
        return True
    except Exception as e:
        print(f"  ❌ OpenCV error: {e}")
        print("  Install with: pip install opencv-python")
        return False

def main():
    """Main test function"""
    print("🧪 Simple Camera Test")
    print("=" * 30)

    # Test OpenCV first
    if not test_opencv_installation():
        print("\n❌ OpenCV not properly installed")
        return 1

    # Test camera access
    if test_camera_access():
        print("\n🎉 Camera test successful!")
        return 0
    else:
        print("\n❌ Camera test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

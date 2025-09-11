#!/usr/bin/env python3
"""
List FFmpeg DirectShow devices for Windows
This helps identify the correct device names for FFmpeg
"""

import subprocess
import sys
import cv2
def check_ffmpeg_capabilities():
    """Check FFmpeg capabilities and DirectShow support"""
    print("🔧 Checking FFmpeg capabilities...")

    try:
        # Check FFmpeg version and configuration
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        version_info = result.stdout.split('\n')[0] if result.stdout else "Unknown"

        print(f"   FFmpeg version: {version_info}")

        # Check if DirectShow is enabled
        if '--enable-dshow' in result.stdout or 'dshow' in result.stdout:
            print("   ✅ DirectShow support: Enabled")
            return True
        else:
            print("   ⚠️  DirectShow support: May not be enabled")
            print("   This FFmpeg build might not have DirectShow support")
            return False

    except Exception as e:
        print(f"   ❌ Error checking FFmpeg capabilities: {e}")
        return False

def try_dshow_enumeration():
    """Try DirectShow device enumeration"""
    print("\n📹 Trying DirectShow device enumeration...")

    try:
        result = subprocess.run([
            'ffmpeg', '-f', 'dshow', '-list_devices', 'true', '-i', 'dummy'
        ], capture_output=True, text=True, timeout=15)

        return result.stderr

    except subprocess.TimeoutExpired:
        print("❌ DirectShow enumeration timed out")
        return None
    except Exception as e:
        print(f"❌ Error in DirectShow enumeration: {e}")
        return None

def try_vfwcap_enumeration():
    """Try Video for Windows capture enumeration (older Windows)"""
    print("\n📽️ Trying VFW capture device enumeration...")

    try:
        result = subprocess.run([
            'ffmpeg', '-f', 'vfwcap', '-list_devices', 'true', '-i', 'dummy'
        ], capture_output=True, text=True, timeout=15)

        return result.stderr

    except Exception as e:
        print(f"❌ VFW enumeration failed: {e}")
        return None

def try_avfoundation_enumeration():
    """Try AVFoundation enumeration (macOS, but let's see)"""
    print("\n🍎 Trying AVFoundation device enumeration...")

    try:
        result = subprocess.run([
            'ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', 'dummy'
        ], capture_output=True, text=True, timeout=15)

        return result.stderr

    except Exception as e:
        print(f"❌ AVFoundation enumeration failed: {e}")
        return None

def list_ffmpeg_devices():
    """List available FFmpeg devices using multiple methods"""
    print("🔍 Listing FFmpeg devices...")
    print("=" * 50)

    # First check FFmpeg capabilities
    dshow_supported = check_ffmpeg_capabilities()

    video_devices = []
    audio_devices = []

    # Try different enumeration methods
    methods = [
        ("DirectShow", try_dshow_enumeration),
        ("VFW Capture", try_vfwcap_enumeration),
        ("AVFoundation", try_avfoundation_enumeration)
    ]

    for method_name, method_func in methods:
        print(f"\n🔍 Trying {method_name}...")
        output = method_func()

        if output:
            print(f"📋 {method_name} Output:")
            lines = output.split('\n')

            in_video_section = False
            in_audio_section = False

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Look for device sections
                if 'video devices' in line.lower() or 'video device' in line.lower():
                    in_video_section = True
                    in_audio_section = False
                    print("   📹 Video devices found in output")
                    continue
                elif 'audio devices' in line.lower() or 'audio device' in line.lower():
                    in_video_section = False
                    in_audio_section = True
                    print("   🎵 Audio devices found in output")
                    continue

                # Look for device names (various patterns)
                device_patterns = ['"', '@device_pnp_', 'device #', 'Camera', 'Webcam']
                if any(pattern in line for pattern in device_patterns):
                    # Try to extract device name
                    if '"' in line:
                        start = line.find('"') + 1
                        end = line.find('"', start)
                        if start > 0 and end > start:
                            device_name = line[start:end]
                            if in_video_section:
                                video_devices.append(device_name)
                                print(f"   • Video: {device_name}")
                            elif in_audio_section:
                                audio_devices.append(device_name)
                                print(f"   • Audio: {device_name}")

    print(f"\n📊 Summary:")
    print(f"   Video devices found: {len(video_devices)}")
    print(f"   Audio devices found: {len(audio_devices)}")

    if not video_devices:
        print("\n❌ No video devices found with any method!")
        print("\n🔧 Troubleshooting suggestions:")
        print("   1. Make sure your camera is connected and powered on")
        print("   2. Update your camera drivers from the manufacturer's website")
        print("   3. Try different USB ports")
        print("   4. Check Windows Device Manager for camera status")
        print("   5. Try restarting your computer")
        print("   6. Test with a different camera if available")

        if not dshow_supported:
            print("\n⚠️  Your FFmpeg build may not have DirectShow support enabled")
            print("   Consider reinstalling FFmpeg with DirectShow support")

    return video_devices

def test_device_access(device_name):
    """Test if we can access a specific device"""
    print(f"\n🧪 Testing device access: {device_name}")

    try:
        # Test with a short capture
        result = subprocess.run([
            'ffmpeg',
            '-f', 'dshow',
            '-i', f'video="{device_name}"',
            '-t', '3',  # 3 seconds
            '-f', 'null',  # Null output
            '-'
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ Device accessible!")
            return True
        else:
            print("❌ Device access failed")
            if result.stderr:
                # Show last few lines of error
                lines = result.stderr.split('\n')
                for line in lines[-3:]:
                    if line.strip():
                        print(f"   {line}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Device test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing device: {e}")
        return False

def test_opencv_fallback():
    """Test OpenCV camera access as fallback"""
    print("\n📷 Testing OpenCV camera access...")

    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                print(f"✅ OpenCV can access camera {i}: {width}x{height}")
                cap.release()
                return True
            cap.release()

    print("❌ OpenCV cannot access any cameras")
    return False

def main():
    """Main function"""
    devices = list_ffmpeg_devices()

    # Test OpenCV fallback regardless of FFmpeg results
    opencv_works = test_opencv_fallback()

    if devices:
        print(f"\n🔧 Testing FFmpeg device: {devices[0]}")
        test_device_access(devices[0])
    else:
        print("\n⚠️  FFmpeg device enumeration failed")
        if opencv_works:
            print("✅ But OpenCV can access cameras - the system will use OpenCV fallback")

    print("\n📝 Usage Examples:")
    print("   python simple_rtsp_server.py --camera 0")
    print("   python opencv_rtsp_server.py --camera 0  # OpenCV fallback")
    print("   python windows_scout_launcher.bat")

if __name__ == "__main__":
    main()

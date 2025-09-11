#!/usr/bin/env python3
"""
Simple RTSP server for Windows using OpenCV
This is a more reliable alternative to the complex FFmpeg approach
"""

import cv2
import time
import threading
import subprocess
import sys
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_ffmpeg_device_name(camera_index=0):
    """Get the correct FFmpeg DirectShow device name"""
    try:
        # List available DirectShow devices
        result = subprocess.run([
            'ffmpeg', '-f', 'dshow', '-list_devices', 'true', '-i', 'dummy'
        ], capture_output=True, text=True, timeout=10)

        lines = result.stderr.split('\n')
        video_devices = []

        for line in lines:
            if 'DirectShow video devices' in line:
                continue
            if '"@device_pnp_' in line and 'DirectShow' in line:
                # Extract device name
                start = line.find('"') + 1
                end = line.find('"', start)
                if start > 0 and end > start:
                    device_name = line[start:end]
                    video_devices.append(device_name)

        if video_devices:
            # Return the device at the specified index
            if camera_index < len(video_devices):
                logger.info(f"Found {len(video_devices)} video devices. Using: {video_devices[camera_index]}")
                return video_devices[camera_index]
            else:
                logger.warning(f"Camera index {camera_index} not found. Available devices: {video_devices}")
                return video_devices[0] if video_devices else None
        else:
            logger.error("No DirectShow video devices found")
            return None

    except Exception as e:
        logger.error(f"Error enumerating DirectShow devices: {e}")
        return None

def start_opencv_fallback(camera_index=0, rtsp_port=8554, width=1920, height=1080, fps=30):
    """Fallback RTSP server using OpenCV VideoWriter"""
    rtsp_url = f"rtsp://localhost:{rtsp_port}/live"
    logger.info(f"Starting OpenCV fallback RTSP server on {rtsp_url}")

    try:
        # Open camera with OpenCV
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            logger.error(f"Failed to open camera {camera_index}")
            return False

        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)

        # Get actual camera properties
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = cap.get(cv2.CAP_PROP_FPS)

        logger.info(f"Camera opened: {actual_width}x{actual_height} @ {actual_fps} FPS")

        # Try different codecs
        codec_attempts = [
            ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),
            ('XVID', cv2.VideoWriter_fourcc(*'XVID')),
            ('DIVX', cv2.VideoWriter_fourcc(*'DIVX')),
        ]

        rtsp_writer = None
        successful_codec = None

        for codec_name, fourcc in codec_attempts:
            try:
                logger.info(f"Trying codec: {codec_name}")
                rtsp_writer = cv2.VideoWriter(
                    rtsp_url,
                    cv2.CAP_FFMPEG,
                    fourcc,
                    fps,
                    (actual_width, actual_height)
                )

                if rtsp_writer.isOpened():
                    logger.info(f"✅ RTSP stream started with {codec_name} codec")
                    successful_codec = codec_name
                    break
                else:
                    logger.warning(f"❌ Failed with {codec_name} codec")
                    rtsp_writer = None

            except Exception as e:
                logger.warning(f"Error with {codec_name}: {e}")
                if rtsp_writer:
                    rtsp_writer.release()
                rtsp_writer = None

        if rtsp_writer is None:
            logger.error("Failed to start RTSP stream with any codec")
            cap.release()
            return False

        logger.info(f"RTSP server streaming at: {rtsp_url}")
        logger.info("Press Ctrl+C to stop...")

        frame_count = 0
        start_time = time.time()

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.error("Failed to read frame from camera")
                    break

                rtsp_writer.write(frame)
                frame_count += 1

                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    fps_actual = frame_count / elapsed
                    logger.info(".1f")

                time.sleep(0.01)

        except KeyboardInterrupt:
            logger.info("Stopping RTSP server...")

        finally:
            logger.info(f"RTSP server stopped. Total frames: {frame_count}")
            cap.release()
            if rtsp_writer:
                rtsp_writer.release()

    except Exception as e:
        logger.error(f"Error in OpenCV fallback: {e}")
        return False

    return True

def start_simple_rtsp_server(camera_index=0, rtsp_port=8554, width=1920, height=1080, fps=30):
    """Start a simple RTSP server using FFmpeg directly"""

    rtsp_url = f"rtsp://localhost:{rtsp_port}/live"
    logger.info(f"Starting FFmpeg RTSP server on {rtsp_url}")

    try:
        # Get the correct device name from FFmpeg
        device_name = get_ffmpeg_device_name(camera_index)
        if device_name is None:
            logger.warning("Could not find a suitable video device with FFmpeg DirectShow")
            logger.info("Falling back to OpenCV RTSP method...")

            # Fallback to OpenCV method
            return start_opencv_fallback(camera_index, rtsp_port, width, height, fps)

        # Test camera access with OpenCV to get properties
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            logger.error(f"Failed to open camera {camera_index} with OpenCV")
            return False

        # Get actual camera properties
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        logger.info(f"Camera {camera_index}: {actual_width}x{actual_height} @ {actual_fps} FPS")
        logger.info(f"Using FFmpeg device: {device_name}")

        # Use FFmpeg command with correct device name
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'dshow',  # DirectShow input for Windows cameras
            '-i', f'video="{device_name}"',  # Camera input with proper device name
            '-f', 'rtsp',  # RTSP output format
            '-rtsp_transport', 'tcp',  # TCP transport
            '-c:v', 'libx264',  # H.264 codec
            '-preset', 'ultrafast',  # Fast encoding
            '-tune', 'zerolatency',  # Low latency
            '-g', '30',  # GOP size
            '-keyint_min', '30',  # Minimum keyframe interval
            '-b:v', '2000k',  # Bitrate
            '-maxrate', '2000k',  # Maximum bitrate
            '-bufsize', '4000k',  # Buffer size
            '-vf', f'scale={min(width, actual_width)}:{min(height, actual_height)}',  # Scale if needed
            '-r', str(min(fps, int(actual_fps))),  # Frame rate
            '-pix_fmt', 'yuv420p',  # Pixel format for H.264
            rtsp_url  # RTSP output URL
        ]

        logger.info(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")

        # Start FFmpeg process
        ffmpeg_proc = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        logger.info(f"FFmpeg RTSP server started for camera {camera_index}")
        logger.info(f"RTSP stream available at: {rtsp_url}")
        logger.info("Press Ctrl+C to stop...")

        try:
            # Monitor the process
            while True:
                if ffmpeg_proc.poll() is not None:
                    # Process ended
                    stdout, stderr = ffmpeg_proc.communicate()
                    if ffmpeg_proc.returncode != 0:
                        logger.error(f"FFmpeg process failed with return code {ffmpeg_proc.returncode}")
                        if stderr:
                            logger.error(f"FFmpeg stderr: {stderr.decode()}")
                    break
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Stopping RTSP server...")

        finally:
            # Clean up
            if ffmpeg_proc and ffmpeg_proc.poll() is None:
                logger.info("Terminating FFmpeg process...")
                ffmpeg_proc.terminate()
                try:
                    ffmpeg_proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    ffmpeg_proc.kill()
                    logger.info("FFmpeg process force killed")

        logger.info("RTSP server stopped")

    except Exception as e:
        logger.error(f"Error in RTSP server: {e}")
        return False

    return True

def test_rtsp_connection(rtsp_url):
    """Test RTSP connection using FFmpeg"""
    logger.info(f"Testing RTSP connection to: {rtsp_url}")

    try:
        # Use FFmpeg to test RTSP connection (more reliable than OpenCV)
        test_cmd = [
            'ffmpeg',
            '-i', rtsp_url,
            '-t', '2',  # Test for 2 seconds
            '-f', 'null',  # Null output (just test connection)
            '-'
        ]

        result = subprocess.run(
            test_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15  # Increased timeout for RTSP connection
        )

        if result.returncode == 0:
            logger.info("✓ RTSP stream working correctly")
            return True
        else:
            logger.error(f"✗ RTSP stream test failed (return code: {result.returncode})")
            return False

    except subprocess.TimeoutExpired:
        logger.error("✗ RTSP connection test timed out")
        return False
    except FileNotFoundError:
        logger.error("✗ FFmpeg not found. Please install FFmpeg and add to PATH")
        return False
    except Exception as e:
        logger.error(f"✗ Error testing RTSP connection: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Simple RTSP Server for Windows')
    parser.add_argument('--camera', type=int, default=0, help='Camera index (default: 0)')
    parser.add_argument('--port', type=int, default=8554, help='RTSP port (default: 8554)')
    parser.add_argument('--width', type=int, default=1920, help='Video width')
    parser.add_argument('--height', type=int, default=1080, help='Video height')
    parser.add_argument('--fps', type=int, default=30, help='Video FPS')
    parser.add_argument('--test-only', action='store_true', help='Only test RTSP connection')

    args = parser.parse_args()

    if args.test_only:
        rtsp_url = f"rtsp://localhost:{args.port}/live"
        test_rtsp_connection(rtsp_url)
    else:
        success = start_simple_rtsp_server(args.camera, args.port, args.width, args.height, args.fps)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Windows Camera Detection and RTSP Streaming System
Replaces v4l2rtspserver and Linux-specific camera detection for Windows compatibility
"""

import cv2
import threading
import time
import subprocess
import os
import sys
from datetime import datetime
import argparse
import logging
import platform

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WindowsCameraManager:
    """Manages camera detection and RTSP streaming on Windows"""

    def __init__(self):
        self.cameras = []
        self.rtsp_servers = []
        self.streaming_threads = []
        self.active_streams = {}

    def detect_cameras(self):
        """Detect available cameras using OpenCV"""
        logger.info("Detecting available cameras...")
        self.cameras = []

        # Test camera indices from 0 to 9
        for i in range(10):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Use DirectShow on Windows
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    # Get camera properties
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)

                    camera_info = {
                        'index': i,
                        'width': width,
                        'height': height,
                        'fps': fps,
                        'name': f"Camera_{i}"
                    }

                    self.cameras.append(camera_info)
                    logger.info(f"Found camera {i}: {width}x{height} @ {fps} FPS")

                cap.release()

        if not self.cameras:
            logger.warning("No cameras detected!")
            return False

        logger.info(f"Successfully detected {len(self.cameras)} camera(s)")
        return True

    def get_camera_info(self):
        """Get information about detected cameras"""
        return self.cameras

    def start_rtsp_server(self, camera_index, rtsp_port=8554, width=1920, height=1080, fps=30):
        """Start RTSP server for a camera using OpenCV and FFmpeg"""

        if camera_index >= len(self.cameras):
            logger.error(f"Camera index {camera_index} not available")
            return False

        camera_info = self.cameras[camera_index]
        rtsp_url = f"rtsp://localhost:{rtsp_port}/live"

        def stream_camera():
            logger.info(f"Starting RTSP stream for camera {camera_index} on port {rtsp_port}")

            # Try OpenCV's RTSP streaming first (more reliable)
            try:
                logger.info("Attempting OpenCV RTSP streaming...")

                # Open camera with OpenCV
                cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
                if not cap.isOpened():
                    raise Exception(f"Failed to open camera {camera_index}")

                # Set camera properties
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                cap.set(cv2.CAP_PROP_FPS, fps)

                # Create RTSP writer using OpenCV
                fourcc = cv2.VideoWriter_fourcc(*'H264')
                rtsp_writer = cv2.VideoWriter(rtsp_url, cv2.CAP_FFMPEG, fourcc, fps, (width, height))

                if not rtsp_writer.isOpened():
                    raise Exception("Failed to create RTSP writer")

                logger.info(f"RTSP server started for camera {camera_index} at {rtsp_url}")

                self.active_streams[camera_index] = {
                    'process': None,
                    'url': rtsp_url,
                    'camera_info': camera_info,
                    'cap': cap,
                    'writer': rtsp_writer
                }

                # Stream frames
                while camera_index in self.active_streams:
                    ret, frame = cap.read()
                    if not ret:
                        logger.error(f"Failed to read frame from camera {camera_index}")
                        break

                    # Write frame to RTSP stream
                    rtsp_writer.write(frame)

                    # Small delay to prevent overwhelming
                    time.sleep(0.01)

                logger.info(f"OpenCV RTSP streaming ended for camera {camera_index}")

            except Exception as e:
                logger.warning(f"OpenCV RTSP streaming failed: {e}")
                logger.info("Falling back to FFmpeg RTSP streaming...")

                # Fallback to FFmpeg approach
                try:
                    # Simple FFmpeg command for RTSP
                    ffmpeg_cmd = [
                        'ffmpeg',
                        '-f', 'dshow',
                        '-i', f'video={camera_index}',
                        '-f', 'rtsp',
                        '-rtsp_transport', 'tcp',
                        '-c:v', 'libx264',
                        '-preset', 'ultrafast',
                        '-tune', 'zerolatency',
                        '-g', '15',
                        '-b:v', '1500k',
                        '-vf', f'scale={width}:{height}',
                        '-r', str(fps),
                        rtsp_url
                    ]

                    logger.info(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")

                    ffmpeg_proc = subprocess.Popen(
                        ffmpeg_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
                    )

                    logger.info(f"FFmpeg RTSP server started for camera {camera_index} at {rtsp_url}")

                    self.active_streams[camera_index] = {
                        'process': ffmpeg_proc,
                        'url': rtsp_url,
                        'camera_info': camera_info,
                        'cap': None,
                        'writer': None
                    }

                    # Monitor FFmpeg process
                    while camera_index in self.active_streams:
                        if ffmpeg_proc.poll() is not None:
                            logger.error(f"FFmpeg process ended for camera {camera_index}")
                            break
                        time.sleep(1)

                except Exception as ffmpeg_e:
                    logger.error(f"FFmpeg fallback also failed: {ffmpeg_e}")
                    return

            finally:
                # Cleanup
                if camera_index in self.active_streams:
                    stream_info = self.active_streams[camera_index]

                    # Close OpenCV resources
                    if 'cap' in stream_info and stream_info['cap']:
                        stream_info['cap'].release()
                    if 'writer' in stream_info and stream_info['writer']:
                        stream_info['writer'].release()

                    # Terminate FFmpeg process
                    if stream_info.get('process') and stream_info['process'].poll() is None:
                        stream_info['process'].terminate()
                        try:
                            stream_info['process'].wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            stream_info['process'].kill()

                    del self.active_streams[camera_index]

        # Start streaming thread
        stream_thread = threading.Thread(target=stream_camera, daemon=True)
        stream_thread.start()
        self.streaming_threads.append(stream_thread)

        # Store RTSP server info
        self.rtsp_servers.append({
            'camera_index': camera_index,
            'port': rtsp_port,
            'url': rtsp_url,
            'thread': stream_thread
        })

        return True

    def stop_rtsp_server(self, camera_index=None):
        """Stop RTSP server for specific camera or all cameras"""
        if camera_index is None:
            # Stop all servers
            for idx in list(self.active_streams.keys()):
                self._stop_single_server(idx)
            return True
        else:
            return self._stop_single_server(camera_index)

    def _stop_single_server(self, camera_index):
        """Stop a single RTSP server"""
        if camera_index in self.active_streams:
            stream_info = self.active_streams[camera_index]
            process = stream_info.get('process')

            if process and process.poll() is None:
                logger.info(f"Terminating RTSP server for camera {camera_index}")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    logger.info(f"RTSP server for camera {camera_index} terminated gracefully")
                except subprocess.TimeoutExpired:
                    process.kill()
                    logger.info(f"RTSP server for camera {camera_index} force killed")

            # Remove from active streams
            del self.active_streams[camera_index]
            return True
        else:
            logger.warning(f"No active RTSP server found for camera {camera_index}")
            return False

    def get_rtsp_urls(self):
        """Get list of active RTSP URLs"""
        return [info['url'] for info in self.active_streams.values()]

    def cleanup(self):
        """Cleanup all resources"""
        logger.info("Cleaning up camera manager...")
        self.stop_rtsp_server()  # Stop all servers

        # Wait for threads to finish
        for thread in self.streaming_threads:
            if thread.is_alive():
                thread.join(timeout=5)

        logger.info("Camera manager cleanup completed")


class WindowsRTSPRecorder:
    """Windows-compatible RTSP recording using OpenCV"""

    def __init__(self, rtsp_url, resolution=(1920, 1080)):
        self.rtsp_url = rtsp_url
        self.resolution = resolution
        self.recording_processes = {}
        self.recording_lock = threading.Lock()

    def start_recording(self, output_path, duration=None):
        """Start recording from RTSP stream"""

        def record():
            logger.info(f"Starting recording to: {output_path}")

            # OpenCV capture from RTSP
            cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)

            if not cap.isOpened():
                logger.error(f"Failed to open RTSP stream: {self.rtsp_url}")
                return

            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0:
                fps = 30  # Default FPS

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            if not out.isOpened():
                logger.error(f"Failed to create output video file: {output_path}")
                cap.release()
                return

            start_time = time.time()
            frame_count = 0

            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        logger.error("Failed to read frame from RTSP stream")
                        break

                    # Write frame to output
                    out.write(frame)
                    frame_count += 1

                    # Check duration limit
                    if duration and (time.time() - start_time) >= duration:
                        logger.info(f"Recording duration limit reached: {duration}s")
                        break

                    # Check if recording should stop
                    with self.recording_lock:
                        if output_path not in self.recording_processes:
                            break

            except Exception as e:
                logger.error(f"Error during recording: {e}")
            finally:
                cap.release()
                out.release()

                with self.recording_lock:
                    if output_path in self.recording_processes:
                        del self.recording_processes[output_path]

                logger.info(f"Recording completed: {output_path} ({frame_count} frames)")

        # Start recording thread
        record_thread = threading.Thread(target=record, daemon=True)
        record_thread.start()

        # Store recording info
        self.recording_processes[output_path] = {
            'thread': record_thread,
            'start_time': datetime.now()
        }

        return True

    def stop_recording(self, output_path=None):
        """Stop recording"""
        with self.recording_lock:
            if output_path:
                if output_path in self.recording_processes:
                    del self.recording_processes[output_path]
                    return True
            else:
                # Stop all recordings
                self.recording_processes.clear()
                return True
        return False


def test_rtsp_connection(rtsp_url):
    """Test if RTSP stream is accessible"""
    logger.info(f"Testing RTSP connection to: {rtsp_url}")
    try:
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                logger.info(f"✓ RTSP stream working: {width}x{height}")
                cap.release()
                return True
            else:
                logger.error("✗ RTSP stream opened but cannot read frames")
        else:
            logger.error("✗ Failed to open RTSP stream")
        cap.release()
    except Exception as e:
        logger.error(f"✗ Error testing RTSP connection: {e}")
    return False

def main():
    """Main function for testing camera detection and RTSP streaming"""
    parser = argparse.ArgumentParser(description='Windows Camera Detection and RTSP Streaming')
    parser.add_argument('--detect-only', action='store_true', help='Only detect cameras, do not start streaming')
    parser.add_argument('--start-stream', type=int, help='Start RTSP stream for specific camera index')
    parser.add_argument('--port', type=int, default=8554, help='RTSP port (default: 8554)')
    parser.add_argument('--width', type=int, default=1920, help='Video width')
    parser.add_argument('--height', type=int, default=1080, help='Video height')
    parser.add_argument('--fps', type=int, default=30, help='Video FPS')
    parser.add_argument('--test-connection', type=str, help='Test RTSP connection to URL')

    args = parser.parse_args()

    # Check if running on Windows
    if platform.system() != 'Windows':
        logger.warning("This script is designed for Windows. Current platform: " + platform.system())

    # Test RTSP connection if requested
    if args.test_connection:
        return 0 if test_rtsp_connection(args.test_connection) else 1

    manager = WindowsCameraManager()

    try:
        # Detect cameras
        if not manager.detect_cameras():
            logger.error("No cameras detected. Exiting.")
            return 1

        cameras = manager.get_camera_info()
        print(f"\nDetected {len(cameras)} camera(s):")
        for cam in cameras:
            print(f"  Camera {cam['index']}: {cam['width']}x{cam['height']} @ {cam['fps']} FPS")

        if args.detect_only:
            return 0

        # Start streaming if requested
        if args.start_stream is not None:
            if args.start_stream >= len(cameras):
                logger.error(f"Camera index {args.start_stream} not available")
                return 1

            logger.info(f"Starting RTSP stream for camera {args.start_stream}...")
            if manager.start_rtsp_server(args.start_stream, args.port, args.width, args.height, args.fps):
                rtsp_url = f"rtsp://localhost:{args.port}/live"
                logger.info(f"RTSP stream started at: {rtsp_url}")
                logger.info("Testing connection in 3 seconds...")

                # Wait a bit for stream to start
                time.sleep(3)

                # Test the connection
                if test_rtsp_connection(rtsp_url):
                    logger.info("✓ RTSP streaming is working correctly!")
                else:
                    logger.error("✗ RTSP streaming failed - check FFmpeg and camera access")

                logger.info("Press Ctrl+C to stop...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Stopping RTSP stream...")
            else:
                logger.error("Failed to start RTSP stream")
                return 1

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    finally:
        manager.cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(main())

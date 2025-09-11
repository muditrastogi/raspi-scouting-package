#!/usr/bin/env python3
"""
Alternative RTSP server using OpenCV VideoWriter
This provides a fallback when FFmpeg DirectShow doesn't work
"""

import cv2
import time
import threading
import sys
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def start_opencv_rtsp_server(camera_index=0, rtsp_port=8554, width=1920, height=1080, fps=30):
    """Start RTSP server using OpenCV VideoWriter"""

    rtsp_url = f"rtsp://localhost:{rtsp_port}/live"
    logger.info(f"Starting OpenCV RTSP server on {rtsp_url}")

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

        # Try different codecs for RTSP output
        codec_attempts = [
            ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),
            ('XVID', cv2.VideoWriter_fourcc(*'XVID')),
            ('DIVX', cv2.VideoWriter_fourcc(*'DIVX')),
            ('H264', cv2.VideoWriter_fourcc(*'H264')),
        ]

        rtsp_writer = None
        successful_codec = None

        # Try each codec
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
                    logger.info(f"✅ RTSP stream started successfully with {codec_name} codec")
                    successful_codec = codec_name
                    break
                else:
                    logger.warning(f"❌ Failed to start RTSP with {codec_name} codec")
                    rtsp_writer = None

            except Exception as e:
                logger.warning(f"Error trying {codec_name} codec: {e}")
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

                # Write frame to RTSP stream
                rtsp_writer.write(frame)
                frame_count += 1

                # Log progress every 100 frames
                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    fps_actual = frame_count / elapsed
                    logger.info(".1f")

                # Small delay to prevent overwhelming
                time.sleep(0.01)

        except KeyboardInterrupt:
            logger.info("Stopping RTSP server...")

        finally:
            logger.info(f"RTSP server stopped. Total frames: {frame_count}")
            cap.release()
            if rtsp_writer:
                rtsp_writer.release()

    except Exception as e:
        logger.error(f"Error in RTSP server: {e}")
        return False

    return True

def test_opencv_rtsp_connection(rtsp_url):
    """Test RTSP connection using OpenCV"""
    logger.info(f"Testing RTSP connection to: {rtsp_url}")

    try:
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        if cap.isOpened():
            logger.info("✅ RTSP connection successful")

            # Try to read a few frames
            for i in range(3):
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    logger.info(f"✓ Frame {i+1}: {width}x{height}")
                else:
                    logger.warning(f"✗ Failed to read frame {i+1}")
                time.sleep(0.1)

            cap.release()
            return True
        else:
            logger.error("✗ Failed to open RTSP stream")
            cap.release()
            return False

    except Exception as e:
        logger.error(f"✗ Error testing RTSP connection: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='OpenCV RTSP Server for Windows')
    parser.add_argument('--camera', type=int, default=0, help='Camera index (default: 0)')
    parser.add_argument('--port', type=int, default=8554, help='RTSP port (default: 8554)')
    parser.add_argument('--width', type=int, default=1920, help='Video width')
    parser.add_argument('--height', type=int, default=1080, help='Video height')
    parser.add_argument('--fps', type=int, default=30, help='Video FPS')
    parser.add_argument('--test-only', action='store_true', help='Only test RTSP connection')

    args = parser.parse_args()

    if args.test_only:
        rtsp_url = f"rtsp://localhost:{args.port}/live"
        test_opencv_rtsp_connection(rtsp_url)
    else:
        success = start_opencv_rtsp_server(args.camera, args.port, args.width, args.height, args.fps)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

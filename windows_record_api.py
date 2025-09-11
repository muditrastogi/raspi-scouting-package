from flask import Flask, Response, request
import cv2
import threading
import time
import os
import argparse
from datetime import datetime
import logging
import platform
import getpass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables
USERNAME = getpass.getuser()
POSITION = "top"
REC_WIDTH = 1920
REC_HEIGHT = 1080
port = 0
CURRENT_DATE = datetime.today().strftime('%Y-%m-%d')
RECORDING_MODE = "frames"  # "frames" or "video"
print(f"Running as user: {USERNAME}")


class WindowsRTSPStream:
    """Windows-compatible RTSP stream recorder using OpenCV"""

    def __init__(self, rtsp_url="rtsp://192.168.1.20:8554/", resolution=(REC_WIDTH, REC_HEIGHT), mode="frames"):
        self.rtsp_url = rtsp_url
        self.resolution = resolution
        self.mode = mode  # "frames" or "video"
        self.active_recordings = {}  # Dictionary to track recordings by grid_name
        self.recording_lock = threading.Lock()

    def start_recording(self, counter, grid_name):
        """Start recording from RTSP stream"""
        with self.recording_lock:
            if grid_name in self.active_recordings:
                return f"Grid {grid_name} is already recording"

            print(f"Starting recording with counter: {counter}, grid: {grid_name}")

            # Create output directory
            if self.mode == "frames":
                save_dir = f"C:\\Users\\{USERNAME}\\Desktop\\scout-videos\\recordings_{CURRENT_DATE}\\{grid_name}-{POSITION}\\"
            else:  # video mode
                save_dir = f"C:\\Users\\{USERNAME}\\Desktop\\scout-videos\\recordings_{CURRENT_DATE}\\"

            os.makedirs(save_dir, exist_ok=True)

            # Clean up any existing malformed files
            if self.mode == "frames":
                import glob
                cleanup_pattern = os.path.join(save_dir, "*%04d.jpg")
                for file_path in glob.glob(cleanup_pattern):
                    try:
                        os.remove(file_path)
                        print(f"Removed malformed file: {file_path}")
                    except Exception as e:
                        print(f"Could not remove file {file_path}: {e}")

            start_time = datetime.now()
            start_time_str = start_time.strftime('%Y%m%d_%H%M%S')

            if self.mode == "frames":
                # Frame capture mode
                filename_prefix = (
                    f"ABC_GRID_{grid_name}_{counter}_recording_"
                    f"{start_time_str}_{POSITION}_frame_"
                )
                output_pattern = os.path.join(save_dir, filename_prefix + "%04d.jpg")
            else:
                # Video recording mode
                filename = (
                    f"ABC_GRID_{grid_name}_{counter}_recording_"
                    f"{start_time_str}_{POSITION}.mp4"
                )
                output_path = os.path.join(save_dir, filename)

            def record_frames():
                """Record frames from RTSP stream"""
                print(f"Recording frames every 0.7s to: {output_pattern}")

                # Open RTSP stream with OpenCV
                cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)

                if not cap.isOpened():
                    logger.error(f"Failed to open RTSP stream: {self.rtsp_url}")
                    return

                frame_count = 1
                last_capture_time = time.time()

                try:
                    while True:
                        ret, frame = cap.read()
                        if not ret:
                            logger.error("Failed to read frame from RTSP stream")
                            break

                        current_time = time.time()

                        # Capture frame every 0.7 seconds
                        if current_time - last_capture_time >= 0.7:
                            # Resize frame if needed
                            if frame.shape[1] != self.resolution[0] or frame.shape[0] != self.resolution[1]:
                                frame = cv2.resize(frame, self.resolution)

                            # Save frame
                            frame_filename = output_pattern % frame_count
                            cv2.imwrite(frame_filename, frame)

                            # Rename with timestamp
                            timestamp = int(current_time)
                            new_name = f"{os.path.splitext(frame_filename)[0]}_{timestamp}.jpg"
                            new_path = os.path.join(save_dir, os.path.basename(new_name))

                            try:
                                os.rename(frame_filename, new_path)
                                print(f"Renamed {os.path.basename(frame_filename)} → {os.path.basename(new_name)}")
                            except Exception as e:
                                print(f"Failed to rename {frame_filename}: {e}")

                            frame_count += 1
                            last_capture_time = current_time

                        # Check if recording should stop
                        with self.recording_lock:
                            if grid_name not in self.active_recordings:
                                break

                        time.sleep(0.1)  # Small delay

                    print(f"Frame recording completed for grid {grid_name}")

                except Exception as e:
                    print(f"Exception in frame recording thread for grid {grid_name}: {e}")
                finally:
                    cap.release()

                    with self.recording_lock:
                        if grid_name in self.active_recordings:
                            del self.active_recordings[grid_name]
                    print(f"Frame recording thread ended for grid {grid_name}")

            def record_video():
                """Record video from RTSP stream"""
                print(f"Recording video to: {output_path}")

                # Open RTSP stream
                cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)

                if not cap.isOpened():
                    logger.error(f"Failed to open RTSP stream: {self.rtsp_url}")
                    return

                # Get video properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps == 0 or fps > 60:  # Invalid FPS
                    fps = 30

                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                # Create video writer
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

                if not out.isOpened():
                    logger.error(f"Failed to create output video file: {output_path}")
                    cap.release()
                    return

                try:
                    while True:
                        ret, frame = cap.read()
                        if not ret:
                            logger.error("Failed to read frame from RTSP stream")
                            break

                        # Write frame to video
                        out.write(frame)

                        # Check if recording should stop
                        with self.recording_lock:
                            if grid_name not in self.active_recordings:
                                break

                        time.sleep(0.01)  # Small delay

                    print(f"Video recording completed for grid {grid_name}")

                except Exception as e:
                    print(f"Exception in video recording thread for grid {grid_name}: {e}")
                finally:
                    cap.release()
                    out.release()

                    with self.recording_lock:
                        if grid_name in self.active_recordings:
                            del self.active_recordings[grid_name]
                    print(f"Video recording thread ended for grid {grid_name}")

            # Create and start the appropriate recording thread
            if self.mode == "frames":
                recording_thread = threading.Thread(target=record_frames, daemon=True)
            else:
                recording_thread = threading.Thread(target=record_video, daemon=True)

            # Register the recording
            recording_info = {
                'thread': recording_thread,
                'output_path': output_pattern if self.mode == "frames" else output_path,
                'start_time': start_time,
                'mode': self.mode
            }

            self.active_recordings[grid_name] = recording_info
            recording_thread.start()

            return f"Started {self.mode} recording grid {grid_name}"

    def stop_recording(self, grid_name=None):
        """Stop recording for specific grid or all recordings"""
        with self.recording_lock:
            if grid_name is None:
                # Stop all recordings if no grid specified
                if not self.active_recordings:
                    return "No recordings are active"

                stopped_grids = []
                for grid in list(self.active_recordings.keys()):
                    result = self._stop_single_recording(grid)
                    stopped_grids.append(grid)

                return f"Stopped recording for grids: {', '.join(stopped_grids)}"
            else:
                # Stop specific grid recording
                if grid_name not in self.active_recordings:
                    return f"Grid {grid_name} is not currently recording"

                return self._stop_single_recording(grid_name)

    def _stop_single_recording(self, grid_name):
        """Helper method to stop a single recording"""
        if grid_name not in self.active_recordings:
            return f"Grid {grid_name} is not recording"

        recording_info = self.active_recordings[grid_name]
        thread = recording_info.get('thread')

        print(f"Stopping recording for grid: {grid_name}")

        # The thread will stop when we remove it from active_recordings
        # No need to terminate threads as they check the active_recordings dict

        # Remove from active recordings
        del self.active_recordings[grid_name]

        return f"Recording stopped for grid {grid_name}"

    def get_recording_status(self):
        """Get status of all active recordings"""
        with self.recording_lock:
            if not self.active_recordings:
                return "No active recordings"

            status_lines = []
            for grid_name, info in self.active_recordings.items():
                duration = datetime.now() - info['start_time']
                # Format duration nicely
                total_seconds = int(duration.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                mode = info.get('mode', 'unknown')
                output_path = info.get('output_path', 'unknown')

                if mode == "frames":
                    # Count existing frames
                    output_dir = os.path.dirname(output_path)
                    if os.path.exists(output_dir):
                        frame_count = len([f for f in os.listdir(output_dir) if f.endswith('.jpg')])
                        status_lines.append(f"Grid {grid_name}: Recording frames for {duration_str} ({frame_count} frames)")
                    else:
                        status_lines.append(f"Grid {grid_name}: Recording frames for {duration_str}")
                else:
                    status_lines.append(f"Grid {grid_name}: Recording video for {duration_str}")

            return "\n".join(status_lines)


# Initialize Flask app
app = Flask(__name__)
rtsp_stream = None  # Global RTSP stream instance


@app.route('/')
def index():
    """Simple status page"""
    rtsp_url = rtsp_stream.rtsp_url if rtsp_stream else "Not initialized"
    mode = rtsp_stream.mode if rtsp_stream else "Not set"
    return f"""
    <html>
    <head>
        <title>Windows RTSP Camera Recorder</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; text-align: center; }}
            .status {{ margin: 20px; padding: 20px; background-color: #f0f0f0; border-radius: 5px; }}
            .controls {{ margin: 20px 0; }}
            button {{ padding: 10px 20px; margin: 0 10px; font-size: 16px; cursor: pointer; }}
            input {{ padding: 8px; margin: 5px; }}
            .debug {{ margin: 20px; padding: 10px; background-color: #e0e0e0; border-radius: 5px; text-align: left; }}
            pre {{ white-space: pre-wrap; word-wrap: break-word; }}
        </style>
    </head>
    <body>
        <h1>Windows RTSP Camera Recorder</h1>
        <div class="status">
            <p>RTSP Stream: {rtsp_url}</p>
            <p>Mode: {mode}</p>
            <p>Recording Status: <span id="status">Not recording</span></p>
        </div>
        <div class="controls">
            <input type="text" id="gridName" placeholder="Grid Name (e.g., A1)" value="A1">
            <br><br>
            <button onclick="startRecording()">Start Recording</button>
            <button onclick="stopRecording()">Stop Recording (Specific Grid)</button>
            <button onclick="stopAllRecordings()">Stop All Recordings</button>
            <button onclick="getStatus()">Get Status</button>
            <button onclick="testConnection()">Test RTSP Connection</button>
        </div>
        <div class="debug">
            <h3>Debug Output:</h3>
            <pre id="debugOutput"></pre>
        </div>
        <script>
            function updateDebug(message) {{
                const debugOutput = document.getElementById('debugOutput');
                debugOutput.textContent = new Date().toLocaleTimeString() + ': ' + message + '\\n' + debugOutput.textContent;
            }}

            function startRecording() {{
                const gridName = document.getElementById('gridName').value || 'default';
                updateDebug('Starting recording for grid: ' + gridName);
                fetch('/record/start?counter=manual_' + Date.now() + '&grid_name=' + gridName)
                    .then(response => response.text())
                    .then(data => {{
                        document.getElementById('status').textContent = 'Recording';
                        updateDebug('Start response: ' + data);
                        alert(data);
                    }})
                    .catch(error => {{
                        updateDebug('Start error: ' + error);
                    }});
            }}

            function stopRecording() {{
                const gridName = document.getElementById('gridName').value || 'default';
                updateDebug('Stopping recording for grid: ' + gridName);
                fetch('/record/stop?grid_name=' + gridName)
                    .then(response => response.text())
                    .then(data => {{
                        updateDebug('Stop response: ' + data);
                        alert(data);
                    }})
                    .catch(error => {{
                        updateDebug('Stop error: ' + error);
                    }});
            }}

            function stopAllRecordings() {{
                updateDebug('Stopping all recordings');
                fetch('/record/stop')
                    .then(response => response.text())
                    .then(data => {{
                        document.getElementById('status').textContent = 'Not recording';
                        updateDebug('Stop all response: ' + data);
                        alert(data);
                    }})
                    .catch(error => {{
                        updateDebug('Stop all error: ' + error);
                    }});
            }}

            function getStatus() {{
                fetch('/status')
                    .then(response => response.text())
                    .then(data => {{
                        document.getElementById('status').textContent = data;
                        updateDebug('Status: ' + data);
                    }})
                    .catch(error => {{
                        updateDebug('Status error: ' + error);
                    }});
            }}

            function testConnection() {{
                updateDebug('Testing RTSP connection...');
                fetch('/test-connection')
                    .then(response => response.text())
                    .then(data => {{
                        updateDebug('Connection test result: ' + data);
                        alert(data);
                    }})
                    .catch(error => {{
                        updateDebug('Connection test error: ' + error);
                    }});
            }}

            // Auto-refresh status every 10 seconds
            setInterval(getStatus, 10000);
        </script>
    </body>
    </html>
    """


@app.route('/record/stop')
def stop():
    """Stop recording endpoint"""
    grid_name = request.args.get('grid_name')
    return rtsp_stream.stop_recording(grid_name)


@app.route('/record/start')
def record():
    """Start recording endpoint"""
    counter = request.args.get('counter', f'default_{int(time.time())}')
    grid_name = request.args.get('grid_name', 'default')
    counter = counter.replace(":", "-")  # Sanitize counter value
    return rtsp_stream.start_recording(counter, grid_name)


@app.route('/status')
def status():
    """Get recording status endpoint"""
    return rtsp_stream.get_recording_status()


@app.route('/test-connection')
def test_connection():
    """Test RTSP connection endpoint"""
    try:
        # Test RTSP connection using OpenCV
        cap = cv2.VideoCapture(rtsp_stream.rtsp_url, cv2.CAP_FFMPEG)

        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()

            if ret and frame is not None:
                return f"RTSP connection successful!\nStream: {rtsp_stream.rtsp_url}"
            else:
                return f"RTSP connection failed - cannot read frames!\nStream: {rtsp_stream.rtsp_url}"
        else:
            return f"RTSP connection failed - cannot open stream!\nStream: {rtsp_stream.rtsp_url}"

    except Exception as e:
        return f"RTSP connection test error: {str(e)}"


def main():
    """Main function"""
    global rtsp_stream, port, POSITION, RECORDING_MODE

    parser = argparse.ArgumentParser(description='Windows RTSP Camera Frame/Video Recorder')
    parser.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    parser.add_argument('--rtsp-url', type=str, default='rtsp://localhost:8554/live',
                       help='RTSP stream URL')
    parser.add_argument('--width', type=int, default=REC_WIDTH, help='Recording width')
    parser.add_argument('--height', type=int, default=REC_HEIGHT, help='Recording height')
    parser.add_argument('--mode', type=str, default='frames', choices=['frames', 'video'],
                       help='Recording mode: frames or video')

    args = parser.parse_args()

    port = args.port
    if port == 5000:
        POSITION = "bottom"
    elif port == 5001:
        POSITION = "middle"
    elif port == 5002:
        POSITION = "top"

    RECORDING_MODE = args.mode
    rtsp_stream = WindowsRTSPStream(
        rtsp_url=args.rtsp_url,
        resolution=(args.width, args.height),
        mode=args.mode
    )

    print("Starting Windows RTSP Recorder on port", args.port)
    print(f"RTSP URL: {args.rtsp_url}")
    print(f"Resolution: {args.width}x{args.height}")
    print(f"Position: {POSITION}")
    print(f"Mode: {args.mode}")

    try:
        app.run(host='0.0.0.0', port=args.port, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        if rtsp_stream:
            rtsp_stream.stop_recording()  # Stop all recordings
    except Exception as e:
        print(f"Error starting server: {e}")


if __name__ == '__main__':
    main()

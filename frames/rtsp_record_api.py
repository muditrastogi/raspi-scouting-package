from flask import Flask, Response, request
import threading
import subprocess
import time
import argparse
from datetime import datetime
import os
import getpass
import signal
import sys

# Global variables
USERNAME = getpass.getuser()
POSITION = "top"
REC_WIDTH = 1920
REC_HEIGHT = 1080
port = 0
CURRENT_DATE = datetime.today().strftime('%Y-%m-%d')
print(f"Running as user: {USERNAME}")


class RTSPStream:
    def __init__(self, rtsp_url="rtsp://192.168.1.20:8554/", resolution=(REC_WIDTH, REC_HEIGHT)):
        self.rtsp_url = rtsp_url
        self.resolution = resolution
        self.active_recordings = {}  # Dictionary to track recordings by grid_name
        self.recording_lock = threading.Lock()

    def start_recording(self, counter, grid_name):
        with self.recording_lock:
            if grid_name in self.active_recordings:
                return f"Grid {grid_name} is already recording"

            print(f"Starting recording with counter: {counter}, grid: {grid_name}")

            save_dir = f"/home/{USERNAME}/Desktop/scout-videos/recordings_{CURRENT_DATE}/{grid_name}/"
            os.makedirs(save_dir, exist_ok=True)
            
            # Clean up any existing files with the literal %04d pattern
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

            filename_prefix = (
                f"ABC_GRID_{grid_name}_{counter}_recording_"
                f"{start_time_str}_{POSITION}_frame_"
            )

            output_pattern = os.path.join(save_dir, filename_prefix + "%04d.jpg")

            def record():
                print(f"Recording images every 0.7s to: {output_pattern}")
                
                # More robust ffmpeg command with better error handling
                cmd = [
                    'ffmpeg',
                    '-y',  # Overwrite output files without asking
                    '-rtsp_transport', 'tcp',  # Use TCP for more reliable connection
                    '-i', self.rtsp_url,
                    '-vf', f'fps=1/0.7,scale={self.resolution[0]}:{self.resolution[1]}',  # 1 frame every 0.7s, scale to resolution
                    '-q:v', '2',         # High quality for JPEG
                    '-f', 'image2',      # Force image2 format
                    '-start_number', '1',  # Start numbering from 1
                    output_pattern
                ]
                
                print(f"FFmpeg command: {' '.join(cmd)}")
                
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )

                    # Store the process in the recording info
                    with self.recording_lock:
                        if grid_name in self.active_recordings:
                            self.active_recordings[grid_name]['process'] = process

                    # Monitor the process
                    while process.poll() is None:
                        # Check if we should stop
                        with self.recording_lock:
                            if grid_name not in self.active_recordings:
                                break
                        time.sleep(0.1)
                    
                    # Get the return code and output
                    stdout, stderr = process.communicate()
                    
                    if process.returncode != 0:
                        print(f"FFmpeg error for grid {grid_name}:")
                        print(f"Return code: {process.returncode}")
                        print(f"STDOUT: {stdout}")
                        print(f"STDERR: {stderr}")
                    else:
                        print(f"Recording completed successfully for grid {grid_name}")
                        
                except Exception as e:
                    print(f"Exception in recording thread for grid {grid_name}: {e}")
                finally:
                    # Clean up the recording entry when process ends
                    with self.recording_lock:
                        if grid_name in self.active_recordings:
                            del self.active_recordings[grid_name]
                    print(f"Recording thread ended for grid {grid_name}")

            recording_thread = threading.Thread(target=record, daemon=True)

            # Store recording information
            self.active_recordings[grid_name] = {
                'thread': recording_thread,
                'process': None,  # Will be set by the recording thread
                'output_path': output_pattern,
                'start_time': start_time
            }

            recording_thread.start()

            return f"Started recording grid {grid_name} to {output_pattern}"

    def stop_recording(self, grid_name=None):
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
        process = recording_info.get('process')

        print(f"Stopping recording for grid: {grid_name}")
        if process and process.poll() is None:  # Check if process is still running
            # Send SIGTERM first for graceful shutdown
            process.terminate()
            try:
                process.wait(timeout=5)  # Wait up to 5 seconds for graceful termination
                print(f"Process terminated gracefully for grid {grid_name}")
            except subprocess.TimeoutExpired:
                print(f"Process didn't terminate gracefully, killing for grid {grid_name}")
                process.kill()  # Force kill if it doesn't terminate gracefully
                process.wait()  # Wait for it to be killed

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
                
                # Check if images are being created
                output_dir = os.path.dirname(info['output_path'])
                if os.path.exists(output_dir):
                    image_count = len([f for f in os.listdir(output_dir) if f.endswith('.jpg')])
                    status_lines.append(f"Grid {grid_name}: Recording for {duration_str} ({image_count} images)")
                else:
                    status_lines.append(f"Grid {grid_name}: Recording for {duration_str} (directory not found)")

            return "\n".join(status_lines)


# Initialize Flask app
app = Flask(__name__)
rtsp_stream = None  # Global RTSP stream instance


@app.route('/')
def index():
    """Simple status page"""
    rtsp_url = rtsp_stream.rtsp_url if rtsp_stream else "Not initialized"
    return f"""
    <html>
    <head>
        <title>RTSP Camera Frame Recorder</title>
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
        <h1>RTSP Camera Frame Recorder</h1>
        <div class="status">
            <p>RTSP Stream: {rtsp_url}</p>
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
            <button onclick="cleanupFiles()">Cleanup Malformed Files</button>
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

            function cleanupFiles() {{
                updateDebug('Cleaning up malformed files...');
                fetch('/cleanup')
                    .then(response => response.text())
                    .then(data => {{
                        updateDebug('Cleanup result: ' + data);
                        alert(data);
                    }})
                    .catch(error => {{
                        updateDebug('Cleanup error: ' + error);
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
    """Stop recording endpoint - can stop specific grid or all recordings"""
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


@app.route('/cleanup')
def cleanup_files():
    """Cleanup malformed files with literal %04d pattern"""
    try:
        import glob
        base_dir = f"/home/{USERNAME}/Desktop/scout-videos/recordings_{CURRENT_DATE}/"
        
        if not os.path.exists(base_dir):
            return "No recordings directory found"
            
        cleanup_pattern = os.path.join(base_dir, "**/*%04d.jpg")
        files_removed = []
        
        for file_path in glob.glob(cleanup_pattern, recursive=True):
            try:
                os.remove(file_path)
                files_removed.append(os.path.basename(file_path))
            except Exception as e:
                print(f"Could not remove file {file_path}: {e}")
        
        if files_removed:
            return f"Removed {len(files_removed)} malformed files: {', '.join(files_removed)}"
        else:
            return "No malformed files found"
            
    except Exception as e:
        return f"Cleanup error: {str(e)}"


@app.route('/test-connection')
def test_connection():
    """Test RTSP connection endpoint"""
    try:
        # Test if we can connect to the RTSP stream
        test_cmd = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-i', rtsp_stream.rtsp_url,
            '-t', '5',  # Test for 5 seconds
            '-f', 'null',
            '-'
        ]
        
        process = subprocess.Popen(
            test_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        stdout, stderr = process.communicate(timeout=15)
        
        if process.returncode == 0:
            return f"RTSP connection successful!\nStream: {rtsp_stream.rtsp_url}"
        else:
            return f"RTSP connection failed!\nReturn code: {process.returncode}\nError: {stderr}"
            
    except subprocess.TimeoutExpired:
        process.kill()
        return "RTSP connection test timed out"
    except Exception as e:
        return f"RTSP connection test error: {str(e)}"


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print("\nShutting down gracefully...")
    if rtsp_stream:
        rtsp_stream.stop_recording()  # Stop all recordings
    sys.exit(0)


def main():
    global rtsp_stream, port, POSITION

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(description='RTSP Camera Frame Recorder')
    parser.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    parser.add_argument('--rtsp-url', type=str, default='rtsp://192.168.1.20:8554/unicast', help='RTSP stream URL')
    parser.add_argument('--width', type=int, default=REC_WIDTH, help='Recording width (default: 1920)')
    parser.add_argument('--height', type=int, default=REC_HEIGHT, help='Recording height (default: 1080)')
    args = parser.parse_args()

    port = args.port
    if port == 5000:
        POSITION = "bottom"
    elif port == 5001:
        POSITION = "middle"
    elif port == 5002:
        POSITION = "top"

    rtsp_stream = RTSPStream(rtsp_url=args.rtsp_url, resolution=(args.width, args.height))

    print(f"Starting RTSP Frame Recorder on port {args.port}")
    print(f"RTSP URL: {args.rtsp_url}")
    print(f"Resolution: {args.width}x{args.height}")
    print(f"Position: {POSITION}")

    try:
        app.run(host='0.0.0.0', port=args.port, threaded=True)
    finally:
        if rtsp_stream:
            rtsp_stream.stop_recording()  # This will stop all recordings


if __name__ == '__main__':
    main()
from flask import Flask, Response, request
import threading
import subprocess
import time
import argparse
from datetime import datetime
import os
import getpass

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

            save_dir = f"/home/{USERNAME}/Desktop/scout-videos/recordings_{CURRENT_DATE}/{grid_name}-{POSITION}/"
            os.makedirs(save_dir, exist_ok=True)

            start_time = datetime.now()
            start_time_str = start_time.strftime('%Y%m%d_%H%M%S')

            filename_prefix = (
                f"ABC_GRID_{grid_name}_{counter}_recording_"
                f"{start_time_str}_{POSITION}_frame_"
            )

            output_pattern = os.path.join(save_dir, filename_prefix + "%04d.jpg")

            def record():
                print(f"Recording images every 0.7s to: {output_pattern}")
                process = subprocess.Popen([
                    'ffmpeg',
                    '-i', self.rtsp_url,
                    '-vf', 'fps=~1.43',          # ~1 frame every 0.7s
                    '-q:v', '2',                # quality for JPEG
                    output_pattern
                ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

                # Store the process in the recording info
                with self.recording_lock:
                    if grid_name in self.active_recordings:
                        self.active_recordings[grid_name]['process'] = process

                process.wait()
                print(f"Recording process ended: {output_pattern}")
                
                # Clean up the recording entry when process ends
                with self.recording_lock:
                    if grid_name in self.active_recordings:
                        del self.active_recordings[grid_name]

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
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)  # Wait up to 5 seconds for graceful termination
            except subprocess.TimeoutExpired:
                process.kill()  # Force kill if it doesn't terminate gracefully
        
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
                status_lines.append(f"Grid {grid_name}: Recording for {duration}")
            
            return "\n".join(status_lines)


# Initialize Flask app
app = Flask(__name__)
rtsp_stream = None  # Global RTSP stream instance


@app.route('/')
def index():
    """Simple status page"""
    return """
    <html>
    <head>
        <title>RTSP Camera Recorder</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; text-align: center; }
            .status { margin: 20px; padding: 20px; background-color: #f0f0f0; border-radius: 5px; }
            .controls { margin: 20px 0; }
            button { padding: 10px 20px; margin: 0 10px; font-size: 16px; cursor: pointer; }
            input { padding: 8px; margin: 5px; }
        </style>
    </head>
    <body>
        <h1>RTSP Camera Recorder</h1>
        <div class="status">
            <p>RTSP Stream: rtsp://192.168.1.20:8554/</p>
            <p>Recording Status: <span id="status">Not recording</span></p>
        </div>
        <div class="controls">
            <input type="text" id="gridName" placeholder="Grid Name (e.g., A1)" value="A1">
            <br><br>
            <button onclick="startRecording()">Start Recording</button>
            <button onclick="stopRecording()">Stop Recording (Specific Grid)</button>
            <button onclick="stopAllRecordings()">Stop All Recordings</button>
            <button onclick="getStatus()">Get Status</button>
        </div>
        <script>
            function startRecording() {
                const gridName = document.getElementById('gridName').value || 'default';
                fetch('/record/start?counter=manual_' + Date.now() + '&grid_name=' + gridName)
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById('status').textContent = 'Recording';
                        console.log(data);
                        alert(data);
                    });
            }

            function stopRecording() {
                const gridName = document.getElementById('gridName').value || 'default';
                fetch('/record/stop?grid_name=' + gridName)
                    .then(response => response.text())
                    .then(data => {
                        console.log(data);
                        alert(data);
                    });
            }

            function stopAllRecordings() {
                fetch('/record/stop')
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById('status').textContent = 'Not recording';
                        console.log(data);
                        alert(data);
                    });
            }

            function getStatus() {
                fetch('/status')
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById('status').textContent = data;
                        console.log(data);
                    });
            }
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


def main():
    global rtsp_stream, port, POSITION

    parser = argparse.ArgumentParser(description='RTSP Camera Recorder')
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

    try:
        print(f"Starting server on port {args.port}")
        app.run(host='0.0.0.0', port=args.port, threaded=True)
    finally:
        if rtsp_stream:
            rtsp_stream.stop_recording()  # This will stop all recordings


if __name__ == '__main__':
    main()

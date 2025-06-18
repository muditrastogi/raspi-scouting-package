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
print(f"Running as user: {USERNAME}")

class RTSPStream:
    def __init__(self, rtsp_url="rtsp://192.168.1.20:8554/", resolution=(REC_WIDTH, REC_HEIGHT)):
        self.rtsp_url = rtsp_url
        self.resolution = resolution
        self.is_recording = False
        self.process = None
        self.recording_thread = None

    def start_recording(self, counter, grid_name):
        if self.is_recording:
            return "Already recording"
        
        print(f"Starting recording with counter: {counter}, {grid_name}")
        
        save_dir = f"/home/{USERNAME}/Desktop/scout-videos/camera_{POSITION}/{counter}/{grid_name}/"
        os.makedirs(save_dir, exist_ok=True)

        start_time = datetime.now()
        filename = f"ABC_{counter}_recording_{start_time.strftime('%Y%m%d_%H%M%S')}_{POSITION}.mp4"
        output_path = os.path.join(save_dir, filename)

        def record():
            print(f"Recording started: {output_path}")
            self.process = subprocess.Popen([
                'ffmpeg',
                '-i', self.rtsp_url,
                '-c', 'copy',
                '-f', 'mp4',
                output_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

            self.process.wait()
            print(f"Recording process ended: {output_path}")

        # Start recording in a new thread
        self.recording_thread = threading.Thread(target=record, daemon=True)
        self.recording_thread.start()
        
        self.is_recording = True
        return f"Started recording to {output_path}"

    def stop_recording(self):
        if not self.is_recording:
            return "Not recording"
        
        print("Stopping recording")
        if self.process:
            self.process.terminate()
            self.process = None
        
        self.is_recording = False
        return "Recording stopped"

# Initialize Flask app
app = Flask(__name__)

# Global RTSP stream instance
rtsp_stream = None

@app.route('/')
def index():
    """Simple status page"""
    return """
    <html>
    <head>
        <title>RTSP Camera Recorder</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px;
                text-align: center;
            }
            .status {
                margin: 20px;
                padding: 20px;
                background-color: #f0f0f0;
                border-radius: 5px;
            }
            .controls {
                margin: 20px 0;
            }
            button {
                padding: 10px 20px;
                margin: 0 10px;
                font-size: 16px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h1>RTSP Camera Recorder</h1>
        <div class="status">
            <p>RTSP Stream: rtsp://192.168.1.20:8554/</p>
            <p>Recording Status: <span id="status">Not recording</span></p>
        </div>
        <div class="controls">
            <button onclick="startRecording()">Start Recording</button>
            <button onclick="stopRecording()">Stop Recording</button>
        </div>
        
        <script>
            function startRecording() {
                fetch('/record/start?counter=manual_' + Date.now())
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById('status').textContent = 'Recording';
                        console.log(data);
                    });
            }
            
            function stopRecording() {
                fetch('/record/stop')
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById('status').textContent = 'Not recording';
                        console.log(data);
                    });
            }
        </script>
    </body>
    </html>
    """

@app.route('/record/stop')
def stop():
    """Stop recording endpoint"""
    return rtsp_stream.stop_recording()

@app.route('/record/start')
def record():
    """Start recording endpoint"""
    counter = request.args.get('counter', f'default_{int(time.time())}')
    grid_name = request.args.get('grid_name', 'default')
    counter = counter.replace(":", "-")  # Sanitize counter value
    return rtsp_stream.start_recording(counter,grid_name)

def main():
    global rtsp_stream
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='RTSP Camera Recorder')
    parser.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    parser.add_argument('--rtsp-url', type=str, default='rtsp://192.168.1.20:8554/unicast', help='RTSP stream URL')
    parser.add_argument('--width', type=int, default=REC_WIDTH, help='Recording width (default: 1920)')
    parser.add_argument('--height', type=int, default=REC_HEIGHT, help='Recording height (default: 1080)')
    args = parser.parse_args()
    global port
    global POSITION
    port = args.port
    if port == 5000:
      POSITION = "bottom"
    elif port == 5001:
      POSITION = "middle"
    elif port == 5002:
      POSITION = "top"
    
    # Initialize RTSP stream
    rtsp_stream = RTSPStream(rtsp_url=args.rtsp_url, resolution=(args.width, args.height))
    
    # Start Flask app
    try:
        print(f"Starting server on port {args.port}")
        app.run(host='0.0.0.0', port=args.port, threaded=True)
    finally:
        if rtsp_stream:
            rtsp_stream.stop_recording()

if __name__ == '__main__':
    main()

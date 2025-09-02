#!/usr/bin/env python3
"""
Windows RTSP Recording API
A Windows-compatible version of rtsp_record_api.py for the Raspberry Pi Scouting Package
"""

from flask import Flask, Response, request
import threading
import subprocess
import time
import argparse
from datetime import datetime
import os
import getpass
from pathlib import Path
import cv2
import json

# Global variables
USERNAME = getpass.getuser()
POSITION = "top"
REC_WIDTH = 1920
REC_HEIGHT = 1080
port = 0
CURRENT_DATE = datetime.today().strftime('%Y-%m-%d')
print(f"Running as user: {USERNAME}")

class WindowsRTSPStream:
    def __init__(self, rtsp_url="rtsp://localhost:8554/camera0", resolution=(REC_WIDTH, REC_HEIGHT)):
        self.rtsp_url = rtsp_url
        self.resolution = resolution
        self.active_recordings = {}  # Dictionary to track recordings by grid_name
        self.recording_lock = threading.Lock()
        
        # Windows-specific paths
        self.video_dir = Path.home() / "Desktop" / "scout-videos" / f"recordings_{CURRENT_DATE}"
        self.video_dir.mkdir(parents=True, exist_ok=True)

    def start_recording(self, counter, grid_name):
        with self.recording_lock:
            if grid_name in self.active_recordings:
                return f"Grid {grid_name} is already recording"

            print(f"Starting recording with counter: {counter}, grid: {grid_name}")

            start_time = datetime.now()
            filename = (
                f"ABC_GRID_{grid_name}_{counter}_recording_"
                f"{start_time.strftime('%Y%m%d_%H%M%S')}_{POSITION}.mp4"
            )
            output_path = self.video_dir / filename

            def record():
                print(f"Recording started: {output_path}")
                
                # Use FFmpeg for Windows recording
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-i', self.rtsp_url,
                    '-c:v', 'libx264',
                    '-preset', 'ultrafast',
                    '-crf', '23',
                    '-f', 'mp4',
                    str(output_path)
                ]
                
                try:
                    process = subprocess.Popen(
                        ffmpeg_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )

                    # Store the process in the recording info
                    with self.recording_lock:
                        if grid_name in self.active_recordings:
                            self.active_recordings[grid_name]['process'] = process

                    process.wait()
                    print(f"Recording process ended: {output_path}")
                    
                except Exception as e:
                    print(f"Error during recording: {e}")
                finally:
                    # Clean up the recording entry when process ends
                    with self.recording_lock:
                        if grid_name in self.active_recordings:
                            del self.active_recordings[grid_name]

            recording_thread = threading.Thread(target=record, daemon=True)
            
            # Store recording information
            self.active_recordings[grid_name] = {
                'thread': recording_thread,
                'process': None,  # Will be set by the recording thread
                'output_path': output_path,
                'start_time': start_time
            }
            
            recording_thread.start()

            return f"Started recording grid {grid_name} to {output_path}"

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
        """Stop recording for a specific grid"""
        recording_info = self.active_recordings[grid_name]
        
        if recording_info['process'] and recording_info['process'].poll() is None:
            try:
                # Terminate the FFmpeg process
                recording_info['process'].terminate()
                recording_info['process'].wait(timeout=5)
                print(f"Stopped recording for grid {grid_name}")
            except subprocess.TimeoutExpired:
                # Force kill if termination takes too long
                recording_info['process'].kill()
                print(f"Force killed recording for grid {grid_name}")
            except Exception as e:
                print(f"Error stopping recording for grid {grid_name}: {e}")
        
        # Remove from active recordings
        del self.active_recordings[grid_name]
        return f"Stopped recording for grid {grid_name}"

    def get_recording_status(self):
        """Get status of all active recordings"""
        with self.recording_lock:
            status = []
            for grid_name, info in self.active_recordings.items():
                duration = datetime.now() - info['start_time']
                status.append({
                    'grid': grid_name,
                    'duration': str(duration).split('.')[0],  # Remove microseconds
                    'output_path': str(info['output_path']),
                    'is_active': info['process'] and info['process'].poll() is None
                })
            return status

# Create Flask app
app = Flask(__name__)

# Global RTSP stream instance
rtsp_stream = None

@app.route('/start_record', methods=['POST'])
def start_record():
    """Start recording for a specific grid"""
    try:
        data = request.get_json()
        if not data:
            return {'error': 'No JSON data provided'}, 400
        
        counter = data.get('counter', 1)
        grid_name = data.get('grid_name', 'default')
        
        if not grid_name:
            return {'error': 'grid_name is required'}, 400
        
        result = rtsp_stream.start_recording(counter, grid_name)
        return {'message': result, 'status': 'success'}
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/stop_record', methods=['POST'])
def stop_record():
    """Stop recording for a specific grid or all grids"""
    try:
        data = request.get_json() or {}
        grid_name = data.get('grid_name')  # None means stop all
        
        result = rtsp_stream.stop_recording(grid_name)
        return {'message': result, 'status': 'success'}
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get current recording status"""
    try:
        status = rtsp_stream.get_recording_status()
        return {
            'status': 'success',
            'active_recordings': status,
            'total_recordings': len(status)
        }
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}

def main():
    global rtsp_stream, port
    
    parser = argparse.ArgumentParser(description='Windows RTSP Recording API')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the API on')
    parser.add_argument('--rtsp-url', type=str, default='rtsp://localhost:8554/camera0', 
                       help='RTSP URL to record from')
    parser.add_argument('--resolution', type=str, default='1920x1080', 
                       help='Recording resolution (WxH)')
    parser.add_argument('--position', type=str, default='top', 
                       help='Camera position (top, middle, bottom)')
    
    args = parser.parse_args()
    port = args.port
    POSITION = args.position
    
    # Parse resolution
    try:
        width, height = args.resolution.split('x')
        REC_WIDTH, REC_HEIGHT = int(width), int(height)
    except ValueError:
        print(f"Invalid resolution format: {args.resolution}. Using default: 1920x1080")
        REC_WIDTH, REC_HEIGHT = 1920, 1080
    
    # Initialize RTSP stream
    rtsp_stream = WindowsRTSPStream(
        rtsp_url=args.rtsp_url,
        resolution=(REC_WIDTH, REC_HEIGHT)
    )
    
    print(f"Starting Windows RTSP Recording API on port {port}")
    print(f"RTSP URL: {args.rtsp_url}")
    print(f"Resolution: {REC_WIDTH}x{REC_HEIGHT}")
    print(f"Position: {POSITION}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

if __name__ == '__main__':
    main()

import tkinter as tk
from tkinter import messagebox
import cv2
import threading
import time
import os
from datetime import datetime
import getpass
import logging
import subprocess
from PIL import Image, ImageTk
from system_performance_logger import SystemPerformanceLogger

# Configure logging to reduce NVIDIA warnings
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Global camera synchronization to prevent NVIDIA driver conflicts
camera_lock = threading.Lock()
camera_initialization_lock = threading.Lock()
active_cameras = set()
camera_delay = 1.5  # Delay between camera initializations to avoid conflicts

# Configuration management
def read_config_file():
    """Read configuration from config.txt"""
    config = {
        # Default values for recording configuration
        'recording_mode': 'image',  # 'image' or 'video'
        'frame_interval': '10',     # Save every Nth frame for images
        'image_format': 'png'       # Image format: 'png', 'jpg', etc.
    }
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, "config.txt")
    
    if not os.path.exists(config_file):
        print(f"⚠️ Config file not found: {config_file}")
        print(f"📝 Using default recording mode: {config['recording_mode']}")
        return config
    
    try:
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        print(f"✅ Configuration loaded from {config_file}")
        print(f"📝 Recording mode: {config.get('recording_mode', 'image')}")
        if config.get('recording_mode', 'image') == 'image':
            print(f"📸 Frame interval: {config.get('frame_interval', '10')}")
            print(f"🖼️ Image format: {config.get('image_format', 'png')}")
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
    
    return config

def get_usb_camera_device_mapping():
    """Get mapping of USB camera device IDs to camera indices using wmic"""
    try:
        cmd = ['wmic', 'path', 'Win32_PnPEntity', 'where', 'Description like "%Camera%" AND DeviceID like "USB%"', 'get', 'DeviceID']
        cmd = [
            'wmic', 'path', 'Win32_PnPEntity',
            'where', '(Name like "%B525%" OR Name like "%Logi%") AND PNPClass="MEDIA"',
            'get', 'DeviceID,Name,PNPClass'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode != 0:
            print(f"❌ wmic command failed: {result.stderr}")
            return {}
        
        usb_devices = []
        lines = result.stdout.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Skip header and empty lines
            if line and not line.startswith('DeviceID') and not line.startswith('---'):
                device_id = line.strip()
                if device_id and device_id.startswith('USB\\'):
                    usb_devices.append(device_id)
        
        print(f"🔍 Found {len(usb_devices)} USB camera device(s)")
        for i, device_id in enumerate(usb_devices):
            print(f"  USB Camera {i}: {device_id}")
        
        # Now map these USB devices to OpenCV camera indices
        device_to_index = {}
        
        # Test OpenCV cameras to find which indices correspond to USB cameras
        available_opencv_cameras = []
        for cv_index in range(10):  # Test first 10 camera indices
            try:
                cap = cv2.VideoCapture(cv_index, cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        available_opencv_cameras.append(cv_index)
                        print(f"  📷 OpenCV Camera {cv_index}: Available")
                cap.release()
            except:
                pass
        
        # Map USB devices to OpenCV indices (assumption: same order)
        # This is the best we can do without more sophisticated device matching
        for i, device_id in enumerate(usb_devices):
            if i < len(available_opencv_cameras):
                opencv_index = available_opencv_cameras[i]
                device_to_index[device_id] = opencv_index
                print(f"  🔗 Mapped USB device {device_id[:30]}... -> OpenCV index {opencv_index}")
        
        return device_to_index
        
    except Exception as e:
        print(f"❌ Error getting USB camera device mapping: {e}")
        return {}

def get_ordered_camera_indices():
    """Get camera indices in the order specified by config.txt (USB cameras only)"""
    config = read_config_file()
    device_mapping = get_usb_camera_device_mapping()
    
    # Get configured device IDs for each position
    positions = ['bottom', 'middle', 'top']
    ordered_indices = []
    used_device_ids = set()
    
    print("🔍 Mapping USB cameras based on config.txt device IDs...")
    
    # Check if we have any configured device IDs
    configured_devices = []
    for position in positions:
        device_id_key = f"{position}camera_deviceid"
        configured_device_id = config.get(device_id_key, "").strip()
        if configured_device_id:
            configured_devices.append((position, configured_device_id))
    
    if not configured_devices:
        print("⚠️ No camera device IDs configured in config.txt")
        print("💡 Run 'windows_configure_cameras.bat' to configure camera positions")
        return []
    
    # Handle duplicate device IDs (same camera model)
    device_id_counts = {}
    for _, device_id in configured_devices:
        device_id_counts[device_id] = device_id_counts.get(device_id, 0) + 1
    
    # Track which instance of each device ID we're using
    device_id_usage = {}
    
    for position, configured_device_id in configured_devices:
        print(f"\n🔍 Looking for {position} camera: {configured_device_id}")
        
        # Check if this device ID exists among USB cameras
        matching_indices = []
        for detected_device_id, opencv_index in device_mapping.items():
            if configured_device_id == detected_device_id:
                matching_indices.append(opencv_index)
        
        if not matching_indices:
            print(f"❌ {position.title()} camera: Device ID not found among USB cameras")
            print(f"   Configured: {configured_device_id}")
            print("   Available USB cameras:")
            for device_id in device_mapping.keys():
                print(f"     {device_id}")
            continue
        
        # Handle multiple cameras with same device ID
        if len(matching_indices) > 1:
            # Use the next available instance of this device ID
            usage_count = device_id_usage.get(configured_device_id, 0)
            if usage_count < len(matching_indices):
                selected_index = matching_indices[usage_count]
                device_id_usage[configured_device_id] = usage_count + 1
                print(f"✅ {position.title()} camera: Using instance {usage_count + 1} of {len(matching_indices)} -> Camera {selected_index}")
            else:
                print(f"⚠️ {position.title()} camera: All instances of this device ID already used")
                continue
        else:
            selected_index = matching_indices[0]
            print(f"✅ {position.title()} camera: Found unique device -> Camera {selected_index}")
        
        # Check if this camera index is already used
        if selected_index in ordered_indices:
            print(f"⚠️ Camera {selected_index} already assigned, skipping duplicate")
            continue
        
        ordered_indices.append(selected_index)
    
    # Only use cameras that are explicitly configured and found
    if len(ordered_indices) == 0:
        print("❌ No configured cameras found among USB devices!")
        print("💡 Please run 'windows_configure_cameras.bat' to configure camera positions")
        return []
    elif len(ordered_indices) < 3:
        print(f"⚠️ Only {len(ordered_indices)} of 3 configured cameras found")
        print("💡 Check camera connections and device IDs in config.txt")
    
    print(f"\n🎬 Using {len(ordered_indices)} configured USB camera(s): {ordered_indices}")
    
    # Verify these cameras actually work with OpenCV
    working_indices = []
    for index in ordered_indices:
        try:
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    working_indices.append(index)
                    print(f"✅ Camera {index}: Working")
                else:
                    print(f"❌ Camera {index}: Cannot read frames")
            else:
                print(f"❌ Camera {index}: Cannot open")
            cap.release()
        except Exception as e:
            print(f"❌ Camera {index}: Error - {e}")
    
    if len(working_indices) != len(ordered_indices):
        print(f"⚠️ {len(ordered_indices) - len(working_indices)} camera(s) failed verification")
    
    return working_indices

class SimpleStream:
    """Simple direct camera streaming and recording without RTSP"""

    def __init__(self, parent, camera_index, stream_index, width=640, height=480):
        self.camera_index = camera_index
        self.stream_index = stream_index
        self.width = width
        self.height = height
        self.stream_running = False
        self.recording = False
        self.app_reference = None

        # Camera naming
        labels = ["bottom", "middle", "top"]
        names = ["first", "second", "third"]
        self.camera_label = labels[stream_index] if stream_index < len(labels) else f"camera_{stream_index + 1}"
        self.camera_name = names[stream_index] if stream_index < len(names) else f"camera_{stream_index + 1}"

        # OpenCV variables
        self.cap = None
        self.stream_thread = None
        self.recorder = None
        self.stop_event = threading.Event()

        # Recording variables
        self.recording_thread = None
        self.recording_filename = None
        
        # Image recording variables
        self.image_frame_counter = 0
        self.saved_image_count = 0
        self.recording_config = read_config_file()

        # Main container
        self.container = tk.Frame(parent, bg='lightgray', relief='solid', bd=1)
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(1, weight=1)  # Video expands
        self.container.rowconfigure(2, weight=0)  # Label row

        # Video frame
        self.video_frame = tk.Frame(self.container, bg='black', highlightbackground="gray", highlightthickness=1)
        self.video_frame.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        self.video_frame.columnconfigure(0, weight=1)
        self.video_frame.rowconfigure(0, weight=1)

        # Canvas for OpenCV display
        self.canvas = tk.Canvas(self.video_frame, bg='black', width=self.width, height=self.height)
        self.canvas.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")

        # Label and optional button
        self._create_label_and_button()

    def _create_label_and_button(self):
        """Create label and (for third camera) button in a horizontal layout."""
        if self.stream_index == 2:  # Third camera: label + button side by side
            container = tk.Frame(self.container, bg='lightgray')
            container.grid(row=2, column=0, padx=6, pady=4, sticky="ew")
            container.columnconfigure(0, weight=3)  # Label takes more space
            container.columnconfigure(1, weight=1)  # Button takes less

            # Label
            self.label = tk.Label(
                container,
                text=f"{self.camera_label} ({self.camera_name})",
                font=('Arial', 11, 'bold'),
                bg='lightgray',
                anchor='w'
            )
            self.label.grid(row=0, column=0, sticky="ew", padx=(4, 2))

            # Button
            self.individual_button = tk.Button(
                container,
                text="Start",
                command=self.toggle_individual_stream,
                bg='#f0f0f0',
                fg='black',
                relief='raised',
                bd=2,
                font=('Arial', 9, 'bold'),
                height=1
            )
            self.individual_button.grid(row=0, column=1, sticky="e", padx=(2, 4))
        else:
            # Regular label below video
            self.label = tk.Label(
                self.container,
                text=f"{self.camera_label} ({self.camera_name})",
                font=('Arial', 12, 'bold'),
                bg='lightgray',
                pady=4
            )
            self.label.grid(row=2, column=0, padx=6, pady=2, sticky="ew")
            self.individual_button = None

    def test_camera_access(self, camera_index):
        """Test if camera can be opened with different methods"""
        print(f"Testing camera {camera_index} access...")

        # Acquire lock to prevent conflicts during camera testing
        with camera_lock:
            try:
                # Try different OpenCV backend combinations
                backends = [
                    (cv2.CAP_DSHOW, "DirectShow"),
                    (cv2.CAP_MSMF, "Media Foundation"),
                    (cv2.CAP_VFW, "Video for Windows"),
                    (cv2.CAP_ANY, "Default")
                ]

                for backend, name in backends:
                    try:
                        print(f"  Trying {name} backend...")
                        cap = cv2.VideoCapture(camera_index, backend)

                        if cap.isOpened():
                            ret, frame = cap.read()
                            if ret and frame is not None:
                                height, width = frame.shape[:2]
                                print(f"  ✅ {name} backend works: {width}x{height}")
                                cap.release()
                                return backend
                            else:
                                print(f"  ⚠️ {name} backend opened but no frames")
                        else:
                            print(f"  ❌ {name} backend failed to open")

                        cap.release()

                    except Exception as e:
                        print(f"  ❌ {name} backend error: {e}")

                return None
            finally:
                # Small delay to prevent rapid camera access
                time.sleep(0.5)

    def start_stream(self):
        """Start the video stream using OpenCV with proper threading and NVIDIA conflict prevention"""
        if self.stream_running:
            return

        # Check if camera is already in use
        if self.camera_index in active_cameras:
            print(f"⚠️ Camera {self.camera_index} already in use")
            return

        self.stream_running = True
        self.stop_event.clear()

        def stream_worker():
            try:
                # Acquire camera initialization lock to prevent concurrent access
                with camera_initialization_lock:
                    print(f"🔒 Initializing camera {self.camera_index}...")

                    # Test camera access with different backends
                    working_backend = self.test_camera_access(self.camera_index)

                    if working_backend is None:
                        print(f"❌ No working backend found for camera {self.camera_index}")
                        messagebox.showerror("Camera Error",
                                           f"Cannot access camera {self.camera_index}\n"
                                           "Try:\n"
                                           "1. Different USB port\n"
                                           "2. Update camera drivers\n"
                                           "3. Restart computer\n"
                                           "4. Check camera in Device Manager")
                        self.stream_running = False
                        return

                    # Add camera to active set
                    active_cameras.add(self.camera_index)

                    # Delay to prevent NVIDIA driver conflicts
                    print(f"⏳ Waiting {camera_delay}s before opening camera...")
                    time.sleep(camera_delay)

                # Open camera with working backend using lock
                with camera_lock:
                    print(f"📷 Opening camera {self.camera_index} with {working_backend}...")
                    self.cap = cv2.VideoCapture(self.camera_index, working_backend)

                    if not self.cap.isOpened():
                        messagebox.showerror("Camera Error", f"Failed to open camera {self.camera_index}")
                        active_cameras.discard(self.camera_index)
                        self.stream_running = False
                        return

                    # Set camera properties if possible
                    try:
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        self.cap.set(cv2.CAP_PROP_FPS, 30)
                    except:
                        pass  # Some cameras don't support property setting

                print(f"✅ Started stream for {self.camera_label} ({self.camera_name})")

                # Test first frame
                ret, test_frame = self.cap.read()
                if not ret or test_frame is None:
                    print(f"❌ Failed to read first frame from {self.camera_label}")
                    with camera_lock:
                        if self.cap:
                            self.cap.release()
                    active_cameras.discard(self.camera_index)
                    self.stream_running = False
                    return

                frame_count = 0
                start_time = time.time()

                while self.stream_running and not self.stop_event.is_set():
                    # Use lock for camera read operations
                    with camera_lock:
                        ret, frame = self.cap.read()
                        if not ret or frame is None:
                            print(f"❌ Failed to read frame from {self.camera_label}")
                            break

                    # Convert BGR to RGB for Tkinter
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Resize frame to fit canvas
                    frame_resized = cv2.resize(frame_rgb, (self.width, self.height))

                    # Convert to PhotoImage for Tkinter
                    img = Image.fromarray(frame_resized)
                    photo = ImageTk.PhotoImage(image=img)

                    # Update canvas on main thread
                    def update_canvas():
                        if self.stream_running:  # Check again in case it stopped
                            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                            self.canvas.photo = photo  # Keep reference

                    self.canvas.after(0, update_canvas)

                    frame_count += 1

                    # Log FPS every 100 frames
                    if frame_count % 100 == 0:
                        elapsed = time.time() - start_time
                        fps = frame_count / elapsed
                        print(".1f")
                    # Small delay to prevent overwhelming the GUI
                    time.sleep(0.03)  # ~30 FPS

            except Exception as e:
                print(f"❌ Error in stream thread for {self.camera_label}: {e}")
            finally:
                # Cleanup with proper locking
                with camera_lock:
                    if hasattr(self, 'cap') and self.cap:
                        self.cap.release()
                active_cameras.discard(self.camera_index)
                self.stream_running = False
                print(f"🛑 Stream stopped for {self.camera_label}")

        self.stream_thread = threading.Thread(target=stream_worker, daemon=True)
        self.stream_thread.start()

    def stop_stream(self):
        """Stop the video stream with proper locking"""
        if not self.stream_running:
            return

        print(f"🛑 Stopping stream for {self.camera_label} ({self.camera_name})")
        self.stream_running = False
        self.stop_event.set()

        # Use lock for camera release to prevent conflicts
        with camera_lock:
            if hasattr(self, 'cap') and self.cap:
                self.cap.release()

        # Remove from active cameras
        active_cameras.discard(self.camera_index)

        print(f"✅ Stream stopped for {self.camera_label} ({self.camera_name})")

    def toggle_individual_stream(self):
        """Toggle individual stream on/off"""
        if self.stream_running:
            self.stop_stream()
            self._update_button_text("Start", '#f0f0f0', 'black', 'raised')
            if self.app_reference:
                self.app_reference.handle_individual_stream_stop(self.stream_index)
        else:
            self.start_stream()
            self._update_button_text("Stop", '#ffcccc', '#cc0000', 'sunken')
            if self.app_reference:
                self.app_reference.handle_individual_stream_start(self.stream_index)

    def _update_button_text(self, text, bg, fg, relief):
        """Update individual button appearance"""
        if hasattr(self, 'individual_button') and self.individual_button:
            self.individual_button.config(text=text, bg=bg, fg=fg, relief=relief)

    def start_recording(self, grid_name, counter):
        """Start recording directly to file (video or images based on config)"""
        if not self.stream_running:
            print(f"Cannot record {self.camera_label} - stream not running")
            return

        if self.recording:
            print(f"Already recording {self.camera_label}")
            return

        self.recording = True
        
        # Reset counters for image recording
        self.image_frame_counter = 0
        self.saved_image_count = 0
        
        # Get recording mode from config
        recording_mode = self.recording_config.get('recording_mode', 'image').lower()
        
        if recording_mode == 'video':
            self._start_video_recording(grid_name, counter)
        else:
            self._start_image_recording(grid_name, counter)

    def _start_video_recording(self, grid_name, counter):
        """Start video recording"""
        def record_worker():
            try:
                # Create output directory
                output_dir = f"C:\\Users\\{getpass.getuser()}\\Desktop\\scout-videos\\recordings_{datetime.now().strftime('%Y-%m-%d')}\\{grid_name}-{self.camera_label}\\"
                os.makedirs(output_dir, exist_ok=True)

                # Create filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{output_dir}ABC_GRID_{grid_name}_{counter}_recording_{timestamp}_{self.camera_label}.avi"
                self.recording_filename = filename

                # Get frame size from camera
                frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = self.cap.get(cv2.CAP_PROP_FPS)

                # Create video writer
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                self.recorder = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))

                if not self.recorder.isOpened():
                    print(f"Failed to create video writer for {self.camera_label}")
                    self.recording = False
                    return

                print(f"📹 Started video recording {self.camera_label} to: {filename}")

                frame_count = 0
                start_time = time.time()

                while self.recording and self.stream_running:
                    ret, frame = self.cap.read()
                    if ret:
                        self.recorder.write(frame)
                        frame_count += 1

                        # Log progress every 100 frames
                        if frame_count % 100 == 0:
                            elapsed = time.time() - start_time
                            fps_actual = frame_count / elapsed
                            print(f"📹 {self.camera_label}: {frame_count} frames, {fps_actual:.1f} FPS")

                    time.sleep(0.01)  # Small delay

                print(f"📹 Video recording stopped for {self.camera_label}. Frames: {frame_count}")

            except Exception as e:
                print(f"❌ Error recording video {self.camera_label}: {e}")
            finally:
                if self.recorder:
                    self.recorder.release()
                    self.recorder = None
                self.recording = False

        self.recording_thread = threading.Thread(target=record_worker, daemon=True)
        self.recording_thread.start()

    def _start_image_recording(self, grid_name, counter):
        """Start image recording"""
        def record_worker():
            try:
                # Create output directory
                output_dir = f"C:\\Users\\{getpass.getuser()}\\Desktop\\scout-images\\recordings_{datetime.now().strftime('%Y-%m-%d')}\\{grid_name}-{self.camera_label}\\"
                os.makedirs(output_dir, exist_ok=True)

                # Get configuration
                frame_interval = int(self.recording_config.get('frame_interval', '10'))
                image_format = self.recording_config.get('image_format', 'png').lower()
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                print(f"📸 Started image recording {self.camera_label} to: {output_dir}")
                print(f"📸 Saving every {frame_interval} frames as {image_format.upper()} images")

                frame_count = 0
                start_time = time.time()

                while self.recording and self.stream_running:
                    ret, frame = self.cap.read()
                    if ret:
                        self.image_frame_counter += 1
                        
                        # Save frame every N frames
                        if self.image_frame_counter % frame_interval == 0:
                            image_filename = f"{output_dir}ABC_GRID_{grid_name}_{counter}_{timestamp}_{self.camera_label}_frame_{self.saved_image_count:06d}.{image_format}"
                            
                            # Convert BGR to RGB for saving
                            if image_format.lower() in ['png', 'jpg', 'jpeg']:
                                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                img = Image.fromarray(frame_rgb)
                                img.save(image_filename)
                            else:
                                # Use OpenCV for other formats
                                cv2.imwrite(image_filename, frame)
                            
                            self.saved_image_count += 1
                            
                            # Log progress every 10 saved images
                            if self.saved_image_count % 10 == 0:
                                elapsed = time.time() - start_time
                                fps_actual = self.image_frame_counter / elapsed
                                print(f"📸 {self.camera_label}: {self.saved_image_count} images saved, {fps_actual:.1f} FPS")

                        frame_count += 1

                    time.sleep(0.01)  # Small delay

                print(f"📸 Image recording stopped for {self.camera_label}. Total frames: {frame_count}, Images saved: {self.saved_image_count}")

            except Exception as e:
                print(f"❌ Error recording images {self.camera_label}: {e}")
            finally:
                self.recording = False

        self.recording_thread = threading.Thread(target=record_worker, daemon=True)
        self.recording_thread.start()

    def stop_recording(self, grid_name):
        """Stop recording"""
        if self.recording:
            self.recording = False
            print(f"Stopping recording for {self.camera_label}")
            if self.recorder:
                self.recorder.release()
                self.recorder = None

    def is_recording(self):
        """Check if currently recording"""
        return self.recording


class SimplePlayerApp:
    """Simple multi-stream player using direct OpenCV access"""

    def __init__(self, master, camera_indices=None):
        if camera_indices is None:
            camera_indices = [0, 1, 2]  # Default cameras

        self.master = master
        master.title("Simple Camera Viewer")
        master.geometry("1400x700")
        master.minsize(800, 500)

        # Configure root grid
        master.rowconfigure(1, weight=1)
        master.columnconfigure(0, weight=1)

        self.streams = []

        self.grid_numbers = [str(i) for i in range(1, 53)]
        self.grid_suffixes = ['A', 'B']
        self.current_grid_index = 0
        self.current_prefix = 'A'
        self.recording_enabled = False
        self.currently_recording_grid = None
        
        # Load recording configuration
        self.recording_config = read_config_file()
        self.recording_mode = self.recording_config.get('recording_mode', 'image').lower()

        # Initialize system performance logger
        self.performance_logger = SystemPerformanceLogger(log_interval=30)
        
        # Setup window close handler to stop logging
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # UI Setup
        self._create_ui()

        # Create streams
        for idx, camera_idx in enumerate(camera_indices):
            stream = SimpleStream(self.grid_frame, camera_idx, idx)
            stream.app_reference = self
            self.streams.append(stream)

        self._layout_streams()
        self.update_grid_display()

    def _create_ui(self):
        """Create the user interface"""
        # Top spacer
        tk.Frame(self.master, height=20).pack(fill=tk.X)

        # Navigation
        nav = tk.Frame(self.master, pady=8)
        nav.pack(fill=tk.X, padx=20)

        self.back_button = tk.Button(nav, text="← Back", command=self.previous_grid, font=('Arial', 10), width=12)
        self.back_button.pack(side=tk.LEFT, padx=5)

        self.grid_label = tk.Label(
            nav, text="", font=('Arial', 14, 'bold'), bg='lightgray', width=20, relief='sunken'
        )
        self.grid_label.pack(side=tk.LEFT, padx=10)

        self.forward_button = tk.Button(nav, text="Forward →", command=self.next_grid, font=('Arial', 10), width=12)
        self.forward_button.pack(side=tk.LEFT, padx=5)

        self.toggle_prefix_button = tk.Button(nav, text="Toggle A/B", command=self.toggle_prefix, font=('Arial', 10), width=12)
        self.toggle_prefix_button.pack(side=tk.LEFT, padx=10)

        # Recording mode info
        info = tk.Frame(self.master, pady=4)
        info.pack(fill=tk.X, padx=20)
        
        mode_text = f"Recording Mode: {self.recording_mode.upper()}"
        if self.recording_mode == 'image':
            frame_interval = self.recording_config.get('frame_interval', '10')
            image_format = self.recording_config.get('image_format', 'png').upper()
            mode_text += f" | Frame Interval: {frame_interval} | Format: {image_format}"
        
        self.mode_label = tk.Label(
            info, text=mode_text, font=('Arial', 10), bg='lightyellow', 
            relief='solid', bd=1, padx=10, pady=4
        )
        self.mode_label.pack(side=tk.LEFT)

        # Control buttons
        ctrl = tk.Frame(self.master, pady=8)
        ctrl.pack(fill=tk.X, padx=20)

        self.toggle_streams_button = tk.Button(
            ctrl, text="Start All Streams", command=self.toggle_all_streams,
            bg='#f0f0f0', fg='black', relief='raised', bd=3, font=('Arial', 10, 'bold'), height=2
        )
        self.toggle_streams_button.pack(side=tk.LEFT, padx=10)

        # Dynamic recording button text based on mode
        record_text = f"Start Recording All ({'Images' if self.recording_mode == 'image' else 'Video'})"
        self.toggle_record_button = tk.Button(
            ctrl, text=record_text, command=self.toggle_recording,
            bg='#f0f0f0', fg='black', relief='raised', bd=3, font=('Arial', 10, 'bold'), height=2
        )
        self.toggle_record_button.pack(side=tk.LEFT, padx=10)
        

        # Center frame for streams
        center = tk.Frame(self.master)
        center.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        center.columnconfigure(0, weight=1)
        center.rowconfigure(0, weight=1)

        self.grid_frame = tk.Frame(center)
        self.grid_frame.grid(row=0, column=0, sticky="nsew")

        # Bottom spacer
        tk.Frame(self.master, height=20).pack(fill=tk.X)
        
        # Auto-start performance logging silently in background
        self.auto_start_logging()

    def _layout_streams(self):
        """Arrange all 3 cameras in a single row"""
        cols = len(self.streams)
        rows = 1

        for i in range(rows):
            self.grid_frame.rowconfigure(i, weight=1, minsize=200)
        for j in range(cols):
            self.grid_frame.columnconfigure(j, weight=1, minsize=300)

        for idx, stream in enumerate(self.streams):
            stream.container.grid(row=0, column=idx, padx=10, pady=10, sticky="nsew")

    def get_current_label(self):
        """Get current grid label"""
        num_idx = self.current_grid_index // 2
        suffix_idx = self.current_grid_index % 2
        return f"{self.current_prefix}-{self.grid_numbers[num_idx]}-{self.grid_suffixes[suffix_idx]}"

    def update_grid_display(self):
        """Update grid display"""
        label = self.get_current_label()
        self.grid_label.config(text=label)

        self.back_button.config(state=tk.NORMAL if self.current_grid_index > 0 else tk.DISABLED)
        self.forward_button.config(
            state=tk.NORMAL if self.current_grid_index < len(self.grid_numbers) * 2 - 1 else tk.DISABLED
        )

        if self.recording_enabled:
            self.start_recording_current_grid()

    def next_grid(self):
        self.current_grid_index += 1
        self.update_grid_display()

    def previous_grid(self):
        self.current_grid_index -= 1
        self.update_grid_display()

    def toggle_prefix(self):
        self.current_prefix = 'B' if self.current_prefix == 'A' else 'A'
        self.update_grid_display()

    def handle_individual_stream_start(self, idx):
        """Handle individual stream start"""
        if self.recording_enabled and self.currently_recording_grid:
            grid_name = self.get_current_label()
            counter = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-")
            self.streams[idx].start_recording(grid_name, f"{counter}{idx}")

    def handle_individual_stream_stop(self, idx):
        """Handle individual stream stop"""
        if self.recording_enabled and self.currently_recording_grid:
            grid_name = self.get_current_label()
            self.streams[idx].stop_recording(grid_name)

    def toggle_all_streams(self):
        """Toggle all streams on/off with proper timing to avoid NVIDIA conflicts"""
        is_running = self.streams[0].stream_running if self.streams else False
        target_state = not is_running

        if target_state:
            # Starting streams - add delays between camera initializations
            print(f"🎬 Starting {len(self.streams)} camera streams with delays to prevent conflicts...")

            for i, stream in enumerate(self.streams):
                if not stream.stream_running:
                    print(f"📷 Starting camera {i+1}/{len(self.streams)}...")
                    stream.start_stream()
                    if hasattr(stream, 'individual_button') and stream.individual_button:
                        stream._update_button_text("Stop", '#ffcccc', '#cc0000', 'sunken')

                    # Add delay between camera starts to prevent NVIDIA driver conflicts
                    if i < len(self.streams) - 1:  # Don't delay after last camera
                        delay = camera_delay + 0.5  # Extra delay for safety
                        print(f"⏳ Waiting {delay}s before next camera...")
                        time.sleep(delay)

        else:
            # Stopping streams - can happen simultaneously
            print("🛑 Stopping all camera streams...")
            for stream in self.streams:
                if stream.stream_running:
                    stream.stop_stream()
                    if hasattr(stream, 'individual_button') and stream.individual_button:
                        stream._update_button_text("Start", '#f0f0f0', 'black', 'raised')

        self.toggle_streams_button.config(
            text="Stop All Streams" if target_state else "Start All Streams",
            bg='#ffcccc' if target_state else '#f0f0f0',
            fg='#cc0000' if target_state else 'black',
            relief='sunken' if target_state else 'raised'
        )

    def toggle_recording(self):
        """Toggle recording on/off"""
        mode_text = 'Images' if self.recording_mode == 'image' else 'Video'
        
        if self.recording_enabled:
            self.stop_recording_current_grid()
            self.recording_enabled = False
            self.toggle_record_button.config(
                text=f"Start Recording All ({mode_text})",
                bg='#f0f0f0', fg='black', relief='raised'
            )
        else:
            self.recording_enabled = True
            self.toggle_record_button.config(
                text=f"Stop Recording All ({mode_text})",
                bg='#ffcccc', fg='#cc0000', relief='sunken'
            )
            self.start_recording_current_grid()

    def start_recording_current_grid(self):
        """Start recording current grid"""
        grid_name = self.get_current_label()
        if self.currently_recording_grid and self.currently_recording_grid != grid_name:
            self.stop_recording_grid(self.currently_recording_grid)
        self.currently_recording_grid = grid_name
        counter = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-")
        for idx, stream in enumerate(self.streams):
            stream.start_recording(grid_name, f"{counter}{idx}")

    def stop_recording_current_grid(self):
        """Stop recording current grid"""
        if self.currently_recording_grid:
            self.stop_recording_grid(self.currently_recording_grid)
            self.currently_recording_grid = None

    def stop_recording_grid(self, grid_name):
        """Stop recording specific grid"""
        for stream in self.streams:
            stream.stop_recording(grid_name)
    
    def auto_start_logging(self):
        """Automatically start performance logging silently in background when application starts"""
        try:
            self.performance_logger.start_logging()
            # Silent background logging - no console output during normal operation
        except Exception as e:
            # Only log errors, not normal status messages
            print(f"⚠️ Could not start background performance logging: {e}")
    
    def on_closing(self):
        """Handle application closing - stop logging and cleanup"""
        try:
            # Stop performance logging silently
            if self.performance_logger.is_running():
                self.performance_logger.stop_logging()
            
            # Stop camera streams
            for stream in self.streams:
                if stream.stream_running:
                    stream.stop_stream()
            
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")
        finally:
            # Destroy the window
            self.master.destroy()


def test_all_cameras():
    """Test all cameras with different backends"""
    print("🔍 Testing camera access with multiple backends...")
    print("=" * 50)

    available_cameras = []

    for camera_idx in range(5):
        print(f"\nTesting camera {camera_idx}:")

        # Try different backends
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
                cap.release()
            except Exception as e:
                print(f"  ❌ {name}: {e}")

        if working_backend:
            available_cameras.append(camera_info)
            print(f"  🎯 Camera {camera_idx} available via {camera_info[4]}")
        else:
            print(f"  ❌ Camera {camera_idx}: No working backend found")

    return available_cameras

def main():
    """Main function with comprehensive camera testing and NVIDIA conflict prevention"""
    print("🚀 Simple Windows Camera Viewer")
    print("=" * 40)
    print("NVIDIA driver conflict prevention enabled")
    print("=" * 40)

    # Try to get ordered camera indices from config.txt first
    print("\n📁 Reading camera configuration...")
    try:
        camera_indices = get_ordered_camera_indices()
        
        if not camera_indices:
            print("\n❌ No configured USB cameras found!")
            print("\n🔧 Camera Configuration Required:")
            print("   • Run 'windows_configure_cameras.bat' to set up camera positions")
            print("   • Or run 'python windows_configure_cameras.py'")
            print("   • Make sure USB cameras are connected and working")
            print("\n💡 This application only uses USB cameras specified in config.txt")
            print("   System/integrated webcams are ignored for safety")
            print("\nPress Enter to exit...")
            input()
            return
        
        print(f"📋 Using {len(camera_indices)} configured USB camera(s): {camera_indices}")
        
    except Exception as e:
        print(f"⚠️ Error reading camera configuration: {e}")
        print("\n❌ Camera configuration failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Check that config.txt exists in the same directory")
        print("2. Run 'windows_configure_cameras.bat' to set up camera positions")
        print("3. Ensure USB cameras are connected")
        print("4. Check Device Manager for camera status")
        print("\n💡 This application requires proper camera configuration")
        print("   It will not use random/system cameras for safety")
        print("\nPress Enter to exit...")
        input()
        return

    print("\n🎬 Starting camera viewer with threading protection...")
    print("This prevents NVIDIA driver conflicts when using multiple cameras")
    print("💡 To configure camera positions, run: windows_configure_cameras.bat")
    print("Close the window to exit.\n")

    try:
        root = tk.Tk()
        app = SimplePlayerApp(root, camera_indices)
        root.mainloop()
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("Press Enter to exit...")
        input()


if __name__ == "__main__":
    main()

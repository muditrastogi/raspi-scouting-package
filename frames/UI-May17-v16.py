import tkinter as tk
from tkinter import ttk
import cv2
import requests
import threading
import PIL.Image, PIL.ImageTk
from typing import Dict, Optional
import time
import os
from pathlib import Path
from datetime import datetime
import csv
import argparse
import getpass

global USERNAME
recording_active = False
USERNAME = getpass.getuser()

class CameraViewer:
    def __init__(self, root: tk.Tk, device_ips, record_api_ips):
        self.root = root
        self.root.title("Enhanced Camera Stream Viewer")
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.last_saved_grid = None
        # Camera streams configuration
        self.cameras = {}
        for idx, (ip, record_ip) in enumerate(zip(device_ips, record_api_ips), start=1):
            self.cameras[f"Camera {idx}"] = {
                "url": f"{ip}",
                "rurl": f"{record_ip}/",
                "active": False,
            }
        print(self.cameras)
        self.recording_status = {
            camera_name: False for camera_name in self.cameras.keys()
        }
        # Initialize grid data
        self.grid_values = [
            'A-1-A', 'A-1-B', 'A-2-A', 'A-2-B', 'A-3-A', 'A-3-B',
            'A-4-A', 'A-4-B', 'A-5-A', 'A-5-B', 'A-6-A', 'A-6-B',
            # Add more grids as needed
        ]
        self.current_grid_index = 0
        # Create style for buttons
        self.style = ttk.Style()
        self.style.configure('Active.TButton',
                             padding=(10, 15),
                             foreground='#ff00ff')
        self.style.configure('TButton',
                             padding=(10, 15),
                             foreground='#666666')
        self.setup_ui()

    def setup_ui(self):
        self.setup_dropdown_frame()
        self.setup_camera_frame()
        self.setup_control_frame()

    def setup_dropdown_frame(self):
        dropdown_frame = ttk.Frame(self.root)
        dropdown_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Grid Section
        grid_frame = ttk.Frame(dropdown_frame)
        grid_frame.grid(row=0, column=0, padx=5, pady=5)

        self.back_grid_button = ttk.Button(
            grid_frame,
            text="← Back Grid",
            command=self.previous_grid,
            style='TButton'
        )
        self.back_grid_button.pack(side=tk.LEFT)

        self.grid_label = ttk.Label(grid_frame, text="--")
        self.grid_label.pack(side=tk.LEFT)

        self.forward_grid_button = ttk.Button(
            grid_frame,
            text="Forward Grid →",
            command=self.next_grid,
            style='TButton'
        )
        self.forward_grid_button.pack(side=tk.LEFT)

        self.toggle_ab_button = ttk.Button(
            grid_frame,
            text="Toggle A/B",
            command=self.toggle_a_b,
            style='TButton'
        )
        self.toggle_ab_button.pack(side=tk.LEFT)

        # Populate initial grid value
        if self.grid_values:
            self.grid_label.config(text=self.grid_values[0])
        else:
            self.grid_label.config(text="No grids available")

    def next_grid(self):
        if not self.grid_values:
            self.grid_label.config(text="No grids available")
            return
        self.current_grid_index = (self.current_grid_index + 1) % len(self.grid_values)
        new_grid_value = self.grid_values[self.current_grid_index]
        self.grid_label.config(text=new_grid_value)
        self.update_metadata_csv(new_grid_value)

    def previous_grid(self):
        if not self.grid_values:
            self.grid_label.config(text="No grids available")
            return
        self.current_grid_index = (self.current_grid_index - 1) % len(self.grid_values)
        new_grid_value = self.grid_values[self.current_grid_index]
        self.grid_label.config(text=new_grid_value)
        self.update_metadata_csv(new_grid_value)

    def toggle_a_b(self):
        current_grid = self.grid_label.cget("text")
        if not current_grid:
            return
        parts = current_grid.split("-")
        if len(parts) == 3:
            prefix, number, ab = parts
            if ab == "A":
                new_ab = "B"
            else:
                new_ab = "A"
            new_grid = f"{prefix}-{number}-{new_ab}"
            self.grid_label.config(text=new_grid)
            self.update_metadata_csv(new_grid)

    def update_metadata_csv(self, grid_value):
        try:
            current_datetime = datetime.now().strftime("%Y-%m-%d")
            for camera_name in self.cameras.keys():
                recording_path = os.path.join(
                    f"/home/{USERNAME}/Desktop/scout-videos",
                    current_datetime,
                    camera_name.lower().replace(" ", "_"),
                    grid_value
                )
                if not os.path.exists(recording_path):
                    os.makedirs(recording_path)
                csv_file = os.path.join(recording_path, "metadata.csv")
                file_exists = os.path.exists(csv_file)
                with open(csv_file, 'a', newline='') as file:
                    writer = csv.writer(file)
                    if not file_exists:
                        writer.writerow(["Camera", "Grid", "Date", "Time"])
                    writer.writerow([
                        camera_name,
                        grid_value,
                        current_datetime,
                        datetime.now().strftime("%H:%M:%S")
                    ])
            self.last_saved_grid = grid_value
        except Exception as e:
            print(f"Error updating metadata: {e}")

    def setup_camera_frame(self):
        # Create video frames
        for idx, camera_name in enumerate(self.cameras.keys()):
            frame = ttk.Frame(self.root)
            if idx < 2:
                frame.grid(row=2, column=idx, padx=5, pady=5, sticky="nsew")
            else:
                frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
            canvas = tk.Canvas(frame, bg='black', height=160)
            canvas.pack(fill=tk.BOTH, expand=True)
            self.cameras[camera_name]["canvas"] = canvas
            self.cameras[camera_name]["thread"] = None
            self.cameras[camera_name]["streaming"] = False

    def setup_control_frame(self):
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=4, column=0, columnspan=2, pady=5)

        self.stream_button = ttk.Button(
            control_frame,
            text="Start All Streams",
            command=self.toggle_all_streams,
            style='TButton'
        )
        self.stream_button.grid(row=0, column=0, padx=5)

        self.record_button = ttk.Button(
            control_frame,
            text="Start Recording All",
            command=self.toggle_all_recordings,
            style='TButton'
        )
        self.record_button.grid(row=0, column=1, padx=5)

    def get_frame_from_stream(self, url: str) -> Optional[PIL.Image.Image]:
        try:
            cap = cv2.VideoCapture(url)
            if not cap.isOpened():
                print(f"Failed to open RTSP stream: {url}")
                return None
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = PIL.Image.fromarray(frame)
                return image
            else:
                print("Failed to read frame from RTSP stream.")
        except Exception as e:
            print(f"Error getting frame: {e}")
        return None

    def update_stream(self, camera_name: str):
        camera_info = self.cameras[camera_name]
        canvas = camera_info["canvas"]
        while camera_info["streaming"]:
            try:
                image = self.get_frame_from_stream(camera_info["url"])
                if image:
                    canvas_width = canvas.winfo_width()
                    canvas_height = canvas.winfo_height()
                    image.thumbnail((canvas_width, canvas_height), PIL.Image.LANCZOS)
                    photo = PIL.ImageTk.PhotoImage(image=image)
                    canvas.create_image(
                        canvas_width // 2,
                        canvas_height // 2,
                        image=photo,
                        anchor=tk.CENTER
                    )
                    canvas.photo = photo
            except Exception as e:
                print(f"Error updating {camera_name}: {e}")
            time.sleep(0.033)

    def toggle_stream(self, camera_name: str):
        camera_info = self.cameras[camera_name]
        if not camera_info["streaming"]:
            camera_info["streaming"] = True
            camera_info["thread"] = threading.Thread(
                target=self.update_stream,
                args=(camera_name,),
                daemon=True
            )
            camera_info["thread"].start()
        else:
            camera_info["streaming"] = False
            if camera_info["thread"]:
                camera_info["thread"].join(timeout=1)

    def toggle_all_streams(self):
        any_streaming = any(cam["streaming"] for cam in self.cameras.values())
        if not any_streaming:
            for camera_name in self.cameras:
                self.toggle_stream(camera_name)
            self.stream_button.config(text="Stop All Streams", style='Active.TButton')
        else:
            for camera_name in self.cameras:
                if self.cameras[camera_name]["streaming"]:
                    self.toggle_stream(camera_name)
            self.stream_button.config(text="Start All Streams", style='TButton')

    def start_recording(self, camera_name: str):
        camera_info = self.cameras[camera_name]
        current_grid = self.grid_label.cget("text")
        if current_grid == "--":
            print("Please select a valid grid before recording.")
            return
        current_datetime = datetime.now().strftime("%Y-%m-%d")
        counter = str(str(current_datetime) + "-" + str(datetime.now().strftime("%H:%M:%S")) + "-")
        counter = counter.replace(":", "-")
        params = {
            "counter": counter,
            "grid_name": current_grid
        }
        response = requests.get(f"{camera_info['rurl']}/record/start", params=params)
        if response.status_code == 200:
            self.recording_status[camera_name] = True
            print(f"Recording started for {camera_name}: {response.text}")
        else:
            print(f"Failed to start recording for {camera_name}: {response.status_code}")

    def stop_recording(self, camera_name: str):
        camera_info = self.cameras[camera_name]
        response = requests.get(f"{camera_info['rurl']}/record/stop")
        if response.status_code == 200:
            self.recording_status[camera_name] = False
            print(f"Recording stopped for {camera_name}: {response.text}")
        else:
            print(f"Failed to stop recording for {camera_name}: {response.status_code}")

    def toggle_all_recordings(self):
        global recording_active
        if not recording_active:
            for camera_name in self.cameras:
                self.start_recording(camera_name)
            recording_active = True
            self.record_button.config(text="Stop Recording All", style='Active.TButton')
        else:
            for camera_name in self.cameras:
                if self.recording_status[camera_name]:
                    self.stop_recording(camera_name)
            recording_active = False
            self.record_button.config(text="Start Recording All", style='TButton')

def main():
    root = tk.Tk()
    root.geometry("800x800")
    parser = argparse.ArgumentParser(description='Camera Viewer')
    parser.add_argument('--devices', type=str, nargs='+', help='List of camera IPs')
    parser.add_argument('--record-api', type=str, nargs='+', help='List of record api IPs')
    args = parser.parse_args()
    app = CameraViewer(root, args.devices, args.record_api)
    root.mainloop()

if __name__ == "__main__":
    main()

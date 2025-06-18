import tkinter as tk
from tkinter import ttk
import cv2
import requests
import threading
import PIL.Image, PIL.ImageTk
from typing import Dict, Optional
import time
import io
import json
import os
from pathlib import Path
from datetime import datetime
import csv
import argparse
import getpass
global USERNAME
recording_active = False

USERNAME = getpass.getuser()


# AWS Credentials


# Raspberry Pi IPs
# raspberrypi1 = "192.168.1.10"
# raspberrypi2 = "192.168.1.20"
# raspberrypi3 = "192.168.1.30"




def check_video_feed(url):
    # Try to open the video capture

    video_url = f"http://{url}:5000/video_feed"
    cap = cv2.VideoCapture(video_url)

    if not cap.isOpened():
        print("Failed to open video feed.")
        return False

#     # Attempt to read a frame

# if check_video_feed(raspberrypi1):
#     print("raspberrypi 1 192.168.1.10 Video feed is working.")
# else:
#     print("raspberrypi 1 192.168.1.10 Video feed Video feed is NOT  working.")
#     raspberrypi1 =  raspberrypi2

# if check_video_feed(raspberrypi3):
#     print("raspberrypi3 192.168.1.30 Video feed is working.")

# else:
#     print("raspberrypi3 192.168.1.30 Video feed is NOT working.")
#     raspberrypi3 =  raspberrypi2

# if not check_video_feed(raspberrypi2):
#     print("raspberrypi2 192.168.1.20 Video feed is NOT working.")


class CameraViewer:
    def __init__(self, root: tk.Tk, device_ips, record_api_ips):
        self.root = root
        self.root.title("Enhanced Camera Stream Viewer")

        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.last_saved_grid = None

        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        # Camera streams configuration
        # self.cameras: Dict[str, dict] = {
        #     "Camera 1": {"url": f"rtsp://{raspberrypi1}:8554/unicast","rurl": f"http://{raspberrypi1}:5000/", "active": False},
        #     "Camera 2": {"url": f"rtsp://{raspberrypi2}:8554/unicast","rurl": f"http://{raspberrypi2}:5000/", "active": False},
        #     "Camera 3": {"url": f"rtsp://{raspberrypi3}:8554/unicast", "rurl": f"http://{raspberrypi3}:5000/","active": False}
        # }
        self.cameras = {}

        # Step 3: Dynamically build the dictionary
        for idx, (ip, record_ip) in enumerate(zip(device_ips, record_api_ips), start=1):
            self.cameras[f"Camera {idx}"] = {
        "url": f"rtsp://{ip}",
        "rurl": f"http://{record_ip}/",
        "active": False
            }

        print(self.cameras)
        self.recording_status = {
            "Camera 1": False,
            "Camera 2": False,
            "Camera 3": False
        }

        # Initialize grid and cycle data
        self.grid_values = []
        self.cycle_values = []
        self.current_grid_index = 0
        self.current_cycle_index = 0

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
        dropdown_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Create dropdowns and labels for Client, Site
        self.dropdowns = {}
        dropdown_names = ["Client", "Site"]

        for i, name in enumerate(dropdown_names):
            frame = ttk.Frame(dropdown_frame)
            frame.grid(row=0, column=i, padx=5, pady=5)

            ttk.Label(frame, text=name).pack()
            dropdown = ttk.Combobox(frame, state="readonly")
            dropdown.pack()
            self.dropdowns[name] = dropdown

        # Create Greenhouse frame with label and buttons
        greenhouse_frame = ttk.Frame(dropdown_frame)
        greenhouse_frame.grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(greenhouse_frame, text="Greenhouse").pack()
        self.greenhouse_label = ttk.Label(greenhouse_frame, text="--")
        self.greenhouse_label.pack()

        self.greenhouse_button = ttk.Button(greenhouse_frame, text="Next Greenhouse",
                                          command=self.next_greenhouse,
                                          style='TButton')
        self.greenhouse_button.pack()

        self.reset_greenhouse_button = ttk.Button(greenhouse_frame, text="Reset Greenhouse",
                                                command=self.reset_greenhouse,
                                                style='TButton')
        self.reset_greenhouse_button.pack()

        # Create Grid and Cycle frames with labels and buttons
        # Grid Section
        grid_frame = ttk.Frame(dropdown_frame)
        grid_frame.grid(row=0, column=4, padx=5, pady=5)
        ttk.Label(grid_frame, text="Grid").pack()
        self.grid_label = ttk.Label(grid_frame, text="--")
        self.grid_label.pack()
        self.grid_button = ttk.Button(grid_frame, text="Select Grid",
                                command=self.next_grid,
                                style='TButton')
        self.grid_button.pack()

        self.reset_grid_button = ttk.Button(grid_frame, text="Reset Grid",
                                command=self.reset_grid,
                                style='TButton')
        self.reset_grid_button.pack()

        # Cycle Section
        cycle_frame = ttk.Frame(dropdown_frame)
        cycle_frame.grid(row=0, column=5, padx=5, pady=5)
        ttk.Label(cycle_frame, text="Cycle").pack()
        self.cycle_label = ttk.Label(cycle_frame, text="--")
        self.cycle_label.pack()
        self.cycle_button = ttk.Button(cycle_frame, text="Select Cycle",
                                    command=self.next_cycle,
                                    style='TButton')
        self.cycle_button.pack()

        self.reset_cycle_button = ttk.Button(cycle_frame, text="Back Cycle",
                                    command=self.reset_cycle,
                                    style='TButton')
        self.reset_cycle_button.pack()

        # Populate initial values
        self.dropdowns["Client"].set("nutrifresh")
        self.dropdowns["Site"].set("farm1")

        # Initialize greenhouse values
        self.greenhouse_values = []
        self.current_greenhouse_index = 0

        # Initial population of greenhouse data
        self.fetch_and_populate_greenhouse_data()

    def update_metadata_csv(self, grid_value):

        """Update metadata CSV whenever grid value changes"""
        try:
            current_cycle = self.cycle_label.cget("text")

            # Check if we have valid values
            if current_cycle == "--" or current_cycle == "No cycles available":
                print("Warning: No valid cycle selected")
                return
            if grid_value == "--" or grid_value == "No grids available":
                print("Warning: No valid grid selected")
                return

            # Create directory structure


            # Create base directory for all cameras
            current_datetime = datetime.now().strftime("%Y-%m-%d")
            for camera_name in self.cameras.keys():
                recording_path = os.path.join(
                    f"/home/{USERNAME}/Desktop/scout-videos",
                    current_datetime,
                    camera_name.lower().replace(" ", "_"),
                    "nutrifresh",
                    "farm1",
                    self.greenhouse_label.cget("text"),
                    str(current_cycle),
                    grid_value
                )

                if not os.path.exists(recording_path):
                    os.makedirs(recording_path)

                csv_file = os.path.join(recording_path, "metadata.csv")



                # Create or append to CSV file
                file_exists = os.path.exists(csv_file)
                if self.recording_status[camera_name]:
                    with open(csv_file, 'a', newline='') as file:
                        writer = csv.writer(file)
                        if not file_exists:
                            writer.writerow(["Camera", "Greenhouse", "Cycle", "Grid", "Date", "Time"])
                        writer.writerow([
                            camera_name,
                            self.greenhouse_label.cget("text"),
                            current_cycle,
                            grid_value,
                            current_datetime,
                            datetime.now().strftime("%H:%M:%S")
                        ])
            self.last_saved_grid = grid_value

        except Exception as e:
            print(f"Error updating metadata: {e}")
            import traceback
            traceback.print_exc()

    def next_grid(self):
        if not self.grid_values:
            self.grid_label.config(text="No grids available")
            self.grid_button.state(['disabled'])
            return

        self.current_grid_index = (self.current_grid_index + 1) % len(self.grid_values)
        new_grid_value = self.grid_values[self.current_grid_index]
        self.grid_label.config(text=new_grid_value)
        self.grid_button.state(['!disabled'])
        self.grid_button.configure(style='Active.TButton')

        # Update metadata when grid changes
        if new_grid_value != self.last_saved_grid:
            self.update_metadata_csv(new_grid_value)
            if recording_active:
                self.record_grid(new_grid_value)

    def record_grid(self, grid_value,from_record_button=False):
        #stop
        global recording_active
        if recording_active:
            for camera in self.cameras.values():
                start_record = requests.get(f"{camera['rurl']}/record/stop")
                if start_record.status_code == 200:
                    print(start_record.text)
                    if not from_record_button:
                        recording_active = False
                else:
                    print(f"Failed to stop recording{start_record.status_code}")

        #start
        #start recording for the grid
        current_datetime = datetime.now().strftime("%Y-%m-%d")
        counter = str(str(current_datetime) + "-" + str(datetime.now().strftime("%H:%M:%S")) + "-")
        counter = counter.replace(":", "-")
        print(counter)
        if not recording_active:
            for camera in self.cameras.values():
                start_record = requests.get(f"{camera['rurl']}/record/start", params={"counter": counter, "grid_name": grid_value})
                if start_record.status_code == 200:
                    print(start_record.text)
                    if not from_record_button:
                        recording_active = True
                else:
                    print(f"Failed to start recording for {grid_value}: {start_record.status_code}")

    def reset_grid(self):
        if not self.grid_values:
            self.grid_label.config(text="No grids available")
            self.grid_button.state(['disabled'])
            return

        self.current_grid_index = (self.current_grid_index - 1) % len(self.grid_values)
        new_grid_value = self.grid_values[self.current_grid_index]
        self.grid_label.config(text=new_grid_value)
        self.grid_button.state(['!disabled'])
        self.grid_button.configure(style='Active.TButton')

        # Update metadata when grid changes
        if new_grid_value != self.last_saved_grid:
            self.update_metadata_csv(new_grid_value)

    def next_cycle(self):
        if not self.cycle_values:
            self.cycle_label.config(text="No cycles available")
            self.cycle_button.state(['disabled'])
            return

        self.current_cycle_index = (self.current_cycle_index + 1) % len(self.cycle_values)
        self.cycle_label.config(text=self.cycle_values[self.current_cycle_index])
        self.cycle_button.state(['!disabled'])
        self.cycle_button.configure(style='Active.TButton')

    def reset_cycle(self):
        if not self.cycle_values:
            self.cycle_label.config(text="No cycles available")
            self.cycle_button.state(['disabled'])
            return

        self.current_cycle_index = 0
        self.cycle_label.config(text=self.cycle_values[self.current_cycle_index])
        self.cycle_button.state(['!disabled'])
        self.cycle_button.configure(style='Active.TButton')

    def fetch_grid_and_cycle_data(self):
        self.fetch_and_populate_grid_data()
        self.fetch_and_populate_cycle_data()

    def fetch_and_populate_greenhouse_data(self):
        try:


 

            #self.greenhouse_values = list(json_data.keys())
            self.greenhouse_values = ['unit4_parta_s1','unit1_greenhouse1']
            print(self.greenhouse_values)
            if self.greenhouse_values:
                self.greenhouse_label.config(text=self.greenhouse_values[0])
                self.greenhouse_button.state(['!disabled'])
                self.fetch_grid_and_cycle_data()
            else:
                self.greenhouse_label.config(text="No greenhouses available")
                self.greenhouse_button.state(['disabled'])

        except Exception as e:
            print(f"Error fetching greenhouse data: {e}")
            self.greenhouse_label.config(text="Error loading greenhouses")
            self.greenhouse_button.state(['disabled'])

    def fetch_and_populate_cycle_data(self):
        try:
            site_name = self.dropdowns["Site"].get()
            greenhouse_name = self.greenhouse_label.cget("text")  # Changed from dropdown to label

            file_path = os.path.join(f"./nutrifresh/{site_name}/{greenhouse_name}/cycle-info.json")
            old_file_path = os.path.join(f"./nutrifresh/{site_name}/{greenhouse_name}/old-cycle-info.json")
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            try:

                response = requests.get(f"https://grai-image.s3.ap-south-1.amazonaws.com/nutrifresh/{site_name}/{greenhouse_name}/cycle-info.json")
                object_content = response.json()
                json_data = json.loads(object_content)


                with open(file_path, 'w') as json_file:
                    json.dump(json_data, json_file, indent=4)
                import shutil
                shutil.copy(file_path, old_file_path)

            except Exception as E:
                with open(old_file_path, 'r') as json_file:
                    json_data = json.load(json_file)


            # Sort cycle values in descending order

            cycle_list = list(json_data.keys())
            new_cycle_list = []

            for cycle_num in cycle_list:
                if 'cycle' in cycle_num:
                    new_cycle_list.append(int(cycle_num.replace('cycle', '')))
                else:
                    new_cycle_list.append(int(cycle_num))

            self.cycle_values = sorted(new_cycle_list, reverse=True)

            self.current_cycle_index = 0
            if self.cycle_values:
                self.cycle_label.config(text=self.cycle_values[0])
            self.cycle_values = sorted(new_cycle_list, reverse=True)
            self.current_cycle_index = 0

            if self.cycle_values:
                self.cycle_label.config(text=self.cycle_values[0])
                self.cycle_button.state(['!disabled'])
            else:
                self.cycle_label.config(text="No cycles available")
                self.cycle_button.state(['disabled'])

        except Exception as e:
            print(f"Error fetching cycle data: {e}")
            print(f"Error fetching cycle data: {e}")
            self.cycle_label.config(text="Error loading cycles")
            self.cycle_button.state(['disabled'])

    def fetch_and_populate_grid_data(self):
        try:
            greenhouse_name = self.greenhouse_label.cget("text")  # Changed from dropdown to label
            # file_path = os.path.join(f"./nutrifresh/farm1/{greenhouse_name}/grids.json")

            # my_file = Path(file_path)
            # if not my_file.exists():
            #     directory = os.path.dirname(file_path)
            #     if not os.path.exists(directory):
            #         os.makedirs(directory)

            #     response = self.s3_client.get_object(
            #         Bucket='grai-image',
            #         Key=f'nutrifresh/farm1/{greenhouse_name}/grids.json'
            #     )
            #     data = response['Body'].read().decode('utf-8')
            #     json_data = json.loads(data)

            #     with open(file_path, 'w') as json_file:
            #         json.dump(json_data, json_file, indent=4)
            # else:
            #     with open(file_path, 'r') as json_file:
            #         json_data = json.load(json_file)

            # grid_labels = []
            # for sublist in json_data:
            #     for item in sublist:
            #         grid_labels.append(item['label'])

            # grid_labels = [item for item in grid_labels if item]
            # # grid_labels = [f"{item}-A" for item in grid_labels] + [f"{item}-B" for item in grid_labels]
            # grid_labels = sorted(grid_labels, key=lambda x: (x[0], int(x[1:].replace('-', ''))))

            # grid_labels = [f"{item}-{suffix}" for item in grid_labels for suffix in ['A', 'B']]
            if greenhouse_name == "unit1_greenhouse1":
                grid_labels = ['A-1-A', 'A-1-B', 'A-2-A', 'A-2-B', 'A-3-A', 'A-3-B', 'A-4-A', 'A-4-B', 'A-5-A', 'A-5-B', 'A-6-A', 'A-6-B', 'A-7-A', 'A-7-B', 'A-8-A', 'A-8-B', 'A-9-A', 'A-9-B', 'A-10-A', 'A-10-B', 'A-11-A', 'A-11-B', 'A-12-A', 'A-12-B', 'A-13-A', 'A-13-B', 'A-14-A', 'A-14-B', 'A-15-A', 'A-15-B', 'A-16-A', 'A-16-B', 'A-17-A', 'A-17-B', 'A-18-A', 'A-18-B', 'A-19-A', 'A-19-B', 'A-20-A', 'A-20-B', 'A-21-A', 'A-21-B', 'A-22-A', 'A-22-B', 'A-23-A', 'A-23-B', 'A-24-A', 'A-24-B', 'A-25-A', 'A-25-B', 'A-26-A', 'A-26-B', 'A-27-A', 'A-27-B', 'A-28-A', 'A-28-B', 'A-29-A', 'A-29-B', 'A-30-A', 'A-30-B', 'A-31-A', 'A-31-B', 'A-32-A', 'A-32-B', 'A-33-A', 'A-33-B', 'A-34-A', 'A-34-B', 'A-35-A', 'A-35-B', 'A-36-A', 'A-36-B', 'A-37-A', 'A-37-B', 'A-38-A', 'A-38-B', 'A-39-A', 'A-39-B', 'A-40-A', 'A-40-B', 'A-41-A', 'A-41-B', 'A-42-A', 'A-42-B', 'A-43-A', 'A-43-B', 'A-44-A', 'A-44-B', 'A-45-A', 'A-45-B', 'A-46-A', 'A-46-B', 'A-47-A', 'A-47-B', 'A-48-A', 'A-48-B', 'A-49-A', 'A-49-B', 'A-50-A', 'A-50-B', 'B-1-A', 'B-1-B', 'B-2-A', 'B-2-B', 'B-3-A', 'B-3-B', 'B-4-A', 'B-4-B', 'B-5-A', 'B-5-B', 'B-6-A', 'B-6-B', 'B-7-A', 'B-7-B', 'B-8-A', 'B-8-B', 'B-9-A', 'B-9-B', 'B-10-A', 'B-10-B', 'B-11-A', 'B-11-B', 'B-12-A', 'B-12-B', 'B-13-A', 'B-13-B', 'B-14-A', 'B-14-B', 'B-15-A', 'B-15-B', 'B-16-A', 'B-16-B', 'B-17-A', 'B-17-B', 'B-18-A', 'B-18-B', 'B-19-A', 'B-19-B', 'B-20-A', 'B-20-B', 'B-21-A', 'B-21-B', 'B-22-A', 'B-22-B', 'B-23-A', 'B-23-B', 'B-24-A', 'B-24-B', 'B-25-A', 'B-25-B', 'B-26-A', 'B-26-B', 'B-27-A', 'B-27-B', 'B-28-A', 'B-28-B', 'B-29-A', 'B-29-B', 'B-30-A', 'B-30-B', 'B-31-A', 'B-31-B', 'B-32-A', 'B-32-B', 'B-33-A', 'B-33-B', 'B-34-A', 'B-34-B', 'B-35-A', 'B-35-B', 'B-36-A', 'B-36-B', 'B-37-A', 'B-37-B', 'B-38-A', 'B-38-B', 'B-39-A', 'B-39-B', 'B-40-A', 'B-40-B', 'B-41-A', 'B-41-B', 'B-42-A', 'B-42-B', 'B-43-A', 'B-43-B', 'B-44-A', 'B-44-B', 'B-45-A', 'B-45-B', 'B-46-A', 'B-46-B', 'B-47-A', 'B-47-B', 'B-48-A', 'B-48-B', 'B-49-A', 'B-49-B', 'B-50-A', 'B-50-B']
            elif greenhouse_name == "unit4_parta_s1":
                grid_labels = ['A-1-A', 'A-1-B', 'A-2-A', 'A-2-B', 'A-3-A', 'A-3-B', 'A-4-A', 'A-4-B', 'A-5-A', 'A-5-B', 'A-6-A', 'A-6-B', 'A-7-A', 'A-7-B', 'A-8-A', 'A-8-B', 'A-9-A', 'A-9-B', 'A-10-A', 'A-10-B', 'A-11-A', 'A-11-B', 'A-12-A', 'A-12-B', 'A-13-A', 'A-13-B', 'A-14-A', 'A-14-B', 'A-15-A', 'A-15-B', 'A-16-A', 'A-16-B', 'A-17-A', 'A-17-B', 'A-18-A', 'A-18-B', 'A-19-A', 'A-19-B', 'A-20-A', 'A-20-B', 'A-21-A', 'A-21-B', 'A-22-A', 'A-22-B', 'A-23-A', 'A-23-B', 'A-24-A', 'A-24-B', 'A-25-A', 'A-25-B', 'A-26-A', 'A-26-B', 'A-27-A', 'A-27-B', 'A-28-A', 'A-28-B', 'A-29-A', 'A-29-B', 'A-30-A', 'A-30-B', 'A-31-A', 'A-31-B', 'A-32-A', 'A-32-B', 'A-33-A', 'A-33-B', 'A-34-A', 'A-34-B', 'A-35-A', 'A-35-B', 'A-36-A', 'A-36-B', 'A-37-A', 'A-37-B', 'A-38-A', 'A-38-B', 'A-39-A', 'A-39-B', 'A-40-A', 'A-40-B', 'A-41-A', 'A-41-B', 'A-42-A', 'A-42-B', 'A-43-A', 'A-43-B', 'A-44-A', 'A-44-B', 'A-45-A', 'A-45-B', 'A-46-A', 'A-46-B', 'A-47-A', 'A-47-B', 'A-48-A', 'A-48-B', 'A-49-A', 'A-49-B', 'A-50-A', 'A-50-B', 'A-51-A', 'A-51-B', 'A-52-A', 'A-52-B']
            grid_labels.insert(0,"Start")
            print (grid_labels)

            self.grid_values = grid_labels
            self.current_grid_index = 0

            if self.grid_values:
                self.grid_label.config(text=self.grid_values[0])
                self.grid_button.state(['!disabled'])
            else:
                self.grid_label.config(text="No grids available")
                self.grid_button.state(['disabled'])

        except Exception as e:
            print(f"Error fetching grid data: {e}")
            self.grid_label.config(text="Error loading grids")
            self.grid_button.state(['disabled'])


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
                        canvas_width//2,
                        canvas_height//2,
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

    def start_recording(self, camera_name: str,start: int):
        camera_info = self.cameras[camera_name]
        if (not self.recording_status[camera_name] and start == 1):
            try:
                # Get the current cycle value from the label instead of dropdown
                current_cycle = self.cycle_label.cget("text")
                current_grid = self.grid_label.cget("text")

                # Check if we have valid values
                if current_cycle == "--" or current_cycle == "No cycles available":
                    raise ValueError("Please select a valid cycle before recording")
                if current_grid == "--" or current_grid == "No grids available":
                    raise ValueError("Please select a valid grid before recording")

                # Create recording directory based on selected options
                current_datetime = datetime.now().strftime("%Y-%m-%d")
                recording_path = os.path.join(
                    f"/home/{USERNAME}/Desktop/scout-videos",
                    current_datetime,
                    camera_name.lower().replace(" ", "_"),
                    "nutrifresh",
                    "farm1",
                    self.greenhouse_label.cget("text"),  # Changed from dropdown to label
                    str(current_cycle),
                    current_grid,
                )

                if not os.path.exists(recording_path):
                    os.makedirs(recording_path)

                counter = str(str(current_datetime) + "-" + str(datetime.now().strftime("%H:%M:%S")) + "-")
                counter = counter.replace(":", "-")
                print(counter)
                self.recording_status[camera_name] = True
                params = {
                    "counter": counter
                }
                response = requests.get(f"{camera_info['rurl']}/record/start", params=params)
                if response.status_code == 200:
                    self.recording_status[camera_name] = True
            except ValueError as ve:
                print(f"Recording error for {camera_name}: {str(ve)}")
            except Exception as e:
                import traceback
                print(traceback.print_exc())
                print(f"Error starting recording for {camera_name}: {e}")


    def stop_recording(self, camera_name: str,start: int):
        camera_info = self.cameras[camera_name]
        if False:
            try:
                # Get the current cycle value from the label instead of dropdown
                current_cycle = self.cycle_label.cget("text")
                current_grid = self.grid_label.cget("text")

                # Check if we have valid values
                if current_cycle == "--" or current_cycle == "No cycles available":
                    raise ValueError("Please select a valid cycle before recording")
                if current_grid == "--" or current_grid == "No grids available":
                    raise ValueError("Please select a valid grid before recording")

                # Create recording directory based on selected options
                current_datetime = datetime.now().strftime("%Y-%m-%d")
                recording_path = os.path.join(
                    f"/home/{USERNAME}/Desktop/scout-videos",
                    current_datetime,
                    camera_name.lower().replace(" ", "_"),
                    "nutrifresh",
                    "farm1",
                    self.greenhouse_label.cget("text"),  # Changed from dropdown to label
                    str(current_cycle),
                    current_grid,
                )

                if not os.path.exists(recording_path):
                    os.makedirs(recording_path)

                counter = str(str(current_datetime) + "-" + str(datetime.now().strftime("%H:%M:%S")) + "-")
                print(counter)
                params = {
                    "counter": counter
                }
                response = requests.get(f"{camera_info['url']}/record/start/", params=params)
                if response.status_code == 200:
                    self.recording_status[camera_name] = True
            except ValueError as ve:
                print(f"Recording error for {camera_name}: {str(ve)}")
            except Exception as e:
                import traceback
                print(traceback.print_exc())
                print(f"Error starting recording for {camera_name}: {e}")
        else:
            try:
                counter = "Stopped"
                response = requests.get(f"{camera_info['rurl']}/record/stop")
                if response.status_code == 200:
                    self.recording_status[camera_name] = False
            except Exception as e:
                print(f"Error stopping recording for {camera_name}: {e}")
    def toggle_all_recordings(self):
        global recording_active
        print(recording_active)
        print(self.grid_values[self.current_grid_index])
        new_grid_value = self.grid_values[self.current_grid_index]
        if new_grid_value != "Start":
            self.record_grid(new_grid_value,from_record_button=True)

        #any_recording = any(self.recording_status.values())
        if not recording_active:
            #for camera_name in self.cameras:
                #self.start_recording(camera_name,1)

            recording_active = True
            self.record_button.config(text="Stop Recording All", style='Active.TButton')
        elif recording_active:
            #for camera_name in self.cameras:
                #if self.recording_status[camera_name]:
                    #self.stop_recording(camera_name,0)
            recording_active = False
            self.record_button.config(text="Start Recording All", style='TButton')
            for camera in self.cameras.values():
                start_record = requests.get(f"{camera['rurl']}/record/stop")
                if start_record.status_code == 200:
                    print(start_record.text)

    def next_greenhouse(self):
        if not self.greenhouse_values:
            self.greenhouse_label.config(text="No greenhouses available")
            self.greenhouse_button.state(['disabled'])
            return

        self.current_greenhouse_index = (self.current_greenhouse_index + 1) % len(self.greenhouse_values)
        new_greenhouse = self.greenhouse_values[self.current_greenhouse_index]
        self.greenhouse_label.config(text=new_greenhouse)
        self.greenhouse_button.state(['!disabled'])
        self.greenhouse_button.configure(style='Active.TButton')

        # Update grid and cycle data when greenhouse changes
        self.fetch_grid_and_cycle_data()

    def reset_greenhouse(self):
        if not self.greenhouse_values:
            self.greenhouse_label.config(text="No greenhouses available")
            self.greenhouse_button.state(['disabled'])
            return

        self.current_greenhouse_index = 0
        new_greenhouse = self.greenhouse_values[self.current_greenhouse_index]
        self.greenhouse_label.config(text=new_greenhouse)
        self.greenhouse_button.state(['!disabled'])
        self.greenhouse_button.configure(style='Active.TButton')

        # Update grid and cycle data when greenhouse changes
        self.fetch_grid_and_cycle_data()


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

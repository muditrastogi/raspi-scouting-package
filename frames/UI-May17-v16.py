import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading
import requests
from datetime import datetime
import argparse
import platform
import sys


class MJPEGStream:
    def __init__(self, parent, rtsp_url, record_api_url):
        self.rtsp_url = rtsp_url
        self.record_api_url = record_api_url
        self.stream_running = False
        self.frame = tk.Frame(parent, bg='black', width=400, height=300, highlightbackground="gray", highlightthickness=1)
        self.frame.pack_propagate(False)
        self.video_label = tk.Label(self.frame, bg='black')
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Video capture
        self.cap = None
        self.current_frame = None
        self.update_job = None

    def start(self):
        if not self.stream_running:
            self.cap = cv2.VideoCapture(self.rtsp_url)
            if not self.cap.isOpened():
                messagebox.showerror("Stream Error", f"Failed to open stream: {self.rtsp_url}")
                return
            self.stream_running = True
            self._update_frame()

    def stop(self):
        self.stream_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.update_job:
            self.video_label.after_cancel(self.update_job)
            self.update_job = None
        self.video_label.config(image='')

    def _update_frame(self):
        if self.stream_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convert to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img.thumbnail((400, 300))
                img_tk = ImageTk.PhotoImage(image=img)
                self.video_label.img_tk = img_tk  # keep reference
                self.video_label.config(image=img_tk)
            # Schedule next update
            self.update_job = self.video_label.after(15, self._update_frame)

    def start_recording(self, grid_name, counter):
        params = {'counter': counter, 'grid_name': grid_name}
        try:
            r = requests.get(f"{self.record_api_url}/record/start", params=params)
            print(f"Started recording {grid_name} @ {self.record_api_url}: {r.status_code}")
        except Exception as e:
            print(f"Failed to start recording: {e}")

    def stop_recording(self, grid_name):
        params = {'grid_name': grid_name}
        try:
            r = requests.get(f"{self.record_api_url}/record/stop", params=params)
            print(f"Stopped recording {grid_name} @ {self.record_api_url}: {r.status_code}")
        except Exception as e:
            print(f"Failed to stop recording: {e}")


class RTSPPlayerApp:
    def __init__(self, master, stream_infos):
        self.master = master
        master.title("Multi MJPEG Stream Player")
        self.streams = []
        self.grid_numbers = [str(i) for i in range(1, 53)]
        self.grid_suffixes = ['A', 'B']
        self.current_grid_index = 0
        self.current_prefix = 'A'
        self.recording_enabled = False
        self.currently_recording_grid = None

        try:
            master.tk.call('tk', 'scaling', 1.0)
        except:
            pass

        self.top_spacer = tk.Frame(master, height=50)
        self.top_spacer.pack(fill=tk.X)

        self.nav_frame = tk.Frame(master, pady=10)
        self.nav_frame.pack()

        self.back_button = tk.Button(self.nav_frame, text="← Back Grid", command=self.previous_grid, width=20, height=2,
                                     font=('Arial', 16))
        self.back_button.pack(side=tk.LEFT, padx=5)

        self.grid_label = tk.Label(self.nav_frame, text="", font=('Arial', 12, 'bold'), bg='lightgray', padx=10, pady=5,
                                   width=20, height=2)
        self.grid_label.pack(side=tk.LEFT, padx=10)

        self.forward_button = tk.Button(self.nav_frame, text="Forward Grid →", command=self.next_grid, width=20, height=2,
                                        font=('Arial', 16))
        self.forward_button.pack(side=tk.LEFT, padx=5)

        self.toggle_prefix_button = tk.Button(self.nav_frame, text="Toggle A/B", command=self.toggle_prefix, width=20,
                                              height=2, font=('Arial', 16))
        self.toggle_prefix_button.pack(side=tk.LEFT, padx=10)

        self.control_frame = tk.Frame(master, pady=10)
        self.control_frame.pack()

        self.toggle_streams_button = tk.Button(
            self.control_frame, text="Start All Streams", command=self.toggle_all_streams,
            bg='#f0f0f0', fg='black', relief='raised', bd=3, padx=10, pady=5, font=('Arial', 16, 'bold'), width=20, height=2
        )
        self.toggle_streams_button.pack(side=tk.LEFT, padx=10)

        self.toggle_record_button = tk.Button(
            self.control_frame, text="Start Recording All", command=self.toggle_recording,
            bg='#f0f0f0', fg='black', relief='raised', bd=3, padx=10, pady=5, font=('Arial', 16, 'bold'), width=20, height=2
        )
        self.toggle_record_button.pack(side=tk.LEFT, padx=10)

        self.center_frame = tk.Frame(master)
        self.center_frame.pack(expand=True)

        self.grid_frame = tk.Frame(self.center_frame)
        self.grid_frame.pack()

        for rtsp_url, record_api_url in stream_infos:
            stream = MJPEGStream(self.grid_frame, rtsp_url, record_api_url)
            self.streams.append(stream)

        self._layout_streams()
        self.bottom_spacer = tk.Frame(master, height=50)
        self.bottom_spacer.pack(fill=tk.X)

        self.stream_running = False
        self.update_grid_display()

    def get_current_label(self):
        number_index = self.current_grid_index // 2
        suffix_index = self.current_grid_index % 2
        return f"{self.current_prefix}-{self.grid_numbers[number_index]}-{self.grid_suffixes[suffix_index]}"

    def update_grid_display(self):
        label = self.get_current_label()
        self.grid_label.config(text=label)
        print(f"Current grid: {label}")
        self.back_button.config(state=tk.NORMAL if self.current_grid_index > 0 else tk.DISABLED)
        self.forward_button.config(
            state=tk.NORMAL if self.current_grid_index < len(self.grid_numbers) * 2 - 1 else tk.DISABLED
        )

    def next_grid(self):
        if self.current_grid_index < len(self.grid_numbers) * 2 - 1:
            self.current_grid_index += 1
            self.update_grid_display()

    def previous_grid(self):
        if self.current_grid_index > 0:
            self.current_grid_index -= 1
            self.update_grid_display()

    def toggle_prefix(self):
        self.current_prefix = 'B' if self.current_prefix == 'A' else 'A'
        self.update_grid_display()

    def _layout_streams(self):
        total = len(self.streams)
        cols = 2 if total > 1 else 1
        rows = (total + cols - 1) // cols
        for idx, stream in enumerate(self.streams):
            row, col = divmod(idx, cols)
            stream.frame.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
        for i in range(rows):
            self.grid_frame.rowconfigure(i, weight=1)
        for i in range(cols):
            self.grid_frame.columnconfigure(i, weight=1)

    def toggle_all_streams(self):
        if self.stream_running:
            for stream in self.streams:
                stream.stop()
            self.toggle_streams_button.config(
                text="Start All Streams",
                bg='#f0f0f0',
                fg='black',
                relief='raised'
            )
            self.stream_running = False
        else:
            for stream in self.streams:
                stream.start()
            self.toggle_streams_button.config(
                text="Stop All Streams",
                bg='#ffcccc',
                fg='#cc0000',
                relief='sunken'
            )
            self.stream_running = True

    def toggle_recording(self):
        if self.recording_enabled:
            self.stop_recording_current_grid()
            self.recording_enabled = False
            self.toggle_record_button.config(
                text="Start Recording All",
                bg='#f0f0f0',
                fg='black',
                relief='raised'
            )
        else:
            self.recording_enabled = True
            self.toggle_record_button.config(
                text="Stop Recording All",
                bg='#ffcccc',
                fg='#cc0000',
                relief='sunken'
            )
            self.start_recording_current_grid()

    def start_recording_current_grid(self):
        grid_name = self.get_current_label()
        if self.currently_recording_grid and self.currently_recording_grid != grid_name:
            self.stop_recording_grid(self.currently_recording_grid)
        self.currently_recording_grid = grid_name
        counter = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-")
        for idx, stream in enumerate(self.streams):
            stream.start_recording(grid_name, f"{counter}{idx}")

    def stop_recording_current_grid(self):
        if self.currently_recording_grid:
            self.stop_recording_grid(self.currently_recording_grid)
            self.currently_recording_grid = None

    def stop_recording_grid(self, grid_name):
        for stream in self.streams:
            stream.stop_recording(grid_name)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--devices', nargs='+', required=True, help='List of RTSP URLs')
    parser.add_argument('--record-api', nargs='+', required=True, help='List of API URLs (by position)')
    return parser.parse_args()


def main():
    args = parse_args()
    if len(args.devices) != len(args.record_api):
        print("Error: Number of devices and record-api entries must match.")
        sys.exit(1)
    stream_infos = list(zip(args.devices, args.record_api))
    root = tk.Tk()
    root.geometry("1200x800")
    try:
        root.tk.call('tk', 'scaling', 1.0)
        if platform.system() == "Linux":
            try:
                root.tk.call("ttk::style", "theme", "use", "classic")
            except:
                pass
    except:
        pass
    app = RTSPPlayerApp(root, stream_infos)
    root.mainloop()


if __name__ == "__main__":
    main()

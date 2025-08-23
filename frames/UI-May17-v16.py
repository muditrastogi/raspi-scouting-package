import tkinter as tk
from tkinter import messagebox
import vlc
import platform
import sys
import requests
from datetime import datetime
import argparse


class RTSPStream:
    """Represents one RTSP video stream with its UI and controls."""
    def __init__(self, parent, vlc_instance, rtsp_url, record_api_url, stream_index):
        self.vlc_instance = vlc_instance
        self.rtsp_url = rtsp_url
        self.record_api_url = record_api_url
        self.stream_index = stream_index
        self.stream_running = False
        self.app_reference = None  # Will be set by app

        # Camera naming
        labels = ["bottom", "middle", "top"]
        names = ["first", "second", "third"]
        self.camera_label = labels[stream_index] if stream_index < len(labels) else f"camera_{stream_index + 1}"
        self.camera_name = names[stream_index] if stream_index < len(names) else f"camera_{stream_index + 1}"

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

        self.video_panel = tk.Frame(self.video_frame, bg='black')
        self.video_panel.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")

        # Label and optional button
        self._create_label_and_button()

        # VLC Player
        self.player = self.vlc_instance.media_player_new()
        parent.after(100, self._set_video_output)

    def _set_video_output(self):
        window_id = self.video_panel.winfo_id()
        system = platform.system()
        if system == "Windows":
            self.player.set_hwnd(window_id)
        elif system == "Linux":
            self.player.set_xwindow(window_id)
        elif system == "Darwin":
            self.player.set_nsobject(window_id)
        else:
            messagebox.showerror("Platform Error", f"Unsupported OS: {system}")

    def start(self):
        if not self.stream_running:
            media = self.vlc_instance.media_new(self.rtsp_url)
            self.player.set_media(media)
            self.player.play()
            self.stream_running = True
            print(f"Started stream for {self.camera_label} ({self.camera_name})")

    def stop(self):
        if self.stream_running:
            self.player.stop()
            self.stream_running = False
            print(f"Stopped stream for {self.camera_label} ({self.camera_name})")

    def toggle_individual_stream(self):
        if self.stream_running:
            self.stop()
            self._update_button_text("Start", '#f0f0f0', 'black', 'raised')
            if self.app_reference:
                self.app_reference.handle_individual_stream_stop(self.stream_index)
        else:
            self.start()
            self._update_button_text("Stop", '#ffcccc', '#cc0000', 'sunken')
            if self.app_reference:
                self.app_reference.handle_individual_stream_start(self.stream_index)

    def _update_button_text(self, text, bg, fg, relief):
        if hasattr(self, 'individual_button') and self.individual_button:
            self.individual_button.config(text=text, bg=bg, fg=fg, relief=relief)

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

    def start_recording(self, grid_name, counter):
        if self.stream_running:
            params = {'counter': counter, 'grid_name': grid_name}
            try:
                r = requests.get(f"{self.record_api_url}/record/start", params=params)
                print(f"Started recording {self.camera_label} @ {self.record_api_url}: {r.status_code}")
            except Exception as e:
                print(f"Failed to start recording {self.camera_label}: {e}")
        else:
            print(f"Skipping recording for {self.camera_label} - stream not running")

    def stop_recording(self, grid_name):
        params = {'grid_name': grid_name}
        try:
            r = requests.get(f"{self.record_api_url}/record/stop", params=params)
            print(f"Stopped recording {self.camera_label} @ {self.record_api_url}: {r.status_code}")
        except Exception as e:
            print(f"Failed to stop recording {self.camera_label}: {e}")


class RTSPPlayerApp:
    def __init__(self, master, stream_infos):
        self.master = master
        master.title("Multi RTSP Stream Player")
        master.geometry("1400x700")
        master.minsize(800, 500)  # Prevent too small

        # Configure root grid
        master.rowconfigure(1, weight=1)
        master.columnconfigure(0, weight=1)

        self.vlc_instance = vlc.Instance()
        self.streams = []

        self.grid_numbers = [str(i) for i in range(1, 53)]
        self.grid_suffixes = ['A', 'B']
        self.current_grid_index = 0
        self.current_prefix = 'A'
        self.recording_enabled = False
        self.currently_recording_grid = None

        # === UI Setup ===
        self._create_ui()

        # Create streams
        for idx, (rtsp_url, record_api_url) in enumerate(stream_infos):
            stream = RTSPStream(self.grid_frame, self.vlc_instance, rtsp_url, record_api_url, idx)
            stream.app_reference = self
            self.streams.append(stream)

        self._layout_streams()
        self.update_grid_display()

    def _create_ui(self):
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

        # Control buttons
        ctrl = tk.Frame(self.master, pady=8)
        ctrl.pack(fill=tk.X, padx=20)

        self.toggle_streams_button = tk.Button(
            ctrl, text="Start All Streams", command=self.toggle_all_streams,
            bg='#f0f0f0', fg='black', relief='raised', bd=3, font=('Arial', 10, 'bold'), height=2
        )
        self.toggle_streams_button.pack(side=tk.LEFT, padx=10)

        self.toggle_record_button = tk.Button(
            ctrl, text="Start Recording All", command=self.toggle_recording,
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

    def _layout_streams(self):
        """Arrange all 3 cameras in a single row."""
        cols = len(self.streams)
        rows = 1

        for i in range(rows):
            self.grid_frame.rowconfigure(i, weight=1, minsize=200)
        for j in range(cols):
            self.grid_frame.columnconfigure(j, weight=1, minsize=300)

        for idx, stream in enumerate(self.streams):
            stream.container.grid(row=0, column=idx, padx=10, pady=10, sticky="nsew")

    def get_current_label(self):
        num_idx = self.current_grid_index // 2
        suffix_idx = self.current_grid_index % 2
        return f"{self.current_prefix}-{self.grid_numbers[num_idx]}-{self.grid_suffixes[suffix_idx]}"

    def update_grid_display(self):
        label = self.get_current_label()
        self.grid_label.config(text=label)

        self.back_button.config(state=tk.NORMAL if self.current_grid_index > 0 else tk.DISABLED)
        self.forward_button.config(
            state=tk.NORMAL if self.current_grid_index < len(self.grid_numbers) * 2 - 1 else tk.DISABLED
        )

        if self.recording_enabled:
            self.start_recording_current_grid()

    def next_grid(self): self.current_grid_index += 1; self.update_grid_display()
    def previous_grid(self): self.current_grid_index -= 1; self.update_grid_display()
    def toggle_prefix(self): self.current_prefix = 'B' if self.current_prefix == 'A' else 'A'; self.update_grid_display()

    def handle_individual_stream_start(self, idx):
        if self.recording_enabled and self.currently_recording_grid:
            grid_name = self.get_current_label()
            counter = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-")
            self.streams[idx].start_recording(grid_name, f"{counter}{idx}")

    def handle_individual_stream_stop(self, idx):
        if self.recording_enabled and self.currently_recording_grid:
            grid_name = self.get_current_label()
            self.streams[idx].stop_recording(grid_name)

    def toggle_all_streams(self):
        is_running = self.streams[0].stream_running if self.streams else False
        target_state = not is_running

        for stream in self.streams:
            if target_state and not stream.stream_running:
                stream.start()
                if hasattr(stream, 'individual_button') and stream.individual_button:
                    stream._update_button_text("Stop", '#ffcccc', '#cc0000', 'sunken')
            elif not target_state and stream.stream_running:
                stream.stop()
                if hasattr(stream, 'individual_button') and stream.individual_button:
                    stream._update_button_text("Start", '#f0f0f0', 'black', 'raised')

        self.toggle_streams_button.config(
            text="Stop All Streams" if target_state else "Start All Streams",
            bg='#ffcccc' if target_state else '#f0f0f0',
            fg='#cc0000' if target_state else 'black',
            relief='sunken' if target_state else 'raised'
        )

    def toggle_recording(self):
        if self.recording_enabled:
            self.stop_recording_current_grid()
            self.recording_enabled = False
            self.toggle_record_button.config(
                text="Start Recording All",
                bg='#f0f0f0', fg='black', relief='raised'
            )
        else:
            self.recording_enabled = True
            self.toggle_record_button.config(
                text="Stop Recording All",
                bg='#ffcccc', fg='#cc0000', relief='sunken'
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


# === CLI & Main ===
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
    app = RTSPPlayerApp(root, stream_infos)
    root.mainloop()


if __name__ == "__main__":
    main()

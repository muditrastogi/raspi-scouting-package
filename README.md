# Raspberry Pi Scouting Package

A modular, GUI-based Raspberry Pi package for capturing video or image frames from USB cameras via RTSP. It offers two modes: continuous video recording or single-frame image capture. The UI is built with Tkinter, with RTSP streaming handled by VLC and recording powered by FFmpeg.

> ✅ This project is designed for robotics, surveillance, or remote monitoring where quick setup, local streaming, and flexible capture modes are essential.

---

## 📦 Features

- 🎥 Live RTSP stream preview using VLC
- 🧪 Two operational modes:
  - **Video Mode** – continuous video recording
  - **Frame Mode** – saves images frame by frame
- 🧠 Simple Tkinter-based GUI with Start/Stop controls
- 🚀 Fast setup via one-click installer
- 🔌 Auto-detection of USB cameras
- 🔧 Lightweight Flask API to trigger recording
- 📈 Background system monitoring via systemd service
- 📤 FTP server included (for remote file access)

---

## 🗂️ Folder Structure (Post Install)

```text
~/Desktop/
├── usb_raspi_package/                    # Video mode version
│   ├── UI-May17-v16.py                  # Tkinter GUI
│   ├── rtsp_record_api.py               # Flask API using FFmpeg (video)
│   ├── desktopmultiv5.sh                # Launcher script
│   └── v4l2rtspserver                   # RTSP server binary
│
├── usb_raspi_package_camerafixed_frame/ # Frame capture mode version
│   ├── UI-May17-v16.py                  # Same GUI layout
│   ├── rtsp_record_api.py               # Flask API using FFmpeg (frames)
│   ├── desktopmultiv5.sh
│   └── v4l2rtspserver
│
├── delete_except_newest.sh              # Cleanup script (retains only latest file)
├── gr-robo/
│   └── venv/                            # Python virtual environment
│
~/
├── ftpserver.py                         # Optional FTP server using pyftpdlib
├── system_monitor.py                    # System metrics monitor (auto-starts via systemd)
└── requirements.txt                     # Python dependencies
```

---

## 🚀 Installation

> **Minimum Requirements**  
> - Raspberry Pi OS (Lite or Full)  
> - Python 3.7+  
> - `git`, `ffmpeg`, `v4l2loopback`, `python3-venv`, `pyftpdlib`

### 🧠 One-Line Setup (Recommended)
Clone the repo and run the installer script:

```bash
git clone https://github.com/greenprem/raspi-scouting-package.git
cd raspi-scouting-package
bash install.sh
```

> ⚠️ **Do not run the script with `sudo`.** It will request sudo permissions where needed.

---

## 🖥️ Usage

### 📽️ Launch the UI

Navigate to either version:

```bash
cd ~/Desktop/usb_raspi_package               # for video recording
./desktopmultiv5.sh
```

or

```bash
cd ~/Desktop/usb_raspi_package_camerafixed_frame  # for frame capture
./desktopmultiv5.sh
```

### 🎮 UI Controls

- **Start Stream**: Begins RTSP preview via Python VLC
- **Start Record**: Calls the internal Flask API → triggers FFmpeg → saves video or frames
- **Stop**: Ends stream or recording

---

## 🔧 Systemd Service (System Monitoring)

A background service is installed to monitor system metrics like CPU usage, temperature, etc.

```bash
sudo systemctl status system-monitor.service
sudo journalctl -u system-monitor.service -f  # View logs
```

---

## 🧪 Optional: FTP Access

Start FTP server (port 21 default):

```bash
python3 ~/ftpserver.py
```

---

## 🔄 Updating

Simply rerun the installer:

```bash
bash install.sh
```

It will pull the latest code and replace old files.

---

## 📜 License

MIT License. See [LICENSE](LICENSE) file.

---

## 🤖 Created by

**Prem / Green Robotics**  
GitHub: [greenprem](https://github.com/greenprem)

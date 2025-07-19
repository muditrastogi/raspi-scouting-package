#!/bin/bash

# Ensure we're running in a proper terminal environment
if [ -z "$TERM" ] || [ "$TERM" = "dumb" ]; then
    # If no terminal or dumb terminal, try to run in a new terminal window
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$(dirname "$0")' && '$0' $@ ; read -p 'Press Enter to close...'"
        exit 0
    elif command -v xterm &> /dev/null; then
        xterm -e "cd '$(dirname "$0")' && '$0' $@ ; read -p 'Press Enter to close...'"
        exit 0
    elif command -v konsole &> /dev/null; then
        konsole -e bash -c "cd '$(dirname "$0")' && '$0' $@ ; read -p 'Press Enter to close...'"
        exit 0
    else
        # Set a basic terminal environment
        export TERM=xterm-256color
    fi
fi

# Set proper working directory to script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure proper PATH (add common binary locations)
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Set environment variables that might be missing
export HOME="${HOME:-$(eval echo ~$(whoami))}"
export USER="${USER:-$(whoami)}"

# Configuration parameters for local USB cameras
RTSP_BASE_PORT=8554
RECORD_API_BASE_PORT=5000
RTSP_CHECK_TIMEOUT=5
FFPLAY_TEST_DURATION=3

# Default configuration values
DEFAULT_RESOLUTION="1920x1080"
DEFAULT_FPS=15
DEFAULT_BOTTOM_CAMERA=""
DEFAULT_MIDDLE_CAMERA=""
DEFAULT_TOP_CAMERA=""

# Configuration variables
CONFIG_RESOLUTION="$DEFAULT_RESOLUTION"
CONFIG_FPS="$DEFAULT_FPS"
CONFIG_BOTTOM_CAMERA="$DEFAULT_BOTTOM_CAMERA"
CONFIG_MIDDLE_CAMERA="$DEFAULT_MIDDLE_CAMERA"
CONFIG_TOP_CAMERA="$DEFAULT_TOP_CAMERA"

# Arrays to track devices and services
PLAYABLE_DEVICES=()
DEVICE_SERIALS=()
RTSP_SERVERS=()
RECORD_APIS=()
RTSP_PIDS=()
RECORD_API_PIDS=()

# Function to display error messages without exiting
show_error() {
    echo -e "\e[31mERROR: $1\e[0m" >&2
}

# Function to display success messages
success_msg() {
    echo -e "\e[32m$1\e[0m"
}

# Function to display info messages
info_msg() {
    echo -e "\e[34m$1\e[0m"
}

# Function to display warning messages
warning_msg() {
    echo -e "\e[33mWARNING: $1\e[0m"
}

# Function to read configuration from config.txt
read_config() {
    local config_file="$SCRIPT_DIR/config.txt"
    
    if [ -f "$config_file" ]; then
        info_msg "Reading configuration from $config_file"
        
        while IFS='=' read -r key value; do
            # Skip empty lines and comments
            [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue
            
            # Remove whitespace
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            
            case "$key" in
                "resolution")
                    CONFIG_RESOLUTION="$value"
                    info_msg "Config: resolution=$CONFIG_RESOLUTION"
                    ;;
                "fps")
                    CONFIG_FPS="$value"
                    info_msg "Config: fps=$CONFIG_FPS"
                    ;;
                "bottomcamera")
                    CONFIG_BOTTOM_CAMERA="$value"
                    info_msg "Config: bottomcamera=$CONFIG_BOTTOM_CAMERA"
                    ;;
                "middlecamera")
                    CONFIG_MIDDLE_CAMERA="$value"
                    info_msg "Config: middlecamera=$CONFIG_MIDDLE_CAMERA"
                    ;;
                "topcamera")
                    CONFIG_TOP_CAMERA="$value"
                    info_msg "Config: topcamera=$CONFIG_TOP_CAMERA"
                    ;;
                *)
                    warning_msg "Unknown config key: $key"
                    ;;
            esac
        done < "$config_file"
    else
        warning_msg "Configuration file not found: $config_file"
        warning_msg "Using default values: resolution=$CONFIG_RESOLUTION, fps=$CONFIG_FPS"
    fi
}

# Function to get USB serial ID for a device
get_device_serial() {
    local device=$1
    local serial=$(udevadm info --query=all --name="$device" 2>/dev/null | grep 'ID_USB_SERIAL_SHORT=' | cut -d'=' -f2)
    echo "$serial"
}

# Function to cleanup on exit
cleanup() {
    info_msg "Cleaning up processes..."
    
    # Kill record API processes
    for pid in "${RECORD_API_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            info_msg "Stopped record API process $pid"
        fi
    done
    
    # Kill RTSP server processes
    for pid in "${RTSP_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            info_msg "Stopped RTSP server process $pid"
        fi
    done
    
    # Keep terminal open if launched from GUI
    if [ -n "$DISPLAY" ] && [ -z "$PS1" ]; then
        read -p "Press Enter to close..."
    fi
    
    exit 0
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Log script start
info_msg "Script started from: $SCRIPT_DIR"
info_msg "Current working directory: $(pwd)"
info_msg "PATH: $PATH"

# Read configuration
read_config

# Parse resolution into width and height
IFS='x' read -r CONFIG_WIDTH CONFIG_HEIGHT <<< "$CONFIG_RESOLUTION"
if [ -z "$CONFIG_WIDTH" ] || [ -z "$CONFIG_HEIGHT" ]; then
    warning_msg "Invalid resolution format: $CONFIG_RESOLUTION. Using default 1920x1080"
    CONFIG_WIDTH=1920
    CONFIG_HEIGHT=1080
fi

info_msg "Using resolution: ${CONFIG_WIDTH}x${CONFIG_HEIGHT}, FPS: $CONFIG_FPS"

# Check if v4l2rtspserver is installed
if ! command -v ./v4l2rtspserver &> /dev/null; then
    show_error "v4l2rtspserver is not installed. Please install it first."
    show_error "You can install it with: sudo apt-get install v4l2rtspserver"
    exit 1
fi

# Check if ffprobe is installed for stream verification
if ! command -v ffprobe &> /dev/null; then
    warning_msg "ffprobe is not installed. RTSP verification will be skipped."
    warning_msg "You can install it with: sudo apt-get install ffmpeg"
    HAS_FFPROBE=false
else
    HAS_FFPROBE=true
fi

# Check if ffplay is installed for device testing
if ! command -v ffplay &> /dev/null; then
    warning_msg "ffplay is not installed. Device playability testing will be skipped."
    warning_msg "You can install it with: sudo apt-get install ffmpeg"
    HAS_FFPLAY=false
else
    HAS_FFPLAY=true
fi

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    show_error "curl is not installed. Please install it first."
    show_error "You can install it with: sudo apt-get install curl"
    exit 1
fi

# Function to kill processes using a specific port
kill_port_processes() {
    local port=$1
    info_msg "Checking for processes using port $port..."
    
    # Find processes using the port
    local pids=$(lsof -t -i:$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        info_msg "Found processes using port $port: $pids"
        for pid in $pids; do
            if kill -0 "$pid" 2>/dev/null; then
                info_msg "Terminating process $pid using port $port"
                kill -TERM "$pid" 2>/dev/null
                sleep 2
                # Force kill if still running
                if kill -0 "$pid" 2>/dev/null; then
                    kill -KILL "$pid" 2>/dev/null
                    info_msg "Force killed process $pid"
                fi
            fi
        done
        sleep 2
        return 0
    else
        info_msg "No processes found using port $port"
        return 1
    fi
}

# Function to test if a video device is playable with ffplay (using your approach)
test_device_playability() {
    local device=$1
    
    if [ "$HAS_FFPLAY" = false ]; then
        warning_msg "ffplay not available, skipping playability test for $device"
        return 0
    fi
    
    info_msg "Testing playability of $device with ffplay..."
    
    # Use your original approach: check if device doesn't return "Inappropriate ioctl for device"
    if ! timeout 3s ffplay -f v4l2 -i "$device" -t 1 -nodisp -loglevel error 2>&1 | grep -q "Inappropriate ioctl for device"; then
        success_msg "Device $device is playable"
        return 0
    else
        warning_msg "Device $device failed playability test (Inappropriate ioctl for device)"
        return 1
    fi
}

# Function to detect available USB cameras
detect_cameras() {
    info_msg "Detecting available USB cameras..."
    
    # Temporary arrays to store devices with their serials
    local temp_devices=()
    local temp_serials=()
    
    for dev in /dev/video*; do 
        if [ -e "$dev" ]; then
            # Use your original approach: check USB device and test playability in one go
            if udevadm info --query=all --name="$dev" 2>/dev/null | grep -q 'ID_BUS=usb'; then
                # Check if device is accessible with v4l2-ctl
                if timeout 3s v4l2-ctl --device="$dev" --list-formats-ext >/dev/null 2>&1; then
                    # Test playability using your approach
                    if [ "$HAS_FFPLAY" = true ]; then
                        if ! timeout 3s ffplay -f v4l2 -i "$dev" -t 1 -nodisp -loglevel error 2>&1 | grep -q "Inappropriate ioctl for device"; then
                            local serial=$(get_device_serial "$dev")
                            temp_devices+=("$dev")
                            temp_serials+=("$serial")
                            success_msg "Found playable camera: $dev (Serial: $serial)"
                        else
                            warning_msg "Device $dev failed playability test (Inappropriate ioctl for device)"
                        fi
                    else
                        # If ffplay is not available, assume device is playable if v4l2-ctl works
                        local serial=$(get_device_serial "$dev")
                        temp_devices+=("$dev")
                        temp_serials+=("$serial")
                        warning_msg "ffplay not available, assuming $dev is playable based on v4l2-ctl test (Serial: $serial)"
                    fi
                else
                    warning_msg "Device $dev is not accessible with v4l2-ctl"
                fi
            else
                info_msg "Skipping non-USB device: $dev"
            fi
        fi
    done
    
    if [ ${#temp_devices[@]} -eq 0 ]; then
        show_error "No playable USB cameras detected."
        show_error "Make sure your cameras are connected and recognized by the system."
        show_error "You can check with: ls -la /dev/video* && v4l2-ctl --list-devices"
        exit 1
    fi
    
    # Order devices based on configuration (bottom, middle, top)
    order_cameras_by_config temp_devices temp_serials
    
    success_msg "Found ${#PLAYABLE_DEVICES[@]} playable camera device(s): ${PLAYABLE_DEVICES[*]}"
    success_msg "Camera order based on config: ${DEVICE_SERIALS[*]}"
}

# Function to order cameras based on configuration
order_cameras_by_config() {
    local -n devices_ref=$1
    local -n serials_ref=$2
    
    info_msg "Ordering cameras based on configuration..."
    
    # Define the desired order: bottom, middle, top
    local desired_order=("$CONFIG_BOTTOM_CAMERA" "$CONFIG_MIDDLE_CAMERA" "$CONFIG_TOP_CAMERA")
    
    # First, add cameras in the specified order
    for target_serial in "${desired_order[@]}"; do
        if [ -n "$target_serial" ]; then
            for i in "${!serials_ref[@]}"; do
                if [ "${serials_ref[$i]}" = "$target_serial" ]; then
                    PLAYABLE_DEVICES+=("${devices_ref[$i]}")
                    DEVICE_SERIALS+=("${serials_ref[$i]}")
                    info_msg "Added camera ${devices_ref[$i]} (Serial: ${serials_ref[$i]}) in configured order"
                    break
                fi
            done
        fi
    done
    
    # Then add any remaining cameras that weren't in the config
    for i in "${!devices_ref[@]}"; do
        local device="${devices_ref[$i]}"
        local serial="${serials_ref[$i]}"
        local found=false
        
        # Check if this device is already in our ordered list
        for existing_device in "${PLAYABLE_DEVICES[@]}"; do
            if [ "$existing_device" = "$device" ]; then
                found=true
                break
            fi
        done
        
        if [ "$found" = false ]; then
            PLAYABLE_DEVICES+=("$device")
            DEVICE_SERIALS+=("$serial")
            warning_msg "Added unconfigured camera $device (Serial: $serial) at the end"
        fi
    done
}

# Function to start RTSP server for a camera using v4l2rtspserver
start_rtsp_server() {
    local camera_dev=$1
    local port=$2
    local log_file="/tmp/rtsp_${port}.log"
    local max_retries=2
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        info_msg "Starting v4l2rtspserver for $camera_dev on port $port (attempt $((retry_count + 1))/$max_retries)..."
        
        # Ensure log directory exists
        mkdir -p "$(dirname "$log_file")"
        
        # Start v4l2rtspserver in background with configuration values
        ./v4l2rtspserver -P "$port" -W "$CONFIG_WIDTH" -H "$CONFIG_HEIGHT" -F "$CONFIG_FPS" "$camera_dev" > "$log_file" 2>&1 &
        local pid=$!
        
        # Wait a moment for startup
        sleep 3
        
        # Check if process is still running
        if kill -0 "$pid" 2>/dev/null; then
            RTSP_PIDS+=($pid)
            success_msg "v4l2rtspserver started for $camera_dev on port $port (PID: $pid)"
            return 0
        else
            show_error "Failed to start v4l2rtspserver for $camera_dev (attempt $((retry_count + 1)))"
            if [ -f "$log_file" ]; then
                info_msg "Error log:"
                cat "$log_file"
            fi
            
            # If this was not the last attempt, try to kill processes using the port and retry
            if [ $retry_count -lt $((max_retries - 1)) ]; then
                warning_msg "Attempting to clear port $port and retry..."
                kill_port_processes "$port"
                sleep 2
            fi
        fi
        
        ((retry_count++))
    done
    
    show_error "Failed to start RTSP server for $camera_dev after $max_retries attempts"
    return 1
}

# Function to check if RTSP server is running properly
check_rtsp_stream() {
    local port=$1
    local rtsp_url="rtsp://localhost:$port/unicast"
    
    if [ "$HAS_FFPROBE" = true ]; then
        info_msg "Verifying RTSP stream at $rtsp_url ..."
        if timeout $RTSP_CHECK_TIMEOUT ffprobe -v error -i "$rtsp_url" -select_streams v -show_entries stream=codec_type -of csv=p=0 2>/dev/null | grep -q "video"; then
            success_msg "RTSP server is running correctly on port $port"
            return 0
        else
            show_error "RTSP server not responding properly on port $port"
            return 1
        fi
    else
        info_msg "Basic connection test to localhost:$port ..."
        if timeout 2 bash -c "echo > /dev/tcp/localhost/$port" 2>/dev/null; then
            info_msg "Port $port is open on localhost"
            return 0
        else
            show_error "Could not connect to RTSP port $port"
            return 1
        fi
    fi
}

# Function to start record API
start_record_api() {
    local rtsp_port=$1
    local api_port=$2
    local rtsp_url="rtsp://localhost:$rtsp_port/unicast"
    local log_file="/tmp/record_api_${api_port}.log"
    local api_script="./rtsp_record_api.py"
    local max_retries=2
    local retry_count=0
    
    # Check if Python script exists
    if [ ! -f "$api_script" ]; then
        show_error "Record API script not found: $api_script"
        return 1
    fi
    
    while [ $retry_count -lt $max_retries ]; do
        info_msg "Starting record API on port $api_port for RTSP stream $rtsp_url (attempt $((retry_count + 1))/$max_retries)..."
        
        # Ensure log directory exists
        mkdir -p "$(dirname "$log_file")"
        
        # Start record API in background
        python3 "$api_script" --port "$api_port" --rtsp-url "$rtsp_url" > "$log_file" 2>&1 &
        local pid=$!
        
        # Wait for API to start
        sleep 3
        
        # Check if process is still running
        if kill -0 "$pid" 2>/dev/null; then
            RECORD_API_PIDS+=($pid)
            success_msg "Record API started on port $api_port (PID: $pid)"
            return 0
        else
            show_error "Failed to start record API on port $api_port (attempt $((retry_count + 1)))"
            if [ -f "$log_file" ]; then
                info_msg "Error log:"
                cat "$log_file"
            fi
            
            # If this was not the last attempt, try to kill processes using the port and retry
            if [ $retry_count -lt $((max_retries - 1)) ]; then
                warning_msg "Attempting to clear port $api_port and retry..."
                kill_port_processes "$api_port"
                sleep 2
            fi
        fi
        
        ((retry_count++))
    done
    
    show_error "Failed to start record API on port $api_port after $max_retries attempts"
    return 1
}

# Main execution
info_msg "Starting local USB camera RTSP setup..."

# Detect and filter cameras
detect_cameras

# Start RTSP servers for each playable camera (now in configured order)
current_rtsp_port=$RTSP_BASE_PORT
for i in "${!PLAYABLE_DEVICES[@]}"; do
    camera_dev="${PLAYABLE_DEVICES[$i]}"
    camera_serial="${DEVICE_SERIALS[$i]}"
    
    info_msg "Processing camera $camera_dev (Serial: $camera_serial)"
    
    if start_rtsp_server "$camera_dev" $current_rtsp_port; then
        # Wait for RTSP server to fully initialize
        info_msg "Waiting for RTSP server to initialize..."
        sleep 5
        
        if check_rtsp_stream $current_rtsp_port; then
            RTSP_SERVERS+=("rtsp://localhost:${current_rtsp_port}/unicast")
            success_msg "Device $camera_dev (Serial: $camera_serial) successfully initialized on port $current_rtsp_port"
        else
            warning_msg "RTSP stream not available on port $current_rtsp_port"
            # Still add it to array in case it works later
            RTSP_SERVERS+=("rtsp://localhost:$current_rtsp_port")
        fi
    else
        show_error "Failed to start RTSP server for $camera_dev (Serial: $camera_serial) after all retry attempts"
    fi
    
    ((current_rtsp_port++))
done

if [ ${#RTSP_SERVERS[@]} -eq 0 ]; then
    show_error "No RTSP servers successfully started."
    exit 1
fi

# Start record APIs for each RTSP server
current_api_port=$RECORD_API_BASE_PORT
rtsp_port=$RTSP_BASE_PORT

for i in "${!RTSP_SERVERS[@]}"; do
    if start_record_api $rtsp_port $current_api_port; then
        RECORD_APIS+=("http://localhost:$current_api_port")
        success_msg "Record API ready on port $current_api_port"
    else
        warning_msg "Failed to start record API on port $current_api_port after all retry attempts"
    fi
    
    ((current_api_port++))
    ((rtsp_port++))
done

# Prepare arguments for UI (following the original script pattern)
DEVICE_ARGS=""
for device in "${RTSP_SERVERS[@]}"; do
    DEVICE_ARGS="$DEVICE_ARGS $device"
done

RECORD_ARGS=""
for api in "${RECORD_APIS[@]}"; do
    RECORD_ARGS="$RECORD_ARGS $api"
done

info_msg "RTSP Servers: ${RTSP_SERVERS[*]}"
info_msg "Record APIs: ${RECORD_APIS[*]}"

# Launch UI application (following original script pattern)
if [ ${#RTSP_SERVERS[@]} -gt 0 ]; then
    info_msg "Launching Python UI application with devices: $DEVICE_ARGS"
    echo "Command: python3 ./UI-May17-v16.py --devices$DEVICE_ARGS --record-api$RECORD_ARGS"
    
    # Check if virtual environment exists and activate it (with proper path expansion)
    VENV_PATH="$HOME/Desktop/gr-robo/venv"
    if [ -d "$VENV_PATH" ]; then
        info_msg "Activating virtual environment: $VENV_PATH"
        source "$VENV_PATH/bin/activate"
    fi
    
    # Check if UI script exists
    UI_SCRIPT="./UI-May17-v16.py"
    if [ ! -f "$UI_SCRIPT" ]; then
        show_error "UI script not found: $UI_SCRIPT"
        exit 1
    fi
    
    python3 "$UI_SCRIPT" --devices$DEVICE_ARGS --record-api$RECORD_ARGS
    
    if [ $? -ne 0 ]; then
        show_error "Failed to launch Python UI."
        exit 1
    else
        success_msg "Python UI launched successfully!"
    fi
else
    show_error "No devices successfully initialized."
    exit 1
fi

exit 0

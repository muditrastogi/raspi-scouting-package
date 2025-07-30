#!/bin/bash

# Camera Configuration Script for Raspberry Pi Scouting Package
# This script helps configure camera positions by detecting connected cameras
# and updating config.txt with their serial IDs

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration file path
CONFIG_FILE="config.txt"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_PATH="$SCRIPT_DIR/$CONFIG_FILE"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${CYAN}$1${NC}"
}

# Function to create default config.txt if it doesn't exist
create_default_config() {
    if [ ! -f "$CONFIG_PATH" ]; then
        print_info "Creating default config.txt file..."
        cat > "$CONFIG_PATH" << EOF
resolution=1920x1080
fps=30
bottomcamera=
middlecamera=
topcamera=
EOF
        print_success "Default config.txt created at $CONFIG_PATH"
    fi
}

# Function to detect connected cameras
detect_cameras() {
    local cameras=()
    local serials=()
    
    print_info "Scanning for connected USB cameras..."
    
    for dev in /dev/video*; do 
        if [ -e "$dev" ]; then
            # Check if it's a USB camera
            if udevadm info --query=all --name="$dev" 2>/dev/null | grep -q 'ID_BUS=usb'; then
                # Get serial ID
                local serial=$(udevadm info --query=all --name="$dev" 2>/dev/null | awk -F= '/ID_SERIAL_SHORT/ {print $2}')
                if [ -n "$serial" ]; then
                    cameras+=("$dev")
                    serials+=("$serial")
                    print_success "Found USB camera: $dev (Serial: $serial)"
                else
                    print_warning "USB camera found at $dev but no serial ID detected"
                    cameras+=("$dev")
                    serials+=("unknown")
                fi
            fi
        fi
    done
    
    echo "${#cameras[@]}"
    return 0
}

# Function to get serial ID of first available camera
get_camera_serial() {
    # Print info to stderr so it doesn't get captured in command substitution
    echo -e "${BLUE}[INFO]${NC} Detecting camera serial ID..." >&2
    
    # Wait a moment for camera to be fully recognized
    sleep 2
    
    # Find first available USB camera
    for dev in /dev/video*; do 
        if [ -e "$dev" ]; then
            # Check if it's a USB camera
            if udevadm info --query=all --name="$dev" 2>/dev/null | grep -q 'ID_BUS=usb'; then
                # Get serial ID using the provided command
                local serial=$(udevadm info --query=all --name="$dev" 2>/dev/null | awk -F= '/ID_SERIAL_SHORT/ {print $2}')
                if [ -n "$serial" ]; then
                    echo "$serial"
                    return 0
                else
                    echo -e "${YELLOW}[WARNING]${NC} Camera detected at $dev but no serial ID found" >&2
                    # Return empty string instead of unknown_ to avoid updating config
                    echo ""
                    return 1
                fi
            fi
        fi
    done
    
    echo ""
    return 1
}

# Function to update config.txt with camera serial
update_config() {
    local position=$1
    local serial=$2
    
    if [ ! -f "$CONFIG_PATH" ]; then
        create_default_config
    fi
    
    # Create temporary file
    local temp_file=$(mktemp)
    
    # Read current config and update the specified position
    while IFS='=' read -r key value; do
        # Skip empty lines and comments
        if [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]]; then
            echo "$key=$value" >> "$temp_file"
            continue
        fi
        
        # Remove whitespace
        key=$(echo "$key" | xargs)
        
        if [ "$key" = "${position}camera" ]; then
            echo "${position}camera=$serial" >> "$temp_file"
            print_success "Updated ${position}camera=$serial"
        else
            echo "$key=$value" >> "$temp_file"
        fi
    done < "$CONFIG_PATH"
    
    # Replace original config with updated version
    mv "$temp_file" "$CONFIG_PATH"
}

# Function to display current configuration
show_current_config() {
    print_header "=== Current Configuration ==="
    if [ -f "$CONFIG_PATH" ]; then
        while IFS='=' read -r key value; do
            if [[ -n "$key" && ! "$key" =~ ^[[:space:]]*# ]]; then
                key=$(echo "$key" | xargs)
                value=$(echo "$value" | xargs)
                printf "%-15s: %s\n" "$key" "$value"
            fi
        done < "$CONFIG_PATH"
    else
        print_warning "Config file not found: $CONFIG_PATH"
    fi
    echo
}

# Function to wait for camera connection
wait_for_camera() {
    local position=$1
    
    print_header "=== Configuring $position Camera ==="
    echo
    print_info "Please follow these steps:"
    echo "  1. Remove any currently connected cameras"
    echo "  2. Connect ONLY the camera you want to assign to the $position position"
    echo "  3. Wait for the camera to be recognized"
    echo "  4. Press Enter when ready to detect the camera"
    echo
    
    read -p "Press Enter when the $position camera is connected and ready..."
    echo
    
    # Detect camera serial
    local serial=$(get_camera_serial)
    
    if [ -n "$serial" ] && [ "$serial" != "" ]; then
        print_success "Detected camera with serial: $serial"
        update_config "$position" "$serial"
        echo
        print_success "$position camera configuration completed!"
        echo
    else
        print_error "No USB camera detected or no valid serial ID found!"
        print_error "Make sure:"
        echo "  - Camera is properly connected"
        echo "  - Camera is USB Video Class (UVC) compatible"
        echo "  - Only one camera is connected at a time"
        echo "  - Camera has a detectable serial ID"
        echo
        print_info "Configuration for $position camera was not updated."
        echo
        return 1
    fi
    
    return 0
}

# Function to show menu
show_menu() {
    clear
    print_header "╔══════════════════════════════════════════════════════════════╗"
    print_header "║              Camera Configuration Menu                       ║"
    print_header "║          Raspberry Pi Scouting Package                      ║"
    print_header "╚══════════════════════════════════════════════════════════════╝"
    echo
    
    show_current_config
    
    echo "Select camera position to configure:"
    echo
    echo "  1) Configure Bottom Camera"
    echo "  2) Configure Middle Camera"  
    echo "  3) Configure Top Camera"
    echo "  4) Show Current Configuration"
    echo "  5) Test Camera Detection"
    echo "  6) Reset Configuration"
    echo "  7) Exit"
    echo
}

# Function to test camera detection
test_camera_detection() {
    print_header "=== Camera Detection Test ==="
    echo
    
    local count=$(detect_cameras)
    echo
    
    if [ "$count" -eq 0 ]; then
        print_warning "No USB cameras detected"
        print_info "Troubleshooting tips:"
        echo "  - Check camera connections"
        echo "  - Ensure cameras are UVC compatible"
        echo "  - Try: lsusb | grep -i video"
        echo "  - Try: v4l2-ctl --list-devices"
    else
        print_success "Found $count USB camera(s)"
    fi
    
    echo
    read -p "Press Enter to continue..."
}

# Function to reset configuration
reset_config() {
    print_warning "This will reset all camera configurations!"
    read -p "Are you sure? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        # Reset camera configurations to empty values
        update_config "bottom" ""
        update_config "middle" ""
        update_config "top" ""
        print_success "All camera configurations reset to empty"
    else
        print_info "Reset cancelled"
    fi
    
    echo
    read -p "Press Enter to continue..."
}

# Main function
main() {
    # Ensure we're in the script directory
    cd "$SCRIPT_DIR"
    
    # Create config file if it doesn't exist
    create_default_config
    
    while true; do
        show_menu
        read -p "Enter your choice (1-7): " choice
        
        case $choice in
            1)
                wait_for_camera "bottom"
                read -p "Press Enter to continue..."
                ;;
            2)
                wait_for_camera "middle"
                read -p "Press Enter to continue..."
                ;;
            3)
                wait_for_camera "top"
                read -p "Press Enter to continue..."
                ;;
            4)
                clear
                show_current_config
                read -p "Press Enter to continue..."
                ;;
            5)
                test_camera_detection
                ;;
            6)
                reset_config
                ;;
            7)
                print_success "Configuration completed!"
                print_info "Config file saved at: $CONFIG_PATH"
                echo
                print_info "You can now run the scouting package with:"
                print_info "  cd ~/Desktop/usb_raspi_package_camerafixed_frame"
                print_info "  ./desktopmultiv5.sh"
                echo
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please enter 1-7."
                sleep 2
                ;;
        esac
    done
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Check if required commands exist
for cmd in udevadm awk; do
    if ! command -v "$cmd" &> /dev/null; then
        print_error "Required command '$cmd' not found. Please install it first."
        exit 1
    fi
done

# Run main function
main "$@" 
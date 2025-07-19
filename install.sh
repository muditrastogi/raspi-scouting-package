#!/bin/bash

# Raspberry Pi Scouting Package Installer
# Repository: https://github.com/greenprem/raspi-scouting-package

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Progress tracking
TOTAL_STEPS=12
CURRENT_STEP=0

# Repository URL
REPO_URL="https://github.com/greenprem/raspi-scouting-package"
TEMP_DIR="/tmp/raspi-scouting-install"

# Function to print colored output
print_status() {
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

# Progress bar function
show_progress() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    local percentage=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    local filled=$((percentage / 5))
    local empty=$((20 - filled))
    
    printf "\r${BLUE}Progress: [${NC}"
    printf "%*s" $filled | tr ' ' '='
    printf "%*s" $empty | tr ' ' '-'
    printf "${BLUE}] %d%% (%d/%d)${NC} %s" $percentage $CURRENT_STEP $TOTAL_STEPS "$1"
    echo
}

# Error handling function
handle_error() {
    print_error "Installation failed at step $CURRENT_STEP: $1"
    print_error "Cleaning up temporary files..."
    cleanup
    exit 1
}

# Cleanup function
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        print_status "Temporary files cleaned up"
    fi
}

# Trap errors
trap 'handle_error "Unexpected error occurred"' ERR

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create directory with error handling
create_directory() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir" || handle_error "Failed to create directory: $dir"
        print_success "Created directory: $dir"
    else
        print_status "Directory already exists: $dir"
    fi
}

# Function to copy file with error handling
copy_file() {
    local src="$1"
    local dest="$2"
    if [ -f "$src" ]; then
        cp "$src" "$dest" || handle_error "Failed to copy $src to $dest"
        print_success "Copied: $(basename "$src") -> $dest"
    else
        handle_error "Source file not found: $src"
    fi
}

# Function to copy file with optional handling (won't fail if file doesn't exist)
copy_file_optional() {
    local src="$1"
    local dest="$2"
    if [ -f "$src" ]; then
        cp "$src" "$dest" || handle_error "Failed to copy $src to $dest"
        print_success "Copied: $(basename "$src") -> $dest"
    else
        print_warning "Optional file not found: $src (skipping)"
    fi
}

# Function to make file executable
make_executable() {
    local file="$1"
    if [ -f "$file" ]; then
        chmod +x "$file" || handle_error "Failed to make $file executable"
        print_success "Made executable: $file"
    else
        print_warning "File not found for chmod: $file"
    fi
}

# Main installation function
main() {
    echo -e "${GREEN}===================================================${NC}"
    echo -e "${GREEN}  Raspberry Pi Scouting Package Installer${NC}"
    echo -e "${GREEN}===================================================${NC}"
    echo
    
    # Step 1: Check prerequisites
    show_progress "Checking prerequisites..."
    
    if ! command_exists git; then
        print_error "Git is not installed. Please install git first:"
        print_error "sudo apt update && sudo apt install -y git"
        exit 1
    fi
    
    if ! command_exists python3; then
        print_error "Python3 is not installed. Please install python3 first:"
        print_error "sudo apt update && sudo apt install -y python3 python3-pip python3-venv"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
    
    # Step 2: Clean up any existing temporary directory
    show_progress "Preparing installation environment..."
    cleanup
    
    # Step 3: Clone or update repository
    show_progress "Fetching latest code from repository..."
    
    if git clone "$REPO_URL" "$TEMP_DIR" 2>/dev/null; then
        print_success "Repository cloned successfully"
    else
        handle_error "Failed to clone repository. Check your internet connection and repository URL."
    fi
    
    cd "$TEMP_DIR" || handle_error "Failed to enter temporary directory"
    
    # Step 4: Verify required files exist
    show_progress "Verifying required files..."
    
    required_files=(
        "frames/UI-May17-v16.py"
        "frames/rtsp_record_api.py"
        "frames/desktopmultiv5.sh"
        "videos/UI-May17-v16.py"
        "videos/rtsp_record_api.py"
        "videos/desktopmultiv5.sh"
        "delete_except_newest.sh"
        "ftpserver.py"
        "requirements.txt"
        "system_monitor.py"
        "v4l2rtspserver"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            handle_error "Required file not found: $file"
        fi
    done
    
    print_success "All required files found"
    
    # Step 5: Create target directories
    show_progress "Creating target directories..."
    
    create_directory "$HOME/Desktop/usb_raspi_package"
    create_directory "$HOME/Desktop/usb_raspi_package_camerafixed_frame"
    create_directory "$HOME/Desktop/gr-robo"
    
    # Step 6: Copy files to ~/Desktop/usb_raspi_package (videos folder files)
    show_progress "Copying files to ~/Desktop/usb_raspi_package..."
    
    # Copy UI and record API from videos folder
    copy_file "videos/UI-May17-v16.py" "$HOME/Desktop/usb_raspi_package/"
    copy_file "videos/rtsp_record_api.py" "$HOME/Desktop/usb_raspi_package/"
    copy_file "videos/desktopmultiv5.sh" "$HOME/Desktop/usb_raspi_package/"
    
    # Copy other files from root
    copy_file "v4l2rtspserver" "$HOME/Desktop/usb_raspi_package/"
    

    
    # Make shell scripts executable
    make_executable "$HOME/Desktop/usb_raspi_package/desktopmultiv5.sh"
    make_executable "$HOME/Desktop/usb_raspi_package/v4l2rtspserver"
    
    # Step 7: Copy files to ~/Desktop/usb_raspi_package_camerafixed_frame (frames folder files)
    show_progress "Copying files to ~/Desktop/usb_raspi_package_camerafixed_frame..."
    
    # Copy UI and record API from frames folder
    copy_file "frames/UI-May17-v16.py" "$HOME/Desktop/usb_raspi_package_camerafixed_frame/"
    copy_file "frames/rtsp_record_api.py" "$HOME/Desktop/usb_raspi_package_camerafixed_frame/"
    copy_file "frames/desktopmultiv5.sh" "$HOME/Desktop/usb_raspi_package_camerafixed_frame/"
    
    # Copy other files from root
    copy_file "v4l2rtspserver" "$HOME/Desktop/usb_raspi_package_camerafixed_frame/"
    
    # Copy config.txt if it exists
    copy_file_optional "config.txt" "$HOME/Desktop/usb_raspi_package_camerafixed_frame/"
    
    # Make shell scripts executable
    make_executable "$HOME/Desktop/usb_raspi_package_camerafixed_frame/desktopmultiv5.sh"
    make_executable "$HOME/Desktop/usb_raspi_package_camerafixed_frame/v4l2rtspserver"
    
    # Step 8: Copy delete_except_newest.sh to ~/Desktop
    show_progress "Copying delete_except_newest.sh to ~/Desktop..."
    
    copy_file "delete_except_newest.sh" "$HOME/Desktop/"
    make_executable "$HOME/Desktop/delete_except_newest.sh"
    
    # Step 9: Copy files to home directory
    show_progress "Copying files to home directory..."
    
    home_files=(
        "ftpserver.py"
        "system_monitor.py"
        "requirements.txt"
    )
    
    for file in "${home_files[@]}"; do
        copy_file "$file" "$HOME/"
    done
    
    # Step 10: Create and activate Python virtual environment
    show_progress "Creating Python virtual environment..."
    
    if [ -d "$HOME/Desktop/gr-robo/venv" ]; then
        print_warning "Virtual environment already exists. Removing old one..."
        rm -rf "$HOME/Desktop/gr-robo/venv"
    fi
    
    python3 -m venv "$HOME/Desktop/gr-robo/venv" || handle_error "Failed to create virtual environment"
    print_success "Virtual environment created"
    
    # Step 11: Install Python packages
    show_progress "Installing Python packages..."
    
    source "$HOME/Desktop/gr-robo/venv/bin/activate" || handle_error "Failed to activate virtual environment"
    
    if [ -f "$HOME/requirements.txt" ]; then
        pip install --upgrade pip || handle_error "Failed to upgrade pip"
        pip install -r "$HOME/requirements.txt" || handle_error "Failed to install requirements"
        print_success "Python packages installed successfully"
    else
        handle_error "requirements.txt not found in home directory"
    fi
    
    deactivate
    
    # Step 12: Install system packages and setup systemd service
    show_progress "Installing system packages and setting up service..."
    
    print_status "Installing python3-pyftpdlib..."
    if sudo apt update && sudo apt install -y python3-pyftpdlib; then
        print_success "python3-pyftpdlib installed successfully"
    else
        handle_error "Failed to install python3-pyftpdlib"
    fi
    
    # Create systemd service file
    SERVICE_FILE="/tmp/system-monitor.service"
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=System Monitor Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME
Environment=PATH=$HOME/Desktop/gr-robo/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$HOME/Desktop/gr-robo/venv/bin/python $HOME/system_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Install and enable the service
    if sudo cp "$SERVICE_FILE" /etc/systemd/system/; then
        print_success "Service file installed"
    else
        handle_error "Failed to install service file"
    fi
    
    if sudo systemctl daemon-reload; then
        print_success "Systemd daemon reloaded"
    else
        handle_error "Failed to reload systemd daemon"
    fi
    
    if sudo systemctl enable system-monitor.service; then
        print_success "System monitor service enabled"
    else
        handle_error "Failed to enable system monitor service"
    fi
    
    if sudo systemctl start system-monitor.service; then
        print_success "System monitor service started"
    else
        print_warning "Failed to start system monitor service (this might be normal if dependencies aren't ready)"
    fi
    
    # Final cleanup
    cleanup
    
    echo
    echo -e "${GREEN}===================================================${NC}"
    echo -e "${GREEN}  Installation completed successfully!${NC}"
    echo -e "${GREEN}===================================================${NC}"
    echo
    print_success "Files installed in the following locations:"
    echo "  • ~/Desktop/usb_raspi_package/ - Main application files (videos version)"
    echo "  • ~/Desktop/usb_raspi_package_camerafixed_frame/ - Main application files (frames version)"
    echo "  • ~/Desktop/delete_except_newest.sh - Cleanup script"
    echo "  • ~/ - FTP server, system monitor, and requirements"
    echo "  • ~/Desktop/gr-robo/venv/ - Python virtual environment"
    echo
    print_success "System monitor service has been installed and started"
    echo "  • Status: sudo systemctl status system-monitor.service"
    echo "  • Logs: sudo journalctl -u system-monitor.service -f"
    echo
    print_status "To check service status run:"
    echo "  sudo systemctl status system-monitor.service"
    echo
    print_status "To update the installation, simply run this script again."
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root (don't use sudo)"
    print_error "The script will ask for sudo permissions when needed"
    exit 1
fi

# Run main installation
main "$@"

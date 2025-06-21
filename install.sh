#!/bin/bash

# Real-time Whisper Dictation System Installer
# This script installs the dictation system with proper permissions and dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/dictation"
SERVICE_NAME="dictation"
USER_SERVICE_DIR="$HOME/.config/systemd/user"

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python version
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_success "Python $python_version found"
    
    # Check pip
    if ! command_exists pip3; then
        print_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Check audio system
    if ! command_exists pactl; then
        print_warning "PulseAudio not found. Audio capture may not work properly"
    else
        print_success "PulseAudio found"
    fi
    
    # Check for uinput module
    if ! lsmod | grep -q uinput; then
        print_warning "uinput kernel module not loaded. Keystroke injection may not work"
        print_status "To load uinput: sudo modprobe uinput"
    else
        print_success "uinput kernel module loaded"
    fi

    # Check PortAudio (for sounddevice)
    if ! ldconfig -p | grep -q portaudio; then
        print_status "Installing PortAudio system libraries (requires sudo)..."
        sudo apt-get update && sudo apt-get install -y libportaudio2 portaudio19-dev
        print_success "PortAudio libraries installed"
    else
        print_success "PortAudio libraries found"
    fi
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies with uv..."
    
    if ! command_exists uv; then
        print_status "Installing uv (requires pipx)..."
        pipx install uv
    fi
    
    uv sync
    print_success "Python dependencies installed"
}

# Function to setup permissions
setup_permissions() {
    print_status "Setting up permissions..."
    
    # Add user to input group if not already
    if ! groups $USER | grep -q input; then
        print_status "Adding user to input group..."
        sudo usermod -a -G input $USER
        print_warning "You may need to log out and back in for group changes to take effect"
    else
        print_success "User already in input group"
    fi
    
    # Add user to audio group if not already
    if ! groups $USER | grep -q audio; then
        print_status "Adding user to audio group..."
        sudo usermod -a -G audio $USER
    else
        print_success "User already in audio group"
    fi
    
    # Create udev rule for uinput
    if [[ ! -f /etc/udev/rules.d/99-uinput.rules ]]; then
        print_status "Creating udev rule for uinput..."
        echo 'KERNEL=="uinput", MODE="0660", GROUP="input"' | sudo tee /etc/udev/rules.d/99-uinput.rules > /dev/null
        sudo udevadm control --reload-rules
        sudo udevadm trigger
        print_success "udev rule created"
    else
        print_success "udev rule already exists"
    fi
}

# Function to install system files
install_system_files() {
    print_status "Installing system files..."
    
    # Create installation directory
    sudo mkdir -p $INSTALL_DIR
    
    # Copy files
    sudo cp -r dictation/ $INSTALL_DIR/
    sudo cp dictation_cli.py $INSTALL_DIR/
    sudo cp config.yaml $INSTALL_DIR/
    sudo cp requirements.txt $INSTALL_DIR/
    
    # Make CLI executable
    sudo chmod +x $INSTALL_DIR/dictation_cli.py
    
    # Set ownership
    sudo chown -R $USER:$USER $INSTALL_DIR
    
    print_success "System files installed to $INSTALL_DIR"
}

# Function to setup systemd service
setup_systemd_service() {
    print_status "Setting up systemd service..."
    
    # Create user service directory
    mkdir -p $USER_SERVICE_DIR
    
    # Copy and modify service file
    cp dictation.service $USER_SERVICE_DIR/
    
    # Update service file with correct paths
    sed -i "s|/path/to/dictation|$INSTALL_DIR|g" $USER_SERVICE_DIR/dictation.service
    sed -i "s|%i|$USER|g" $USER_SERVICE_DIR/dictation.service
    
    # Reload systemd user daemon
    systemctl --user daemon-reload
    
    # Enable service
    systemctl --user enable dictation.service
    
    print_success "Systemd service configured"
    print_status "To start the service: systemctl --user start dictation"
    print_status "To enable auto-start: systemctl --user enable dictation"
}

# Function to create configuration
setup_configuration() {
    print_status "Setting up configuration..."
    
    # Create config directory
    mkdir -p $HOME/.config/dictation
    
    # Copy default config if it doesn't exist
    if [[ ! -f $HOME/.config/dictation/config.yaml ]]; then
        cp config.yaml $HOME/.config/dictation/
        print_success "Default configuration created at $HOME/.config/dictation/config.yaml"
    else
        print_success "Configuration already exists"
    fi
    
    # Create transcript directory
    mkdir -p $HOME/.local/share/dictation
    print_success "Transcript directory created at $HOME/.local/share/dictation"
}

# Function to create desktop entry
create_desktop_entry() {
    print_status "Creating desktop entry..."
    
    # Create applications directory
    mkdir -p $HOME/.local/share/applications
    
    # Create desktop entry
    cat > $HOME/.local/share/applications/dictation.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Dictation System
Comment=Real-time Whisper-powered dictation system
Exec=$INSTALL_DIR/dictation_cli.py
Icon=audio-input-microphone
Terminal=true
Categories=AudioVideo;Audio;Utility;
Keywords=dictation;speech;whisper;voice;
EOF
    
    print_success "Desktop entry created"
}

# Function to run tests
run_tests() {
    print_status "Running basic tests..."
    
    # Test Python imports
    if python3 -c "import sounddevice, faster_whisper, uinput, pynput" 2>/dev/null; then
        print_success "All Python dependencies imported successfully"
    else
        print_error "Some Python dependencies failed to import"
        exit 1
    fi
    
    # Test audio devices
    if python3 -c "import sounddevice; print('Audio devices:', len(sounddevice.query_devices()))" 2>/dev/null; then
        print_success "Audio system test passed"
    else
        print_warning "Audio system test failed"
    fi
    
    print_success "Basic tests completed"
}

# Function to show post-install instructions
show_post_install() {
    echo
    print_success "Installation completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Log out and log back in for group permissions to take effect"
    echo "2. Load uinput module: sudo modprobe uinput"
    echo "3. Test the system: $INSTALL_DIR/dictation_cli.py"
    echo "4. Start the service: systemctl --user start dictation"
    echo "5. Enable auto-start: systemctl --user enable dictation"
    echo
    echo "Configuration:"
    echo "- Edit: $HOME/.config/dictation/config.yaml"
    echo "- Transcripts: $HOME/.local/share/dictation/"
    echo
    echo "Usage:"
    echo "- Press Ctrl+Alt+D to toggle dictation"
    echo "- Say 'computer' to activate command mode"
    echo "- Say 'stop listening' to stop dictation"
    echo
    echo "For help: $INSTALL_DIR/dictation_cli.py --help"
}

# Main installation function
main() {
    echo "Real-time Whisper Dictation System Installer"
    echo "============================================="
    echo
    
    # Check if not running as root
    check_root
    
    # Check requirements
    check_requirements
    
    # Install dependencies
    install_dependencies
    
    # Setup permissions
    setup_permissions
    
    # Install system files
    install_system_files
    
    # Setup configuration
    setup_configuration
    
    # Setup systemd service
    setup_systemd_service
    
    # Create desktop entry
    create_desktop_entry
    
    # Run tests
    run_tests
    
    # Show post-install instructions
    show_post_install
}

# Run main function
main "$@" 
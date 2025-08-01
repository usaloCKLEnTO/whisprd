# Whisprd Setup Guide for Immutable Linux (Bluefin OS)

This guide documents the complete setup process for getting whisprd (or similar speech-to-text applications) working on immutable Linux distributions like Bluefin OS (Fedora Silverblue-based).

## System Context

- **OS**: Bluefin OS (immutable Fedora Silverblue-based)
- **Hardware**: RTX 4070 Ti SUPER GPU, 4K display
- **Key Constraint**: System packages are read-only, requiring alternative installation methods

## Essential System Dependencies

### Homebrew Installations (Critical)

```bash
# Core compiler toolchain - REQUIRED for building Python packages
brew install gcc          # Provides gcc-15, g++-15, and complete toolchain

# Audio system library - REQUIRED for real-time audio capture
brew install portaudio    # Provides libportaudio for sounddevice Python package
```

**Why These Are Needed:**
- **gcc**: Immutable OS lacks development tools; needed to compile native Python extensions
- **portaudio**: System audio libraries not accessible to Python packages in user space

## Python Environment Setup

### Package Manager
Use `uv` (faster than pip) for Python package management:

```bash
# Install dependencies with CUDA support
uv sync --extra cuda
```

### Key Python Packages
```python
# Core speech recognition
"faster-whisper>=0.10.0"    # GPU-accelerated Whisper (faster than openai/whisper)
"torch>=2.2.0"              # PyTorch with CUDA support
"nvidia-cudnn-cu12"         # CUDA Deep Neural Network library

# Audio processing  
"sounddevice>=0.4.6"        # Real-time audio capture
"numpy>=1.24.0,<2"          # Audio data processing

# System integration
"python-uinput>=0.11.2"     # Keystroke injection (Linux)
"pynput>=1.7.6"             # Global hotkey detection

# Configuration and UI
"PyYAML>=6.0.1"             # Configuration management
"dearpygui>=1.10.0"         # Modern GPU-accelerated GUI (optional)
```

## Critical Build Environment Setup

### Compiler Environment Variables
```bash
# Required for compiling packages on immutable Linux
export CC=gcc-15           # Use Homebrew's GCC
export CXX=g++-15          # Use Homebrew's G++
```

### Library Path Configuration
```bash
# Include Homebrew libraries in library search path
export LD_LIBRARY_PATH=/home/linuxbrew/.linuxbrew/lib:$LD_LIBRARY_PATH

# Include cuDNN libraries (for GPU acceleration)
export LD_LIBRARY_PATH=/path/to/venv/lib/python3.13/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH
```

## Audio System Configuration

### Hardware Detection
```python
import sounddevice as sd

# Query available audio devices
print(sd.query_devices())

# Test supported sample rates for your input device
device_id = 7  # Your default input device
for rate in [8000, 16000, 22050, 44100, 48000]:
    try:
        sd.check_input_settings(device=device_id, channels=1, samplerate=rate)
        print(f'{rate} Hz: ✓ Supported')
    except Exception as e:
        print(f'{rate} Hz: ✗ Not supported')
```

### Common Audio Configuration
Most modern audio hardware supports:
- **Sample Rate**: 44.1kHz or 48kHz (NOT 16kHz)
- **Channels**: 1 (mono) for speech recognition
- **Buffer Size**: 24000 samples (0.5s at 48kHz)

## GPU Acceleration Setup

### CUDA Compatibility Issues

**Problem**: cuDNN version mismatches between PyTorch and faster-whisper

**Solution**: Create symbolic links for version compatibility
```bash
cd /path/to/venv/lib/python3.13/site-packages/nvidia/cudnn/lib/
ln -sf libcudnn_ops.so.9 libcudnn_ops.so.9.1.0
ln -sf libcudnn_ops.so.9 libcudnn_ops.so.9.1
```

### GPU Memory Configuration
For RTX 4070 Ti SUPER (16GB VRAM):
```yaml
whisper:
  model_size: "large"              # Use largest model for best accuracy
  use_cuda: true
  cuda_device: 0
  gpu_memory_fraction: 0.8         # Use 80% of VRAM
  enable_memory_efficient_attention: true
```

## System Permissions (Linux-specific)

### uinput Access (for keystroke injection)
```bash
# Add user to input group
sudo usermod -a -G input $USER

# Load uinput kernel module
sudo modprobe uinput

# Create udev rule for uinput access
echo 'KERNEL=="uinput", MODE="0660", GROUP="input"' | sudo tee /etc/udev/rules.d/99-uinput.rules
sudo udevadm control --reload-rules

# Log out and back in for group changes to take effect
```

## GUI Development (4K Display Support)

### DearPyGui Scaling Issues
**Problem**: Fixed-size layouts don't respond to window resizing

**Solution**: Use responsive sizing
```python
# Main window - fill viewport
with dpg.window(width=-1, height=-1, no_close=True):
    
    # Child windows - responsive
    with dpg.child_window(width=400, height=-1):  # Fixed width, variable height
        pass
    with dpg.child_window(width=-1, height=-1):   # Fill remaining space
        pass

# Set as primary window to fill viewport
dpg.set_primary_window("main_window", True)
```

### Scaling Detection
```python
def detect_scaling():
    # Check environment variables
    gdk_scale = os.environ.get("GDK_SCALE")
    if gdk_scale:
        return float(gdk_scale)
    
    # Check gsettings for GNOME
    try:
        import subprocess
        result = subprocess.check_output([
            "gsettings", "get", "org.gnome.desktop.interface", "text-scaling-factor"
        ], encoding="utf-8").strip()
        return float(result)
    except:
        pass
    
    # Default scaling
    return 2.5  # Good for 4K displays
```

## Whisper Model Optimization

### Model Selection by Hardware
- **RTX 4070 Ti SUPER**: Use "large" model (excellent accuracy)
- **RTX 4060/4070**: Use "medium" model (good balance)
- **GTX series**: Use "small" model (basic accuracy)

### Accuracy Tuning for Noisy Environments
```yaml
whisper:
  model_size: "large"
  initial_prompt: "The following is a dictation of clear speech without background music or noise."
  beam_size: 5
  best_of: 5
  temperature: 0.0
  condition_on_previous_text: false

whisprd:
  confidence_threshold: 0.9          # Higher = more selective
  pause_duration: 1.5                # Longer pause for cleaner cuts
  min_utterance_duration: 1.0        # Avoid processing short noise bursts
```

## Common Issues and Solutions

### 1. Package Compilation Failures
**Symptoms**: `gcc-11 not found`, `g++ not found`
**Solution**: Install and configure Homebrew GCC toolchain

### 2. Audio Device Not Found
**Symptoms**: `PortAudio library not found`
**Solution**: Install PortAudio via Homebrew and set LD_LIBRARY_PATH

### 3. CUDA Memory Errors
**Symptoms**: Out of memory errors with large models
**Solution**: Reduce `gpu_memory_fraction` or use smaller model

### 4. Poor Transcription Accuracy
**Symptoms**: Hallucinated text, incorrect transcriptions
**Solutions**: 
- Use larger model
- Increase confidence threshold
- Add descriptive initial_prompt
- Ensure quiet environment during recording

### 5. GUI Scaling Issues
**Symptoms**: Tiny text on 4K displays, layout breaks on resize
**Solution**: Implement responsive layouts and proper scaling detection

## Development Architecture Recommendations

### For Speech-to-Text Applications

1. **Modular Design**: Separate audio capture, transcription, and output handling
2. **Async Processing**: Use threading for real-time audio processing
3. **Configuration Management**: YAML-based configuration for easy tuning
4. **Error Handling**: Graceful fallbacks (GPU→CPU, large→small model)
5. **System Integration**: Support for global hotkeys and keystroke injection

### Essential Components
```python
class SpeechToTextApp:
    def __init__(self):
        self.audio_capture = AudioCapture()      # sounddevice-based
        self.transcriber = WhisperTranscriber()  # faster-whisper
        self.output_handler = OutputHandler()    # uinput/clipboard
        self.hotkey_manager = HotkeyManager()    # pynput
        self.config = ConfigManager()            # PyYAML
```

## Testing Your Setup

### Verification Script
```python
#!/usr/bin/env python3
"""Test script to verify speech-to-text setup"""

def test_audio():
    import sounddevice as sd
    devices = sd.query_devices()
    print("✓ Audio devices detected:", len(devices))
    return True

def test_gpu():
    import torch
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        gpu_name = torch.cuda.get_device_name(0)
        print(f"✓ CUDA GPU detected: {gpu_name}")
    return cuda_available

def test_whisper():
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("tiny", device="cuda")
        print("✓ Whisper model loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Whisper test failed: {e}")
        return False

if __name__ == "__main__":
    test_audio()
    test_gpu()
    test_whisper()
```

## Final Notes

This setup process addresses the unique challenges of immutable Linux distributions where:
- System packages are read-only
- Development tools must be installed via alternative methods (Homebrew)
- Library paths need manual configuration
- Python package compilation requires specific compiler settings

The end result is a fully functional speech-to-text system with GPU acceleration, suitable for real-time dictation applications.
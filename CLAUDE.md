# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Whisprd is a real-time Whisper-powered dictation system for Linux that converts speech to text and injects keystrokes into applications. It's a personal project focused on providing Windows-like dictation functionality with voice commands, auto-punctuation, and low-latency transcription.

## Essential Commands

### Development & Testing
- `uv sync` - Install dependencies (uses uv package manager)
- `uv sync --extra dev` - Install with development dependencies  
- `uv sync --extra cuda` - Install with CUDA GPU support
- `pytest` - Run all tests
- `pytest tests/unit/` - Run unit tests only
- `pytest tests/integration/` - Run integration tests only
- `pytest tests/gui/` - Run GUI tests only
- `pytest -m "not slow"` - Skip slow tests
- `black .` - Format code
- `isort .` - Sort imports
- `flake8` - Lint code
- `mypy whisprd/` - Type checking

### Application Usage
- `python whisprd_cli.py` - Start CLI interface
- `python whisprd_gui.py` - Start GUI interface
- `python demo_gui.py` - Demo GUI without engine
- `./install.sh` - Install system-wide to /opt/whisprd/
- `systemctl --user enable whisprd` - Enable systemd service

## High-Level Architecture

### Core Components

The system follows a modular architecture with these key components:

1. **DictationEngine** (`dictation_engine.py`) - Main orchestrator that coordinates all components
2. **AudioCapture** (`audio_capture.py`) - Real-time audio capture using sounddevice 
3. **WhisperTranscriber** (`whisper_transcriber.py`) - Speech-to-text using faster-whisper
4. **CommandProcessor** (`command_processor.py`) - Voice command recognition and mapping
5. **KeystrokeInjector** (`keystroke_injector.py`) - Low-latency keystroke injection via uinput
6. **HotkeyManager** (`hotkey_manager.py`) - Global hotkey detection using pynput
7. **Config** (`config.py`) - YAML-based configuration management

### Data Flow

1. Audio is captured from microphone in real-time chunks
2. Audio data is queued and processed by Whisper transcriber
3. Transcribed text is analyzed by command processor for voice commands
4. Regular text or command keystrokes are injected into active application
5. Global hotkey toggles dictation on/off

### GUI Architecture

The GUI uses DearPyGui with these panels:
- **ControlPanel** - Start/stop engine, toggle dictation
- **StatusPanel** - Real-time engine status and statistics  
- **TranscriptionPanel** - Live transcription display with history
- **ConfigPanel** - 6 organized tabs for all settings
- **MainWindow** - Coordinates panels with HiDPI scaling support

### Configuration System

Configuration is managed through `config.yaml` with sections for:
- **audio**: Sample rate, channels, buffer settings
- **whisper**: Model size, language, CUDA settings, alternate prompts
- **whisprd**: Confidence threshold, hotkeys, auto-punctuation
- **commands**: Voice command to keystroke mappings
- **output**: Transcript logging, console output
- **performance**: Threading, latency, GPU memory settings

### Testing Strategy

- **Unit tests** (`tests/unit/`) - Test individual components in isolation
- **Integration tests** (`tests/integration/`) - Test component interactions
- **GUI tests** (`tests/gui/`) - Test GUI components
- **Mocking**: Extensive mocking of hardware dependencies (audio, GPU, uinput)
- **Fixtures**: Common test data and mock objects in `conftest.py`

## Key Implementation Notes

### Audio Processing
- Uses 16kHz mono audio capture with configurable buffer sizes
- Implements pause detection for utterance boundary detection
- Supports configurable audio devices and fallback to defaults

### Whisper Integration  
- Uses faster-whisper for optimized inference
- Automatic CUDA GPU acceleration with CPU fallback
- Supports multiple model sizes (tiny to large) 
- Configurable beam search and temperature settings
- Alternate prompt system for domain-specific transcription

### System Integration
- Linux-specific using uinput for keystroke injection
- Requires input group membership for uinput access
- SystemD service integration for daemon mode
- Global hotkey support (default Ctrl+Alt+D)

### Voice Commands
- Regex-based command matching with confidence scoring
- Configurable command mappings in YAML
- Special "computer" prefix for command mode activation
- Auto-punctuation detection and insertion

### GUI Features
- Automatic HiDPI/fractional scaling detection
- Manual scaling override options
- Real-time status updates and transcription display
- Comprehensive configuration interface
- Demo mode for testing without audio hardware

## Important Development Considerations

- All hardware dependencies (audio, GPU, uinput) should be mocked in tests
- The system requires Linux-specific permissions and modules (input group, uinput)
- GPU acceleration is optional with automatic CPU fallback
- Configuration changes require engine restart to take effect
- GUI scaling must account for various display configurations
- Thread safety is critical for real-time audio processing
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive contribution guidelines
- MIT license
- Gitignore file
- Changelog tracking
- **CUDA GPU acceleration support**
  - Automatic CUDA detection and fallback to CPU
  - Configurable GPU memory usage
  - Memory-efficient attention for large models
  - Multi-GPU support with device selection
  - Performance optimization for GPU inference
- **Personal project documentation**
  - Updated README to reflect personal project nature
  - Set appropriate expectations for contributors
  - Clear communication about maintenance priorities

### Changed
- Renamed project from "dictation" to "whisprd"
- Updated all package names, file names, and references
- Improved branding and project identity
- Enhanced Whisper model loading with GPU support
- Added automatic device selection and fallback
- **Project ownership and expectations**
  - Clearly identified as personal project by @AgenticToaster
  - Set realistic expectations for response times and maintenance
  - Encouraged forking and taking ownership for active contributors

## [1.0.0] - 2024-06-21

### Added
- Initial release of Whisprd dictation system
- Real-time speech recognition using faster-whisper
- Voice command processing with customizable commands
- Keystroke injection using uinput
- Global hotkey support (Ctrl+Alt+D)
- Auto-punctuation and text formatting
- Systemd service integration
- Rich CLI interface with real-time statistics
- YAML-based configuration system
- Audio capture and processing
- Transcript logging and file output
- Pause duration and utterance boundary detection
- Alternate prompts support
- Comprehensive error handling and logging

### Technical Features
- Python 3.12+ compatibility
- Linux-specific optimizations
- Modular architecture for easy extension
- Comprehensive logging and debugging
- Performance monitoring and statistics
- Graceful error recovery and fallbacks

---

**Note**: This is a personal project by @AgenticToaster. I'll update it when I can, but it's not my top priority. Feel free to fork and maintain your own version if you find it useful!

## Version History

### 1.0.0 (Initial Release)
- Complete real-time dictation system
- All core functionality implemented
- Production-ready with comprehensive documentation
- Linux system integration
- Professional-grade error handling and logging

---

## Release Notes

### Breaking Changes
- None in 1.0.0 (initial release)

### Deprecations
- None in 1.0.0

### Security
- User-level service execution (not root)
- Proper permission handling for audio and input devices
- Local audio processing (no cloud upload)
- Secure configuration file handling

### Performance
- Optimized audio buffer management
- Efficient transcription queue processing
- Memory-conscious Whisper model loading
- Low-latency keystroke injection

### Compatibility
- Linux distributions (tested on Ubuntu, Fedora, Arch)
- Python 3.12+
- PulseAudio and PipeWire audio systems
- X11 and Wayland display servers

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to Whisprd.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
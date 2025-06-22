# Whisprd Test Suite

This directory contains comprehensive unit and integration tests for the whisprd dictation system.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and fixtures
├── README.md                # This file
├── unit/                    # Unit tests for individual components
│   ├── __init__.py
│   ├── test_config.py       # Configuration management tests
│   ├── test_audio_capture.py # Audio capture tests
│   ├── test_whisper_transcriber.py # Whisper transcription tests
│   ├── test_command_processor.py # Command processing tests
│   ├── test_keystroke_injector.py # Keystroke injection tests
│   └── test_hotkey_manager.py # Hotkey management tests
├── integration/             # Integration tests
│   ├── __init__.py
│   └── test_dictation_engine.py # Full dictation engine tests
├── gui/                     # GUI component tests
│   ├── __init__.py
│   └── test_gui_components.py # GUI component tests
└── utils/                   # Utility tests
    ├── __init__.py
    └── test_utils.py        # Common utility tests
```

## Running Tests

### Prerequisites

Install the development dependencies:

```bash
pip install -e ".[dev]"
```

Or using uv:

```bash
uv sync --group dev
```

### Running All Tests

```bash
pytest
```

### Running Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# GUI tests only
pytest tests/gui/

# Utility tests only
pytest tests/utils/
```

### Running Tests with Coverage

```bash
# Run with coverage report
pytest --cov=whisprd --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=whisprd --cov-report=html
```

### Running Tests with Markers

```bash
# Run only fast tests
pytest -m "not slow"

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

## Test Categories

### Unit Tests (`tests/unit/`)

Unit tests focus on testing individual components in isolation:

- **`test_config.py`**: Tests for configuration management
  - Configuration loading and validation
  - Configuration updates and reloading
  - Error handling for invalid configurations

- **`test_audio_capture.py`**: Tests for audio capture functionality
  - Audio device initialization
  - Audio recording start/stop
  - Audio data handling and buffering
  - Device enumeration and selection

- **`test_whisper_transcriber.py`**: Tests for Whisper transcription
  - Model loading and initialization
  - Transcription processing
  - CUDA/CPU fallback handling
  - Audio processing and silence detection

- **`test_command_processor.py`**: Tests for command processing
  - Voice command recognition
  - Command mapping and execution
  - Text processing and cleaning

- **`test_keystroke_injector.py`**: Tests for keystroke injection
  - Virtual keyboard device management
  - Key injection and combinations
  - Error handling and retry logic

- **`test_hotkey_manager.py`**: Tests for hotkey management
  - Hotkey detection and parsing
  - Keyboard event handling
  - Callback management

### Integration Tests (`tests/integration/`)

Integration tests verify that components work together correctly:

- **`test_dictation_engine.py`**: Tests for the complete dictation engine
  - Full workflow from audio capture to keystroke injection
  - Component interaction and coordination
  - Error handling and recovery
  - Performance and resource management

### GUI Tests (`tests/gui/`)

GUI tests verify the user interface components:

- **`test_gui_components.py`**: Tests for GUI components
  - Window management and display
  - User interaction handling
  - Status updates and feedback
  - Configuration interface

### Utility Tests (`tests/utils/`)

Utility tests cover common functionality and helpers:

- **`test_utils.py`**: Tests for utility functions
  - Configuration utilities
  - File and directory operations
  - YAML processing
  - Mock data generation
  - Threading utilities

## Test Fixtures

The `conftest.py` file provides common test fixtures:

- **`sample_config`**: Complete sample configuration for testing
- **`temp_config_file`**: Temporary configuration file
- **`mock_audio_data`**: Mock audio data for testing
- **`mock_transcription_result`**: Mock transcription results
- **`mock_whisper_model`**: Mock Whisper model
- **`mock_sounddevice`**: Mock sounddevice module
- **`mock_faster_whisper`**: Mock faster-whisper module
- **`mock_uinput`**: Mock uinput module
- **`mock_pynput`**: Mock pynput module
- **`temp_dir`**: Temporary directory for file operations

## Test Configuration

The test suite is configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=whisprd",
    "--cov-report=term-missing",
    "--cov-report=html",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

## Mocking Strategy

The test suite uses extensive mocking to isolate components:

1. **External Dependencies**: All external libraries (sounddevice, faster-whisper, uinput, pynput) are mocked
2. **Hardware Access**: Audio devices and keyboard input are mocked
3. **File System**: Temporary files and directories are used for file operations
4. **Threading**: Threading behavior is tested with controlled environments

## Coverage Goals

The test suite aims for:

- **Unit Tests**: 90%+ line coverage for each component
- **Integration Tests**: Full workflow coverage
- **Error Handling**: 100% coverage of error paths
- **Edge Cases**: Comprehensive edge case testing

## Continuous Integration

Tests are automatically run in CI/CD pipelines:

- Unit tests run on every commit
- Integration tests run on pull requests
- Coverage reports are generated and tracked
- Performance benchmarks are monitored

## Contributing

When adding new features or fixing bugs:

1. **Write Tests First**: Follow TDD principles
2. **Maintain Coverage**: Ensure new code is well-tested
3. **Update Fixtures**: Add new fixtures as needed
4. **Document Changes**: Update this README for new test categories

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Permission Errors**: Some tests require elevated permissions (use sudo for uinput tests)
3. **Audio Device Errors**: Tests use mocked audio devices
4. **GUI Test Failures**: GUI tests are skipped if DearPyGui is not available

### Debug Mode

Run tests with verbose output:

```bash
pytest -v -s
```

### Specific Test Debugging

Run a specific test with detailed output:

```bash
pytest tests/unit/test_config.py::TestConfig::test_init_with_valid_config -v -s
```

## Performance Testing

For performance-critical components:

```bash
# Run performance benchmarks
pytest tests/unit/ -m "performance" --benchmark-only

# Run stress tests
pytest tests/integration/ -m "stress"
```

## Security Testing

Security-focused tests:

```bash
# Run security tests
pytest tests/unit/ -m "security"

# Run input validation tests
pytest tests/unit/ -m "validation"
``` 
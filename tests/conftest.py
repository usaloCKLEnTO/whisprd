"""
Pytest configuration and common fixtures for whisprd tests.
"""

import pytest
import tempfile
import os
import yaml
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any, Generator

# Add the project root to the Python path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Provide a sample configuration for testing."""
    return {
        'audio': {
            'sample_rate': 16000,
            'channels': 1,
            'buffer_size': 8000,
            'device': None
        },
        'whisper': {
            'model_size': 'tiny',
            'language': 'en',
            'beam_size': 5,
            'best_of': 5,
            'temperature': 0.0,
            'condition_on_previous_text': True,
            'initial_prompt': '',
            'use_cuda': False,
            'cuda_device': 0,
            'gpu_memory_fraction': 0.8,
            'enable_memory_efficient_attention': True,
            'pause_duration': 1.0,
            'min_utterance_duration': 0.7
        },
        'whisprd': {
            'confidence_threshold': 0.5,
            'max_retries': 3,
            'retry_delay': 0.1
        },
        'commands': {
            'new line': 'enter',
            'new paragraph': 'enter enter',
            'delete word': 'ctrl+backspace',
            'delete line': 'ctrl+u',
            'select all': 'ctrl+a',
            'copy': 'ctrl+c',
            'paste': 'ctrl+v',
            'cut': 'ctrl+x',
            'undo': 'ctrl+z',
            'redo': 'ctrl+y'
        },
        'output': {
            'transcript_file': '~/whisprd_transcript.txt',
            'log_level': 'INFO'
        },
        'performance': {
            'max_queue_size': 1000,
            'processing_timeout': 30.0
        }
    }


@pytest.fixture
def temp_config_file(sample_config: Dict[str, Any]) -> str:
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_config, f)
        return f.name


@pytest.fixture
def mock_audio_data() -> bytes:
    """Provide mock audio data for testing."""
    # Generate 1 second of silence at 16kHz, 16-bit mono
    import numpy as np
    samples = np.zeros(16000, dtype=np.int16)
    return samples.tobytes()


@pytest.fixture
def mock_transcription_result() -> Dict[str, Any]:
    """Provide mock transcription result for testing."""
    return {
        'text': 'Hello world',
        'language': 'en',
        'language_probability': 0.99,
        'segments': [
            {
                'start': 0.0,
                'end': 1.0,
                'text': 'Hello world',
                'words': [
                    {'start': 0.0, 'end': 0.5, 'word': 'Hello'},
                    {'start': 0.5, 'end': 1.0, 'word': 'world'}
                ]
            }
        ]
    }


@pytest.fixture
def mock_whisper_model() -> Mock:
    """Mock WhisperModel for testing."""
    mock_model = Mock()
    mock_model.transcribe.return_value = Mock(
        text="Hello world",
        language="en",
        language_probability=0.99,
        segments=[
            Mock(
                start=0.0,
                end=1.0,
                text="Hello world",
                words=[
                    Mock(start=0.0, end=0.5, word="Hello"),
                    Mock(start=0.5, end=1.0, word="world")
                ]
            )
        ]
    )
    return mock_model


@pytest.fixture
def mock_sounddevice() -> Generator[Mock, None, None]:
    """Mock sounddevice module for testing."""
    with patch('whisprd.audio_capture.sd') as mock_sd:
        mock_sd.RawInputStream.return_value = Mock()
        mock_sd.query_devices.return_value = [
            {'name': 'Test Device', 'max_inputs': 1, 'max_outputs': 0}
        ]
        mock_sd.default.device = [0, 1]
        yield mock_sd


@pytest.fixture
def mock_faster_whisper() -> Generator[Mock, None, None]:
    """Mock faster_whisper module for testing."""
    with patch('whisprd.whisper_transcriber.WhisperModel') as mock_whisper:
        mock_whisper.return_value = Mock()
        yield mock_whisper


@pytest.fixture
def mock_uinput() -> Generator[Mock, None, None]:
    """Mock uinput module for testing."""
    with patch('whisprd.keystroke_injector.uinput') as mock_ui:
        mock_ui.Device.return_value = Mock()
        yield mock_ui


@pytest.fixture
def mock_pynput() -> Generator[Mock, None, None]:
    """Mock pynput module for testing."""
    with patch('whisprd.hotkey_manager.pynput') as mock_pynput:
        mock_pynput.keyboard.Listener.return_value = Mock()
        yield mock_pynput


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(autouse=True)
def setup_logging() -> None:
    """Setup logging for tests."""
    import logging
    logging.basicConfig(level=logging.WARNING)
    # Suppress specific logger warnings during tests
    logging.getLogger('whisprd').setLevel(logging.ERROR) 
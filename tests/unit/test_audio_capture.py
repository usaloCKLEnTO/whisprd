"""
Unit tests for the audio_capture module.
"""

import pytest
import queue
import time
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from whisprd.audio_capture import AudioCapture


class TestAudioCapture:
    """Test cases for the AudioCapture class."""

    def test_init_with_valid_config(self, sample_config: dict) -> None:
        """Test AudioCapture initialization with valid config."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        assert capture.sample_rate == 16000
        assert capture.channels == 1
        assert capture.buffer_size == 8000
        assert capture.device is None
        assert capture.is_recording is False
        assert capture.stream is None

    def test_init_with_custom_config(self) -> None:
        """Test AudioCapture initialization with custom config."""
        audio_config = {
            'sample_rate': 44100,
            'channels': 2,
            'buffer_size': 4096,
            'device': 1
        }
        capture = AudioCapture(audio_config)
        
        assert capture.sample_rate == 44100
        assert capture.channels == 2
        assert capture.buffer_size == 4096
        assert capture.device == 1

    def test_init_with_audio_callback(self, sample_config: dict) -> None:
        """Test AudioCapture initialization with audio callback."""
        audio_config = sample_config['audio']
        callback = Mock()
        capture = AudioCapture(audio_config, callback)
        
        assert capture.audio_callback == callback

    def test_start_recording_success(self, sample_config: dict, mock_sounddevice) -> None:
        """Test successful start of audio recording."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        # Mock the stream
        mock_stream = Mock()
        mock_sounddevice.RawInputStream.return_value = mock_stream
        
        capture.start_recording()
        
        assert capture.is_recording is True
        assert capture.stream == mock_stream
        mock_stream.start.assert_called_once()

    def test_start_recording_already_recording(self, sample_config: dict) -> None:
        """Test starting recording when already recording."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        capture.is_recording = True
        
        with patch('whisprd.audio_capture.logger') as mock_logger:
            capture.start_recording()
            mock_logger.warning.assert_called_with("Audio recording already started")

    def test_start_recording_failure(self, sample_config: dict, mock_sounddevice) -> None:
        """Test starting recording with failure."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        mock_sounddevice.RawInputStream.side_effect = Exception("Audio device error")
        
        with pytest.raises(Exception, match="Audio device error"):
            capture.start_recording()

    def test_stop_recording_success(self, sample_config: dict) -> None:
        """Test successful stop of audio recording."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        capture.is_recording = True
        capture.stream = Mock()
        
        capture.stop_recording()
        
        assert capture.is_recording is False
        assert capture.stream is None
        capture.stream.stop.assert_called_once()
        capture.stream.close.assert_called_once()

    def test_stop_recording_not_recording(self, sample_config: dict) -> None:
        """Test stopping recording when not recording."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        capture.is_recording = False
        
        with patch('whisprd.audio_capture.logger') as mock_logger:
            capture.stop_recording()
            mock_logger.warning.assert_called_with("Audio recording not started")

    def test_stop_recording_with_error(self, sample_config: dict) -> None:
        """Test stopping recording with error."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        capture.is_recording = True
        capture.stream = Mock()
        capture.stream.stop.side_effect = Exception("Stop error")
        
        with patch('whisprd.audio_capture.logger') as mock_logger:
            capture.stop_recording()
            mock_logger.error.assert_called_with("Error stopping audio recording: Stop error")

    def test_audio_callback_with_external_callback(self, sample_config: dict) -> None:
        """Test audio callback with external callback function."""
        audio_config = sample_config['audio']
        external_callback = Mock()
        capture = AudioCapture(audio_config, external_callback)
        
        # Mock audio data
        mock_indata = np.array([[1000, 2000]], dtype=np.int16)
        mock_time = Mock()
        
        capture._audio_callback(mock_indata, 1, mock_time, None)
        
        # Check that data was added to queue
        assert capture.audio_queue.qsize() == 1
        
        # Check that external callback was called
        external_callback.assert_called_once()

    def test_audio_callback_with_status(self, sample_config: dict) -> None:
        """Test audio callback with status warning."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        mock_indata = np.array([[1000, 2000]], dtype=np.int16)
        mock_time = Mock()
        
        with patch('whisprd.audio_capture.logger') as mock_logger:
            capture._audio_callback(mock_indata, 1, mock_time, "Buffer underrun")
            mock_logger.warning.assert_called_with("Audio callback status: Buffer underrun")

    def test_audio_callback_external_callback_error(self, sample_config: dict) -> None:
        """Test audio callback when external callback raises error."""
        audio_config = sample_config['audio']
        external_callback = Mock(side_effect=Exception("Callback error"))
        capture = AudioCapture(audio_config, external_callback)
        
        mock_indata = np.array([[1000, 2000]], dtype=np.int16)
        mock_time = Mock()
        
        with patch('whisprd.audio_capture.logger') as mock_logger:
            capture._audio_callback(mock_indata, 1, mock_time, None)
            mock_logger.error.assert_called_with("Error in audio callback: Callback error")

    def test_get_audio_data_success(self, sample_config: dict) -> None:
        """Test getting audio data successfully."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        test_data = b"test audio data"
        capture.audio_queue.put(test_data)
        
        result = capture.get_audio_data(timeout=1.0)
        assert result == test_data

    def test_get_audio_data_timeout(self, sample_config: dict) -> None:
        """Test getting audio data with timeout."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        result = capture.get_audio_data(timeout=0.1)
        assert result is None

    def test_get_audio_buffer_success(self, sample_config: dict) -> None:
        """Test getting audio buffer successfully."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        # Add enough data to the queue
        chunk_size = 16000 * 1 * 2  # 1 second of audio
        for _ in range(10):
            capture.audio_queue.put(b"x" * (chunk_size // 10))
        
        result = capture.get_audio_buffer(duration_seconds=1.0)
        assert result is not None
        assert len(result) >= chunk_size

    def test_get_audio_buffer_timeout(self, sample_config: dict) -> None:
        """Test getting audio buffer with timeout."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        result = capture.get_audio_buffer(duration_seconds=1.0)
        assert result is None

    def test_get_queue_size(self, sample_config: dict) -> None:
        """Test getting queue size."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        assert capture.get_queue_size() == 0
        
        capture.audio_queue.put(b"data1")
        capture.audio_queue.put(b"data2")
        
        assert capture.get_queue_size() == 2

    def test_clear_queue(self, sample_config: dict) -> None:
        """Test clearing the audio queue."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        capture.audio_queue.put(b"data1")
        capture.audio_queue.put(b"data2")
        
        assert capture.get_queue_size() == 2
        
        capture.clear_queue()
        assert capture.get_queue_size() == 0

    def test_list_devices_success(self, sample_config: dict, mock_sounddevice) -> None:
        """Test listing audio devices successfully."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        devices = capture.list_devices()
        assert devices == [{'name': 'Test Device', 'max_inputs': 1, 'max_outputs': 0}]

    def test_list_devices_error(self, sample_config: dict, mock_sounddevice) -> None:
        """Test listing audio devices with error."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        mock_sounddevice.query_devices.side_effect = Exception("Device error")
        
        with patch('whisprd.audio_capture.logger') as mock_logger:
            devices = capture.list_devices()
            assert devices == []
            mock_logger.error.assert_called_with("Error listing audio devices: Device error")

    def test_get_default_device_success(self, sample_config: dict, mock_sounddevice) -> None:
        """Test getting default device successfully."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        device = capture.get_default_device()
        assert device == 0

    def test_get_default_device_error(self, sample_config: dict, mock_sounddevice) -> None:
        """Test getting default device with error."""
        audio_config = sample_config['audio']
        capture = AudioCapture(audio_config)
        
        mock_sounddevice.default.device = Exception("Device error")
        
        with patch('whisprd.audio_capture.logger') as mock_logger:
            device = capture.get_default_device()
            assert device is None
            mock_logger.error.assert_called_with("Error getting default device: Device error")

    def test_context_manager(self, sample_config: dict, mock_sounddevice) -> None:
        """Test AudioCapture as context manager."""
        audio_config = sample_config['audio']
        mock_stream = Mock()
        mock_sounddevice.RawInputStream.return_value = mock_stream
        
        with AudioCapture(audio_config) as capture:
            assert capture.is_recording is True
            assert capture.stream == mock_stream
        
        # After context exit
        assert capture.is_recording is False
        assert capture.stream is None
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()

    def test_context_manager_with_exception(self, sample_config: dict, mock_sounddevice) -> None:
        """Test AudioCapture context manager with exception."""
        audio_config = sample_config['audio']
        mock_stream = Mock()
        mock_sounddevice.RawInputStream.return_value = mock_stream
        
        with pytest.raises(ValueError):
            with AudioCapture(audio_config) as capture:
                assert capture.is_recording is True
                raise ValueError("Test exception")
        
        # Should still clean up
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once() 
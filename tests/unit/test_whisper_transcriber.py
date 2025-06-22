"""
Unit tests for the whisper_transcriber module.
"""

import pytest
import numpy as np
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from whisprd.whisper_transcriber import WhisperTranscriber, check_cuda_availability, get_optimal_compute_type


class TestWhisperTranscriber:
    """Test cases for the WhisperTranscriber class."""

    def test_init_with_valid_config(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test WhisperTranscriber initialization with valid config."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        assert transcriber.model_size == 'tiny'
        assert transcriber.language == 'en'
        assert transcriber.beam_size == 5
        assert transcriber.best_of == 5
        assert transcriber.temperature == 0.0
        assert transcriber.condition_on_previous_text is True
        assert transcriber.initial_prompt == ''
        assert transcriber.use_cuda is False
        assert transcriber.device == 'cpu'
        assert transcriber.compute_type == 'int8'

    def test_init_with_cuda_config(self, mock_faster_whisper) -> None:
        """Test WhisperTranscriber initialization with CUDA config."""
        whisper_config = {
            'model_size': 'small',
            'language': 'en',
            'use_cuda': True,
            'cuda_device': 0,
            'gpu_memory_fraction': 0.8,
            'enable_memory_efficient_attention': True,
            'pause_duration': 1.0,
            'min_utterance_duration': 0.7
        }
        
        with patch('whisprd.whisper_transcriber.check_cuda_availability', return_value=True):
            transcriber = WhisperTranscriber(whisper_config)
            
            assert transcriber.use_cuda is True
            assert transcriber.cuda_device == 0
            assert transcriber.device == 'cuda'
            assert transcriber.compute_type == 'float16'

    def test_init_without_faster_whisper(self) -> None:
        """Test WhisperTranscriber initialization without faster-whisper."""
        whisper_config = {'model_size': 'tiny'}
        
        with patch('whisprd.whisper_transcriber.WHISPER_AVAILABLE', False):
            with pytest.raises(ImportError, match="faster-whisper is required but not installed"):
                WhisperTranscriber(whisper_config)

    def test_load_model_cpu_fallback(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test model loading with CPU fallback when CUDA fails."""
        whisper_config = sample_config['whisper']
        whisper_config['use_cuda'] = True
        
        # Mock CUDA check to fail
        with patch('whisprd.whisper_transcriber.check_cuda_availability', return_value=False):
            transcriber = WhisperTranscriber(whisper_config)
            
            assert transcriber.device == 'cpu'
            assert transcriber.compute_type == 'int8'

    def test_start_transcription_success(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test successful start of transcription."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        transcriber.start_transcription()
        
        assert transcriber.is_running is True
        assert transcriber.transcription_thread is not None
        assert transcriber.transcription_thread.is_alive()

    def test_start_transcription_already_running(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test starting transcription when already running."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        transcriber.is_running = True
        
        with patch('whisprd.whisper_transcriber.logger') as mock_logger:
            transcriber.start_transcription()
            mock_logger.warning.assert_called_with("Transcription already running")

    def test_stop_transcription_success(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test successful stop of transcription."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        transcriber.is_running = True
        transcriber.transcription_thread = Mock()
        
        transcriber.stop_transcription()
        
        assert transcriber.is_running is False
        transcriber.transcription_thread.join.assert_called_once_with(timeout=5.0)

    def test_stop_transcription_not_running(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test stopping transcription when not running."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        transcriber.is_running = False
        
        with patch('whisprd.whisper_transcriber.logger') as mock_logger:
            transcriber.stop_transcription()
            mock_logger.warning.assert_called_with("Transcription not running")

    def test_add_audio_data(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test adding audio data to the queue."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        test_data = b"test audio data"
        transcriber.add_audio_data(test_data)
        
        assert transcriber.audio_queue.qsize() == 1
        assert transcriber.audio_queue.get() == test_data

    def test_get_queue_size(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test getting queue size."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        assert transcriber.get_queue_size() == 0
        
        transcriber.audio_queue.put(b"data1")
        transcriber.audio_queue.put(b"data2")
        
        assert transcriber.get_queue_size() == 2

    def test_clear_queue(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test clearing the audio queue."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        transcriber.audio_queue.put(b"data1")
        transcriber.audio_queue.put(b"data2")
        
        assert transcriber.get_queue_size() == 2
        
        transcriber.clear_queue()
        assert transcriber.get_queue_size() == 0

    def test_is_silence_with_silence(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test silence detection with silent audio."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        # Create silent audio data
        silent_audio = np.zeros(16000, dtype=np.int16)
        
        assert transcriber._is_silence(silent_audio, threshold=0.01) is True

    def test_is_silence_with_sound(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test silence detection with audio containing sound."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        # Create audio data with sound
        audio_with_sound = np.random.randint(-1000, 1000, 16000, dtype=np.int16)
        
        assert transcriber._is_silence(audio_with_sound, threshold=0.01) is False

    def test_is_new_content_new_text(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test new content detection with new text."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        assert transcriber._is_new_content("Hello world", "Hello") is True
        assert transcriber._is_new_content("Hello world", "") is True

    def test_is_new_content_same_text(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test new content detection with same text."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        assert transcriber._is_new_content("Hello world", "Hello world") is False

    def test_is_new_content_similar_text(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test new content detection with similar text."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        # Test with very similar text (should be considered the same)
        assert transcriber._is_new_content("Hello world", "Hello world.") is False
        assert transcriber._is_new_content("Hello world", "Hello world!") is False

    def test_transcribe_audio_success(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test successful audio transcription."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        # Mock the model's transcribe method
        mock_result = Mock()
        mock_result.text = "Hello world"
        mock_result.language = "en"
        mock_result.language_probability = 0.99
        transcriber.model.transcribe.return_value = mock_result
        
        audio_data = b"test audio data"
        result = transcriber._transcribe_audio(audio_data)
        
        assert result == "Hello world"
        transcriber.model.transcribe.assert_called_once()

    def test_transcribe_audio_failure(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test audio transcription failure."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        # Mock the model's transcribe method to raise an exception
        transcriber.model.transcribe.side_effect = Exception("Transcription error")
        
        audio_data = b"test audio data"
        result = transcriber._transcribe_audio(audio_data)
        
        assert result is None

    def test_process_transcription_with_callback(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test processing transcription with callback."""
        whisper_config = sample_config['whisper']
        callback = Mock()
        transcriber = WhisperTranscriber(whisper_config, callback)
        
        transcriber._process_transcription("Hello world")
        
        callback.assert_called_once_with("Hello world")

    def test_process_transcription_without_callback(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test processing transcription without callback."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        # Should not raise any exception
        transcriber._process_transcription("Hello world")

    def test_context_manager(self, sample_config: Dict[str, Any], mock_faster_whisper) -> None:
        """Test WhisperTranscriber as context manager."""
        whisper_config = sample_config['whisper']
        transcriber = WhisperTranscriber(whisper_config)
        
        with transcriber as t:
            assert t.is_running is True
            assert t.transcription_thread is not None
        
        # After context exit
        assert t.is_running is False


class TestUtilityFunctions:
    """Test cases for utility functions."""

    def test_check_cuda_availability_with_cuda(self) -> None:
        """Test CUDA availability check when CUDA is available."""
        with patch('torch.cuda.is_available', return_value=True), \
             patch('torch.device') as mock_device, \
             patch('torch.tensor') as mock_tensor, \
             patch('torch.cuda.get_device_name', return_value='Test GPU'):
            
            result = check_cuda_availability()
            assert result is True

    def test_check_cuda_availability_without_cuda(self) -> None:
        """Test CUDA availability check when CUDA is not available."""
        with patch('torch.cuda.is_available', return_value=False):
            result = check_cuda_availability()
            assert result is False

    def test_check_cuda_availability_without_torch(self) -> None:
        """Test CUDA availability check when PyTorch is not available."""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'torch'")):
            result = check_cuda_availability()
            assert result is False

    def test_get_optimal_compute_type_cuda(self) -> None:
        """Test getting optimal compute type for CUDA."""
        result = get_optimal_compute_type("cuda", "small")
        assert result == "float16"

    def test_get_optimal_compute_type_cpu(self) -> None:
        """Test getting optimal compute type for CPU."""
        result = get_optimal_compute_type("cpu", "small")
        assert result == "int8"

    def test_get_optimal_compute_type_cpu_tiny_model(self) -> None:
        """Test getting optimal compute type for CPU with tiny model."""
        result = get_optimal_compute_type("cpu", "tiny")
        assert result == "int8" 
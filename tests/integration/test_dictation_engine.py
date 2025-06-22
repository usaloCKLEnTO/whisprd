"""
Integration tests for the dictation engine.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from whisprd.dictation_engine import DictationEngine


class TestDictationEngine:
    """Integration test cases for the DictationEngine class."""

    def test_init_with_valid_config(self, sample_config: Dict[str, Any]) -> None:
        """Test DictationEngine initialization with valid config."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            
            assert engine.config == sample_config
            assert engine.audio_capture == mock_audio
            assert engine.transcriber == mock_trans
            assert engine.command_processor == mock_proc
            assert engine.keystroke_injector == mock_inj
            assert engine.hotkey_manager == mock_hk
            assert engine.is_running is False
            assert engine.is_paused is False

    def test_start_dictation_success(self, sample_config: Dict[str, Any]) -> None:
        """Test successful start of dictation."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            engine.start_dictation()
            
            assert engine.is_running is True
            mock_audio.start_recording.assert_called_once()
            mock_trans.start_transcription.assert_called_once()
            mock_hk.start_listening.assert_called_once()

    def test_start_dictation_already_running(self, sample_config: Dict[str, Any]) -> None:
        """Test starting dictation when already running."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            engine.is_running = True
            
            with patch('whisprd.dictation_engine.logger') as mock_logger:
                engine.start_dictation()
                mock_logger.warning.assert_called_with("Dictation already running")

    def test_stop_dictation_success(self, sample_config: Dict[str, Any]) -> None:
        """Test successful stop of dictation."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            engine.is_running = True
            
            engine.stop_dictation()
            
            assert engine.is_running is False
            mock_audio.stop_recording.assert_called_once()
            mock_trans.stop_transcription.assert_called_once()
            mock_hk.stop_listening.assert_called_once()

    def test_stop_dictation_not_running(self, sample_config: Dict[str, Any]) -> None:
        """Test stopping dictation when not running."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            engine.is_running = False
            
            with patch('whisprd.dictation_engine.logger') as mock_logger:
                engine.stop_dictation()
                mock_logger.warning.assert_called_with("Dictation not running")

    def test_pause_dictation_success(self, sample_config: Dict[str, Any]) -> None:
        """Test successful pause of dictation."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            engine.is_running = True
            engine.is_paused = False
            
            engine.pause_dictation()
            
            assert engine.is_paused is True
            mock_audio.stop_recording.assert_called_once()
            mock_trans.stop_transcription.assert_called_once()

    def test_resume_dictation_success(self, sample_config: Dict[str, Any]) -> None:
        """Test successful resume of dictation."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            engine.is_running = True
            engine.is_paused = True
            
            engine.resume_dictation()
            
            assert engine.is_paused is False
            mock_audio.start_recording.assert_called_once()
            mock_trans.start_transcription.assert_called_once()

    def test_process_transcription_success(self, sample_config: Dict[str, Any]) -> None:
        """Test successful processing of transcription."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            # Mock command matches
            mock_match = Mock()
            mock_match.command = "new line"
            mock_match.action = "enter"
            mock_proc.process_text.return_value = [mock_match]
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            engine.is_running = True
            
            engine.process_transcription("Hello new line world")
            
            mock_proc.process_text.assert_called_once_with("Hello new line world")
            mock_inj.inject_command.assert_called_once_with("enter")

    def test_process_transcription_no_commands(self, sample_config: Dict[str, Any]) -> None:
        """Test processing transcription with no commands."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            # Mock no command matches
            mock_proc.process_text.return_value = []
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            engine.is_running = True
            
            engine.process_transcription("Hello world")
            
            mock_proc.process_text.assert_called_once_with("Hello world")
            mock_inj.inject_text.assert_called_once_with("Hello world")

    def test_process_transcription_paused(self, sample_config: Dict[str, Any]) -> None:
        """Test processing transcription when paused."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            engine.is_running = True
            engine.is_paused = True
            
            engine.process_transcription("Hello world")
            
            # Should not process when paused
            mock_proc.process_text.assert_not_called()
            mock_inj.inject_text.assert_not_called()

    def test_process_transcription_not_running(self, sample_config: Dict[str, Any]) -> None:
        """Test processing transcription when not running."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            engine.is_running = False
            
            engine.process_transcription("Hello world")
            
            # Should not process when not running
            mock_proc.process_text.assert_not_called()
            mock_inj.inject_text.assert_not_called()

    def test_clear_transcript(self, sample_config: Dict[str, Any]) -> None:
        """Test clearing transcript."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            engine.transcript = "Some transcript text"
            
            engine.clear_transcript()
            
            assert engine.transcript == ""

    def test_get_status(self, sample_config: Dict[str, Any]) -> None:
        """Test getting engine status."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            engine.is_running = True
            engine.is_paused = False
            engine.transcript = "Test transcript"
            
            status = engine.get_status()
            
            assert status['running'] is True
            assert status['paused'] is False
            assert status['transcript'] == "Test transcript"

    def test_context_manager(self, sample_config: Dict[str, Any]) -> None:
        """Test DictationEngine as context manager."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            with DictationEngine(sample_config) as engine:
                assert engine.is_running is True
                assert engine.audio_capture == mock_audio
                assert engine.transcriber == mock_trans
            
            # After context exit
            assert engine.is_running is False
            mock_audio.stop_recording.assert_called_once()
            mock_trans.stop_transcription.assert_called_once()
            mock_hk.stop_listening.assert_called_once()

    def test_context_manager_with_exception(self, sample_config: Dict[str, Any]) -> None:
        """Test DictationEngine context manager with exception."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            with pytest.raises(ValueError):
                with DictationEngine(sample_config) as engine:
                    assert engine.is_running is True
                    raise ValueError("Test exception")
            
            # Should still clean up
            mock_audio.stop_recording.assert_called_once()
            mock_trans.stop_transcription.assert_called_once()
            mock_hk.stop_listening.assert_called_once()

    def test_save_transcript(self, sample_config: Dict[str, Any], temp_dir: str) -> None:
        """Test saving transcript to file."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            engine.transcript = "Test transcript content"
            
            transcript_file = f"{temp_dir}/test_transcript.txt"
            engine.save_transcript(transcript_file)
            
            # Check that file was created with content
            with open(transcript_file, 'r') as f:
                content = f.read()
                assert content == "Test transcript content"

    def test_load_transcript(self, sample_config: Dict[str, Any], temp_dir: str) -> None:
        """Test loading transcript from file."""
        with patch('whisprd.dictation_engine.AudioCapture') as mock_audio_capture, \
             patch('whisprd.dictation_engine.WhisperTranscriber') as mock_transcriber, \
             patch('whisprd.dictation_engine.CommandProcessor') as mock_processor, \
             patch('whisprd.dictation_engine.KeystrokeInjector') as mock_injector, \
             patch('whisprd.dictation_engine.HotkeyManager') as mock_hotkey:
            
            mock_audio = Mock()
            mock_trans = Mock()
            mock_proc = Mock()
            mock_inj = Mock()
            mock_hk = Mock()
            
            mock_audio_capture.return_value = mock_audio
            mock_transcriber.return_value = mock_trans
            mock_processor.return_value = mock_proc
            mock_injector.return_value = mock_inj
            mock_hotkey.return_value = mock_hk
            
            engine = DictationEngine(sample_config)
            
            transcript_file = f"{temp_dir}/test_transcript.txt"
            with open(transcript_file, 'w') as f:
                f.write("Loaded transcript content")
            
            engine.load_transcript(transcript_file)
            
            assert engine.transcript == "Loaded transcript content" 
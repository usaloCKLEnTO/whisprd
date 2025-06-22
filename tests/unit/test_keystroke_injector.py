"""
Unit tests for the keystroke_injector module.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from whisprd.keystroke_injector import KeystrokeInjector


class TestKeystrokeInjector:
    """Test cases for the KeystrokeInjector class."""

    def test_init_with_valid_config(self, sample_config: Dict[str, Any]) -> None:
        """Test KeystrokeInjector initialization with valid config."""
        output_config = sample_config['output']
        injector = KeystrokeInjector(output_config)
        
        assert injector.config == output_config
        assert injector.device is None
        assert injector.is_initialized is False

    def test_init_with_custom_config(self) -> None:
        """Test KeystrokeInjector initialization with custom config."""
        output_config = {
            'keystroke_delay': 0.1,
            'max_retries': 5,
            'retry_delay': 0.05
        }
        injector = KeystrokeInjector(output_config)
        
        assert injector.keystroke_delay == 0.1
        assert injector.max_retries == 5
        assert injector.retry_delay == 0.05

    def test_initialize_success(self, mock_uinput) -> None:
        """Test successful initialization."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        mock_device = Mock()
        mock_uinput.Device.return_value = mock_device
        
        injector.initialize()
        
        assert injector.is_initialized is True
        assert injector.device == mock_device
        mock_uinput.Device.assert_called_once()

    def test_initialize_failure(self, mock_uinput) -> None:
        """Test initialization failure."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        mock_uinput.Device.side_effect = Exception("Device error")
        
        with pytest.raises(Exception, match="Device error"):
            injector.initialize()

    def test_initialize_already_initialized(self, mock_uinput) -> None:
        """Test initialization when already initialized."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        injector.is_initialized = True
        
        injector.initialize()  # Should not raise exception
        
        # Should not call uinput.Device again
        mock_uinput.Device.assert_not_called()

    def test_cleanup_success(self) -> None:
        """Test successful cleanup."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        injector.is_initialized = True
        injector.device = Mock()
        
        injector.cleanup()
        
        assert injector.is_initialized is False
        assert injector.device is None

    def test_cleanup_not_initialized(self) -> None:
        """Test cleanup when not initialized."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        injector.is_initialized = False
        
        # Should not raise exception
        injector.cleanup()

    def test_inject_text_success(self, mock_uinput) -> None:
        """Test successful text injection."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        mock_device = Mock()
        mock_uinput.Device.return_value = mock_device
        injector.initialize()
        
        injector.inject_text("Hello")
        
        # Should call emit for each character
        assert mock_device.emit.call_count == 5  # 5 characters in "Hello"

    def test_inject_text_not_initialized(self) -> None:
        """Test text injection when not initialized."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        with pytest.raises(RuntimeError, match="KeystrokeInjector not initialized"):
            injector.inject_text("Hello")

    def test_inject_text_empty(self, mock_uinput) -> None:
        """Test text injection with empty text."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        mock_device = Mock()
        mock_uinput.Device.return_value = mock_device
        injector.initialize()
        
        injector.inject_text("")
        
        # Should not call emit for empty text
        mock_device.emit.assert_not_called()

    def test_inject_text_with_special_characters(self, mock_uinput) -> None:
        """Test text injection with special characters."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        mock_device = Mock()
        mock_uinput.Device.return_value = mock_device
        injector.initialize()
        
        injector.inject_text("Hello\nWorld\tTest")
        
        # Should call emit for each character including special chars
        assert mock_device.emit.call_count > 0

    def test_inject_key_success(self, mock_uinput) -> None:
        """Test successful key injection."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        mock_device = Mock()
        mock_uinput.Device.return_value = mock_device
        injector.initialize()
        
        injector.inject_key("KEY_ENTER")
        
        mock_device.emit.assert_called_once()

    def test_inject_key_not_initialized(self) -> None:
        """Test key injection when not initialized."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        with pytest.raises(RuntimeError, match="KeystrokeInjector not initialized"):
            injector.inject_key("KEY_ENTER")

    def test_inject_key_sequence_success(self, mock_uinput) -> None:
        """Test successful key sequence injection."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        mock_device = Mock()
        mock_uinput.Device.return_value = mock_device
        injector.initialize()
        
        injector.inject_key_sequence(["KEY_CTRL", "KEY_A"])
        
        # Should call emit for each key in sequence
        assert mock_device.emit.call_count == 2

    def test_inject_key_sequence_not_initialized(self) -> None:
        """Test key sequence injection when not initialized."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        with pytest.raises(RuntimeError, match="KeystrokeInjector not initialized"):
            injector.inject_key_sequence(["KEY_CTRL", "KEY_A"])

    def test_inject_key_sequence_empty(self, mock_uinput) -> None:
        """Test key sequence injection with empty sequence."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        mock_device = Mock()
        mock_uinput.Device.return_value = mock_device
        injector.initialize()
        
        injector.inject_key_sequence([])
        
        # Should not call emit for empty sequence
        mock_device.emit.assert_not_called()

    def test_parse_key_sequence_simple(self) -> None:
        """Test parsing simple key sequence."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        result = injector.parse_key_sequence("ctrl+a")
        assert result == ["KEY_CTRL", "KEY_A"]

    def test_parse_key_sequence_complex(self) -> None:
        """Test parsing complex key sequence."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        result = injector.parse_key_sequence("ctrl+shift+delete")
        assert result == ["KEY_CTRL", "KEY_SHIFT", "KEY_DELETE"]

    def test_parse_key_sequence_single_key(self) -> None:
        """Test parsing single key."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        result = injector.parse_key_sequence("enter")
        assert result == ["KEY_ENTER"]

    def test_parse_key_sequence_with_spaces(self) -> None:
        """Test parsing key sequence with spaces."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        result = injector.parse_key_sequence("ctrl + a")
        assert result == ["KEY_CTRL", "KEY_A"]

    def test_parse_key_sequence_unknown_key(self) -> None:
        """Test parsing key sequence with unknown key."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        result = injector.parse_key_sequence("ctrl+unknown")
        assert result == ["KEY_CTRL", "KEY_UNKNOWN"]

    def test_inject_command_success(self, mock_uinput) -> None:
        """Test successful command injection."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        mock_device = Mock()
        mock_uinput.Device.return_value = mock_device
        injector.initialize()
        
        injector.inject_command("ctrl+a")
        
        mock_device.emit.assert_called()

    def test_inject_command_not_initialized(self) -> None:
        """Test command injection when not initialized."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        with pytest.raises(RuntimeError, match="KeystrokeInjector not initialized"):
            injector.inject_command("ctrl+a")

    def test_inject_command_with_retry(self, mock_uinput) -> None:
        """Test command injection with retry logic."""
        output_config = {
            'keystroke_delay': 0.05,
            'max_retries': 3,
            'retry_delay': 0.01
        }
        injector = KeystrokeInjector(output_config)
        
        mock_device = Mock()
        mock_device.emit.side_effect = [Exception("Error"), Exception("Error"), None]
        mock_uinput.Device.return_value = mock_device
        injector.initialize()
        
        # Should succeed on third try
        injector.inject_command("ctrl+a")
        
        assert mock_device.emit.call_count == 3

    def test_inject_command_max_retries_exceeded(self, mock_uinput) -> None:
        """Test command injection with max retries exceeded."""
        output_config = {
            'keystroke_delay': 0.05,
            'max_retries': 2,
            'retry_delay': 0.01
        }
        injector = KeystrokeInjector(output_config)
        
        mock_device = Mock()
        mock_device.emit.side_effect = Exception("Error")
        mock_uinput.Device.return_value = mock_device
        injector.initialize()
        
        with pytest.raises(Exception, match="Error"):
            injector.inject_command("ctrl+a")

    def test_context_manager(self, mock_uinput) -> None:
        """Test KeystrokeInjector as context manager."""
        output_config = {'keystroke_delay': 0.05}
        mock_device = Mock()
        mock_uinput.Device.return_value = mock_device
        
        with KeystrokeInjector(output_config) as injector:
            assert injector.is_initialized is True
            assert injector.device == mock_device
        
        # After context exit
        assert injector.is_initialized is False
        assert injector.device is None

    def test_context_manager_with_exception(self, mock_uinput) -> None:
        """Test KeystrokeInjector context manager with exception."""
        output_config = {'keystroke_delay': 0.05}
        mock_device = Mock()
        mock_uinput.Device.return_value = mock_device
        
        with pytest.raises(ValueError):
            with KeystrokeInjector(output_config) as injector:
                assert injector.is_initialized is True
                raise ValueError("Test exception")
        
        # Should still clean up
        assert injector.is_initialized is False
        assert injector.device is None

    def test_get_key_code_valid(self) -> None:
        """Test getting valid key code."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        key_code = injector.get_key_code("KEY_ENTER")
        assert key_code is not None

    def test_get_key_code_invalid(self) -> None:
        """Test getting invalid key code."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        key_code = injector.get_key_code("INVALID_KEY")
        assert key_code is None

    def test_is_initialized_property(self, mock_uinput) -> None:
        """Test is_initialized property."""
        output_config = {'keystroke_delay': 0.05}
        injector = KeystrokeInjector(output_config)
        
        assert injector.is_initialized is False
        
        mock_device = Mock()
        mock_uinput.Device.return_value = mock_device
        injector.initialize()
        
        assert injector.is_initialized is True 
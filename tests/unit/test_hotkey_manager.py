"""
Unit tests for the hotkey_manager module.
"""

import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Callable

from whisprd.hotkey_manager import HotkeyManager


class TestHotkeyManager:
    """Test cases for the HotkeyManager class."""

    def test_init_with_valid_config(self, sample_config: Dict[str, Any]) -> None:
        """Test HotkeyManager initialization with valid config."""
        hotkey_config = {
            'start_stop_key': 'ctrl+shift+d',
            'pause_resume_key': 'ctrl+shift+p',
            'clear_key': 'ctrl+shift+c'
        }
        manager = HotkeyManager(hotkey_config)
        
        assert manager.config == hotkey_config
        assert manager.start_stop_key == 'ctrl+shift+d'
        assert manager.pause_resume_key == 'ctrl+shift+p'
        assert manager.clear_key == 'ctrl+shift+c'
        assert manager.is_listening is False
        assert manager.listener is None

    def test_init_with_default_config(self) -> None:
        """Test HotkeyManager initialization with default config."""
        manager = HotkeyManager({})
        
        assert manager.start_stop_key == 'ctrl+shift+d'
        assert manager.pause_resume_key == 'ctrl+shift+p'
        assert manager.clear_key == 'ctrl+shift+c'

    def test_start_listening_success(self, mock_pynput) -> None:
        """Test successful start of hotkey listening."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        mock_listener = Mock()
        mock_pynput.keyboard.Listener.return_value = mock_listener
        
        manager.start_listening()
        
        assert manager.is_listening is True
        assert manager.listener == mock_listener
        mock_listener.start.assert_called_once()

    def test_start_listening_already_listening(self, mock_pynput) -> None:
        """Test starting listening when already listening."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        manager.is_listening = True
        
        with patch('whisprd.hotkey_manager.logger') as mock_logger:
            manager.start_listening()
            mock_logger.warning.assert_called_with("Hotkey listener already running")

    def test_start_listening_failure(self, mock_pynput) -> None:
        """Test starting listening with failure."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        mock_pynput.keyboard.Listener.side_effect = Exception("Listener error")
        
        with pytest.raises(Exception, match="Listener error"):
            manager.start_listening()

    def test_stop_listening_success(self) -> None:
        """Test successful stop of hotkey listening."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        manager.is_listening = True
        manager.listener = Mock()
        
        manager.stop_listening()
        
        assert manager.is_listening is False
        assert manager.listener is None
        manager.listener.stop.assert_called_once()

    def test_stop_listening_not_listening(self) -> None:
        """Test stopping listening when not listening."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        manager.is_listening = False
        
        with patch('whisprd.hotkey_manager.logger') as mock_logger:
            manager.stop_listening()
            mock_logger.warning.assert_called_with("Hotkey listener not running")

    def test_stop_listening_with_error(self) -> None:
        """Test stopping listening with error."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        manager.is_listening = True
        manager.listener = Mock()
        manager.listener.stop.side_effect = Exception("Stop error")
        
        with patch('whisprd.hotkey_manager.logger') as mock_logger:
            manager.stop_listening()
            mock_logger.error.assert_called_with("Error stopping hotkey listener: Stop error")

    def test_set_callbacks(self) -> None:
        """Test setting callbacks."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        start_callback = Mock()
        pause_callback = Mock()
        clear_callback = Mock()
        
        manager.set_callbacks(start_callback, pause_callback, clear_callback)
        
        assert manager.start_callback == start_callback
        assert manager.pause_callback == pause_callback
        assert manager.clear_callback == clear_callback

    def test_on_key_press_start_stop_key(self) -> None:
        """Test key press handling for start/stop key."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        start_callback = Mock()
        manager.set_callbacks(start_callback, None, None)
        
        # Mock key object
        mock_key = Mock()
        mock_key.name = 'd'
        
        # Mock current pressed keys
        manager.current_keys = {'ctrl', 'shift', 'd'}
        
        manager.on_key_press(mock_key)
        
        start_callback.assert_called_once()

    def test_on_key_press_pause_resume_key(self) -> None:
        """Test key press handling for pause/resume key."""
        hotkey_config = {'pause_resume_key': 'ctrl+shift+p'}
        manager = HotkeyManager(hotkey_config)
        
        pause_callback = Mock()
        manager.set_callbacks(None, pause_callback, None)
        
        # Mock key object
        mock_key = Mock()
        mock_key.name = 'p'
        
        # Mock current pressed keys
        manager.current_keys = {'ctrl', 'shift', 'p'}
        
        manager.on_key_press(mock_key)
        
        pause_callback.assert_called_once()

    def test_on_key_press_clear_key(self) -> None:
        """Test key press handling for clear key."""
        hotkey_config = {'clear_key': 'ctrl+shift+c'}
        manager = HotkeyManager(hotkey_config)
        
        clear_callback = Mock()
        manager.set_callbacks(None, None, clear_callback)
        
        # Mock key object
        mock_key = Mock()
        mock_key.name = 'c'
        
        # Mock current pressed keys
        manager.current_keys = {'ctrl', 'shift', 'c'}
        
        manager.on_key_press(mock_key)
        
        clear_callback.assert_called_once()

    def test_on_key_press_no_match(self) -> None:
        """Test key press handling for non-matching key."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        start_callback = Mock()
        manager.set_callbacks(start_callback, None, None)
        
        # Mock key object
        mock_key = Mock()
        mock_key.name = 'x'
        
        # Mock current pressed keys
        manager.current_keys = {'ctrl', 'shift', 'x'}
        
        manager.on_key_press(mock_key)
        
        start_callback.assert_not_called()

    def test_on_key_press_partial_match(self) -> None:
        """Test key press handling for partial key match."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        start_callback = Mock()
        manager.set_callbacks(start_callback, None, None)
        
        # Mock key object
        mock_key = Mock()
        mock_key.name = 'd'
        
        # Mock current pressed keys (missing shift)
        manager.current_keys = {'ctrl', 'd'}
        
        manager.on_key_press(mock_key)
        
        start_callback.assert_not_called()

    def test_on_key_release(self) -> None:
        """Test key release handling."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        # Mock key object
        mock_key = Mock()
        mock_key.name = 'd'
        
        # Add key to current keys
        manager.current_keys = {'ctrl', 'shift', 'd'}
        
        manager.on_key_release(mock_key)
        
        # Key should be removed from current keys
        assert 'd' not in manager.current_keys
        assert 'ctrl' in manager.current_keys
        assert 'shift' in manager.current_keys

    def test_on_key_release_unknown_key(self) -> None:
        """Test key release handling for unknown key."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        # Mock key object
        mock_key = Mock()
        mock_key.name = 'unknown'
        
        # Add key to current keys
        manager.current_keys = {'ctrl', 'shift', 'unknown'}
        
        manager.on_key_release(mock_key)
        
        # Key should be removed from current keys
        assert 'unknown' not in manager.current_keys

    def test_parse_hotkey_simple(self) -> None:
        """Test parsing simple hotkey."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        result = manager.parse_hotkey('ctrl+a')
        assert result == {'ctrl', 'a'}

    def test_parse_hotkey_complex(self) -> None:
        """Test parsing complex hotkey."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        result = manager.parse_hotkey('ctrl+shift+alt+delete')
        assert result == {'ctrl', 'shift', 'alt', 'delete'}

    def test_parse_hotkey_single_key(self) -> None:
        """Test parsing single key hotkey."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        result = manager.parse_hotkey('f1')
        assert result == {'f1'}

    def test_parse_hotkey_with_spaces(self) -> None:
        """Test parsing hotkey with spaces."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        result = manager.parse_hotkey('ctrl + shift + d')
        assert result == {'ctrl', 'shift', 'd'}

    def test_parse_hotkey_case_insensitive(self) -> None:
        """Test parsing hotkey with case insensitive keys."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        result = manager.parse_hotkey('CTRL+SHIFT+D')
        assert result == {'ctrl', 'shift', 'd'}

    def test_is_hotkey_pressed_match(self) -> None:
        """Test hotkey pressed detection with match."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        manager.current_keys = {'ctrl', 'shift', 'd'}
        
        assert manager.is_hotkey_pressed('ctrl+shift+d') is True

    def test_is_hotkey_pressed_no_match(self) -> None:
        """Test hotkey pressed detection with no match."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        manager.current_keys = {'ctrl', 'shift', 'x'}
        
        assert manager.is_hotkey_pressed('ctrl+shift+d') is False

    def test_is_hotkey_pressed_partial_match(self) -> None:
        """Test hotkey pressed detection with partial match."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        manager.current_keys = {'ctrl', 'd'}
        
        assert manager.is_hotkey_pressed('ctrl+shift+d') is False

    def test_is_hotkey_pressed_extra_keys(self) -> None:
        """Test hotkey pressed detection with extra keys pressed."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        manager.current_keys = {'ctrl', 'shift', 'd', 'alt'}
        
        assert manager.is_hotkey_pressed('ctrl+shift+d') is True

    def test_context_manager(self, mock_pynput) -> None:
        """Test HotkeyManager as context manager."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        mock_listener = Mock()
        mock_pynput.keyboard.Listener.return_value = mock_listener
        
        with HotkeyManager(hotkey_config) as manager:
            assert manager.is_listening is True
            assert manager.listener == mock_listener
        
        # After context exit
        assert manager.is_listening is False
        assert manager.listener is None
        mock_listener.stop.assert_called_once()

    def test_context_manager_with_exception(self, mock_pynput) -> None:
        """Test HotkeyManager context manager with exception."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        mock_listener = Mock()
        mock_pynput.keyboard.Listener.return_value = mock_listener
        
        with pytest.raises(ValueError):
            with HotkeyManager(hotkey_config) as manager:
                assert manager.is_listening is True
                raise ValueError("Test exception")
        
        # Should still clean up
        mock_listener.stop.assert_called_once()

    def test_get_current_keys(self) -> None:
        """Test getting current pressed keys."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        manager.current_keys = {'ctrl', 'shift', 'd'}
        
        result = manager.get_current_keys()
        assert result == {'ctrl', 'shift', 'd'}

    def test_clear_current_keys(self) -> None:
        """Test clearing current pressed keys."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        manager.current_keys = {'ctrl', 'shift', 'd'}
        
        manager.clear_current_keys()
        
        assert manager.current_keys == set()

    def test_update_config(self) -> None:
        """Test updating configuration."""
        hotkey_config = {'start_stop_key': 'ctrl+shift+d'}
        manager = HotkeyManager(hotkey_config)
        
        new_config = {
            'start_stop_key': 'ctrl+shift+x',
            'pause_resume_key': 'ctrl+shift+y',
            'clear_key': 'ctrl+shift+z'
        }
        
        manager.update_config(new_config)
        
        assert manager.start_stop_key == 'ctrl+shift+x'
        assert manager.pause_resume_key == 'ctrl+shift+y'
        assert manager.clear_key == 'ctrl+shift+z' 
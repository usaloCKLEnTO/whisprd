"""
Hotkey manager for global hotkey detection.
"""

import threading
import time
from typing import Dict, Any, List, Optional, Callable
import logging

try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logging.warning("pynput not available. Install with: pip install pynput")

logger = logging.getLogger(__name__)


class HotkeyManager:
    """Global hotkey manager using pynput."""
    
    def __init__(self, config: Dict[str, Any], hotkey_callback: Optional[Callable] = None):
        """
        Initialize hotkey manager.
        
        Args:
            config: Dictation configuration dictionary
            hotkey_callback: Callback function for hotkey events
        """
        if not PYNPUT_AVAILABLE:
            raise ImportError("pynput is required but not installed")
        
        self.config = config
        self.hotkey_callback = hotkey_callback
        self.listener = None
        self.is_listening = False
        
        # Parse hotkey configuration
        self.hotkey_combination = self._parse_hotkey_config()
        self.pressed_keys = set()
        
        logger.info(f"Hotkey manager initialized with hotkey: {self.hotkey_combination}")
    
    def _parse_hotkey_config(self) -> List[str]:
        """Parse hotkey configuration from config."""
        hotkey_config = self.config.get('toggle_hotkey', ['ctrl', 'alt', 'd'])
        
        if isinstance(hotkey_config, list):
            return [str(key).lower() for key in hotkey_config]
        else:
            logger.warning("Invalid hotkey configuration, using default: Ctrl+Alt+D")
            return ['ctrl', 'alt', 'd']
    
    def _key_to_string(self, key) -> str:
        """Convert pynput key to string representation."""
        if isinstance(key, KeyCode):
            return key.char.lower() if key.char else str(key)
        elif isinstance(key, Key):
            return key.name.lower() if key.name else str(key)
        else:
            return str(key).lower()
    
    def _string_to_key(self, key_str: str):
        """Convert string to pynput key."""
        key_str = key_str.lower()
        
        # Map common key names
        key_mapping = {
            'ctrl': Key.ctrl,
            'alt': Key.alt,
            'shift': Key.shift,
            'cmd': Key.cmd,
            'super': Key.cmd,
            'meta': Key.cmd,
            'enter': Key.enter,
            'return': Key.enter,
            'space': Key.space,
            'tab': Key.tab,
            'escape': Key.esc,
            'esc': Key.esc,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'home': Key.home,
            'end': Key.end,
            'page_up': Key.page_up,
            'page_down': Key.page_down,
            'f1': Key.f1,
            'f2': Key.f2,
            'f3': Key.f3,
            'f4': Key.f4,
            'f5': Key.f5,
            'f6': Key.f6,
            'f7': Key.f7,
            'f8': Key.f8,
            'f9': Key.f9,
            'f10': Key.f10,
            'f11': Key.f11,
            'f12': Key.f12,
        }
        
        if key_str in key_mapping:
            return key_mapping[key_str]
        elif len(key_str) == 1:
            return KeyCode.from_char(key_str)
        else:
            logger.warning(f"Unknown key: {key_str}")
            return None
    
    def _on_press(self, key):
        """Handle key press events."""
        try:
            key_str = self._key_to_string(key)
            self.pressed_keys.add(key_str)
            
            logger.debug(f"Key pressed: {key_str}, pressed keys: {self.pressed_keys}")
            
            # Check if hotkey combination is pressed
            if self._is_hotkey_pressed():
                logger.info("Hotkey combination detected")
                if self.hotkey_callback:
                    self.hotkey_callback()
                
        except Exception as e:
            logger.error(f"Error handling key press: {e}")
    
    def _on_release(self, key):
        """Handle key release events."""
        try:
            key_str = self._key_to_string(key)
            if key_str in self.pressed_keys:
                self.pressed_keys.remove(key_str)
            
            logger.debug(f"Key released: {key_str}, pressed keys: {self.pressed_keys}")
            
        except Exception as e:
            logger.error(f"Error handling key release: {e}")
    
    def _is_hotkey_pressed(self) -> bool:
        """Check if the configured hotkey combination is pressed."""
        required_keys = set(self.hotkey_combination)
        return required_keys.issubset(self.pressed_keys)
    
    def start_listening(self):
        """Start listening for hotkeys."""
        if self.is_listening:
            logger.warning("Hotkey listener already running")
            return
        
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            self.is_listening = True
            
            logger.info("Hotkey listener started")
            
        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}")
            raise
    
    def stop_listening(self):
        """Stop listening for hotkeys."""
        if not self.is_listening:
            logger.warning("Hotkey listener not running")
            return
        
        try:
            if self.listener:
                self.listener.stop()
                self.listener.join(timeout=5.0)
                self.listener = None
            
            self.is_listening = False
            self.pressed_keys.clear()
            
            logger.info("Hotkey listener stopped")
            
        except Exception as e:
            logger.error(f"Error stopping hotkey listener: {e}")
    
    def update_hotkey(self, new_hotkey: List[str]):
        """
        Update the hotkey combination.
        
        Args:
            new_hotkey: New hotkey combination as list of strings
        """
        self.hotkey_combination = [str(key).lower() for key in new_hotkey]
        self.pressed_keys.clear()
        
        logger.info(f"Hotkey updated to: {self.hotkey_combination}")
    
    def get_current_hotkey(self) -> List[str]:
        """
        Get the current hotkey combination.
        
        Returns:
            Current hotkey combination
        """
        return self.hotkey_combination.copy()
    
    def is_listener_active(self) -> bool:
        """
        Check if the listener is active.
        
        Returns:
            True if listener is active
        """
        return self.is_listening and self.listener and self.listener.is_alive()
    
    def get_pressed_keys(self) -> set:
        """
        Get currently pressed keys.
        
        Returns:
            Set of currently pressed keys
        """
        return self.pressed_keys.copy()
    
    def clear_pressed_keys(self):
        """Clear the set of pressed keys."""
        self.pressed_keys.clear()
    
    def test_hotkey(self) -> bool:
        """
        Test if the current hotkey combination is pressed.
        
        Returns:
            True if hotkey is currently pressed
        """
        return self._is_hotkey_pressed()
    
    def __enter__(self):
        """Context manager entry."""
        self.start_listening()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_listening() 
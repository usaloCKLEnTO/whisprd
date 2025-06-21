"""
Keystroke injection module using uinput.
"""

import time
import threading
from typing import Dict, Any, List, Optional
import logging

try:
    import uinput
    UINPUT_AVAILABLE = True
except ImportError:
    UINPUT_AVAILABLE = False
    logging.warning("python-uinput not available. Install with: pip install python-uinput")

logger = logging.getLogger(__name__)


class KeystrokeInjector:
    """Keystroke injection using uinput."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize keystroke injector.
        
        Args:
            config: Output configuration dictionary
        """
        if not UINPUT_AVAILABLE:
            raise ImportError("python-uinput is required but not installed")
        
        self.config = config
        self.device = None
        self.is_initialized = False
        
        # Key mappings
        self.key_mappings = self._create_key_mappings()
        
        # Initialize uinput device
        self._initialize_device()
        
        logger.info("Keystroke injector initialized")
    
    def _create_key_mappings(self) -> Dict[str, int]:
        """Create key code mappings."""
        return {
            # Letters
            'a': uinput.KEY_A, 'b': uinput.KEY_B, 'c': uinput.KEY_C, 'd': uinput.KEY_D,
            'e': uinput.KEY_E, 'f': uinput.KEY_F, 'g': uinput.KEY_G, 'h': uinput.KEY_H,
            'i': uinput.KEY_I, 'j': uinput.KEY_J, 'k': uinput.KEY_K, 'l': uinput.KEY_L,
            'm': uinput.KEY_M, 'n': uinput.KEY_N, 'o': uinput.KEY_O, 'p': uinput.KEY_P,
            'q': uinput.KEY_Q, 'r': uinput.KEY_R, 's': uinput.KEY_S, 't': uinput.KEY_T,
            'u': uinput.KEY_U, 'v': uinput.KEY_V, 'w': uinput.KEY_W, 'x': uinput.KEY_X,
            'y': uinput.KEY_Y, 'z': uinput.KEY_Z,
            # Numbers
            '0': uinput.KEY_0, '1': uinput.KEY_1, '2': uinput.KEY_2, '3': uinput.KEY_3,
            '4': uinput.KEY_4, '5': uinput.KEY_5, '6': uinput.KEY_6, '7': uinput.KEY_7,
            '8': uinput.KEY_8, '9': uinput.KEY_9,
            # Punctuation (only those available)
            '.': uinput.KEY_DOT, ',': uinput.KEY_COMMA, ';': uinput.KEY_SEMICOLON,
            ':': uinput.KEY_SEMICOLON,  # Shift+semicolon for colon
            '(': uinput.KEY_9,  # Shift+9
            ')': uinput.KEY_0,  # Shift+0
            '[': uinput.KEY_LEFTBRACE, ']': uinput.KEY_RIGHTBRACE,
            "'": uinput.KEY_APOSTROPHE, '"': uinput.KEY_APOSTROPHE,  # Shift+apostrophe for double quote
            '!': uinput.KEY_1,  # Shift+1
            '?': uinput.KEY_SLASH,  # Shift+slash
            # Special keys
            ' ': uinput.KEY_SPACE, '\n': uinput.KEY_ENTER, '\t': uinput.KEY_TAB,
            'backspace': uinput.KEY_BACKSPACE, 'delete': uinput.KEY_DELETE,
            'enter': uinput.KEY_ENTER, 'return': uinput.KEY_ENTER,
            'escape': uinput.KEY_ESC, 'tab': uinput.KEY_TAB,
            # Modifier keys
            'ctrl': uinput.KEY_LEFTCTRL, 'shift': uinput.KEY_LEFTSHIFT, 'alt': uinput.KEY_LEFTALT,
            'meta': uinput.KEY_LEFTMETA, 'super': uinput.KEY_LEFTMETA,
            # Navigation
            'up': uinput.KEY_UP, 'down': uinput.KEY_DOWN, 'left': uinput.KEY_LEFT, 'right': uinput.KEY_RIGHT,
            'home': uinput.KEY_HOME, 'end': uinput.KEY_END, 'pageup': uinput.KEY_PAGEUP, 'pagedown': uinput.KEY_PAGEDOWN,
            # Function keys
            'f1': uinput.KEY_F1, 'f2': uinput.KEY_F2, 'f3': uinput.KEY_F3, 'f4': uinput.KEY_F4,
            'f5': uinput.KEY_F5, 'f6': uinput.KEY_F6, 'f7': uinput.KEY_F7, 'f8': uinput.KEY_F8,
            'f9': uinput.KEY_F9, 'f10': uinput.KEY_F10, 'f11': uinput.KEY_F11, 'f12': uinput.KEY_F12,
        }
    
    def _initialize_device(self):
        """Initialize uinput device."""
        try:
            # Get all available key codes
            all_keys = list(self.key_mappings.values())
            
            # Create virtual keyboard device
            self.device = uinput.Device(all_keys)
            self.is_initialized = True
            
            logger.info("Uinput device initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize uinput device: {e}")
            logger.error("Make sure you have appropriate permissions (run with sudo or add user to input group)")
            raise
    
    def inject_text(self, text: str, delay: float = 0.01):
        """
        Inject text as keystrokes.
        
        Args:
            text: Text to inject
            delay: Delay between keystrokes in seconds
        """
        if not self.is_initialized:
            logger.error("Keystroke injector not initialized")
            return
        
        try:
            for char in text:
                self._inject_character(char)
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"Error injecting text: {e}")
    
    def _inject_character(self, char: str):
        """Inject a single character."""
        char_lower = char.lower()
        # Handle uppercase letters
        if char.isupper() and char_lower in self.key_mappings:
            self._inject_key_combination([uinput.KEY_LEFTSHIFT, self.key_mappings[char_lower]])
            return
        # Handle symbols that require shift
        shift_symbols = {
            ':': uinput.KEY_SEMICOLON,
            '(': uinput.KEY_9,
            ')': uinput.KEY_0,
            '!': uinput.KEY_1,
            '?': uinput.KEY_SLASH,
            '"': uinput.KEY_APOSTROPHE,
        }
        if char in shift_symbols:
            self._inject_key_combination([uinput.KEY_LEFTSHIFT, shift_symbols[char]])
            return
        # Handle regular characters
        if char in self.key_mappings:
            self._inject_key(self.key_mappings[char])
        elif char_lower in self.key_mappings:
            self._inject_key(self.key_mappings[char_lower])
        else:
            logger.warning(f"Unknown character: {char}")
    
    def _inject_key(self, key_code: int):
        """Inject a single key press and release."""
        try:
            self.device.emit(key_code, 1)  # Key down
            time.sleep(0.01)
            self.device.emit(key_code, 0)  # Key up
        except Exception as e:
            logger.error(f"Error injecting key {key_code}: {e}")
    
    def _inject_key_combination(self, key_codes: List[int]):
        """Inject a key combination (e.g., Shift+A)."""
        try:
            # Press all keys
            for key_code in key_codes:
                self.device.emit(key_code, 1)
            
            time.sleep(0.01)
            
            # Release all keys in reverse order
            for key_code in reversed(key_codes):
                self.device.emit(key_code, 0)
                
        except Exception as e:
            logger.error(f"Error injecting key combination: {e}")
    
    def inject_command(self, command: str):
        """
        Inject a command string (e.g., "KEY_CTRL+KEY_A").
        
        Args:
            command: Command string to inject
        """
        if not self.is_initialized:
            logger.error("Keystroke injector not initialized")
            return
        
        try:
            # Parse command string
            if '+' in command:
                # Key combination
                keys = command.split('+')
                key_codes = []
                
                for key_name in keys:
                    key_name = key_name.strip()
                    if key_name.startswith('KEY_'):
                        key_name = key_name[4:].lower()  # Remove 'KEY_' prefix
                    
                    if key_name in self.key_mappings:
                        key_codes.append(self.key_mappings[key_name])
                    else:
                        logger.warning(f"Unknown key: {key_name}")
                
                if key_codes:
                    self._inject_key_combination(key_codes)
            else:
                # Single key
                key_name = command.strip()
                if key_name.startswith('KEY_'):
                    key_name = key_name[4:].lower()
                
                if key_name in self.key_mappings:
                    self._inject_key(self.key_mappings[key_name])
                else:
                    logger.warning(f"Unknown key: {key_name}")
                    
        except Exception as e:
            logger.error(f"Error injecting command '{command}': {e}")
    
    def inject_multiple_commands(self, commands: List[str], delay: float = 0.1):
        """
        Inject multiple commands with delay between them.
        
        Args:
            commands: List of command strings
            delay: Delay between commands in seconds
        """
        for command in commands:
            self.inject_command(command)
            time.sleep(delay)
    
    def backspace(self, count: int = 1):
        """
        Inject backspace keystrokes.
        
        Args:
            count: Number of backspace keystrokes
        """
        for _ in range(count):
            self._inject_key(uinput.KEY_BACKSPACE)
            time.sleep(0.01)
    
    def enter(self):
        """Inject enter keystroke."""
        self._inject_key(uinput.KEY_ENTER)
    
    def tab(self):
        """Inject tab keystroke."""
        self._inject_key(uinput.KEY_TAB)
    
    def escape(self):
        """Inject escape keystroke."""
        self._inject_key(uinput.KEY_ESC)
    
    def select_all(self):
        """Inject Ctrl+A (select all)."""
        self._inject_key_combination([uinput.KEY_CTRL, uinput.KEY_A])
    
    def copy(self):
        """Inject Ctrl+C (copy)."""
        self._inject_key_combination([uinput.KEY_CTRL, uinput.KEY_C])
    
    def paste(self):
        """Inject Ctrl+V (paste)."""
        self._inject_key_combination([uinput.KEY_CTRL, uinput.KEY_V])
    
    def cut(self):
        """Inject Ctrl+X (cut)."""
        self._inject_key_combination([uinput.KEY_CTRL, uinput.KEY_X])
    
    def undo(self):
        """Inject Ctrl+Z (undo)."""
        self._inject_key_combination([uinput.KEY_CTRL, uinput.KEY_Z])
    
    def redo(self):
        """Inject Ctrl+Y (redo)."""
        self._inject_key_combination([uinput.KEY_CTRL, uinput.KEY_Y])
    
    def close(self):
        """Close the uinput device."""
        if self.device:
            try:
                self.device.destroy()
                self.is_initialized = False
                logger.info("Uinput device closed")
            except Exception as e:
                logger.error(f"Error closing uinput device: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 
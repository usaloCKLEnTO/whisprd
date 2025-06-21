"""
Main dictation engine that orchestrates all components.
"""

import threading
import time
import os
from typing import Dict, Any, Optional, Callable
import logging
from datetime import datetime
import re

from .config import Config
from .audio_capture import AudioCapture
from .whisper_transcriber import WhisperTranscriber
from .command_processor import CommandProcessor
from .keystroke_injector import KeystrokeInjector
from .hotkey_manager import HotkeyManager

logger = logging.getLogger(__name__)


class DictationEngine:
    """Main dictation engine that coordinates all components."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the dictation engine.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = Config(config_path)
        
        # Initialize components
        self.audio_capture = None
        self.transcriber = None
        self.command_processor = None
        self.keystroke_injector = None
        self.hotkey_manager = None
        
        # State management
        self.is_running = False
        self.is_dictating = False
        self.main_thread = None
        
        # Callbacks
        self.status_callback = None
        self.transcription_callback = None
        
        # Statistics
        self.stats = {
            'start_time': None,
            'total_transcriptions': 0,
            'total_commands': 0,
            'total_characters': 0,
            'errors': 0
        }
        
        # Track last injected text for proper spacing
        self.last_injected_text = ""
        
        logger.info("Dictation engine initialized")
    
    def initialize_components(self):
        """Initialize all dictation components."""
        try:
            # Initialize command processor with both dictation and commands config
            dictation_config = self.config.get_dictation_config()
            commands_config = self.config.get_commands()
            command_config = {**dictation_config, 'commands': commands_config}
            self.command_processor = CommandProcessor(command_config)
            
            # Initialize keystroke injector if enabled
            if self.config.get_output_config().get('inject_keystrokes', True):
                self.keystroke_injector = KeystrokeInjector(self.config.get_output_config())
            
            # Initialize hotkey manager
            self.hotkey_manager = HotkeyManager(
                self.config.get_dictation_config(),
                hotkey_callback=self._toggle_dictation
            )
            
            # Initialize audio capture
            self.audio_capture = AudioCapture(
                self.config.get_audio_config(),
                audio_callback=self._on_audio_data
            )
            
            # Initialize transcriber
            self.transcriber = WhisperTranscriber(
                self.config.get_whisper_config(),
                transcription_callback=self._on_transcription
            )
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def start(self):
        """Start the dictation engine."""
        if self.is_running:
            logger.warning("Dictation engine already running")
            return
        
        try:
            # Initialize components
            self.initialize_components()
            
            # Start hotkey listener
            self.hotkey_manager.start_listening()
            
            # Start main processing thread
            self.is_running = True
            self.main_thread = threading.Thread(target=self._main_loop, daemon=True)
            self.main_thread.start()
            
            # Update statistics
            self.stats['start_time'] = datetime.now()
            
            logger.info("Dictation engine started")
            self._notify_status("started")
            
        except Exception as e:
            logger.error(f"Failed to start dictation engine: {e}")
            self.stop()
            raise
    
    def stop(self):
        """Stop the dictation engine."""
        if not self.is_running:
            logger.warning("Dictation engine not running")
            return
        
        try:
            # Stop dictation if active
            if self.is_dictating:
                self.stop_dictation()
            
            # Stop main thread
            self.is_running = False
            if self.main_thread:
                self.main_thread.join(timeout=5.0)
            
            # Stop components
            if self.hotkey_manager:
                self.hotkey_manager.stop_listening()
            
            if self.audio_capture:
                self.audio_capture.stop_recording()
            
            if self.transcriber:
                self.transcriber.stop_transcription()
            
            if self.keystroke_injector:
                self.keystroke_injector.close()
            
            logger.info("Dictation engine stopped")
            self._notify_status("stopped")
            
        except Exception as e:
            logger.error(f"Error stopping dictation engine: {e}")
    
    def start_dictation(self):
        """Start dictation mode."""
        if self.is_dictating:
            logger.warning("Dictation already active")
            return
        
        try:
            # Start audio capture
            self.audio_capture.start_recording()
            
            # Start transcription
            self.transcriber.start_transcription()
            
            self.is_dictating = True
            logger.info("Dictation started")
            self._notify_status("dictating")
            
        except Exception as e:
            logger.error(f"Failed to start dictation: {e}")
            self.stats['errors'] += 1
            raise
    
    def stop_dictation(self):
        """Stop dictation mode."""
        if not self.is_dictating:
            logger.warning("Dictation not active")
            return
        
        try:
            # Don't stop transcription - keep it running for command detection
            # self.transcriber.stop_transcription()
            
            # Keep audio capture running so we can hear "start listening" command
            # Only stop audio capture if we're completely shutting down
            # self.audio_capture.stop_recording()
            
            self.is_dictating = False
            logger.info("Dictation stopped")
            self._notify_status("idle")
            
        except Exception as e:
            logger.error(f"Error stopping dictation: {e}")
            self.stats['errors'] += 1
    
    def _toggle_dictation(self):
        """Toggle dictation on/off."""
        if self.is_dictating:
            self.stop_dictation()
        else:
            self.start_dictation()
    
    def _main_loop(self):
        """Main processing loop."""
        while self.is_running:
            try:
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.stats['errors'] += 1
                time.sleep(1.0)
    
    def _on_audio_data(self, audio_data: bytes, timestamp: float):
        """Handle incoming audio data."""
        if self.transcriber:
            # Always send audio to transcriber, whether dictating or not
            self.transcriber.add_audio_data(audio_data)
    
    def _on_transcription(self, text: str):
        """Handle transcription results."""
        try:
            self.stats['total_transcriptions'] += 1
            
            # Clean up the text before processing
            cleaned_text = self._clean_transcription_text(text)
            
            # Process commands
            matches = self.command_processor.process_text(cleaned_text)
            
            # Extract clean text
            clean_text = self.command_processor.extract_clean_text(cleaned_text, matches)
            
            # Execute commands (always execute commands, whether dictating or not)
            for match in matches:
                self._execute_command(match)
            
            # Only inject text if dictation is active
            if self.is_dictating and clean_text and self.keystroke_injector:
                # Always add a space at the beginning unless the last text ended with a space
                if self.last_injected_text and not self.last_injected_text.endswith(' '):
                    clean_text = " " + clean_text
                
                # Inject the text
                self.keystroke_injector.inject_text(clean_text)
                
                # Update last injected text to include any added space
                self.last_injected_text = clean_text
                self.stats['total_characters'] += len(clean_text)
                
                # Log the transcription
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] {clean_text}")
                print(f"🎤 {clean_text}")
            
            # Save to file if enabled
            if self.config.get_output_config().get('save_to_file', True):
                self._save_transcription(cleaned_text, clean_text, matches)
            
            # Console output if enabled
            if self.config.get_output_config().get('console_output', True):
                self._print_transcription(cleaned_text, clean_text, matches)
            
            # Call transcription callback
            if self.transcription_callback:
                self.transcription_callback(cleaned_text, clean_text, matches)
            
        except Exception as e:
            logger.error(f"Error processing transcription: {e}")
            self.stats['errors'] += 1
    
    def _clean_transcription_text(self, text: str) -> str:
        """
        Clean up transcription text to remove artifacts and improve quality.
        
        Args:
            text: Raw transcription text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove common transcription artifacts
        text = text.strip()
        
        # Normalize spacing
        text = " ".join(text.split())
        
        # Remove repeated words at the beginning (common with overlapping audio)
        words = text.split()
        if len(words) > 1:
            # Check for repeated words at the start
            cleaned_words = []
            for i, word in enumerate(words):
                # Skip if this word is repeated from the previous word
                if i > 0 and word.lower() == words[i-1].lower():
                    continue
                cleaned_words.append(word)
            text = " ".join(cleaned_words)
        
        # Fix sentence spacing - ensure proper spacing after punctuation
        # Add space after periods, commas, question marks, exclamation points if followed by a letter
        text = re.sub(r'([.!?,])([A-Za-z])', r'\1 \2', text)
        
        # Fix double punctuation (common with overlapping audio)
        text = re.sub(r'([.!?,])\1+', r'\1', text)
        
        # Remove very short fragments (likely artifacts)
        if len(text.strip()) < 3:
            return ""
        
        # Ensure proper capitalization at the start
        if text and text[0].isalpha():
            text = text[0].upper() + text[1:]
        
        # Ensure the text ends with proper punctuation if it's a complete sentence
        if text and not text.endswith(('.', '!', '?', ':', ';')):
            # Check if it looks like a complete sentence (ends with a word)
            if text.split()[-1] and text.split()[-1][-1].isalpha():
                text += "."
        
        return text.strip()
    
    def _execute_command(self, match):
        """Execute a command match."""
        try:
            action = match.action
            
            if action == 'STOP_DICTATION':
                self.stop_dictation()
            elif action == 'START_DICTATION':
                self.start_dictation()
            elif self.keystroke_injector:
                self.keystroke_injector.inject_command(action)
            
            self.stats['total_commands'] += 1
            logger.debug(f"Executed command: {match.command} -> {action}")
            
        except Exception as e:
            logger.error(f"Error executing command {match.command}: {e}")
            self.stats['errors'] += 1
    
    def _save_transcription(self, original_text: str, clean_text: str, matches):
        """Save transcription to file."""
        try:
            file_path = self.config.get_transcript_file_path()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] Original: {original_text}\n")
                if clean_text:
                    f.write(f"[{timestamp}] Clean: {clean_text}\n")
                if matches:
                    commands = [f"{m.command}->{m.action}" for m in matches]
                    f.write(f"[{timestamp}] Commands: {', '.join(commands)}\n")
                f.write("\n")
                
        except Exception as e:
            logger.error(f"Error saving transcription: {e}")
    
    def _print_transcription(self, original_text: str, clean_text: str, matches):
        """Print transcription to console."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"[{timestamp}] {original_text}")
        if clean_text and clean_text != original_text:
            print(f"[{timestamp}] Clean: {clean_text}")
        if matches:
            commands = [f"{m.command}->{m.action}" for m in matches]
            print(f"[{timestamp}] Commands: {', '.join(commands)}")
    
    def _notify_status(self, status: str):
        """Notify status change."""
        if self.status_callback:
            try:
                self.status_callback(status)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Set status change callback."""
        self.status_callback = callback
    
    def set_transcription_callback(self, callback: Callable[[str, str, list], None]):
        """Set transcription callback."""
        self.transcription_callback = callback
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status information."""
        return {
            'is_running': self.is_running,
            'is_dictating': self.is_dictating,
            'stats': self.stats.copy(),
            'hotkey': self.hotkey_manager.get_current_hotkey() if self.hotkey_manager else None,
            'audio_queue_size': self.audio_capture.get_queue_size() if self.audio_capture else 0,
            'transcription_queue_size': self.transcriber.get_queue_size() if self.transcriber else 0
        }
    
    def get_commands(self) -> Dict[str, str]:
        """Get available commands."""
        if self.command_processor:
            return self.command_processor.get_command_help()
        return {}
    
    def add_command(self, phrase: str, action: str):
        """Add a new voice command."""
        if self.command_processor:
            self.command_processor.add_command(phrase, action)
    
    def remove_command(self, phrase: str) -> bool:
        """Remove a voice command."""
        if self.command_processor:
            return self.command_processor.remove_command(phrase)
        return False
    
    def reload_config(self):
        """Reload configuration from file."""
        try:
            self.config.reload()
            
            # Update command processor
            if self.command_processor:
                self.command_processor.update_config(self.config.get_dictation_config())
            
            # Update hotkey manager
            if self.hotkey_manager:
                self.hotkey_manager.update_hotkey(self.config.get_dictation_config().get('toggle_hotkey', ['ctrl', 'alt', 'd']))
            
            logger.info("Configuration reloaded")
            
        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")
            raise
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop() 
"""
Command processor for voice command recognition and mapping.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CommandMatch:
    """Represents a matched command."""
    command: str
    action: str
    confidence: float
    start_pos: int
    end_pos: int


class CommandProcessor:
    """Process voice commands and map them to actions."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize command processor.
        
        Args:
            config: Dictation configuration dictionary
        """
        self.config = config
        self.commands = config.get('commands', {})
        self.command_mode_word = config.get('command_mode_word', 'computer')
        self.confidence_threshold = config.get('confidence_threshold', 0.5)
        self.auto_punctuation = config.get('auto_punctuation', True)
        
        # Punctuation mappings
        self.sentence_end_words = config.get('sentence_end_words', ['period', 'full stop', 'dot'])
        self.comma_words = config.get('comma_words', ['comma', 'pause'])
        self.question_words = config.get('question_words', ['question mark', 'question'])
        
        # Compile regex patterns for better performance
        self._compile_patterns()
        
        logger.info(f"Command processor initialized with {len(self.commands)} commands")
    
    def _compile_patterns(self):
        """Compile regex patterns for command matching."""
        # Create pattern for command mode word
        self.command_mode_pattern = re.compile(
            rf'\b{re.escape(self.command_mode_word)}\b',
            re.IGNORECASE
        )
        
        # Create patterns for punctuation words
        self.sentence_end_pattern = re.compile(
            r'\b(' + '|'.join(map(re.escape, self.sentence_end_words)) + r')\b',
            re.IGNORECASE
        )
        self.comma_pattern = re.compile(
            r'\b(' + '|'.join(map(re.escape, self.comma_words)) + r')\b',
            re.IGNORECASE
        )
        self.question_pattern = re.compile(
            r'\b(' + '|'.join(map(re.escape, self.question_words)) + r')\b',
            re.IGNORECASE
        )
    
    def process_text(self, text: str, confidence: float = 1.0) -> List[CommandMatch]:
        """
        Process text and find command matches.
        
        Args:
            text: Input text to process
            confidence: Confidence score for the transcription
            
        Returns:
            List of command matches found
        """
        if confidence < self.confidence_threshold:
            return []
        
        matches = []
        text_lower = text.lower()
        
        # Check for command mode activation
        if self.command_mode_pattern.search(text):
            # Process commands in command mode
            matches.extend(self._find_commands_in_mode(text, text_lower, True))
        else:
            # Process regular commands and auto-punctuation
            matches.extend(self._find_commands_in_mode(text, text_lower, False))
            
            if self.auto_punctuation:
                matches.extend(self._find_punctuation_commands(text, text_lower))
        
        # Sort matches by position
        matches.sort(key=lambda x: x.start_pos)
        
        return matches
    
    def _find_commands_in_mode(self, text: str, text_lower: str, command_mode: bool) -> List[CommandMatch]:
        """Find commands in the given text."""
        matches = []
        
        for command_phrase, action in self.commands.items():
            # Allow system commands in both regular and command mode
            # Skip other special commands in non-command mode
            if not command_mode and action not in ['STOP_DICTATION', 'START_DICTATION'] and action.startswith('STOP_'):
                continue
            
            # Find all occurrences of the command
            pattern = re.compile(r'\b' + re.escape(command_phrase.lower()) + r'\b', re.IGNORECASE)
            
            for match in pattern.finditer(text_lower):
                start_pos = match.start()
                end_pos = match.end()
                
                # Calculate confidence based on exact match
                confidence = 1.0 if match.group().lower() == command_phrase.lower() else 0.8
                
                matches.append(CommandMatch(
                    command=command_phrase,
                    action=action,
                    confidence=confidence,
                    start_pos=start_pos,
                    end_pos=end_pos
                ))
        
        return matches
    
    def _find_punctuation_commands(self, text: str, text_lower: str) -> List[CommandMatch]:
        """Find auto-punctuation commands."""
        matches = []
        
        # Find sentence endings
        for match in self.sentence_end_pattern.finditer(text_lower):
            matches.append(CommandMatch(
                command=match.group(),
                action="KEY_DOT",
                confidence=0.9,
                start_pos=match.start(),
                end_pos=match.end()
            ))
        
        # Find commas
        for match in self.comma_pattern.finditer(text_lower):
            matches.append(CommandMatch(
                command=match.group(),
                action="KEY_COMMA",
                confidence=0.9,
                start_pos=match.start(),
                end_pos=match.end()
            ))
        
        # Find question marks
        for match in self.question_pattern.finditer(text_lower):
            matches.append(CommandMatch(
                command=match.group(),
                action="KEY_QUESTION",
                confidence=0.9,
                start_pos=match.start(),
                end_pos=match.end()
            ))
        
        return matches
    
    def extract_clean_text(self, text: str, matches: List[CommandMatch]) -> str:
        """
        Extract clean text by removing command phrases.
        
        Args:
            text: Original text
            matches: List of command matches to remove
            
        Returns:
            Clean text with commands removed
        """
        if not matches:
            return text
        
        # Sort matches by position in reverse order to avoid index shifting
        sorted_matches = sorted(matches, key=lambda x: x.start_pos, reverse=True)
        
        clean_text = text
        for match in sorted_matches:
            # Remove the command phrase
            before = clean_text[:match.start_pos]
            after = clean_text[match.end_pos:]
            clean_text = before + after
        
        # Clean up extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
    def get_command_help(self) -> Dict[str, str]:
        """
        Get help information for all available commands.
        
        Returns:
            Dictionary mapping command phrases to descriptions
        """
        help_text = {}
        
        for command, action in self.commands.items():
            if action.startswith('KEY_'):
                help_text[command] = f"Press {action}"
            elif action in ['STOP_DICTATION', 'START_DICTATION']:
                help_text[command] = f"{action.replace('_', ' ').title()}"
            else:
                help_text[command] = f"Execute: {action}"
        
        return help_text
    
    def add_command(self, phrase: str, action: str):
        """
        Add a new command mapping.
        
        Args:
            phrase: Voice command phrase
            action: Action to execute
        """
        self.commands[phrase] = action
        logger.info(f"Added command: '{phrase}' -> '{action}'")
    
    def remove_command(self, phrase: str) -> bool:
        """
        Remove a command mapping.
        
        Args:
            phrase: Voice command phrase to remove
            
        Returns:
            True if command was removed, False if not found
        """
        if phrase in self.commands:
            del self.commands[phrase]
            logger.info(f"Removed command: '{phrase}'")
            return True
        return False
    
    def update_config(self, new_config: Dict[str, Any]):
        """
        Update configuration and recompile patterns.
        
        Args:
            new_config: New configuration dictionary
        """
        self.config.update(new_config)
        self.commands = self.config.get('commands', self.commands)
        self.command_mode_word = self.config.get('command_mode_word', self.command_mode_word)
        self.confidence_threshold = self.config.get('confidence_threshold', self.confidence_threshold)
        self.auto_punctuation = self.config.get('auto_punctuation', self.auto_punctuation)
        
        # Update punctuation mappings
        self.sentence_end_words = self.config.get('sentence_end_words', self.sentence_end_words)
        self.comma_words = self.config.get('comma_words', self.comma_words)
        self.question_words = self.config.get('question_words', self.question_words)
        
        # Recompile patterns
        self._compile_patterns()
        
        logger.info("Command processor configuration updated")
    
    def is_command_mode_activated(self, text: str) -> bool:
        """
        Check if command mode is activated in the text.
        
        Args:
            text: Text to check
            
        Returns:
            True if command mode is activated
        """
        return bool(self.command_mode_pattern.search(text.lower()))
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available command phrases.
        
        Returns:
            List of command phrases
        """
        return list(self.commands.keys()) 
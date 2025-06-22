"""
Unit tests for the command_processor module.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from whisprd.command_processor import CommandProcessor, CommandMatch


class TestCommandProcessor:
    """Test cases for the CommandProcessor class."""

    def test_init_with_valid_config(self, sample_config: Dict[str, Any]) -> None:
        """Test CommandProcessor initialization with valid config."""
        commands = sample_config['commands']
        processor = CommandProcessor({'commands': commands})
        
        assert processor.commands == commands
        assert processor.commands['new line'] == 'enter'
        assert processor.commands['new paragraph'] == 'enter enter'

    def test_init_with_empty_commands(self) -> None:
        """Test CommandProcessor initialization with empty commands."""
        processor = CommandProcessor({'commands': {}})
        assert processor.commands == {}

    def test_process_text_no_commands(self) -> None:
        """Test processing text with no commands."""
        processor = CommandProcessor({'commands': {}})
        result = processor.process_text("Hello world")
        assert result == []

    def test_process_text_with_commands(self) -> None:
        """Test processing text with commands."""
        commands = {
            'new line': 'enter',
            'new paragraph': 'enter enter',
            'delete word': 'ctrl+backspace'
        }
        processor = CommandProcessor({'commands': commands})
        
        result = processor.process_text("Hello new line world")
        assert len(result) == 1
        assert result[0].command == 'new line'
        assert result[0].action == 'enter'

    def test_process_text_with_multiple_commands(self) -> None:
        """Test processing text with multiple commands."""
        commands = {
            'new line': 'enter',
            'new paragraph': 'enter enter',
            'delete word': 'ctrl+backspace'
        }
        processor = CommandProcessor({'commands': commands})
        
        result = processor.process_text("Hello new line world new paragraph test")
        assert len(result) == 2
        assert result[0].command == 'new line'
        assert result[0].action == 'enter'
        assert result[1].command == 'new paragraph'
        assert result[1].action == 'enter enter'

    def test_process_text_case_insensitive(self) -> None:
        """Test processing text with case insensitive command matching."""
        commands = {
            'new line': 'enter',
            'NEW PARAGRAPH': 'enter enter'
        }
        processor = CommandProcessor({'commands': commands})
        
        result = processor.process_text("Hello new line world NEW PARAGRAPH test")
        assert len(result) == 2
        assert result[0].command == 'new line'
        assert result[1].command == 'NEW PARAGRAPH'

    def test_process_text_partial_matches(self) -> None:
        """Test processing text with partial command matches."""
        commands = {
            'new line': 'enter',
            'new paragraph': 'enter enter'
        }
        processor = CommandProcessor({'commands': commands})
        
        # Should not match partial words
        result = processor.process_text("Hello new lines world")
        assert result == []

    def test_process_text_with_special_characters(self) -> None:
        """Test processing text with special characters in commands."""
        commands = {
            'new line': 'enter',
            'delete word': 'ctrl+backspace',
            'select all': 'ctrl+a'
        }
        processor = CommandProcessor({'commands': commands})
        
        result = processor.process_text("Hello delete word select all")
        assert len(result) == 2
        assert result[0].command == 'delete word'
        assert result[0].action == 'ctrl+backspace'
        assert result[1].command == 'select all'
        assert result[1].action == 'ctrl+a'

    def test_process_text_with_numbers(self) -> None:
        """Test processing text with numbers in commands."""
        commands = {
            'new line': 'enter',
            'page 1': 'ctrl+1',
            'page 2': 'ctrl+2'
        }
        processor = CommandProcessor({'commands': commands})
        
        result = processor.process_text("Go to page 1 then page 2")
        assert len(result) == 2
        assert result[0].command == 'page 1'
        assert result[0].action == 'ctrl+1'
        assert result[1].command == 'page 2'
        assert result[1].action == 'ctrl+2'

    def test_process_text_with_overlapping_commands(self) -> None:
        """Test processing text with overlapping commands."""
        commands = {
            'new line': 'enter',
            'new line break': 'shift+enter'
        }
        processor = CommandProcessor({'commands': commands})
        
        # Should match the longest command first
        result = processor.process_text("Hello new line break world")
        assert len(result) == 1
        assert result[0].command == 'new line break'
        assert result[0].action == 'shift+enter'

    def test_process_text_with_empty_text(self) -> None:
        """Test processing empty text."""
        commands = {'new line': 'enter'}
        processor = CommandProcessor({'commands': commands})
        
        result = processor.process_text("")
        assert result == []

    def test_process_text_with_whitespace_only(self) -> None:
        """Test processing text with only whitespace."""
        commands = {'new line': 'enter'}
        processor = CommandProcessor({'commands': commands})
        
        result = processor.process_text("   \n\t   ")
        assert result == []

    def test_add_command(self) -> None:
        """Test adding a new command."""
        processor = CommandProcessor({'commands': {}})
        processor.add_command("test command", "ctrl+t")
        
        assert processor.commands["test command"] == "ctrl+t"

    def test_add_command_overwrite(self) -> None:
        """Test adding a command that overwrites existing one."""
        processor = CommandProcessor({'commands': {"test": "old_value"}})
        processor.add_command("test", "new_value")
        
        assert processor.commands["test"] == "new_value"

    def test_remove_command(self) -> None:
        """Test removing a command."""
        processor = CommandProcessor({'commands': {"test": "value"}})
        result = processor.remove_command("test")
        
        assert "test" not in processor.commands
        assert result is True

    def test_remove_nonexistent_command(self) -> None:
        """Test removing a command that doesn't exist."""
        processor = CommandProcessor({'commands': {}})
        result = processor.remove_command("nonexistent")
        assert result is False

    def test_get_available_commands(self) -> None:
        """Test getting available commands."""
        commands = {"test1": "value1", "test2": "value2"}
        processor = CommandProcessor({'commands': commands})
        
        result = processor.get_available_commands()
        assert "test1" in result
        assert "test2" in result

    def test_extract_clean_text(self) -> None:
        """Test extracting clean text by removing commands."""
        commands = {"new line": "enter", "delete word": "ctrl+backspace"}
        processor = CommandProcessor({'commands': commands})
        
        text = "Hello new line world delete word test"
        matches = processor.process_text(text)
        clean_text = processor.extract_clean_text(text, matches)
        
        assert clean_text == "Hello world test"

    def test_extract_clean_text_no_matches(self) -> None:
        """Test extracting clean text with no matches."""
        processor = CommandProcessor({'commands': {}})
        
        text = "Hello world"
        clean_text = processor.extract_clean_text(text, [])
        
        assert clean_text == "Hello world"

    def test_is_command_mode_activated(self) -> None:
        """Test command mode activation detection."""
        processor = CommandProcessor({
            'commands': {},
            'command_mode_word': 'computer'
        })
        
        assert processor.is_command_mode_activated("Hello computer world") is True
        assert processor.is_command_mode_activated("Hello world") is False

    def test_process_text_with_confidence_threshold(self) -> None:
        """Test processing text with confidence threshold."""
        commands = {"new line": "enter"}
        processor = CommandProcessor({
            'commands': commands,
            'confidence_threshold': 0.8
        })
        
        # Test with low confidence
        result = processor.process_text("Hello new line world", confidence=0.5)
        assert result == []
        
        # Test with high confidence
        result = processor.process_text("Hello new line world", confidence=0.9)
        assert len(result) == 1

    def test_process_text_with_auto_punctuation(self) -> None:
        """Test processing text with auto-punctuation."""
        processor = CommandProcessor({
            'commands': {},
            'auto_punctuation': True,
            'sentence_end_words': ['period'],
            'comma_words': ['comma'],
            'question_words': ['question mark']
        })
        
        result = processor.process_text("Hello world period How are you comma question mark")
        assert len(result) == 3
        assert result[0].action == "KEY_DOT"
        assert result[1].action == "KEY_COMMA"
        assert result[2].action == "KEY_QUESTION"

    def test_process_text_without_auto_punctuation(self) -> None:
        """Test processing text without auto-punctuation."""
        processor = CommandProcessor({
            'commands': {},
            'auto_punctuation': False,
            'sentence_end_words': ['period']
        })
        
        result = processor.process_text("Hello world period")
        assert result == []

    def test_update_config(self) -> None:
        """Test updating configuration."""
        processor = CommandProcessor({'commands': {"old": "value"}})
        
        new_config = {
            'commands': {"new": "value"},
            'confidence_threshold': 0.8,
            'auto_punctuation': False
        }
        
        processor.update_config(new_config)
        
        assert processor.commands == {"new": "value"}
        assert processor.confidence_threshold == 0.8
        assert processor.auto_punctuation is False

    def test_get_command_help(self) -> None:
        """Test getting command help."""
        commands = {"new line": "enter", "delete word": "ctrl+backspace"}
        processor = CommandProcessor({'commands': commands})
        
        help_text = processor.get_command_help()
        assert "new line" in help_text
        assert "delete word" in help_text 
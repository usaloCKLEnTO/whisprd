"""
Unit tests for the config module.
"""

import pytest
import tempfile
import os
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from whisprd.config import Config


class TestConfig:
    """Test cases for the Config class."""

    def test_init_with_valid_config_file(self, temp_config_file: str) -> None:
        """Test Config initialization with a valid config file."""
        config = Config(temp_config_file)
        assert config.config_path == Path(temp_config_file)
        assert 'audio' in config.config
        assert 'whisper' in config.config
        assert 'whisprd' in config.config

    def test_init_with_none_config_path(self) -> None:
        """Test Config initialization with None config path."""
        with patch('os.path.expanduser') as mock_expanduser, \
             patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=yaml.dump({
                 'audio': {'sample_rate': 16000, 'channels': 1, 'buffer_size': 8000},
                 'whisper': {'model_size': 'tiny'},
                 'whisprd': {'confidence_threshold': 0.5},
                 'commands': {},
                 'output': {},
                 'performance': {}
             }))):
            
            mock_expanduser.return_value = '/home/user/.config/whisprd/config.yaml'
            mock_exists.return_value = True
            
            config = Config()
            assert config.config_path == Path('/home/user/.config/whisprd/config.yaml')

    def test_init_with_missing_config_file(self) -> None:
        """Test Config initialization with missing config file."""
        with pytest.raises(FileNotFoundError):
            Config('/nonexistent/config.yaml')

    def test_init_with_invalid_yaml(self) -> None:
        """Test Config initialization with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [')
            f.flush()
            
            with pytest.raises(Exception):  # yaml.YAMLError
                Config(f.name)
            
            os.unlink(f.name)

    def test_validate_config_missing_sections(self) -> None:
        """Test config validation with missing required sections."""
        invalid_config = {
            'audio': {'sample_rate': 16000, 'channels': 1, 'buffer_size': 8000},
            'whisper': {'model_size': 'tiny'},
            # Missing other required sections
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            f.flush()
            
            with pytest.raises(ValueError, match="Missing required configuration section"):
                Config(f.name)
            
            os.unlink(f.name)

    def test_validate_config_invalid_audio_settings(self) -> None:
        """Test config validation with invalid audio settings."""
        invalid_config = {
            'audio': {'sample_rate': 'invalid', 'channels': 1, 'buffer_size': 8000},
            'whisper': {'model_size': 'tiny'},
            'whisprd': {'confidence_threshold': 0.5},
            'commands': {},
            'output': {},
            'performance': {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            f.flush()
            
            with pytest.raises(ValueError, match="audio.sample_rate must be an integer"):
                Config(f.name)
            
            os.unlink(f.name)

    def test_validate_config_invalid_whisper_model(self) -> None:
        """Test config validation with invalid whisper model size."""
        invalid_config = {
            'audio': {'sample_rate': 16000, 'channels': 1, 'buffer_size': 8000},
            'whisper': {'model_size': 'invalid_model'},
            'whisprd': {'confidence_threshold': 0.5},
            'commands': {},
            'output': {},
            'performance': {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            f.flush()
            
            with pytest.raises(ValueError, match="whisper.model_size must be one of"):
                Config(f.name)
            
            os.unlink(f.name)

    def test_validate_config_invalid_confidence_threshold(self) -> None:
        """Test config validation with invalid confidence threshold."""
        invalid_config = {
            'audio': {'sample_rate': 16000, 'channels': 1, 'buffer_size': 8000},
            'whisper': {'model_size': 'tiny'},
            'whisprd': {'confidence_threshold': 1.5},  # Out of range
            'commands': {},
            'output': {},
            'performance': {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            f.flush()
            
            with pytest.raises(ValueError, match="whisprd.confidence_threshold must be between 0 and 1"):
                Config(f.name)
            
            os.unlink(f.name)

    def test_get_with_dot_notation(self, temp_config_file: str) -> None:
        """Test getting config values using dot notation."""
        config = Config(temp_config_file)
        
        assert config.get('audio.sample_rate') == 16000
        assert config.get('whisper.model_size') == 'tiny'
        assert config.get('whisprd.confidence_threshold') == 0.5
        assert config.get('nonexistent.key') is None
        assert config.get('nonexistent.key', 'default') == 'default'

    def test_get_audio_config(self, temp_config_file: str) -> None:
        """Test getting audio configuration."""
        config = Config(temp_config_file)
        audio_config = config.get_audio_config()
        
        assert audio_config['sample_rate'] == 16000
        assert audio_config['channels'] == 1
        assert audio_config['buffer_size'] == 8000

    def test_get_whisper_config(self, temp_config_file: str) -> None:
        """Test getting whisper configuration."""
        config = Config(temp_config_file)
        whisper_config = config.get_whisper_config()
        
        assert whisper_config['model_size'] == 'tiny'
        assert whisper_config['language'] == 'en'

    def test_get_whisprd_config(self, temp_config_file: str) -> None:
        """Test getting whisprd configuration."""
        config = Config(temp_config_file)
        whisprd_config = config.get_whisprd_config()
        
        assert whisprd_config['confidence_threshold'] == 0.5
        assert whisprd_config['max_retries'] == 3

    def test_get_commands(self, temp_config_file: str) -> None:
        """Test getting commands configuration."""
        config = Config(temp_config_file)
        commands = config.get_commands()
        
        assert commands['new line'] == 'enter'
        assert commands['new paragraph'] == 'enter enter'
        assert commands['delete word'] == 'ctrl+backspace'

    def test_get_output_config(self, temp_config_file: str) -> None:
        """Test getting output configuration."""
        config = Config(temp_config_file)
        output_config = config.get_output_config()
        
        assert output_config['transcript_file'] == '~/whisprd_transcript.txt'
        assert output_config['log_level'] == 'INFO'

    def test_get_performance_config(self, temp_config_file: str) -> None:
        """Test getting performance configuration."""
        config = Config(temp_config_file)
        performance_config = config.get_performance_config()
        
        assert performance_config['max_queue_size'] == 1000
        assert performance_config['processing_timeout'] == 30.0

    def test_get_transcript_file_path(self, temp_config_file: str) -> None:
        """Test getting expanded transcript file path."""
        config = Config(temp_config_file)
        
        with patch('os.path.expanduser') as mock_expanduser:
            mock_expanduser.return_value = '/home/user/whisprd_transcript.txt'
            path = config.get_transcript_file_path()
            assert path == '/home/user/whisprd_transcript.txt'

    def test_get_alternate_prompts_disabled(self, temp_config_file: str) -> None:
        """Test getting alternate prompts when disabled."""
        config = Config(temp_config_file)
        prompts = config.get_alternate_prompts()
        assert prompts is None

    def test_get_alternate_prompts_enabled_missing_file(self) -> None:
        """Test getting alternate prompts when enabled but file missing."""
        config_data = {
            'audio': {'sample_rate': 16000, 'channels': 1, 'buffer_size': 8000},
            'whisper': {
                'model_size': 'tiny',
                'use_alternate_prompts': True,
                'alternate_prompts_file': '/nonexistent/prompts.yaml'
            },
            'whisprd': {'confidence_threshold': 0.5},
            'commands': {},
            'output': {},
            'performance': {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            f.flush()
            
            config = Config(f.name)
            prompts = config.get_alternate_prompts()
            assert prompts is None
            
            os.unlink(f.name)

    def test_get_alternate_prompts_enabled_valid_file(self) -> None:
        """Test getting alternate prompts when enabled with valid file."""
        prompts_data = {
            'general': {
                'greeting': 'Hello, how are you?',
                'farewell': 'Goodbye!'
            },
            'commands': {
                'save': 'Save the document',
                'open': 'Open a new file'
            }
        }
        
        config_data = {
            'audio': {'sample_rate': 16000, 'channels': 1, 'buffer_size': 8000},
            'whisper': {
                'model_size': 'tiny',
                'use_alternate_prompts': True,
                'alternate_prompts_file': 'prompts.yaml'
            },
            'whisprd': {'confidence_threshold': 0.5},
            'commands': {},
            'output': {},
            'performance': {}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, 'config.yaml')
            prompts_file = os.path.join(temp_dir, 'prompts.yaml')
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            with open(prompts_file, 'w') as f:
                yaml.dump(prompts_data, f)
            
            config = Config(config_file)
            prompts = config.get_alternate_prompts()
            
            assert prompts is not None
            assert prompts['general']['greeting'] == 'Hello, how are you?'
            assert prompts['commands']['save'] == 'Save the document'

    def test_get_prompt_by_category(self) -> None:
        """Test getting a specific prompt by category and name."""
        prompts_data = {
            'general': {
                'greeting': 'Hello, how are you?',
                'farewell': 'Goodbye!'
            },
            'commands': {
                'save': 'Save the document',
                'open': 'Open a new file'
            }
        }
        
        config_data = {
            'audio': {'sample_rate': 16000, 'channels': 1, 'buffer_size': 8000},
            'whisper': {
                'model_size': 'tiny',
                'use_alternate_prompts': True,
                'alternate_prompts_file': 'prompts.yaml'
            },
            'whisprd': {'confidence_threshold': 0.5},
            'commands': {},
            'output': {},
            'performance': {}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, 'config.yaml')
            prompts_file = os.path.join(temp_dir, 'prompts.yaml')
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            with open(prompts_file, 'w') as f:
                yaml.dump(prompts_data, f)
            
            config = Config(config_file)
            
            # Test valid prompt
            prompt = config.get_prompt_by_category('general', 'greeting')
            assert prompt == 'Hello, how are you?'
            
            # Test invalid category
            prompt = config.get_prompt_by_category('invalid', 'greeting')
            assert prompt is None
            
            # Test invalid prompt name
            prompt = config.get_prompt_by_category('general', 'invalid')
            assert prompt is None

    def test_list_available_prompts(self) -> None:
        """Test listing all available prompts by category."""
        prompts_data = {
            'general': {
                'greeting': 'Hello, how are you?',
                'farewell': 'Goodbye!'
            },
            'commands': {
                'save': 'Save the document',
                'open': 'Open a new file'
            }
        }
        
        config_data = {
            'audio': {'sample_rate': 16000, 'channels': 1, 'buffer_size': 8000},
            'whisper': {
                'model_size': 'tiny',
                'use_alternate_prompts': True,
                'alternate_prompts_file': 'prompts.yaml'
            },
            'whisprd': {'confidence_threshold': 0.5},
            'commands': {},
            'output': {},
            'performance': {}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, 'config.yaml')
            prompts_file = os.path.join(temp_dir, 'prompts.yaml')
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            with open(prompts_file, 'w') as f:
                yaml.dump(prompts_data, f)
            
            config = Config(config_file)
            available = config.list_available_prompts()
            
            assert 'general' in available
            assert 'commands' in available
            assert 'greeting' in available['general']
            assert 'farewell' in available['general']
            assert 'save' in available['commands']
            assert 'open' in available['commands']

    def test_reload_config(self, temp_config_file: str) -> None:
        """Test reloading configuration from file."""
        config = Config(temp_config_file)
        original_value = config.get('whisprd.confidence_threshold')
        
        # Modify the config file
        with open(temp_config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        config_data['whisprd']['confidence_threshold'] = 0.8
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Reload and check
        config.reload()
        new_value = config.get('whisprd.confidence_threshold')
        assert new_value == 0.8
        assert new_value != original_value 
"""
Utility tests for common functionality.
"""

import pytest
import tempfile
import os
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from whisprd.config import Config


class TestConfigUtils:
    """Test cases for configuration utilities."""

    def test_config_validation(self) -> None:
        """Test configuration validation."""
        valid_config = {
            'audio': {
                'sample_rate': 16000,
                'channels': 1,
                'buffer_size': 8000
            },
            'whisper': {
                'model_size': 'tiny'
            },
            'whisprd': {
                'confidence_threshold': 0.5
            },
            'commands': {},
            'output': {},
            'performance': {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config, f)
            f.flush()
            
            config = Config(f.name)
            assert config is not None
            
            os.unlink(f.name)

    def test_config_invalidation(self) -> None:
        """Test configuration invalidation."""
        invalid_config = {
            'audio': {
                'sample_rate': 'invalid',  # Should be int
                'channels': 1,
                'buffer_size': 8000
            },
            'whisper': {
                'model_size': 'tiny'
            },
            'whisprd': {
                'confidence_threshold': 0.5
            },
            'commands': {},
            'output': {},
            'performance': {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            f.flush()
            
            with pytest.raises(ValueError):
                Config(f.name)
            
            os.unlink(f.name)

    def test_config_reload(self) -> None:
        """Test configuration reloading."""
        config_data = {
            'audio': {
                'sample_rate': 16000,
                'channels': 1,
                'buffer_size': 8000
            },
            'whisper': {
                'model_size': 'tiny'
            },
            'whisprd': {
                'confidence_threshold': 0.5
            },
            'commands': {},
            'output': {},
            'performance': {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            f.flush()
            
            config = Config(f.name)
            original_value = config.get('whisprd.confidence_threshold')
            
            # Modify config file
            config_data['whisprd']['confidence_threshold'] = 0.8
            with open(f.name, 'w') as f2:
                yaml.dump(config_data, f2)
            
            config.reload()
            new_value = config.get('whisprd.confidence_threshold')
            
            assert new_value == 0.8
            assert new_value != original_value
            
            os.unlink(f.name)


class TestFileUtils:
    """Test cases for file utilities."""

    def test_temp_file_creation(self) -> None:
        """Test temporary file creation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            f.flush()
            
            assert os.path.exists(f.name)
            
            with open(f.name, 'r') as f2:
                content = f2.read()
                assert content == "test content"
            
            os.unlink(f.name)

    def test_directory_creation(self) -> None:
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, 'test_subdir')
            os.makedirs(test_dir, exist_ok=True)
            
            assert os.path.exists(test_dir)
            assert os.path.isdir(test_dir)

    def test_path_operations(self) -> None:
        """Test path operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / 'test_file.txt'
            
            # Create file
            test_file.write_text("test content")
            assert test_file.exists()
            
            # Read file
            content = test_file.read_text()
            assert content == "test content"
            
            # Delete file
            test_file.unlink()
            assert not test_file.exists()


class TestYamlUtils:
    """Test cases for YAML utilities."""

    def test_yaml_dump_load(self) -> None:
        """Test YAML dump and load operations."""
        test_data = {
            'string': 'test',
            'number': 42,
            'boolean': True,
            'list': [1, 2, 3],
            'dict': {'key': 'value'}
        }
        
        # Dump to string
        yaml_string = yaml.dump(test_data)
        assert isinstance(yaml_string, str)
        
        # Load from string
        loaded_data = yaml.safe_load(yaml_string)
        assert loaded_data == test_data

    def test_yaml_file_operations(self) -> None:
        """Test YAML file operations."""
        test_data = {
            'test': 'data',
            'nested': {
                'key': 'value'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            # Dump to file
            yaml.dump(test_data, f)
            f.flush()
            
            # Load from file
            with open(f.name, 'r') as f2:
                loaded_data = yaml.safe_load(f2)
            
            assert loaded_data == test_data
            os.unlink(f.name)

    def test_yaml_invalid_content(self) -> None:
        """Test handling of invalid YAML content."""
        invalid_yaml = "invalid: yaml: content: ["
        
        with pytest.raises(yaml.YAMLError):
            yaml.safe_load(invalid_yaml)


class TestMockUtils:
    """Test cases for mock utilities."""

    def test_mock_audio_data(self) -> None:
        """Test mock audio data generation."""
        import numpy as np
        
        # Generate mock audio data
        sample_rate = 16000
        duration = 1.0
        samples = np.zeros(int(sample_rate * duration), dtype=np.int16)
        audio_data = samples.tobytes()
        
        assert len(audio_data) == sample_rate * 2  # 2 bytes per sample
        assert isinstance(audio_data, bytes)

    def test_mock_transcription_result(self) -> None:
        """Test mock transcription result creation."""
        mock_result = {
            'text': 'Hello world',
            'language': 'en',
            'language_probability': 0.99,
            'segments': [
                {
                    'start': 0.0,
                    'end': 1.0,
                    'text': 'Hello world',
                    'words': [
                        {'start': 0.0, 'end': 0.5, 'word': 'Hello'},
                        {'start': 0.5, 'end': 1.0, 'word': 'world'}
                    ]
                }
            ]
        }
        
        assert mock_result['text'] == 'Hello world'
        assert mock_result['language'] == 'en'
        assert len(mock_result['segments']) == 1
        assert len(mock_result['segments'][0]['words']) == 2

    def test_mock_device_list(self) -> None:
        """Test mock device list creation."""
        mock_devices = [
            {'name': 'Test Device 1', 'max_inputs': 1, 'max_outputs': 0},
            {'name': 'Test Device 2', 'max_inputs': 2, 'max_outputs': 2}
        ]
        
        assert len(mock_devices) == 2
        assert mock_devices[0]['name'] == 'Test Device 1'
        assert mock_devices[1]['max_inputs'] == 2


class TestThreadingUtils:
    """Test cases for threading utilities."""

    def test_thread_safety(self) -> None:
        """Test thread safety of shared resources."""
        import threading
        import time
        
        shared_counter = 0
        lock = threading.Lock()
        
        def increment_counter():
            nonlocal shared_counter
            for _ in range(100):
                with lock:
                    shared_counter += 1
                time.sleep(0.001)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=increment_counter)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        assert shared_counter == 500

    def test_thread_communication(self) -> None:
        """Test thread communication using queues."""
        import queue
        import threading
        
        message_queue = queue.Queue()
        
        def producer():
            for i in range(5):
                message_queue.put(f"Message {i}")
        
        def consumer():
            messages = []
            for _ in range(5):
                message = message_queue.get()
                messages.append(message)
                message_queue.task_done()
            return messages
        
        # Start producer thread
        producer_thread = threading.Thread(target=producer)
        producer_thread.start()
        
        # Consumer runs in main thread
        messages = consumer()
        
        producer_thread.join()
        
        assert len(messages) == 5
        assert messages[0] == "Message 0"
        assert messages[4] == "Message 4" 
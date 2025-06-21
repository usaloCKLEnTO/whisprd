"""
Configuration management for the whisprd system.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the whisprd system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from YAML file."""
        if config_path is None:
            # Try user config first, then fallback to default
            user_config = os.path.expanduser("~/.config/whisprd/config.yaml")
            if os.path.exists(user_config):
                config_path = user_config
            else:
                config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
    
    def _validate_config(self):
        """Validate configuration structure and values."""
        required_sections = ['audio', 'whisper', 'whisprd', 'commands', 'output', 'performance']
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate audio settings
        audio = self.config['audio']
        if not isinstance(audio.get('sample_rate'), int):
            raise ValueError("audio.sample_rate must be an integer")
        if not isinstance(audio.get('channels'), int):
            raise ValueError("audio.channels must be an integer")
        if not isinstance(audio.get('buffer_size'), int):
            raise ValueError("audio.buffer_size must be an integer")
        
        # Validate whisper settings
        whisper = self.config['whisper']
        valid_models = ['tiny', 'base', 'small', 'medium', 'large']
        if whisper.get('model_size') not in valid_models:
            raise ValueError(f"whisper.model_size must be one of: {valid_models}")
        
        # Validate whisprd settings
        whisprd = self.config['whisprd']
        if not isinstance(whisprd.get('confidence_threshold'), (int, float)):
            raise ValueError("whisprd.confidence_threshold must be a number")
        if not 0 <= whisprd.get('confidence_threshold', 0) <= 1:
            raise ValueError("whisprd.confidence_threshold must be between 0 and 1")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio configuration."""
        return self.config['audio']
    
    def get_whisper_config(self) -> Dict[str, Any]:
        """Get Whisper configuration."""
        return self.config['whisper']
    
    def get_whisprd_config(self) -> Dict[str, Any]:
        """Get whisprd configuration."""
        return self.config['whisprd']
    
    def get_commands(self) -> Dict[str, str]:
        """Get voice commands mapping."""
        return self.config['commands']
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration."""
        return self.config['output']
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration."""
        return self.config['performance']
    
    def get_transcript_file_path(self) -> str:
        """Get expanded transcript file path."""
        path = self.config['output']['transcript_file']
        return os.path.expanduser(path)
    
    def get_alternate_prompts(self) -> Optional[Dict[str, Any]]:
        """Get alternate prompts from YAML file if enabled."""
        whisper_config = self.config['whisper']
        
        if not whisper_config.get('use_alternate_prompts', False):
            return None
        
        prompts_file = whisper_config.get('alternate_prompts_file')
        if not prompts_file:
            logger.warning("use_alternate_prompts is enabled but alternate_prompts_file is not specified")
            return None
        
        try:
            prompts_path = Path(os.path.expanduser(prompts_file))
            if not prompts_path.exists():
                logger.warning(f"Alternate prompts file not found: {prompts_path}")
                return None
            
            with open(prompts_path, 'r') as f:
                prompts = yaml.safe_load(f)
            logger.info(f"Loaded alternate prompts from {prompts_path}")
            return prompts
        except yaml.YAMLError as e:
            logger.error(f"Error parsing alternate prompts file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading alternate prompts: {e}")
            return None
    
    def get_prompt_by_category(self, category: str, prompt_name: str) -> Optional[str]:
        """Get a specific prompt from alternate prompts by category and name."""
        prompts = self.get_alternate_prompts()
        if not prompts:
            return None
        
        try:
            return prompts.get(category, {}).get(prompt_name)
        except (KeyError, TypeError):
            return None
    
    def list_available_prompts(self) -> Dict[str, List[str]]:
        """List all available prompts by category."""
        prompts = self.get_alternate_prompts()
        if not prompts:
            return {}
        
        available = {}
        for category, category_prompts in prompts.items():
            if isinstance(category_prompts, dict):
                available[category] = list(category_prompts.keys())
        
        return available
    
    def reload(self):
        """Reload configuration from file."""
        self.config = self._load_config()
        self._validate_config()
        logger.info("Configuration reloaded") 
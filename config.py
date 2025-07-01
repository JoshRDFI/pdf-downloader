"""Configuration for the PDF Downloader application.

This module contains configuration settings for the application.
"""

import os
import json
import logging
from typing import Dict, Any, Optional


logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the application.
    
    This class handles loading, saving, and accessing configuration settings.
    """
    
    # Default configuration settings
    DEFAULT_CONFIG = {
        "download": {
            "directory": "downloads",
            "concurrent_downloads": 3,
            "retry_count": 3,
            "timeout": 30
        },
        "network": {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "proxy": None,
            "delay": 1.0
        },
        "ui": {
            "theme": "system",
            "font_size": 10,
            "show_status_bar": True
        },
        "logging": {
            "level": "INFO",
            "max_files": 10,
            "max_size_mb": 10
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file (optional)
        """
        # Determine the configuration file path
        if config_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.config_file = os.path.join(base_dir, "config.json")
        else:
            self.config_file = config_file
        
        # Load the configuration
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load the configuration from the file.
        
        Returns:
            Dictionary containing the configuration settings
        """
        # Start with the default configuration
        config = self.DEFAULT_CONFIG.copy()
        
        # Try to load the configuration from the file
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    file_config = json.load(f)
                
                # Update the default configuration with the file configuration
                self._update_dict(config, file_config)
                
                logger.info(f"Loaded configuration from {self.config_file}")
            else:
                logger.info(f"Configuration file {self.config_file} not found, using defaults")
                self.save_config(config)  # Save the default configuration
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
        
        return config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Save the configuration to the file.
        
        Args:
            config: Dictionary containing the configuration settings (optional)
            
        Returns:
            True if the configuration was saved successfully, False otherwise
        """
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"Saved configuration to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            section: Section of the configuration
            key: Key within the section
            default: Default value to return if the key is not found
            
        Returns:
            The configuration value, or the default value if not found
        """
        try:
            return self.config[section][key]
        except KeyError:
            return default
    
    def set(self, section: str, key: str, value: Any) -> bool:
        """Set a configuration value.
        
        Args:
            section: Section of the configuration
            key: Key within the section
            value: Value to set
            
        Returns:
            True if the value was set successfully, False otherwise
        """
        try:
            # Create the section if it doesn't exist
            if section not in self.config:
                self.config[section] = {}
            
            # Set the value
            self.config[section][key] = value
            
            # Save the configuration
            return self.save_config()
        except Exception as e:
            logger.error(f"Error setting configuration value: {e}")
            return False
    
    def _update_dict(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Recursively update a dictionary.
        
        Args:
            target: Dictionary to update
            source: Dictionary with values to update from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict(target[key], value)
            else:
                target[key] = value


# Create a global configuration instance
config = Config()
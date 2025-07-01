"""Configuration for the PDF Downloader application.

This module contains configuration settings for the application.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union


logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the application.
    
    This class handles loading, saving, and accessing configuration settings.
    It can use either a JSON file or the database for storage.
    """
    
    # Default configuration settings
    DEFAULT_CONFIG = {
        "download": {
            "directory": "downloads",
            "concurrent_downloads": 3,
            "rate_limit_kbps": 500,
            "retry_count": 3,
            "retry_delay": 5,
            "timeout": 30
        },
        "network": {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "proxy_enabled": False,
            "proxy_url": "",
            "proxy_username": "",
            "proxy_password": "",
            "timeout": 30
        },
        "file_types": {
            "pdf_enabled": True,
            "epub_enabled": True,
            "txt_enabled": True
        },
        "notification": {
            "enabled": True,
            "download_completed": True,
            "download_failed": True,
            "scan_completed": True
        },
        "appearance": {
            "theme": "system",
            "font_size": 12
        },
        "local_library": {
            "directories": [],
            "scan_on_startup": False,
            "validate_files": True
        }
    }
    
    def __init__(self, config_file: Optional[str] = None, use_db: bool = True):
        """Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file (optional)
            use_db: Whether to use the database for settings (default: True)
        """
        # Determine the configuration file path
        if config_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.config_file = os.path.join(base_dir, "config.json")
        else:
            self.config_file = config_file
        
        self.use_db = use_db
        self.settings_model = None
        
        # Load the configuration
        self.config = self.load_config()
    
    def _get_settings_model(self):
        """Get the settings model instance.
        
        Returns:
            SettingsModel instance
        """
        if self.settings_model is None:
            # Import here to avoid circular imports
            from src.db.settings_model import SettingsModel
            self.settings_model = SettingsModel()
        
        return self.settings_model
    
    def load_config(self) -> Dict[str, Any]:
        """Load the configuration.
        
        Returns:
            Dictionary containing the configuration settings
        """
        # Start with the default configuration
        config = self.DEFAULT_CONFIG.copy()
        
        if self.use_db:
            try:
                # Load settings from the database
                settings_model = self._get_settings_model()
                db_settings = settings_model.get_all()
                
                # Update the configuration with database settings
                for key, value in db_settings.items():
                    if "." in key:
                        # Split the key into category and name
                        category, name = key.split(".", 1)
                        
                        # Ensure the category exists in the config
                        if category not in config:
                            config[category] = {}
                        
                        # Update the config
                        config[category][name] = value
                
                logger.info("Loaded configuration from database")
            except Exception as e:
                logger.error(f"Error loading configuration from database: {e}")
        else:
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
                logger.error(f"Error loading configuration from file: {e}")
        
        return config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Save the configuration.
        
        Args:
            config: Dictionary containing the configuration settings (optional)
            
        Returns:
            True if the configuration was saved successfully, False otherwise
        """
        if config is None:
            config = self.config
        
        if self.use_db:
            try:
                # Save settings to the database
                settings_model = self._get_settings_model()
                
                # Flatten the config dictionary
                for category, settings in config.items():
                    for name, value in settings.items():
                        key = f"{category}.{name}"
                        settings_model.set(key, value)
                
                logger.info("Saved configuration to database")
                return True
            except Exception as e:
                logger.error(f"Error saving configuration to database: {e}")
                return False
        else:
            # Save the configuration to the file
            try:
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                
                # Save the configuration to the file
                with open(self.config_file, "w") as f:
                    json.dump(config, f, indent=4)
                
                logger.info(f"Saved configuration to {self.config_file}")
                return True
            except Exception as e:
                logger.error(f"Error saving configuration to file: {e}")
                return False
    
    def get(self, category: str, name: str, default: Any = None) -> Any:
        """Get a configuration setting.
        
        Args:
            category: Category of the setting
            name: Name of the setting
            default: Default value to return if the setting is not found
            
        Returns:
            Value of the setting, or default if not found
        """
        if self.use_db:
            try:
                # Get the setting from the database
                settings_model = self._get_settings_model()
                key = f"{category}.{name}"
                value = settings_model.get(key)
                
                if value is not None:
                    return value
            except Exception as e:
                logger.error(f"Error getting setting {category}.{name} from database: {e}")
        
        # Get the setting from the config dictionary
        try:
            return self.config.get(category, {}).get(name, default)
        except Exception as e:
            logger.error(f"Error getting setting {category}.{name} from config: {e}")
            return default
    
    def set(self, category: str, name: str, value: Any) -> bool:
        """Set a configuration setting.
        
        Args:
            category: Category of the setting
            name: Name of the setting
            value: Value of the setting
            
        Returns:
            True if the setting was set successfully, False otherwise
        """
        try:
            # Update the config dictionary
            if category not in self.config:
                self.config[category] = {}
            
            self.config[category][name] = value
            
            if self.use_db:
                # Update the setting in the database
                settings_model = self._get_settings_model()
                key = f"{category}.{name}"
                settings_model.set(key, value)
            else:
                # Save the updated config to the file
                self.save_config()
            
            return True
        except Exception as e:
            logger.error(f"Error setting {category}.{name} to {value}: {e}")
            return False
    
    def _update_dict(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Update a dictionary recursively.
        
        Args:
            target: Target dictionary to update
            source: Source dictionary with new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict(target[key], value)
            else:
                target[key] = value


# Create a global config instance
config = Config()
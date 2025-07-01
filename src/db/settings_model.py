"""Settings model for the PDF Downloader application.

This module contains the SettingsModel class for managing application settings.
"""

import logging
import sqlite3
import json
from typing import Dict, Any, List, Optional, Union

from src.db.database import Database


logger = logging.getLogger(__name__)


class SettingsModel:
    """Model for managing application settings in the database.
    
    This class provides methods for getting, setting, and managing application settings.
    Settings are stored in the database and can be accessed by key.
    """
    
    def __init__(self):
        """Initialize the settings model."""
        self.db = Database()
        self._ensure_default_settings()
    
    def _ensure_default_settings(self):
        """Ensure that default settings exist in the database."""
        default_settings = [
            # Network settings
            {
                "key": "network.proxy_enabled",
                "value": "false",
                "category": "network",
                "description": "Whether to use a proxy for network connections"
            },
            {
                "key": "network.proxy_url",
                "value": "",
                "category": "network",
                "description": "Proxy URL (e.g., http://proxy.example.com:8080)"
            },
            {
                "key": "network.proxy_username",
                "value": "",
                "category": "network",
                "description": "Proxy username"
            },
            {
                "key": "network.proxy_password",
                "value": "",
                "category": "network",
                "description": "Proxy password"
            },
            {
                "key": "network.user_agent",
                "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "category": "network",
                "description": "User agent string for HTTP requests"
            },
            {
                "key": "network.timeout",
                "value": "30",
                "category": "network",
                "description": "Timeout for network requests in seconds"
            },
            
            # Download settings
            {
                "key": "download.concurrent_downloads",
                "value": "3",
                "category": "download",
                "description": "Number of concurrent downloads"
            },
            {
                "key": "download.rate_limit_kbps",
                "value": "500",
                "category": "download",
                "description": "Download rate limit in KB/s (0 for unlimited)"
            },
            {
                "key": "download.retry_count",
                "value": "3",
                "category": "download",
                "description": "Number of times to retry a failed download"
            },
            {
                "key": "download.retry_delay",
                "value": "5",
                "category": "download",
                "description": "Delay between retry attempts in seconds"
            },
            
            # File type preferences
            {
                "key": "file_types.pdf_enabled",
                "value": "true",
                "category": "file_types",
                "description": "Whether to download PDF files"
            },
            {
                "key": "file_types.epub_enabled",
                "value": "true",
                "category": "file_types",
                "description": "Whether to download EPUB files"
            },
            {
                "key": "file_types.txt_enabled",
                "value": "true",
                "category": "file_types",
                "description": "Whether to download TXT files"
            },
            
            # Notification settings
            {
                "key": "notification.enabled",
                "value": "true",
                "category": "notification",
                "description": "Whether to show notifications"
            },
            {
                "key": "notification.download_completed",
                "value": "true",
                "category": "notification",
                "description": "Whether to show notifications for completed downloads"
            },
            {
                "key": "notification.download_failed",
                "value": "true",
                "category": "notification",
                "description": "Whether to show notifications for failed downloads"
            },
            {
                "key": "notification.scan_completed",
                "value": "true",
                "category": "notification",
                "description": "Whether to show notifications for completed scans"
            },
            
            # Appearance settings
            {
                "key": "appearance.theme",
                "value": "system",
                "category": "appearance",
                "description": "Application theme (system, light, dark)"
            },
            {
                "key": "appearance.font_size",
                "value": "12",
                "category": "appearance",
                "description": "Font size for the application"
            }
        ]
        
        for setting in default_settings:
            try:
                # Check if the setting already exists
                query = "SELECT * FROM settings WHERE key = ?"
                params = (setting["key"],)
                result = self.db.fetch_one(query, params)
                
                if not result:
                    # Insert the default setting
                    query = """
                    INSERT INTO settings (key, value, category, description)
                    VALUES (?, ?, ?, ?)
                    """
                    params = (
                        setting["key"],
                        setting["value"],
                        setting["category"],
                        setting["description"]
                    )
                    self.db.execute_query(query, params)
                    logger.info(f"Added default setting: {setting['key']}")
            except sqlite3.Error as e:
                logger.error(f"Error ensuring default setting {setting['key']}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value by key.
        
        Args:
            key: Setting key
            default: Default value to return if the setting is not found
            
        Returns:
            Setting value, or default if not found
        """
        try:
            query = "SELECT value FROM settings WHERE key = ?"
            params = (key,)
            result = self.db.fetch_one(query, params)
            
            if result:
                value = result["value"]
                
                # Try to convert the value to the appropriate type
                if value.lower() == "true":
                    return True
                elif value.lower() == "false":
                    return False
                
                try:
                    # Try to convert to int
                    return int(value)
                except ValueError:
                    pass
                
                try:
                    # Try to convert to float
                    return float(value)
                except ValueError:
                    pass
                
                try:
                    # Try to convert to JSON
                    return json.loads(value)
                except json.JSONDecodeError:
                    pass
                
                # Return as string
                return value
            
            return default
        except sqlite3.Error as e:
            logger.error(f"Error getting setting {key}: {e}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set a setting value by key.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if the setting was set, False otherwise
        """
        try:
            # Convert the value to a string
            if isinstance(value, bool):
                value_str = str(value).lower()
            elif isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)
            
            # Check if the setting exists
            query = "SELECT * FROM settings WHERE key = ?"
            params = (key,)
            result = self.db.fetch_one(query, params)
            
            if result:
                # Update the setting
                query = "UPDATE settings SET value = ? WHERE key = ?"
                params = (value_str, key)
                self.db.execute_query(query, params)
            else:
                # Get the category from the key (e.g., "network.proxy_enabled" -> "network")
                category = key.split(".")[0] if "." in key else "general"
                
                # Insert the setting
                query = """
                INSERT INTO settings (key, value, category, description)
                VALUES (?, ?, ?, ?)
                """
                params = (key, value_str, category, "")
                self.db.execute_query(query, params)
            
            logger.info(f"Set setting {key} to {value}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error setting setting {key}: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings.
        
        Returns:
            Dictionary of all settings
        """
        try:
            query = "SELECT key, value FROM settings"
            results = self.db.fetch_all(query)
            
            settings = {}
            for result in results:
                key = result["key"]
                value = result["value"]
                
                # Try to convert the value to the appropriate type
                if value.lower() == "true":
                    settings[key] = True
                elif value.lower() == "false":
                    settings[key] = False
                else:
                    try:
                        # Try to convert to int
                        settings[key] = int(value)
                    except ValueError:
                        try:
                            # Try to convert to float
                            settings[key] = float(value)
                        except ValueError:
                            try:
                                # Try to convert to JSON
                                settings[key] = json.loads(value)
                            except json.JSONDecodeError:
                                # Return as string
                                settings[key] = value
            
            return settings
        except sqlite3.Error as e:
            logger.error(f"Error getting all settings: {e}")
            return {}
    
    def get_by_category(self, category: str) -> Dict[str, Any]:
        """Get settings by category.
        
        Args:
            category: Setting category
            
        Returns:
            Dictionary of settings in the specified category
        """
        try:
            query = "SELECT key, value FROM settings WHERE category = ?"
            params = (category,)
            results = self.db.fetch_all(query, params)
            
            settings = {}
            for result in results:
                key = result["key"]
                value = result["value"]
                
                # Try to convert the value to the appropriate type
                if value.lower() == "true":
                    settings[key] = True
                elif value.lower() == "false":
                    settings[key] = False
                else:
                    try:
                        # Try to convert to int
                        settings[key] = int(value)
                    except ValueError:
                        try:
                            # Try to convert to float
                            settings[key] = float(value)
                        except ValueError:
                            try:
                                # Try to convert to JSON
                                settings[key] = json.loads(value)
                            except json.JSONDecodeError:
                                # Return as string
                                settings[key] = value
            
            return settings
        except sqlite3.Error as e:
            logger.error(f"Error getting settings for category {category}: {e}")
            return {}
    
    def delete(self, key: str) -> bool:
        """Delete a setting by key.
        
        Args:
            key: Setting key
            
        Returns:
            True if the setting was deleted, False otherwise
        """
        try:
            query = "DELETE FROM settings WHERE key = ?"
            params = (key,)
            self.db.execute_query(query, params)
            
            logger.info(f"Deleted setting {key}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error deleting setting {key}: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to their default values.
        
        Returns:
            True if the settings were reset, False otherwise
        """
        try:
            # Delete all settings
            query = "DELETE FROM settings"
            self.db.execute_query(query)
            
            # Re-add default settings
            self._ensure_default_settings()
            
            logger.info("Reset all settings to defaults")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error resetting settings to defaults: {e}")
            return False
"""File type plugin system for the PDF Downloader application.

This module provides functionality for loading and managing file type plugins.
"""

import os
import logging
from typing import Dict, Type, Optional, List, Any, Callable

from src.plugins import PluginManager

logger = logging.getLogger(__name__)


class FileTypeValidator:
    """Base class for file type validators.
    
    This class defines the interface that all file type validators must implement.
    """
    
    # File type identifier (e.g., "pdf", "epub")
    FILE_TYPE = ""
    
    # File extensions supported by this validator (e.g., [".pdf"])
    EXTENSIONS = []
    
    @classmethod
    def can_validate(cls, file_path: str) -> bool:
        """Check if this validator can validate the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this validator can validate the file, False otherwise
        """
        _, ext = os.path.splitext(file_path)
        return ext.lower() in cls.EXTENSIONS
    
    def validate(self, file_path: str) -> Dict[str, Any]:
        """Validate the given file.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Dictionary containing validation results
        """
        raise NotImplementedError("Subclasses must implement validate()")


class FileTypePluginManager(PluginManager):
    """Manager for file type plugins.
    
    This class provides functionality for loading and managing file type plugins.
    """
    
    _instance = None
    
    def __new__(cls):
        """Create a singleton instance of the file type plugin manager."""
        if cls._instance is None:
            cls._instance = super(FileTypePluginManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the file type plugin manager."""
        if not hasattr(self, "_initialized") or not self._initialized:
            plugin_dir = os.path.join("src", "plugins", "file_types")
            super().__init__(plugin_dir, FileTypeValidator)
            self._initialized = True
            self._extension_map = {}
            self._update_extension_map()
    
    def _update_extension_map(self) -> None:
        """Update the extension map with registered plugins."""
        self._extension_map = {}
        
        for plugin_id, plugin_class in self.plugins.items():
            for ext in plugin_class.EXTENSIONS:
                self._extension_map[ext.lower()] = plugin_id
    
    def register_plugin(self, plugin_id: str, plugin_class: Type) -> None:
        """Register a plugin with the manager.
        
        Args:
            plugin_id: ID for the plugin
            plugin_class: Plugin class to register
        """
        super().register_plugin(plugin_id, plugin_class)
        self._update_extension_map()
    
    def get_validator_for_file(self, file_path: str) -> Optional[FileTypeValidator]:
        """Get a validator for the given file.
        
        Args:
            file_path: Path to the file to get a validator for
            
        Returns:
            Validator instance if found, None otherwise
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        plugin_id = self._extension_map.get(ext)
        if plugin_id is None:
            return None
        
        plugin_class = self.get_plugin(plugin_id)
        if plugin_class is None:
            return None
        
        try:
            return plugin_class()
        except Exception as e:
            logger.error(f"Error creating validator {plugin_id}: {e}")
            return None
    
    def get_validator_for_type(self, file_type: str) -> Optional[FileTypeValidator]:
        """Get a validator for the given file type.
        
        Args:
            file_type: Type of the file to get a validator for
            
        Returns:
            Validator instance if found, None otherwise
        """
        for plugin_id, plugin_class in self.plugins.items():
            if plugin_class.FILE_TYPE == file_type:
                try:
                    return plugin_class()
                except Exception as e:
                    logger.error(f"Error creating validator {plugin_id}: {e}")
                    return None
        
        return None
    
    def get_supported_extensions(self) -> List[str]:
        """Get a list of supported file extensions.
        
        Returns:
            List of supported file extensions
        """
        return list(self._extension_map.keys())
    
    def get_supported_types(self) -> List[str]:
        """Get a list of supported file types.
        
        Returns:
            List of supported file types
        """
        return [plugin_class.FILE_TYPE for plugin_class in self.plugins.values() if plugin_class.FILE_TYPE]


# Initialize the file type plugin manager
file_type_plugin_manager = FileTypePluginManager()
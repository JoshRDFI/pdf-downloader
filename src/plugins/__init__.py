"""Plugin system for the PDF Downloader application.

This module provides the base functionality for the plugin system.
"""

import os
import sys
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Type, Optional, Callable

logger = logging.getLogger(__name__)


class PluginManager:
    """Base class for plugin managers.
    
    This class provides common functionality for loading and managing plugins.
    """
    
    def __init__(self, plugin_dir: str, base_class: Type):
        """Initialize the plugin manager.
        
        Args:
            plugin_dir: Directory to load plugins from
            base_class: Base class that all plugins must inherit from
        """
        self.plugin_dir = plugin_dir
        self.base_class = base_class
        self.plugins: Dict[str, Type] = {}
    
    def discover_plugins(self) -> None:
        """Discover plugins in the plugin directory."""
        plugin_path = Path(self.plugin_dir)
        
        # Create the plugin directory if it doesn't exist
        os.makedirs(plugin_path, exist_ok=True)
        
        # Add the plugin directory to the Python path if it's not already there
        if str(plugin_path.parent) not in sys.path:
            sys.path.insert(0, str(plugin_path.parent))
        
        # Discover plugins
        for file in plugin_path.glob("*.py"):
            if file.name.startswith("__"):
                continue
            
            module_name = file.stem
            full_module_name = f"{plugin_path.name}.{module_name}"
            
            try:
                # Import the module
                module = importlib.import_module(full_module_name)
                
                # Look for plugin classes in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    # Check if it's a class that inherits from the base class
                    if isinstance(attr, type) and issubclass(attr, self.base_class) and attr is not self.base_class:
                        # Get the plugin ID
                        plugin_id = getattr(attr, "PLUGIN_ID", module_name)
                        
                        # Register the plugin
                        self.register_plugin(plugin_id, attr)
            except Exception as e:
                logger.error(f"Error loading plugin module {module_name}: {e}")
    
    def register_plugin(self, plugin_id: str, plugin_class: Type) -> None:
        """Register a plugin with the manager.
        
        Args:
            plugin_id: ID for the plugin
            plugin_class: Plugin class to register
        """
        if not issubclass(plugin_class, self.base_class):
            raise TypeError(f"Plugin class must inherit from {self.base_class.__name__}: {plugin_class.__name__}")
        
        self.plugins[plugin_id] = plugin_class
        logger.info(f"Registered plugin: {plugin_id} -> {plugin_class.__name__}")
    
    def get_plugin(self, plugin_id: str) -> Optional[Type]:
        """Get a plugin by its ID.
        
        Args:
            plugin_id: ID of the plugin to get
            
        Returns:
            Plugin class if found, None otherwise
        """
        return self.plugins.get(plugin_id)
    
    def get_all_plugins(self) -> Dict[str, Type]:
        """Get all registered plugins.
        
        Returns:
            Dictionary mapping plugin IDs to plugin classes
        """
        return self.plugins.copy()
"""Scraper plugin system for the PDF Downloader application.

This module provides functionality for loading and managing scraper plugins.
"""

import os
import logging
from typing import Dict, Type, Optional, List, Any

from src.plugins import PluginManager
from src.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class ScraperPluginManager(PluginManager):
    """Manager for scraper plugins.
    
    This class provides functionality for loading and managing scraper plugins.
    """
    
    _instance = None
    
    def __new__(cls):
        """Create a singleton instance of the scraper plugin manager."""
        if cls._instance is None:
            cls._instance = super(ScraperPluginManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the scraper plugin manager."""
        if not hasattr(self, "_initialized") or not self._initialized:
            plugin_dir = os.path.join("src", "plugins", "scrapers")
            super().__init__(plugin_dir, BaseScraper)
            self._initialized = True
    
    def create_scraper(self, scraper_type: str, base_url: str, **kwargs) -> Optional[BaseScraper]:
        """Create a scraper instance for the given type and URL.
        
        Args:
            scraper_type: Type identifier for the scraper
            base_url: Base URL for the scraper
            **kwargs: Additional arguments to pass to the scraper constructor
            
        Returns:
            Scraper instance if the type is registered, None otherwise
        """
        scraper_class = self.get_plugin(scraper_type)
        if scraper_class is None:
            logger.warning(f"No scraper registered for type: {scraper_type}")
            return None
        
        try:
            scraper = scraper_class(base_url, **kwargs)
            return scraper
        except Exception as e:
            logger.error(f"Error creating scraper {scraper_type}: {e}")
            return None


# Initialize the scraper plugin manager
scraper_plugin_manager = ScraperPluginManager()
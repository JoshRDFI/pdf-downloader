"""Scraper registry for the PDF Downloader application.

This module provides a registry for scraper classes and functions to load and manage scrapers.
"""

import importlib
import logging
import os
from pathlib import Path
from typing import Dict, Type, Optional

from src.scrapers.base_scraper import BaseScraper


logger = logging.getLogger(__name__)


class ScraperRegistry:
    """Registry for scraper classes.
    
    This class maintains a registry of available scrapers and provides methods
    for registering, loading, and retrieving scrapers.
    """
    
    _instance = None
    
    def __new__(cls):
        """Create a singleton instance of the scraper registry."""
        if cls._instance is None:
            cls._instance = super(ScraperRegistry, cls).__new__(cls)
            cls._instance._scrapers = {}
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the scraper registry."""
        if not self._initialized:
            self._scrapers = {}
            self._initialized = True
    
    def register_scraper(self, scraper_type: str, scraper_class: Type[BaseScraper]) -> None:
        """Register a scraper class with the registry.
        
        Args:
            scraper_type: Type identifier for the scraper
            scraper_class: Scraper class to register
        """
        if not issubclass(scraper_class, BaseScraper):
            raise TypeError(f"Scraper class must inherit from BaseScraper: {scraper_class.__name__}")
        
        self._scrapers[scraper_type] = scraper_class
        logger.info(f"Registered scraper: {scraper_type} -> {scraper_class.__name__}")
    
    def get_scraper_class(self, scraper_type: str) -> Optional[Type[BaseScraper]]:
        """Get a scraper class by its type identifier.
        
        Args:
            scraper_type: Type identifier for the scraper
            
        Returns:
            Scraper class if found, None otherwise
        """
        return self._scrapers.get(scraper_type)
    
    def create_scraper(self, scraper_type: str, base_url: str, **kwargs) -> Optional[BaseScraper]:
        """Create a scraper instance for the given type and URL.
        
        Args:
            scraper_type: Type identifier for the scraper
            base_url: Base URL for the scraper
            **kwargs: Additional arguments to pass to the scraper constructor
            
        Returns:
            Scraper instance if the type is registered, None otherwise
        """
        scraper_class = self.get_scraper_class(scraper_type)
        if scraper_class is None:
            logger.warning(f"No scraper registered for type: {scraper_type}")
            return None
        
        try:
            scraper = scraper_class(base_url, **kwargs)
            return scraper
        except Exception as e:
            logger.error(f"Error creating scraper {scraper_type}: {e}")
            return None
    
    def get_available_scrapers(self) -> Dict[str, Type[BaseScraper]]:
        """Get all registered scrapers.
        
        Returns:
            Dictionary mapping scraper types to scraper classes
        """
        return self._scrapers.copy()


def load_scrapers() -> None:
    """Load all available scrapers from the scrapers directory.
    
    This function scans the scrapers directory for Python modules and attempts
    to load and register any scraper classes defined in them.
    """
    registry = ScraperRegistry()
    scrapers_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Skip __init__.py and base_scraper.py
    skip_files = {"__init__.py", "base_scraper.py"}
    
    for file in scrapers_dir.glob("*.py"):
        if file.name in skip_files:
            continue
        
        module_name = file.stem
        full_module_name = f"src.scrapers.{module_name}"
        
        try:
            module = importlib.import_module(full_module_name)
            
            # Look for scraper classes in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # Check if it's a class that inherits from BaseScraper
                if isinstance(attr, type) and issubclass(attr, BaseScraper) and attr is not BaseScraper:
                    # Use the module name as the scraper type if not specified
                    scraper_type = getattr(attr, "SCRAPER_TYPE", module_name)
                    registry.register_scraper(scraper_type, attr)
        except Exception as e:
            logger.error(f"Error loading scraper module {module_name}: {e}")


# Register the built-in scrapers
def register_builtin_scrapers() -> None:
    """Register built-in scrapers with the registry."""
    registry = ScraperRegistry()
    
    # Register the generic scraper as a fallback
    from src.scrapers.generic_scraper import GenericScraper
    registry.register_scraper("generic", GenericScraper)
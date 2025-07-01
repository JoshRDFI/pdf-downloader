"""Modular site scrapers for the PDF Downloader application.

This module contains site-specific scraper implementations, including:
- Base scraper class with common functionality
- Site-specific scraper implementations
- Scraper registration and discovery
"""

from src.scrapers.base_scraper import BaseScraper
from src.scrapers.registry import ScraperRegistry, load_scrapers, register_builtin_scrapers

# Initialize the scraper registry
register_builtin_scrapers()
load_scrapers()

__all__ = ['BaseScraper', 'ScraperRegistry', 'load_scrapers']
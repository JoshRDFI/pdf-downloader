"""Base scraper implementation for the PDF Downloader application.

This module provides the base scraper class that all site-specific scrapers should inherit from.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup


class BaseScraper(ABC):
    """Base class for all site scrapers.
    
    This abstract class defines the interface that all site-specific scrapers
    must implement. It also provides common functionality for making HTTP requests
    and parsing HTML.
    """
    
    def __init__(self, base_url: str, user_agent: Optional[str] = None, 
                 proxy: Optional[Dict[str, str]] = None):
        """Initialize the scraper with the given base URL and optional settings.
        
        Args:
            base_url: Base URL of the site to scrape
            user_agent: Optional user agent string to use for requests
            proxy: Optional proxy configuration for requests
        """
        self.base_url = base_url
        self.user_agent = user_agent or "PDF Downloader/1.0"
        self.proxy = proxy
        self.session = requests.Session()
        
        # Configure session
        self.session.headers.update({"User-Agent": self.user_agent})
        if self.proxy:
            self.session.proxies.update(self.proxy)
    
    def get_page(self, url: str) -> BeautifulSoup:
        """Fetch a page and return a BeautifulSoup object for parsing.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object for the fetched page
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    
    @abstractmethod
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get a list of categories from the site.
        
        Returns:
            List of dictionaries containing category information
        """
        pass
    
    @abstractmethod
    def get_files_in_category(self, category_id: str) -> List[Dict[str, Any]]:
        """Get a list of files in the given category.
        
        Args:
            category_id: ID or path of the category to get files from
            
        Returns:
            List of dictionaries containing file information
        """
        pass
    
    @abstractmethod
    def get_download_url(self, file_id: str) -> str:
        """Get the download URL for the given file.
        
        Args:
            file_id: ID or path of the file to get the download URL for
            
        Returns:
            Download URL for the file
        """
        pass
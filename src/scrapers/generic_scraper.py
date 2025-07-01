"""Generic scraper implementation for the PDF Downloader application.

This module provides a generic scraper that can be used for basic websites.
"""

import logging
from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.scrapers.base_scraper import BaseScraper


logger = logging.getLogger(__name__)


class GenericScraper(BaseScraper):
    """Generic scraper for basic websites.
    
    This scraper provides a basic implementation that can work with simple websites
    by looking for links to PDF files.
    """
    
    SCRAPER_TYPE = "generic"
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get a list of categories from the site.
        
        For the generic scraper, this simply returns a single "default" category.
        
        Returns:
            List of dictionaries containing category information
        """
        return [{
            "id": "default",
            "name": "Default",
            "url": self.base_url,
            "parent_id": None
        }]
    
    def get_files_in_category(self, category_id: str) -> List[Dict[str, Any]]:
        """Get a list of files in the given category.
        
        For the generic scraper, this scans the base URL for links to PDF files.
        
        Args:
            category_id: ID or path of the category to get files from
            
        Returns:
            List of dictionaries containing file information
        """
        files = []
        
        try:
            # Use the base URL if category is default, otherwise use the category URL
            url = self.base_url if category_id == "default" else category_id
            
            # Get the page content
            soup = self.get_page(url)
            
            # Find all links
            links = soup.find_all("a")
            
            for link in links:
                href = link.get("href")
                if not href:
                    continue
                
                # Check if the link points to a PDF file
                if href.lower().endswith(".pdf"):
                    # Get the full URL
                    file_url = urljoin(url, href)
                    
                    # Get the file name from the URL or link text
                    file_name = link.text.strip() or href.split("/")[-1]
                    
                    files.append({
                        "id": file_url,
                        "name": file_name,
                        "url": file_url,
                        "size": None,  # Size is unknown
                        "file_type": "pdf",
                        "category_id": category_id
                    })
            
            logger.info(f"Found {len(files)} PDF files at {url}")
        except Exception as e:
            logger.error(f"Error scraping files from {category_id}: {e}")
        
        return files
    
    def get_download_url(self, file_id: str) -> str:
        """Get the download URL for the given file.
        
        For the generic scraper, the file ID is already the download URL.
        
        Args:
            file_id: ID or path of the file to get the download URL for
            
        Returns:
            Download URL for the file
        """
        return file_id
"""Example scraper plugin for the PDF Downloader application.

This module demonstrates how to create a custom scraper plugin.
"""

import logging
from typing import List, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.scrapers.base_scraper import BaseScraper


logger = logging.getLogger(__name__)


class ExampleScraper(BaseScraper):
    """Example scraper plugin.
    
    This scraper demonstrates how to create a custom scraper plugin.
    It's similar to the generic scraper but with a different implementation.
    """
    
    # Unique identifier for this scraper
    PLUGIN_ID = "example"
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get a list of categories from the site.
        
        For this example, we'll return a few hardcoded categories.
        
        Returns:
            List of dictionaries containing category information
        """
        return [
            {
                "id": "books",
                "name": "Books",
                "url": urljoin(self.base_url, "/books"),
                "parent_id": None
            },
            {
                "id": "articles",
                "name": "Articles",
                "url": urljoin(self.base_url, "/articles"),
                "parent_id": None
            },
            {
                "id": "fiction",
                "name": "Fiction",
                "url": urljoin(self.base_url, "/books/fiction"),
                "parent_id": "books"
            },
            {
                "id": "non-fiction",
                "name": "Non-Fiction",
                "url": urljoin(self.base_url, "/books/non-fiction"),
                "parent_id": "books"
            }
        ]
    
    def get_files_in_category(self, category_id: str) -> List[Dict[str, Any]]:
        """Get a list of files in the given category.
        
        For this example, we'll return some hardcoded files for each category.
        
        Args:
            category_id: ID or path of the category to get files from
            
        Returns:
            List of dictionaries containing file information
        """
        # In a real scraper, you would fetch the page and parse it
        # For this example, we'll just return some hardcoded files
        
        if category_id == "books":
            return [
                {
                    "id": "book1",
                    "name": "Example Book 1",
                    "url": urljoin(self.base_url, "/books/example-book-1.pdf"),
                    "size": 1024 * 1024,  # 1 MB
                    "file_type": "pdf",
                    "category_id": category_id
                },
                {
                    "id": "book2",
                    "name": "Example Book 2",
                    "url": urljoin(self.base_url, "/books/example-book-2.epub"),
                    "size": 2 * 1024 * 1024,  # 2 MB
                    "file_type": "epub",
                    "category_id": category_id
                }
            ]
        elif category_id == "articles":
            return [
                {
                    "id": "article1",
                    "name": "Example Article 1",
                    "url": urljoin(self.base_url, "/articles/example-article-1.pdf"),
                    "size": 512 * 1024,  # 512 KB
                    "file_type": "pdf",
                    "category_id": category_id
                },
                {
                    "id": "article2",
                    "name": "Example Article 2",
                    "url": urljoin(self.base_url, "/articles/example-article-2.txt"),
                    "size": 10 * 1024,  # 10 KB
                    "file_type": "txt",
                    "category_id": category_id
                }
            ]
        elif category_id == "fiction":
            return [
                {
                    "id": "fiction1",
                    "name": "Example Fiction 1",
                    "url": urljoin(self.base_url, "/books/fiction/example-fiction-1.pdf"),
                    "size": 1.5 * 1024 * 1024,  # 1.5 MB
                    "file_type": "pdf",
                    "category_id": category_id
                },
                {
                    "id": "fiction2",
                    "name": "Example Fiction 2",
                    "url": urljoin(self.base_url, "/books/fiction/example-fiction-2.epub"),
                    "size": 3 * 1024 * 1024,  # 3 MB
                    "file_type": "epub",
                    "category_id": category_id
                }
            ]
        elif category_id == "non-fiction":
            return [
                {
                    "id": "non-fiction1",
                    "name": "Example Non-Fiction 1",
                    "url": urljoin(self.base_url, "/books/non-fiction/example-non-fiction-1.pdf"),
                    "size": 2.5 * 1024 * 1024,  # 2.5 MB
                    "file_type": "pdf",
                    "category_id": category_id
                },
                {
                    "id": "non-fiction2",
                    "name": "Example Non-Fiction 2",
                    "url": urljoin(self.base_url, "/books/non-fiction/example-non-fiction-2.txt"),
                    "size": 20 * 1024,  # 20 KB
                    "file_type": "txt",
                    "category_id": category_id
                }
            ]
        else:
            logger.warning(f"Unknown category: {category_id}")
            return []
    
    def get_download_url(self, file_id: str) -> str:
        """Get the download URL for the given file.
        
        For this example, we'll just return a URL based on the file ID.
        
        Args:
            file_id: ID or path of the file to get the download URL for
            
        Returns:
            Download URL for the file
        """
        # In a real scraper, you might need to fetch a page and extract the download URL
        # For this example, we'll just construct a URL based on the file ID
        
        # Map file IDs to URLs
        url_map = {
            "book1": urljoin(self.base_url, "/download/books/example-book-1.pdf"),
            "book2": urljoin(self.base_url, "/download/books/example-book-2.epub"),
            "article1": urljoin(self.base_url, "/download/articles/example-article-1.pdf"),
            "article2": urljoin(self.base_url, "/download/articles/example-article-2.txt"),
            "fiction1": urljoin(self.base_url, "/download/books/fiction/example-fiction-1.pdf"),
            "fiction2": urljoin(self.base_url, "/download/books/fiction/example-fiction-2.epub"),
            "non-fiction1": urljoin(self.base_url, "/download/books/non-fiction/example-non-fiction-1.pdf"),
            "non-fiction2": urljoin(self.base_url, "/download/books/non-fiction/example-non-fiction-2.txt")
        }
        
        return url_map.get(file_id, file_id)
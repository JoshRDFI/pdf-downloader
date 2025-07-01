"""Test utilities for scrapers.

This module provides utilities for testing scrapers.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Type
from unittest.mock import MagicMock, patch

from src.scrapers.base_scraper import BaseScraper


logger = logging.getLogger(__name__)


class MockResponse:
    """Mock response object for testing scrapers."""
    
    def __init__(self, text: str, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        """Initialize the mock response.
        
        Args:
            text: Response text
            status_code: HTTP status code
            headers: Response headers
        """
        self.text = text
        self.status_code = status_code
        self.headers = headers or {}
    
    def raise_for_status(self):
        """Raise an exception if the status code indicates an error."""
        if self.status_code >= 400:
            from requests.exceptions import HTTPError
            raise HTTPError(f"HTTP Error: {self.status_code}")


class ScraperTester:
    """Utility for testing scrapers.
    
    This class provides methods for testing scrapers with mock data.
    """
    
    def __init__(self, scraper_class: Type[BaseScraper], base_url: str = "http://example.com"):
        """Initialize the scraper tester.
        
        Args:
            scraper_class: Scraper class to test
            base_url: Base URL for the scraper
        """
        self.scraper_class = scraper_class
        self.base_url = base_url
        self.mock_responses = {}
    
    def add_mock_response(self, url: str, html: str, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        """Add a mock response for a URL.
        
        Args:
            url: URL to mock
            html: HTML response
            status_code: HTTP status code
            headers: Response headers
        """
        self.mock_responses[url] = MockResponse(html, status_code, headers)
    
    def add_mock_responses_from_directory(self, directory: str):
        """Add mock responses from a directory of HTML files.
        
        Args:
            directory: Directory containing HTML files
        """
        for file in os.listdir(directory):
            if file.endswith(".html"):
                file_path = os.path.join(directory, file)
                url = file.replace(".html", "")
                
                # If the file name is a URL, use it as is
                if url.startswith("http"):
                    pass
                # Otherwise, join it with the base URL
                else:
                    url = f"{self.base_url}/{url}"
                
                with open(file_path, "r", encoding="utf-8") as f:
                    html = f.read()
                
                self.add_mock_response(url, html)
    
    def _mock_get(self, url, **kwargs):
        """Mock the requests.get method.
        
        Args:
            url: URL to get
            **kwargs: Additional arguments
            
        Returns:
            Mock response
        """
        if url in self.mock_responses:
            return self.mock_responses[url]
        else:
            logger.warning(f"No mock response for URL: {url}")
            return MockResponse("", 404)
    
    def test_scraper(self) -> Dict[str, Any]:
        """Test the scraper with mock data.
        
        Returns:
            Dictionary containing test results
        """
        results = {
            "categories": [],
            "files": {},
            "download_urls": {},
            "errors": []
        }
        
        # Create a mock session
        mock_session = MagicMock()
        mock_session.get.side_effect = self._mock_get
        
        # Create the scraper with the mock session
        with patch("requests.Session", return_value=mock_session):
            scraper = self.scraper_class(self.base_url)
            
            # Test get_categories
            try:
                categories = scraper.get_categories()
                results["categories"] = categories
            except Exception as e:
                logger.error(f"Error testing get_categories: {e}")
                results["errors"].append(f"get_categories: {str(e)}")
            
            # Test get_files_in_category for each category
            for category in results["categories"]:
                category_id = category["id"]
                try:
                    files = scraper.get_files_in_category(category_id)
                    results["files"][category_id] = files
                except Exception as e:
                    logger.error(f"Error testing get_files_in_category for {category_id}: {e}")
                    results["errors"].append(f"get_files_in_category({category_id}): {str(e)}")
            
            # Test get_download_url for each file
            for category_id, files in results["files"].items():
                for file in files:
                    file_id = file["id"]
                    try:
                        download_url = scraper.get_download_url(file_id)
                        results["download_urls"][file_id] = download_url
                    except Exception as e:
                        logger.error(f"Error testing get_download_url for {file_id}: {e}")
                        results["errors"].append(f"get_download_url({file_id}): {str(e)}")
        
        return results
    
    def save_test_results(self, results: Dict[str, Any], output_file: str):
        """Save test results to a JSON file.
        
        Args:
            results: Test results
            output_file: Output file path
        """
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved test results to {output_file}")
    
    @staticmethod
    def load_test_results(input_file: str) -> Dict[str, Any]:
        """Load test results from a JSON file.
        
        Args:
            input_file: Input file path
            
        Returns:
            Test results
        """
        with open(input_file, "r", encoding="utf-8") as f:
            results = json.load(f)
        
        logger.info(f"Loaded test results from {input_file}")
        return results
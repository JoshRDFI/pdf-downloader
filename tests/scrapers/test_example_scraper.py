"""Test for the example scraper plugin.

This module demonstrates how to test a scraper plugin.
"""

import os
import unittest
from unittest.mock import patch

from src.plugins.scrapers.example_scraper import ExampleScraper
from tests.scrapers import ScraperTester


class TestExampleScraper(unittest.TestCase):
    """Test case for the example scraper plugin."""
    
    def setUp(self):
        """Set up the test case."""
        self.base_url = "http://example.com"
        self.tester = ScraperTester(ExampleScraper, self.base_url)
    
    def test_get_categories(self):
        """Test the get_categories method."""
        # Since the example scraper doesn't actually fetch any pages,
        # we don't need to add mock responses
        
        # Create the scraper directly
        scraper = ExampleScraper(self.base_url)
        
        # Get the categories
        categories = scraper.get_categories()
        
        # Check the results
        self.assertEqual(len(categories), 4)
        self.assertEqual(categories[0]["id"], "books")
        self.assertEqual(categories[1]["id"], "articles")
        self.assertEqual(categories[2]["id"], "fiction")
        self.assertEqual(categories[3]["id"], "non-fiction")
    
    def test_get_files_in_category(self):
        """Test the get_files_in_category method."""
        # Create the scraper directly
        scraper = ExampleScraper(self.base_url)
        
        # Get the files in each category
        books_files = scraper.get_files_in_category("books")
        articles_files = scraper.get_files_in_category("articles")
        fiction_files = scraper.get_files_in_category("fiction")
        non_fiction_files = scraper.get_files_in_category("non-fiction")
        
        # Check the results
        self.assertEqual(len(books_files), 2)
        self.assertEqual(books_files[0]["id"], "book1")
        self.assertEqual(books_files[1]["id"], "book2")
        
        self.assertEqual(len(articles_files), 2)
        self.assertEqual(articles_files[0]["id"], "article1")
        self.assertEqual(articles_files[1]["id"], "article2")
        
        self.assertEqual(len(fiction_files), 2)
        self.assertEqual(fiction_files[0]["id"], "fiction1")
        self.assertEqual(fiction_files[1]["id"], "fiction2")
        
        self.assertEqual(len(non_fiction_files), 2)
        self.assertEqual(non_fiction_files[0]["id"], "non-fiction1")
        self.assertEqual(non_fiction_files[1]["id"], "non-fiction2")
    
    def test_get_download_url(self):
        """Test the get_download_url method."""
        # Create the scraper directly
        scraper = ExampleScraper(self.base_url)
        
        # Get the download URL for each file
        book1_url = scraper.get_download_url("book1")
        book2_url = scraper.get_download_url("book2")
        
        # Check the results
        self.assertEqual(book1_url, "http://example.com/download/books/example-book-1.pdf")
        self.assertEqual(book2_url, "http://example.com/download/books/example-book-2.epub")
    
    def test_full_scraper(self):
        """Test the full scraper using the ScraperTester."""
        # Run the test
        results = self.tester.test_scraper()
        
        # Check the results
        self.assertEqual(len(results["categories"]), 4)
        self.assertEqual(len(results["files"]), 4)
        self.assertEqual(len(results["download_urls"]), 8)
        self.assertEqual(len(results["errors"]), 0)


if __name__ == "__main__":
    unittest.main()
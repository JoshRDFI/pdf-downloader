# Developing Scraper Plugins

This document explains how to develop new scraper plugins for the PDF Downloader application.

## Overview

The PDF Downloader application uses a modular scraper system to support different websites. Each scraper is responsible for extracting information about files from a specific website. The application provides a base scraper class that all scrapers must inherit from, and a plugin system for loading and managing scrapers.

## Creating a New Scraper

To create a new scraper, you need to create a Python module that defines a class inheriting from `BaseScraper`. The module should be placed in the `src/plugins/scrapers` directory.

### Basic Structure

```python
from src.scrapers.base_scraper import BaseScraper

class MyScraper(BaseScraper):
    # Unique identifier for this scraper
    PLUGIN_ID = "my_scraper"
    
    def get_categories(self):
        # Implementation...
        
    def get_files_in_category(self, category_id):
        # Implementation...
        
    def get_download_url(self, file_id):
        # Implementation...
```

### Required Methods

All scrapers must implement the following methods:

#### `get_categories()`

This method should return a list of dictionaries containing category information. Each dictionary should have the following keys:

- `id`: Unique identifier for the category
- `name`: Display name for the category
- `url`: URL of the category page
- `parent_id`: ID of the parent category, or `None` if this is a top-level category

#### `get_files_in_category(category_id)`

This method should return a list of dictionaries containing file information for the given category. Each dictionary should have the following keys:

- `id`: Unique identifier for the file
- `name`: Display name for the file
- `url`: URL of the file page
- `size`: Size of the file in bytes, or `None` if unknown
- `file_type`: Type of the file (e.g., "pdf", "epub", "txt")
- `category_id`: ID of the category this file belongs to

#### `get_download_url(file_id)`

This method should return the direct download URL for the given file ID.

### Example

Here's a simple example of a scraper that extracts PDF files from a website:

```python
from src.scrapers.base_scraper import BaseScraper
from urllib.parse import urljoin

class ExampleScraper(BaseScraper):
    PLUGIN_ID = "example"
    
    def get_categories(self):
        # Get the page content
        soup = self.get_page(self.base_url)
        
        # Find all category links
        categories = []
        for link in soup.select(".category-link"):
            category_id = link.get("data-id")
            category_name = link.text.strip()
            category_url = urljoin(self.base_url, link.get("href"))
            
            categories.append({
                "id": category_id,
                "name": category_name,
                "url": category_url,
                "parent_id": None
            })
        
        return categories
    
    def get_files_in_category(self, category_id):
        # Get the category URL
        category_url = None
        for category in self.get_categories():
            if category["id"] == category_id:
                category_url = category["url"]
                break
        
        if not category_url:
            return []
        
        # Get the page content
        soup = self.get_page(category_url)
        
        # Find all file links
        files = []
        for link in soup.select(".file-link"):
            file_id = link.get("data-id")
            file_name = link.text.strip()
            file_url = urljoin(category_url, link.get("href"))
            file_size = int(link.get("data-size", 0)) or None
            file_type = link.get("data-type", "pdf")
            
            files.append({
                "id": file_id,
                "name": file_name,
                "url": file_url,
                "size": file_size,
                "file_type": file_type,
                "category_id": category_id
            })
        
        return files
    
    def get_download_url(self, file_id):
        # In this example, the file ID is the download URL
        return file_id
```

## Testing Your Scraper

The application provides a testing framework for scrapers. You can use this framework to test your scraper with mock data.

### Creating a Test

To create a test for your scraper, create a Python module in the `tests/scrapers` directory. The module should define a test case that inherits from `unittest.TestCase` and uses the `ScraperTester` class to test your scraper.

```python
import unittest
from src.plugins.scrapers.my_scraper import MyScraper
from tests.scrapers import ScraperTester

class TestMyScraper(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://example.com"
        self.tester = ScraperTester(MyScraper, self.base_url)
        
        # Add mock responses for your scraper
        self.tester.add_mock_response(
            self.base_url,
            "<html><body><a class='category-link' data-id='cat1' href='/cat1'>Category 1</a></body></html>"
        )
    
    def test_get_categories(self):
        # Run the test
        results = self.tester.test_scraper()
        
        # Check the results
        self.assertEqual(len(results["categories"]), 1)
        self.assertEqual(results["categories"][0]["id"], "cat1")

if __name__ == "__main__":
    unittest.main()
```

### Running the Test

To run the test, use the `unittest` module:

```bash
python -m unittest tests.scrapers.test_my_scraper
```

## Registering Your Scraper

The application will automatically discover and register your scraper when it's placed in the `src/plugins/scrapers` directory. You don't need to do anything else to register it.

## Best Practices

- Use the `get_page` method provided by the base class to fetch pages. This method handles session management, user agents, and proxies.
- Handle errors gracefully and log them using the `logging` module.
- Use meaningful names for your scraper class and methods.
- Document your scraper with docstrings.
- Write tests for your scraper to ensure it works correctly.
- Follow the PEP8 style guide for Python code.

## Troubleshooting

- If your scraper isn't being discovered, make sure it's in the correct directory and inherits from `BaseScraper`.
- If you're getting errors when fetching pages, check the URL and make sure it's accessible.
- If you're having trouble parsing HTML, try using different CSS selectors or XPath expressions.
- If you're getting errors when running tests, make sure your mock responses match the expected format.
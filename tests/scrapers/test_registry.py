import unittest
from unittest.mock import patch, MagicMock

from src.scrapers.registry import ScraperRegistry
from src.scrapers.base_scraper import BaseScraper
from src.scrapers.generic_scraper import GenericScraper


class TestScraperRegistry(unittest.TestCase):
    """Test case for the ScraperRegistry class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test scraper class
        class TestScraper(BaseScraper):
            def scan(self):
                return []
            
            def get_file_details(self, file_url):
                return {}
        
        # Save the test scraper class
        self.TestScraper = TestScraper
        
        # Create a registry
        self.registry = ScraperRegistry()
    
    def test_register_scraper(self):
        """Test registering a scraper."""
        # Register the test scraper
        self.registry.register_scraper("test", self.TestScraper)
        
        # Check that the scraper was registered
        self.assertIn("test", self.registry.scrapers)
        self.assertEqual(self.registry.scrapers["test"], self.TestScraper)
    
    def test_get_scraper(self):
        """Test getting a scraper."""
        # Register the test scraper
        self.registry.register_scraper("test", self.TestScraper)
        
        # Get the scraper
        scraper_class = self.registry.get_scraper("test")
        
        # Check that the correct scraper was returned
        self.assertEqual(scraper_class, self.TestScraper)
    
    def test_get_scraper_not_found(self):
        """Test getting a scraper that doesn't exist."""
        # Try to get a scraper that doesn't exist
        scraper_class = self.registry.get_scraper("nonexistent")
        
        # Check that the generic scraper was returned
        self.assertEqual(scraper_class, GenericScraper)
    
    def test_get_scraper_instance(self):
        """Test getting a scraper instance."""
        # Register the test scraper
        self.registry.register_scraper("test", self.TestScraper)
        
        # Get a scraper instance
        scraper = self.registry.get_scraper_instance(
            "test",
            "http://example.com",
            "user",
            "pass"
        )
        
        # Check that the correct scraper was returned
        self.assertIsInstance(scraper, self.TestScraper)
        self.assertEqual(scraper.site_url, "http://example.com")
        self.assertEqual(scraper.username, "user")
        self.assertEqual(scraper.password, "pass")
    
    def test_get_scraper_instance_not_found(self):
        """Test getting a scraper instance for a scraper that doesn't exist."""
        # Try to get a scraper instance for a scraper that doesn't exist
        scraper = self.registry.get_scraper_instance(
            "nonexistent",
            "http://example.com"
        )
        
        # Check that a generic scraper was returned
        self.assertIsInstance(scraper, GenericScraper)
        self.assertEqual(scraper.site_url, "http://example.com")
    
    def test_get_available_scrapers(self):
        """Test getting the available scrapers."""
        # Register some scrapers
        self.registry.register_scraper("test1", self.TestScraper)
        self.registry.register_scraper("test2", self.TestScraper)
        
        # Get the available scrapers
        scrapers = self.registry.get_available_scrapers()
        
        # Check the result
        self.assertIn("test1", scrapers)
        self.assertIn("test2", scrapers)
        self.assertEqual(len(scrapers), 2)
    
    def test_load_scrapers(self):
        """Test loading scrapers from plugins."""
        # Mock the importlib.import_module function
        with patch('importlib.import_module') as mock_import_module:
            # Set up the mock module
            mock_module = MagicMock()
            mock_module.register_scrapers = MagicMock()
            mock_import_module.return_value = mock_module
            
            # Mock the os.listdir function
            with patch('os.listdir') as mock_listdir:
                # Set up the mock directory listing
                mock_listdir.return_value = ["test_scraper.py"]
                
                # Mock the os.path.isfile function
                with patch('os.path.isfile') as mock_isfile:
                    # Set up the mock file check
                    mock_isfile.return_value = True
                    
                    # Call the load_scrapers method
                    self.registry.load_scrapers()
                    
                    # Check that the module was imported
                    mock_import_module.assert_called_once_with(
                        "src.plugins.scrapers.test_scraper"
                    )
                    
                    # Check that register_scrapers was called
                    mock_module.register_scrapers.assert_called_once_with(self.registry)


if __name__ == "__main__":
    unittest.main()
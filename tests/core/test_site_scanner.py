import unittest
from unittest.mock import patch, MagicMock

from src.core.site_scanner import SiteScanner


class TestSiteScanner(unittest.TestCase):
    """Test case for the SiteScanner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock models
        self.mock_site_model = MagicMock()
        self.mock_remote_file_model = MagicMock()
        
        # Create the site scanner
        self.scanner = SiteScanner(
            self.mock_site_model,
            self.mock_remote_file_model
        )
    
    def test_init(self):
        """Test the constructor."""
        # Check that the models were saved
        self.assertEqual(self.scanner.site_model, self.mock_site_model)
        self.assertEqual(self.scanner.remote_file_model, self.mock_remote_file_model)
    
    def test_scan(self):
        """Test the scan method."""
        # Set up the mock site model to return a site
        self.mock_site_model.get_site.return_value = {
            "id": 1,
            "name": "Test Site",
            "url": "http://example.com",
            "scraper_type": "generic",
            "username": "user",
            "password": "pass",
            "last_scan": 1609459200
        }
        
        # Mock the scraper registry
        with patch('src.scrapers.registry.ScraperRegistry') as mock_registry_class:
            # Set up the mock registry
            mock_registry = MagicMock()
            mock_registry_class.return_value = mock_registry
            
            # Set up the mock scraper
            mock_scraper = MagicMock()
            mock_registry.get_scraper.return_value = mock_scraper
            
            # Set up the mock scraper to return files
            mock_scraper.scrape.return_value = [
                {
                    "url": "http://example.com/file1.pdf",
                    "name": "file1.pdf",
                    "file_type": "pdf",
                    "size": 1024,
                    "category": "Category 1"
                },
                {
                    "url": "http://example.com/file2.pdf",
                    "name": "file2.pdf",
                    "file_type": "pdf",
                    "size": 2048,
                    "category": "Category 2"
                }
            ]
            
            # Set up the mock category model to return categories
            self.mock_category_model = MagicMock()
            self.mock_category_model.get_or_create_category.side_effect = lambda name: {
                "Category 1": {"id": 1, "name": "Category 1", "parent_id": None},
                "Category 2": {"id": 2, "name": "Category 2", "parent_id": None}
            }.get(name)
            
            # Set up the mock remote file model to return existing files
            self.mock_remote_file_model.get_file_by_url.side_effect = lambda url: None  # No existing files
            
            # Call the scan method
            result = self.scanner.scan(1)
            
            # Check that the site model was queried
            self.mock_site_model.get_site.assert_called_once_with(1)
            
            # Check that the scraper registry was used
            mock_registry_class.assert_called_once()
            mock_registry.get_scraper.assert_called_once_with("generic")
            
            # Check that the scraper was used
            mock_scraper.scrape.assert_called_once_with(
                "http://example.com",
                "user",
                "pass"
            )
            
            # Check that the files were found
            self.assertEqual(len(result), 2)
            
            # Check that the files were added to the database
            self.assertEqual(self.mock_remote_file_model.add_file.call_count, 2)
            
            # Check the first file
            args, kwargs = self.mock_remote_file_model.add_file.call_args_list[0]
            self.assertEqual(kwargs["site_id"], 1)
            self.assertEqual(kwargs["url"], "http://example.com/file1.pdf")
            self.assertEqual(kwargs["name"], "file1.pdf")
            self.assertEqual(kwargs["file_type"], "pdf")
            self.assertEqual(kwargs["size"], 1024)
    
    def test_scan_with_existing_files(self):
        """Test the scan method with existing files."""
        # Set up the mock site model to return a site
        self.mock_site_model.get_site.return_value = {
            "id": 1,
            "name": "Test Site",
            "url": "http://example.com",
            "scraper_type": "generic",
            "username": "user",
            "password": "pass",
            "last_scan": 1609459200
        }
        
        # Mock the scraper registry
        with patch('src.scrapers.registry.ScraperRegistry') as mock_registry_class:
            # Set up the mock registry
            mock_registry = MagicMock()
            mock_registry_class.return_value = mock_registry
            
            # Set up the mock scraper
            mock_scraper = MagicMock()
            mock_registry.get_scraper.return_value = mock_scraper
            
            # Set up the mock scraper to return files
            mock_scraper.scrape.return_value = [
                {
                    "url": "http://example.com/file1.pdf",
                    "name": "file1.pdf",
                    "file_type": "pdf",
                    "size": 1024,
                    "category": "Category 1"
                },
                {
                    "url": "http://example.com/file2.pdf",
                    "name": "file2.pdf",
                    "file_type": "pdf",
                    "size": 2048,
                    "category": "Category 2"
                }
            ]
            
            # Set up the mock category model to return categories
            self.mock_category_model = MagicMock()
            self.mock_category_model.get_or_create_category.side_effect = lambda name: {
                "Category 1": {"id": 1, "name": "Category 1", "parent_id": None},
                "Category 2": {"id": 2, "name": "Category 2", "parent_id": None}
            }.get(name)
            
            # Set up the mock remote file model to return existing files
            self.mock_remote_file_model.get_file_by_url.side_effect = lambda url: {
                "http://example.com/file1.pdf": {
                    "id": 1,
                    "site_id": 1,
                    "url": "http://example.com/file1.pdf",
                    "name": "file1.pdf",
                    "file_type": "pdf",
                    "size": 1024,
                    "category_id": 1,
                    "hash": None,
                    "last_updated": 1609459200
                }
            }.get(url)
            
            # Call the scan method
            result = self.scanner.scan(1)
            
            # Check that the files were found
            self.assertEqual(len(result), 2)
            
            # Check that only the new file was added to the database
            self.mock_remote_file_model.add_file.assert_called_once()
            args, kwargs = self.mock_remote_file_model.add_file.call_args
            self.assertEqual(kwargs["url"], "http://example.com/file2.pdf")
    
    def test_scan_with_updated_files(self):
        """Test the scan method with updated files."""
        # Set up the mock site model to return a site
        self.mock_site_model.get_site.return_value = {
            "id": 1,
            "name": "Test Site",
            "url": "http://example.com",
            "scraper_type": "generic",
            "username": "user",
            "password": "pass",
            "last_scan": 1609459200
        }
        
        # Mock the scraper registry
        with patch('src.scrapers.registry.ScraperRegistry') as mock_registry_class:
            # Set up the mock registry
            mock_registry = MagicMock()
            mock_registry_class.return_value = mock_registry
            
            # Set up the mock scraper
            mock_scraper = MagicMock()
            mock_registry.get_scraper.return_value = mock_scraper
            
            # Set up the mock scraper to return files
            mock_scraper.scrape.return_value = [
                {
                    "url": "http://example.com/file1.pdf",
                    "name": "file1.pdf",
                    "file_type": "pdf",
                    "size": 2048,  # Updated size
                    "category": "Category 1"
                }
            ]
            
            # Set up the mock category model to return categories
            self.mock_category_model = MagicMock()
            self.mock_category_model.get_or_create_category.return_value = {
                "id": 1,
                "name": "Category 1",
                "parent_id": None
            }
            
            # Set up the mock remote file model to return existing files
            self.mock_remote_file_model.get_file_by_url.return_value = {
                "id": 1,
                "site_id": 1,
                "url": "http://example.com/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,  # Old size
                "category_id": 1,
                "hash": None,
                "last_updated": 1609459200
            }
            
            # Call the scan method
            result = self.scanner.scan(1)
            
            # Check that the file was found
            self.assertEqual(len(result), 1)
            
            # Check that the file was updated in the database
            self.mock_remote_file_model.update_file.assert_called_once_with(
                file_id=1,
                name="file1.pdf",
                file_type="pdf",
                size=2048,
                category_id=1
            )
    
    def test_scan_with_error(self):
        """Test the scan method with an error."""
        # Set up the mock site model to return a site
        self.mock_site_model.get_site.return_value = {
            "id": 1,
            "name": "Test Site",
            "url": "http://example.com",
            "scraper_type": "generic",
            "username": "user",
            "password": "pass",
            "last_scan": 1609459200
        }
        
        # Mock the scraper registry
        with patch('src.scrapers.registry.ScraperRegistry') as mock_registry_class:
            # Set up the mock registry
            mock_registry = MagicMock()
            mock_registry_class.return_value = mock_registry
            
            # Set up the mock registry to raise an exception
            mock_registry.get_scraper.side_effect = ValueError("Unknown scraper type")
            
            # Call the scan method
            with self.assertRaises(ValueError):
                self.scanner.scan(1)
            
            # Check that the site model was queried
            self.mock_site_model.get_site.assert_called_once_with(1)
            
            # Check that the scraper registry was used
            mock_registry_class.assert_called_once()
            mock_registry.get_scraper.assert_called_once_with("generic")
            
            # Check that no files were added to the database
            self.mock_remote_file_model.add_file.assert_not_called()


if __name__ == "__main__":
    unittest.main()
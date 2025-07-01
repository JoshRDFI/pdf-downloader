import unittest
from unittest.mock import patch, MagicMock

from src.db.site_model import SiteModel
from src.db.database import Database


class TestSiteModel(unittest.TestCase):
    """Test case for the SiteModel class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock database
        self.mock_db = MagicMock(spec=Database)
        
        # Create the site model with the mock database
        self.site_model = SiteModel(self.mock_db)
    
    def test_add_site(self):
        """Test adding a site."""
        # Set up the mock database to return a site ID
        self.mock_db.execute_query.return_value = [{"id": 1}]
        
        # Add a site
        site_id = self.site_model.add_site(
            name="Test Site",
            url="http://example.com",
            scraper_type="example",
            username="user",
            password="pass"
        )
        
        # Check the result
        self.assertEqual(site_id, 1)
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("INSERT INTO sites" in args[0])
        self.assertEqual(kwargs["params"][0], "Test Site")
        self.assertEqual(kwargs["params"][1], "http://example.com")
        self.assertEqual(kwargs["params"][2], "example")
        self.assertEqual(kwargs["params"][3], "user")
        # Password should be hashed or encrypted
        self.assertNotEqual(kwargs["params"][4], "pass")
    
    def test_update_site(self):
        """Test updating a site."""
        # Update a site
        self.site_model.update_site(
            site_id=1,
            name="Updated Site",
            url="http://updated.com",
            scraper_type="updated",
            username="new_user",
            password="new_pass"
        )
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("UPDATE sites" in args[0])
        self.assertEqual(kwargs["params"][0], "Updated Site")
        self.assertEqual(kwargs["params"][1], "http://updated.com")
        self.assertEqual(kwargs["params"][2], "updated")
        self.assertEqual(kwargs["params"][3], "new_user")
        # Password should be hashed or encrypted
        self.assertNotEqual(kwargs["params"][4], "new_pass")
        self.assertEqual(kwargs["params"][5], 1)  # site_id
    
    def test_delete_site(self):
        """Test deleting a site."""
        # Delete a site
        self.site_model.delete_site(1)
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("DELETE FROM sites" in args[0])
        self.assertEqual(kwargs["params"][0], 1)
    
    def test_get_site(self):
        """Test getting a site."""
        # Set up the mock database to return a site
        self.mock_db.execute_query.return_value = [{
            "id": 1,
            "name": "Test Site",
            "url": "http://example.com",
            "scraper_type": "example",
            "username": "user",
            "password": "hashed_password",
            "last_scan": 1609459200
        }]
        
        # Get a site
        site = self.site_model.get_site(1)
        
        # Check the result
        self.assertEqual(site["id"], 1)
        self.assertEqual(site["name"], "Test Site")
        self.assertEqual(site["url"], "http://example.com")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM sites" in args[0])
        self.assertEqual(kwargs["params"][0], 1)
    
    def test_get_site_not_found(self):
        """Test getting a site that doesn't exist."""
        # Set up the mock database to return no sites
        self.mock_db.execute_query.return_value = []
        
        # Get a site that doesn't exist
        site = self.site_model.get_site(999)
        
        # Check the result
        self.assertIsNone(site)
    
    def test_get_all_sites(self):
        """Test getting all sites."""
        # Set up the mock database to return sites
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "name": "Site 1",
                "url": "http://example1.com",
                "scraper_type": "example",
                "username": "user1",
                "password": "hashed_password1",
                "last_scan": 1609459200
            },
            {
                "id": 2,
                "name": "Site 2",
                "url": "http://example2.com",
                "scraper_type": "example",
                "username": "user2",
                "password": "hashed_password2",
                "last_scan": 1609545600
            }
        ]
        
        # Get all sites
        sites = self.site_model.get_all_sites()
        
        # Check the result
        self.assertEqual(len(sites), 2)
        self.assertEqual(sites[0]["name"], "Site 1")
        self.assertEqual(sites[1]["name"], "Site 2")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM sites" in args[0])
    
    def test_update_last_scan(self):
        """Test updating the last scan time for a site."""
        # Update the last scan time
        self.site_model.update_last_scan(1)
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("UPDATE sites SET last_scan" in args[0])
        self.assertEqual(kwargs["params"][1], 1)  # site_id
    
    def test_get_sites_by_scraper_type(self):
        """Test getting sites by scraper type."""
        # Set up the mock database to return sites
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "name": "Site 1",
                "url": "http://example1.com",
                "scraper_type": "example",
                "username": "user1",
                "password": "hashed_password1",
                "last_scan": 1609459200
            },
            {
                "id": 2,
                "name": "Site 2",
                "url": "http://example2.com",
                "scraper_type": "example",
                "username": "user2",
                "password": "hashed_password2",
                "last_scan": 1609545600
            }
        ]
        
        # Get sites by scraper type
        sites = self.site_model.get_sites_by_scraper_type("example")
        
        # Check the result
        self.assertEqual(len(sites), 2)
        self.assertEqual(sites[0]["name"], "Site 1")
        self.assertEqual(sites[1]["name"], "Site 2")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM sites WHERE scraper_type" in args[0])
        self.assertEqual(kwargs["params"][0], "example")


if __name__ == "__main__":
    unittest.main()
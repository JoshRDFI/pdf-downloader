import unittest
from unittest.mock import patch, MagicMock

from src.db.remote_file_model import RemoteFileModel
from src.db.database import Database


class TestRemoteFileModel(unittest.TestCase):
    """Test case for the RemoteFileModel class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock database
        self.mock_db = MagicMock(spec=Database)
        
        # Create the remote file model with the mock database
        self.remote_file_model = RemoteFileModel(self.mock_db)
    
    def test_add_file(self):
        """Test adding a remote file."""
        # Set up the mock database to return a file ID
        self.mock_db.execute_query.return_value = [{"id": 1}]
        
        # Add a remote file
        file_id = self.remote_file_model.add_file(
            site_id=1,
            url="http://example.com/file.pdf",
            name="file.pdf",
            file_type="pdf",
            size=1024,
            category_id=2,
            hash_value="abc123"
        )
        
        # Check the result
        self.assertEqual(file_id, 1)
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("INSERT INTO remote_files" in args[0])
        self.assertEqual(kwargs["params"][0], 1)  # site_id
        self.assertEqual(kwargs["params"][1], "http://example.com/file.pdf")
        self.assertEqual(kwargs["params"][2], "file.pdf")
        self.assertEqual(kwargs["params"][3], "pdf")
        self.assertEqual(kwargs["params"][4], 1024)  # size
        self.assertEqual(kwargs["params"][5], 2)  # category_id
        self.assertEqual(kwargs["params"][6], "abc123")  # hash_value
    
    def test_update_file(self):
        """Test updating a remote file."""
        # Update a remote file
        self.remote_file_model.update_file(
            file_id=1,
            url="http://example.com/updated.pdf",
            name="updated.pdf",
            file_type="pdf",
            size=2048,
            category_id=3,
            hash_value="def456"
        )
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("UPDATE remote_files" in args[0])
        self.assertEqual(kwargs["params"][0], "http://example.com/updated.pdf")
        self.assertEqual(kwargs["params"][1], "updated.pdf")
        self.assertEqual(kwargs["params"][2], "pdf")
        self.assertEqual(kwargs["params"][3], 2048)  # size
        self.assertEqual(kwargs["params"][4], 3)  # category_id
        self.assertEqual(kwargs["params"][5], "def456")  # hash_value
        self.assertEqual(kwargs["params"][6], 1)  # file_id
    
    def test_delete_file(self):
        """Test deleting a remote file."""
        # Delete a remote file
        self.remote_file_model.delete_file(1)
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("DELETE FROM remote_files" in args[0])
        self.assertEqual(kwargs["params"][0], 1)
    
    def test_get_file(self):
        """Test getting a remote file."""
        # Set up the mock database to return a file
        self.mock_db.execute_query.return_value = [{
            "id": 1,
            "site_id": 1,
            "url": "http://example.com/file.pdf",
            "name": "file.pdf",
            "file_type": "pdf",
            "size": 1024,
            "category_id": 2,
            "hash": "abc123",
            "last_updated": 1609459200
        }]
        
        # Get a remote file
        file = self.remote_file_model.get_file(1)
        
        # Check the result
        self.assertEqual(file["id"], 1)
        self.assertEqual(file["url"], "http://example.com/file.pdf")
        self.assertEqual(file["name"], "file.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM remote_files" in args[0])
        self.assertEqual(kwargs["params"][0], 1)
    
    def test_get_file_not_found(self):
        """Test getting a remote file that doesn't exist."""
        # Set up the mock database to return no files
        self.mock_db.execute_query.return_value = []
        
        # Get a remote file that doesn't exist
        file = self.remote_file_model.get_file(999)
        
        # Check the result
        self.assertIsNone(file)
    
    def test_get_files_by_site(self):
        """Test getting remote files by site."""
        # Set up the mock database to return files
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "site_id": 1,
                "url": "http://example.com/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 2,
                "hash": "abc123",
                "last_updated": 1609459200
            },
            {
                "id": 2,
                "site_id": 1,
                "url": "http://example.com/file2.pdf",
                "name": "file2.pdf",
                "file_type": "pdf",
                "size": 2048,
                "category_id": 2,
                "hash": "def456",
                "last_updated": 1609459300
            }
        ]
        
        # Get remote files by site
        files = self.remote_file_model.get_files_by_site(1)
        
        # Check the result
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]["name"], "file1.pdf")
        self.assertEqual(files[1]["name"], "file2.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM remote_files WHERE site_id" in args[0])
        self.assertEqual(kwargs["params"][0], 1)
    
    def test_get_files_by_category(self):
        """Test getting remote files by category."""
        # Set up the mock database to return files
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "site_id": 1,
                "url": "http://example.com/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 2,
                "hash": "abc123",
                "last_updated": 1609459200
            },
            {
                "id": 2,
                "site_id": 1,
                "url": "http://example.com/file2.pdf",
                "name": "file2.pdf",
                "file_type": "pdf",
                "size": 2048,
                "category_id": 2,
                "hash": "def456",
                "last_updated": 1609459300
            }
        ]
        
        # Get remote files by category
        files = self.remote_file_model.get_files_by_category(2)
        
        # Check the result
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]["name"], "file1.pdf")
        self.assertEqual(files[1]["name"], "file2.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM remote_files WHERE category_id" in args[0])
        self.assertEqual(kwargs["params"][0], 2)
    
    def test_get_files_by_type(self):
        """Test getting remote files by type."""
        # Set up the mock database to return files
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "site_id": 1,
                "url": "http://example.com/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 2,
                "hash": "abc123",
                "last_updated": 1609459200
            },
            {
                "id": 2,
                "site_id": 1,
                "url": "http://example.com/file2.pdf",
                "name": "file2.pdf",
                "file_type": "pdf",
                "size": 2048,
                "category_id": 3,
                "hash": "def456",
                "last_updated": 1609459300
            }
        ]
        
        # Get remote files by type
        files = self.remote_file_model.get_files_by_type("pdf")
        
        # Check the result
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]["name"], "file1.pdf")
        self.assertEqual(files[1]["name"], "file2.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM remote_files WHERE file_type" in args[0])
        self.assertEqual(kwargs["params"][0], "pdf")
    
    def test_get_file_by_url(self):
        """Test getting a remote file by URL."""
        # Set up the mock database to return a file
        self.mock_db.execute_query.return_value = [{
            "id": 1,
            "site_id": 1,
            "url": "http://example.com/file.pdf",
            "name": "file.pdf",
            "file_type": "pdf",
            "size": 1024,
            "category_id": 2,
            "hash": "abc123",
            "last_updated": 1609459200
        }]
        
        # Get a remote file by URL
        file = self.remote_file_model.get_file_by_url("http://example.com/file.pdf")
        
        # Check the result
        self.assertEqual(file["id"], 1)
        self.assertEqual(file["url"], "http://example.com/file.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM remote_files WHERE url" in args[0])
        self.assertEqual(kwargs["params"][0], "http://example.com/file.pdf")
    
    def test_get_file_by_url_not_found(self):
        """Test getting a remote file by URL that doesn't exist."""
        # Set up the mock database to return no files
        self.mock_db.execute_query.return_value = []
        
        # Get a remote file by URL that doesn't exist
        file = self.remote_file_model.get_file_by_url("http://example.com/nonexistent.pdf")
        
        # Check the result
        self.assertIsNone(file)
    
    def test_get_file_by_hash(self):
        """Test getting a remote file by hash."""
        # Set up the mock database to return a file
        self.mock_db.execute_query.return_value = [{
            "id": 1,
            "site_id": 1,
            "url": "http://example.com/file.pdf",
            "name": "file.pdf",
            "file_type": "pdf",
            "size": 1024,
            "category_id": 2,
            "hash": "abc123",
            "last_updated": 1609459200
        }]
        
        # Get a remote file by hash
        file = self.remote_file_model.get_file_by_hash("abc123")
        
        # Check the result
        self.assertEqual(file["id"], 1)
        self.assertEqual(file["hash"], "abc123")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM remote_files WHERE hash" in args[0])
        self.assertEqual(kwargs["params"][0], "abc123")
    
    def test_get_file_by_hash_not_found(self):
        """Test getting a remote file by hash that doesn't exist."""
        # Set up the mock database to return no files
        self.mock_db.execute_query.return_value = []
        
        # Get a remote file by hash that doesn't exist
        file = self.remote_file_model.get_file_by_hash("nonexistent")
        
        # Check the result
        self.assertIsNone(file)
    
    def test_search_files(self):
        """Test searching for remote files."""
        # Set up the mock database to return files
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "site_id": 1,
                "url": "http://example.com/test_file.pdf",
                "name": "test_file.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 2,
                "hash": "abc123",
                "last_updated": 1609459200
            }
        ]
        
        # Search for remote files
        files = self.remote_file_model.search_files("test")
        
        # Check the result
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["name"], "test_file.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM remote_files WHERE name LIKE" in args[0])
        self.assertEqual(kwargs["params"][0], "%test%")


if __name__ == "__main__":
    unittest.main()
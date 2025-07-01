import unittest
from unittest.mock import patch, MagicMock

from src.db.local_file_model import LocalFileModel
from src.db.database import Database


class TestLocalFileModel(unittest.TestCase):
    """Test case for the LocalFileModel class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock database
        self.mock_db = MagicMock(spec=Database)
        
        # Create the local file model with the mock database
        self.local_file_model = LocalFileModel(self.mock_db)
    
    def test_add_file(self):
        """Test adding a local file."""
        # Set up the mock database to return a file ID
        self.mock_db.execute_query.return_value = [{"id": 1}]
        
        # Add a local file
        file_id = self.local_file_model.add_file(
            path="/downloads/file.pdf",
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
        self.assertTrue("INSERT INTO local_files" in args[0])
        self.assertEqual(kwargs["params"][0], "/downloads/file.pdf")
        self.assertEqual(kwargs["params"][1], "file.pdf")
        self.assertEqual(kwargs["params"][2], "pdf")
        self.assertEqual(kwargs["params"][3], 1024)  # size
        self.assertEqual(kwargs["params"][4], 2)  # category_id
        self.assertEqual(kwargs["params"][5], "abc123")  # hash_value
    
    def test_update_file(self):
        """Test updating a local file."""
        # Update a local file
        self.local_file_model.update_file(
            file_id=1,
            path="/downloads/updated.pdf",
            name="updated.pdf",
            file_type="pdf",
            size=2048,
            category_id=3,
            hash_value="def456"
        )
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("UPDATE local_files" in args[0])
        self.assertEqual(kwargs["params"][0], "/downloads/updated.pdf")
        self.assertEqual(kwargs["params"][1], "updated.pdf")
        self.assertEqual(kwargs["params"][2], "pdf")
        self.assertEqual(kwargs["params"][3], 2048)  # size
        self.assertEqual(kwargs["params"][4], 3)  # category_id
        self.assertEqual(kwargs["params"][5], "def456")  # hash_value
        self.assertEqual(kwargs["params"][6], 1)  # file_id
    
    def test_delete_file(self):
        """Test deleting a local file."""
        # Delete a local file
        self.local_file_model.delete_file(1)
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("DELETE FROM local_files" in args[0])
        self.assertEqual(kwargs["params"][0], 1)
    
    def test_get_file(self):
        """Test getting a local file."""
        # Set up the mock database to return a file
        self.mock_db.execute_query.return_value = [{
            "id": 1,
            "path": "/downloads/file.pdf",
            "name": "file.pdf",
            "file_type": "pdf",
            "size": 1024,
            "category_id": 2,
            "hash": "abc123",
            "last_updated": 1609459200
        }]
        
        # Get a local file
        file = self.local_file_model.get_file(1)
        
        # Check the result
        self.assertEqual(file["id"], 1)
        self.assertEqual(file["path"], "/downloads/file.pdf")
        self.assertEqual(file["name"], "file.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM local_files" in args[0])
        self.assertEqual(kwargs["params"][0], 1)
    
    def test_get_file_not_found(self):
        """Test getting a local file that doesn't exist."""
        # Set up the mock database to return no files
        self.mock_db.execute_query.return_value = []
        
        # Get a local file that doesn't exist
        file = self.local_file_model.get_file(999)
        
        # Check the result
        self.assertIsNone(file)
    
    def test_get_files_by_category(self):
        """Test getting local files by category."""
        # Set up the mock database to return files
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "path": "/downloads/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 2,
                "hash": "abc123",
                "last_updated": 1609459200
            },
            {
                "id": 2,
                "path": "/downloads/file2.pdf",
                "name": "file2.pdf",
                "file_type": "pdf",
                "size": 2048,
                "category_id": 2,
                "hash": "def456",
                "last_updated": 1609459300
            }
        ]
        
        # Get local files by category
        files = self.local_file_model.get_files_by_category(2)
        
        # Check the result
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]["name"], "file1.pdf")
        self.assertEqual(files[1]["name"], "file2.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM local_files WHERE category_id" in args[0])
        self.assertEqual(kwargs["params"][0], 2)
    
    def test_get_files_by_type(self):
        """Test getting local files by type."""
        # Set up the mock database to return files
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "path": "/downloads/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 2,
                "hash": "abc123",
                "last_updated": 1609459200
            },
            {
                "id": 2,
                "path": "/downloads/file2.pdf",
                "name": "file2.pdf",
                "file_type": "pdf",
                "size": 2048,
                "category_id": 3,
                "hash": "def456",
                "last_updated": 1609459300
            }
        ]
        
        # Get local files by type
        files = self.local_file_model.get_files_by_type("pdf")
        
        # Check the result
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]["name"], "file1.pdf")
        self.assertEqual(files[1]["name"], "file2.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM local_files WHERE file_type" in args[0])
        self.assertEqual(kwargs["params"][0], "pdf")
    
    def test_get_file_by_path(self):
        """Test getting a local file by path."""
        # Set up the mock database to return a file
        self.mock_db.execute_query.return_value = [{
            "id": 1,
            "path": "/downloads/file.pdf",
            "name": "file.pdf",
            "file_type": "pdf",
            "size": 1024,
            "category_id": 2,
            "hash": "abc123",
            "last_updated": 1609459200
        }]
        
        # Get a local file by path
        file = self.local_file_model.get_file_by_path("/downloads/file.pdf")
        
        # Check the result
        self.assertEqual(file["id"], 1)
        self.assertEqual(file["path"], "/downloads/file.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM local_files WHERE path" in args[0])
        self.assertEqual(kwargs["params"][0], "/downloads/file.pdf")
    
    def test_get_file_by_path_not_found(self):
        """Test getting a local file by path that doesn't exist."""
        # Set up the mock database to return no files
        self.mock_db.execute_query.return_value = []
        
        # Get a local file by path that doesn't exist
        file = self.local_file_model.get_file_by_path("/downloads/nonexistent.pdf")
        
        # Check the result
        self.assertIsNone(file)
    
    def test_get_file_by_hash(self):
        """Test getting a local file by hash."""
        # Set up the mock database to return a file
        self.mock_db.execute_query.return_value = [{
            "id": 1,
            "path": "/downloads/file.pdf",
            "name": "file.pdf",
            "file_type": "pdf",
            "size": 1024,
            "category_id": 2,
            "hash": "abc123",
            "last_updated": 1609459200
        }]
        
        # Get a local file by hash
        file = self.local_file_model.get_file_by_hash("abc123")
        
        # Check the result
        self.assertEqual(file["id"], 1)
        self.assertEqual(file["hash"], "abc123")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM local_files WHERE hash" in args[0])
        self.assertEqual(kwargs["params"][0], "abc123")
    
    def test_get_file_by_hash_not_found(self):
        """Test getting a local file by hash that doesn't exist."""
        # Set up the mock database to return no files
        self.mock_db.execute_query.return_value = []
        
        # Get a local file by hash that doesn't exist
        file = self.local_file_model.get_file_by_hash("nonexistent")
        
        # Check the result
        self.assertIsNone(file)
    
    def test_search_files(self):
        """Test searching for local files."""
        # Set up the mock database to return files
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "path": "/downloads/test_file.pdf",
                "name": "test_file.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 2,
                "hash": "abc123",
                "last_updated": 1609459200
            }
        ]
        
        # Search for local files
        files = self.local_file_model.search_files("test")
        
        # Check the result
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["name"], "test_file.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM local_files WHERE name LIKE" in args[0])
        self.assertEqual(kwargs["params"][0], "%test%")
    
    def test_get_all_files(self):
        """Test getting all local files."""
        # Set up the mock database to return files
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "path": "/downloads/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 2,
                "hash": "abc123",
                "last_updated": 1609459200
            },
            {
                "id": 2,
                "path": "/downloads/file2.pdf",
                "name": "file2.pdf",
                "file_type": "pdf",
                "size": 2048,
                "category_id": 3,
                "hash": "def456",
                "last_updated": 1609459300
            }
        ]
        
        # Get all local files
        files = self.local_file_model.get_all_files()
        
        # Check the result
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]["name"], "file1.pdf")
        self.assertEqual(files[1]["name"], "file2.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM local_files" in args[0])


if __name__ == "__main__":
    unittest.main()
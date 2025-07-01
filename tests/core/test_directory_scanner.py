import unittest
from unittest.mock import patch, MagicMock, mock_open
import os

from src.core.directory_scanner import DirectoryScanner


class TestDirectoryScanner(unittest.TestCase):
    """Test case for the DirectoryScanner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock models
        self.mock_local_file_model = MagicMock()
        self.mock_category_model = MagicMock()
        
        # Create the directory scanner
        self.scanner = DirectoryScanner(
            self.mock_local_file_model,
            self.mock_category_model
        )
    
    def test_init(self):
        """Test the constructor."""
        # Check that the models were saved
        self.assertEqual(self.scanner.local_file_model, self.mock_local_file_model)
        self.assertEqual(self.scanner.category_model, self.mock_category_model)
    
    @patch('os.walk')
    @patch('os.path.getsize')
    @patch('src.utils.file_utils.calculate_file_hash')
    def test_scan(self, mock_calculate_hash, mock_getsize, mock_walk):
        """Test the scan method."""
        # Set up the mock os.walk to return files
        mock_walk.return_value = [
            ("/downloads", ["subdir"], ["file1.pdf", "file2.pdf"]),
            ("/downloads/subdir", [], ["file3.pdf"])
        ]
        
        # Set up the mock os.path.getsize to return file sizes
        mock_getsize.side_effect = lambda path: {
            "/downloads/file1.pdf": 1024,
            "/downloads/file2.pdf": 2048,
            "/downloads/subdir/file3.pdf": 3072
        }.get(path)
        
        # Set up the mock calculate_file_hash to return file hashes
        mock_calculate_hash.side_effect = lambda path: {
            "/downloads/file1.pdf": "abc123",
            "/downloads/file2.pdf": "def456",
            "/downloads/subdir/file3.pdf": "ghi789"
        }.get(path)
        
        # Set up the mock local_file_model to return existing files
        self.mock_local_file_model.get_file_by_path.side_effect = lambda path: None  # No existing files
        
        # Set up the mock category_model to return the default category
        self.mock_category_model.get_default_category.return_value = {
            "id": 1,
            "name": "Uncategorized",
            "parent_id": None
        }
        
        # Call the scan method
        result = self.scanner.scan("/downloads")
        
        # Check that the files were found
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["path"], "/downloads/file1.pdf")
        self.assertEqual(result[1]["path"], "/downloads/file2.pdf")
        self.assertEqual(result[2]["path"], "/downloads/subdir/file3.pdf")
        
        # Check that the files were added to the database
        self.assertEqual(self.mock_local_file_model.add_file.call_count, 3)
        
        # Check the first file
        args, kwargs = self.mock_local_file_model.add_file.call_args_list[0]
        self.assertEqual(kwargs["path"], "/downloads/file1.pdf")
        self.assertEqual(kwargs["name"], "file1.pdf")
        self.assertEqual(kwargs["file_type"], "pdf")
        self.assertEqual(kwargs["size"], 1024)
        self.assertEqual(kwargs["category_id"], 1)
        self.assertEqual(kwargs["hash"], "abc123")
    
    @patch('os.walk')
    @patch('os.path.getsize')
    @patch('src.utils.file_utils.calculate_file_hash')
    def test_scan_with_existing_files(self, mock_calculate_hash, mock_getsize, mock_walk):
        """Test the scan method with existing files."""
        # Set up the mock os.walk to return files
        mock_walk.return_value = [
            ("/downloads", [], ["file1.pdf", "file2.pdf"])
        ]
        
        # Set up the mock os.path.getsize to return file sizes
        mock_getsize.side_effect = lambda path: {
            "/downloads/file1.pdf": 1024,
            "/downloads/file2.pdf": 2048
        }.get(path)
        
        # Set up the mock calculate_file_hash to return file hashes
        mock_calculate_hash.side_effect = lambda path: {
            "/downloads/file1.pdf": "abc123",
            "/downloads/file2.pdf": "def456"
        }.get(path)
        
        # Set up the mock local_file_model to return existing files
        self.mock_local_file_model.get_file_by_path.side_effect = lambda path: {
            "/downloads/file1.pdf": {
                "id": 1,
                "path": "/downloads/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 1,
                "hash": "abc123",
                "last_updated": 1609459200
            }
        }.get(path)
        
        # Set up the mock category_model to return the default category
        self.mock_category_model.get_default_category.return_value = {
            "id": 1,
            "name": "Uncategorized",
            "parent_id": None
        }
        
        # Call the scan method
        result = self.scanner.scan("/downloads")
        
        # Check that the files were found
        self.assertEqual(len(result), 2)
        
        # Check that only the new file was added to the database
        self.mock_local_file_model.add_file.assert_called_once()
        args, kwargs = self.mock_local_file_model.add_file.call_args
        self.assertEqual(kwargs["path"], "/downloads/file2.pdf")
    
    @patch('os.walk')
    @patch('os.path.getsize')
    @patch('src.utils.file_utils.calculate_file_hash')
    def test_scan_with_updated_files(self, mock_calculate_hash, mock_getsize, mock_walk):
        """Test the scan method with updated files."""
        # Set up the mock os.walk to return files
        mock_walk.return_value = [
            ("/downloads", [], ["file1.pdf"])
        ]
        
        # Set up the mock os.path.getsize to return file sizes
        mock_getsize.return_value = 2048  # Updated size
        
        # Set up the mock calculate_file_hash to return file hashes
        mock_calculate_hash.return_value = "def456"  # Updated hash
        
        # Set up the mock local_file_model to return existing files
        self.mock_local_file_model.get_file_by_path.return_value = {
            "id": 1,
            "path": "/downloads/file1.pdf",
            "name": "file1.pdf",
            "file_type": "pdf",
            "size": 1024,  # Old size
            "category_id": 1,
            "hash": "abc123",  # Old hash
            "last_updated": 1609459200
        }
        
        # Call the scan method
        result = self.scanner.scan("/downloads")
        
        # Check that the file was found
        self.assertEqual(len(result), 1)
        
        # Check that the file was updated in the database
        self.mock_local_file_model.update_file.assert_called_once_with(
            file_id=1,
            size=2048,
            hash="def456"
        )
    
    @patch('os.walk')
    def test_scan_empty_directory(self, mock_walk):
        """Test the scan method with an empty directory."""
        # Set up the mock os.walk to return no files
        mock_walk.return_value = [
            ("/downloads", [], [])
        ]
        
        # Call the scan method
        result = self.scanner.scan("/downloads")
        
        # Check that no files were found
        self.assertEqual(len(result), 0)
        
        # Check that no files were added to the database
        self.mock_local_file_model.add_file.assert_not_called()
    
    @patch('os.walk')
    @patch('os.path.getsize')
    def test_scan_with_error(self, mock_getsize, mock_walk):
        """Test the scan method with an error."""
        # Set up the mock os.walk to return files
        mock_walk.return_value = [
            ("/downloads", [], ["file1.pdf"])
        ]
        
        # Set up the mock os.path.getsize to raise an exception
        mock_getsize.side_effect = OSError("Permission denied")
        
        # Call the scan method
        result = self.scanner.scan("/downloads")
        
        # Check that no files were found (due to the error)
        self.assertEqual(len(result), 0)
        
        # Check that no files were added to the database
        self.mock_local_file_model.add_file.assert_not_called()


if __name__ == "__main__":
    unittest.main()
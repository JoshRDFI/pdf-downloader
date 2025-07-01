import unittest
from unittest.mock import patch, MagicMock

from src.core.file_comparison import FileComparison


class TestFileComparison(unittest.TestCase):
    """Test case for the FileComparison class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock models
        self.mock_local_file_model = MagicMock()
        self.mock_remote_file_model = MagicMock()
        
        # Create the file comparison
        self.comparison = FileComparison(
            self.mock_local_file_model,
            self.mock_remote_file_model
        )
    
    def test_init(self):
        """Test the constructor."""
        # Check that the models were saved
        self.assertEqual(self.comparison.local_file_model, self.mock_local_file_model)
        self.assertEqual(self.comparison.remote_file_model, self.mock_remote_file_model)
    
    def test_compare_all(self):
        """Test the compare method with all categories."""
        # Set up the mock local file model to return files
        self.mock_local_file_model.get_all_files.return_value = [
            {
                "id": 1,
                "path": "/downloads/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 1,
                "hash": "abc123",
                "last_updated": 1609459200
            },
            {
                "id": 2,
                "path": "/downloads/file2.pdf",
                "name": "file2.pdf",
                "file_type": "pdf",
                "size": 2048,
                "category_id": 1,
                "hash": "def456",
                "last_updated": 1609459300
            }
        ]
        
        # Set up the mock remote file model to return files
        self.mock_remote_file_model.get_all_files.return_value = [
            {
                "id": 1,
                "site_id": 1,
                "url": "http://example.com/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 1,
                "hash": "abc123",
                "last_updated": 1609459200
            },
            {
                "id": 2,
                "site_id": 1,
                "url": "http://example.com/file3.pdf",
                "name": "file3.pdf",
                "file_type": "pdf",
                "size": 3072,
                "category_id": 1,
                "hash": "ghi789",
                "last_updated": 1609459400
            }
        ]
        
        # Call the compare method
        result = self.comparison.compare()
        
        # Check that the models were queried
        self.mock_local_file_model.get_all_files.assert_called_once()
        self.mock_remote_file_model.get_all_files.assert_called_once()
        
        # Check the result
        self.assertEqual(len(result["matching"]), 1)  # file1.pdf matches
        self.assertEqual(len(result["missing"]), 1)   # file3.pdf is missing locally
        self.assertEqual(len(result["different"]), 0)  # No files with same name but different hash
        
        # Check the matching file
        self.assertEqual(result["matching"][0]["local"]["name"], "file1.pdf")
        self.assertEqual(result["matching"][0]["remote"]["name"], "file1.pdf")
        
        # Check the missing file
        self.assertEqual(result["missing"][0]["name"], "file3.pdf")
    
    def test_compare_by_category(self):
        """Test the compare method with a specific category."""
        # Set up the mock local file model to return files
        self.mock_local_file_model.get_files_by_category.return_value = [
            {
                "id": 1,
                "path": "/downloads/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 1,
                "hash": "abc123",
                "last_updated": 1609459200
            }
        ]
        
        # Set up the mock remote file model to return files
        self.mock_remote_file_model.get_files_by_category.return_value = [
            {
                "id": 1,
                "site_id": 1,
                "url": "http://example.com/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 1,
                "hash": "abc123",
                "last_updated": 1609459200
            },
            {
                "id": 2,
                "site_id": 1,
                "url": "http://example.com/file3.pdf",
                "name": "file3.pdf",
                "file_type": "pdf",
                "size": 3072,
                "category_id": 1,
                "hash": "ghi789",
                "last_updated": 1609459400
            }
        ]
        
        # Call the compare method with a category ID
        result = self.comparison.compare(category_id=1)
        
        # Check that the models were queried with the category ID
        self.mock_local_file_model.get_files_by_category.assert_called_once_with(1)
        self.mock_remote_file_model.get_files_by_category.assert_called_once_with(1)
        
        # Check the result
        self.assertEqual(len(result["matching"]), 1)  # file1.pdf matches
        self.assertEqual(len(result["missing"]), 1)   # file3.pdf is missing locally
        self.assertEqual(len(result["different"]), 0)  # No files with same name but different hash
    
    def test_compare_with_different_files(self):
        """Test the compare method with files that have the same name but different hash."""
        # Set up the mock local file model to return files
        self.mock_local_file_model.get_all_files.return_value = [
            {
                "id": 1,
                "path": "/downloads/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 1,
                "hash": "abc123",  # Different hash
                "last_updated": 1609459200
            }
        ]
        
        # Set up the mock remote file model to return files
        self.mock_remote_file_model.get_all_files.return_value = [
            {
                "id": 1,
                "site_id": 1,
                "url": "http://example.com/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 2048,  # Different size
                "category_id": 1,
                "hash": "def456",  # Different hash
                "last_updated": 1609459300  # Different timestamp
            }
        ]
        
        # Call the compare method
        result = self.comparison.compare()
        
        # Check the result
        self.assertEqual(len(result["matching"]), 0)  # No matching files
        self.assertEqual(len(result["missing"]), 0)   # No missing files
        self.assertEqual(len(result["different"]), 1)  # file1.pdf has different hash
        
        # Check the different file
        self.assertEqual(result["different"][0]["local"]["name"], "file1.pdf")
        self.assertEqual(result["different"][0]["local"]["hash"], "abc123")
        self.assertEqual(result["different"][0]["remote"]["name"], "file1.pdf")
        self.assertEqual(result["different"][0]["remote"]["hash"], "def456")
    
    def test_compare_with_no_files(self):
        """Test the compare method with no files."""
        # Set up the mock models to return no files
        self.mock_local_file_model.get_all_files.return_value = []
        self.mock_remote_file_model.get_all_files.return_value = []
        
        # Call the compare method
        result = self.comparison.compare()
        
        # Check the result
        self.assertEqual(len(result["matching"]), 0)  # No matching files
        self.assertEqual(len(result["missing"]), 0)   # No missing files
        self.assertEqual(len(result["different"]), 0)  # No different files
    
    def test_compare_with_only_local_files(self):
        """Test the compare method with only local files."""
        # Set up the mock local file model to return files
        self.mock_local_file_model.get_all_files.return_value = [
            {
                "id": 1,
                "path": "/downloads/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 1,
                "hash": "abc123",
                "last_updated": 1609459200
            }
        ]
        
        # Set up the mock remote file model to return no files
        self.mock_remote_file_model.get_all_files.return_value = []
        
        # Call the compare method
        result = self.comparison.compare()
        
        # Check the result
        self.assertEqual(len(result["matching"]), 0)  # No matching files
        self.assertEqual(len(result["missing"]), 0)   # No missing files (only counts remote files missing locally)
        self.assertEqual(len(result["different"]), 0)  # No different files
    
    def test_compare_with_only_remote_files(self):
        """Test the compare method with only remote files."""
        # Set up the mock local file model to return no files
        self.mock_local_file_model.get_all_files.return_value = []
        
        # Set up the mock remote file model to return files
        self.mock_remote_file_model.get_all_files.return_value = [
            {
                "id": 1,
                "site_id": 1,
                "url": "http://example.com/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 1,
                "hash": "abc123",
                "last_updated": 1609459200
            }
        ]
        
        # Call the compare method
        result = self.comparison.compare()
        
        # Check the result
        self.assertEqual(len(result["matching"]), 0)  # No matching files
        self.assertEqual(len(result["missing"]), 1)   # file1.pdf is missing locally
        self.assertEqual(len(result["different"]), 0)  # No different files


if __name__ == "__main__":
    unittest.main()
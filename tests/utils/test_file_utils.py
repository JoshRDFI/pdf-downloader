import os
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.utils import file_utils


class TestFileUtils(unittest.TestCase):
    """Test case for the file_utils module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create a test file
        self.test_file = self.test_dir / "test.txt"
        with open(self.test_file, "w") as f:
            f.write("Test content")
        
        # Create a test PDF file
        self.pdf_file = self.test_dir / "test.pdf"
        with open(self.pdf_file, "w") as f:
            f.write("%PDF-1.5\nFake PDF content")
        
        # Create a test EPUB file
        self.epub_file = self.test_dir / "test.epub"
        with open(self.epub_file, "w") as f:
            f.write("Fake EPUB content")
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_get_file_extension(self):
        """Test the get_file_extension function."""
        # Test with various file paths
        self.assertEqual(file_utils.get_file_extension("file.txt"), ".txt")
        self.assertEqual(file_utils.get_file_extension("file.PDF"), ".pdf")  # Should be lowercase
        self.assertEqual(file_utils.get_file_extension("path/to/file.txt"), ".txt")
        self.assertEqual(file_utils.get_file_extension("file"), "")  # No extension
        self.assertEqual(file_utils.get_file_extension("file."), ".")  # Empty extension
    
    def test_get_file_name(self):
        """Test the get_file_name function."""
        # Test with various file paths
        self.assertEqual(file_utils.get_file_name("file.txt"), "file")
        self.assertEqual(file_utils.get_file_name("path/to/file.txt"), "file")
        self.assertEqual(file_utils.get_file_name("file"), "file")  # No extension
        self.assertEqual(file_utils.get_file_name("file."), "file")  # Empty extension
        self.assertEqual(file_utils.get_file_name(".hidden"), "")  # Hidden file
    
    def test_get_file_metadata(self):
        """Test the get_file_metadata function."""
        # Get metadata for the test file
        metadata = file_utils.get_file_metadata(str(self.test_file))
        
        # Check the metadata
        self.assertEqual(metadata["name"], "test.txt")
        self.assertEqual(metadata["extension"], ".txt")
        self.assertTrue(metadata["size"] > 0)
        self.assertTrue(metadata["modified"] > 0)
        self.assertTrue(os.path.exists(metadata["path"]))
    
    def test_is_valid_pdf(self):
        """Test the is_valid_pdf function."""
        # Test with a valid PDF file
        self.assertTrue(file_utils.is_valid_pdf(str(self.pdf_file)))
        
        # Test with a non-PDF file
        self.assertFalse(file_utils.is_valid_pdf(str(self.test_file)))
    
    def test_is_valid_epub(self):
        """Test the is_valid_epub function."""
        # Mock the epub.read_epub function
        with patch('ebooklib.epub.read_epub') as mock_read_epub:
            # Test with a valid EPUB file
            mock_read_epub.return_value = MagicMock()
            self.assertTrue(file_utils.is_valid_epub(str(self.epub_file)))
            
            # Test with an invalid EPUB file
            mock_read_epub.side_effect = Exception("Invalid EPUB")
            self.assertFalse(file_utils.is_valid_epub(str(self.epub_file)))
    
    def test_get_file_hash(self):
        """Test the get_file_hash function."""
        # Get the hash of the test file
        hash_value = file_utils.get_file_hash(str(self.test_file))
        
        # Check that the hash is a non-empty string
        self.assertTrue(isinstance(hash_value, str))
        self.assertTrue(len(hash_value) > 0)
        
        # Create a file with different content
        different_file = self.test_dir / "different.txt"
        with open(different_file, "w") as f:
            f.write("Different content")
        
        # Get the hash of the different file
        different_hash = file_utils.get_file_hash(str(different_file))
        
        # Check that the hashes are different
        self.assertNotEqual(hash_value, different_hash)
        
        # Create a file with the same content
        same_file = self.test_dir / "same.txt"
        with open(same_file, "w") as f:
            f.write("Test content")
        
        # Get the hash of the same file
        same_hash = file_utils.get_file_hash(str(same_file))
        
        # Check that the hashes are the same
        self.assertEqual(hash_value, same_hash)
    
    def test_create_directory(self):
        """Test the create_directory function."""
        # Create a new directory
        new_dir = self.test_dir / "new_dir"
        file_utils.create_directory(str(new_dir))
        
        # Check that the directory was created
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))
        
        # Create a nested directory
        nested_dir = self.test_dir / "parent" / "child"
        file_utils.create_directory(str(nested_dir))
        
        # Check that the nested directory was created
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(os.path.isdir(nested_dir))
    
    def test_delete_file(self):
        """Test the delete_file function."""
        # Create a file to delete
        file_to_delete = self.test_dir / "to_delete.txt"
        with open(file_to_delete, "w") as f:
            f.write("Delete me")
        
        # Check that the file exists
        self.assertTrue(os.path.exists(file_to_delete))
        
        # Delete the file
        file_utils.delete_file(str(file_to_delete))
        
        # Check that the file was deleted
        self.assertFalse(os.path.exists(file_to_delete))
    
    def test_delete_file_nonexistent(self):
        """Test deleting a file that doesn't exist."""
        # Try to delete a file that doesn't exist
        nonexistent_file = self.test_dir / "nonexistent.txt"
        
        # This should not raise an exception
        file_utils.delete_file(str(nonexistent_file))
    
    def test_scan_directory(self):
        """Test the scan_directory function."""
        # Create a directory structure with various files
        category_dir = self.test_dir / "category1"
        category_dir.mkdir()
        
        pdf_file = category_dir / "test.pdf"
        with open(pdf_file, "w") as f:
            f.write("%PDF-1.5\nFake PDF content")
        
        txt_file = category_dir / "test.txt"
        with open(txt_file, "w") as f:
            f.write("Text content")
        
        # Scan for all files
        all_files = file_utils.scan_directory(str(self.test_dir))
        
        # Check the result
        self.assertEqual(len(all_files), 5)  # 3 files in root + 2 files in category1
        
        # Scan for PDF files only
        pdf_files = file_utils.scan_directory(str(self.test_dir), extensions=[".pdf"])
        
        # Check the result
        self.assertEqual(len(pdf_files), 2)  # 1 in root + 1 in category1
        
        # Check that the category is correctly identified
        category1_files = [f for f in pdf_files if f["category"] == "category1"]
        self.assertEqual(len(category1_files), 1)
        self.assertEqual(category1_files[0]["name"], "test.pdf")
    
    def test_get_category_from_path(self):
        """Test the get_category_from_path function."""
        # Test with various paths
        self.assertEqual(
            file_utils.get_category_from_path(
                "/root/category/file.pdf",
                "/root"
            ),
            "category"
        )
        
        self.assertEqual(
            file_utils.get_category_from_path(
                "/root/category/subcategory/file.pdf",
                "/root"
            ),
            "category/subcategory"
        )
        
        self.assertEqual(
            file_utils.get_category_from_path(
                "/root/file.pdf",
                "/root"
            ),
            ""
        )
    
    def test_normalize_path(self):
        """Test the normalize_path function."""
        # Test with various paths
        self.assertEqual(
            file_utils.normalize_path("path/to/file"),
            os.path.normpath("path/to/file")
        )
        
        self.assertEqual(
            file_utils.normalize_path("path\\to\\file"),
            os.path.normpath("path/to/file")
        )
        
        self.assertEqual(
            file_utils.normalize_path("path/../file"),
            os.path.normpath("file")
        )


if __name__ == "__main__":
    unittest.main()
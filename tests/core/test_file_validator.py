import unittest
from unittest.mock import patch, MagicMock, mock_open
import os

from src.core.file_validator import FileValidator


class TestFileValidator(unittest.TestCase):
    """Test case for the FileValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create the file validator
        self.validator = FileValidator()
    
    def test_init(self):
        """Test the constructor."""
        # Check that the validator was created
        self.assertIsInstance(self.validator, FileValidator)
    
    @patch('os.path.exists')
    def test_validate_nonexistent_file(self, mock_exists):
        """Test the validate method with a nonexistent file."""
        # Set up the mock os.path.exists to return False
        mock_exists.return_value = False
        
        # Call the validate method
        result = self.validator.validate("/downloads/file1.pdf", "pdf")
        
        # Check the result
        self.assertFalse(result)
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_validate_empty_file(self, mock_getsize, mock_exists):
        """Test the validate method with an empty file."""
        # Set up the mock os.path.exists to return True
        mock_exists.return_value = True
        
        # Set up the mock os.path.getsize to return 0
        mock_getsize.return_value = 0
        
        # Call the validate method
        result = self.validator.validate("/downloads/file1.pdf", "pdf")
        
        # Check the result
        self.assertFalse(result)
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('PyPDF2.PdfReader')
    def test_validate_pdf(self, mock_pdf_reader, mock_getsize, mock_exists):
        """Test the validate method with a PDF file."""
        # Set up the mock os.path.exists to return True
        mock_exists.return_value = True
        
        # Set up the mock os.path.getsize to return a non-zero size
        mock_getsize.return_value = 1024
        
        # Set up the mock PdfReader
        mock_reader = MagicMock()
        mock_pdf_reader.return_value = mock_reader
        mock_reader.pages = [MagicMock()]  # One page
        
        # Call the validate method
        result = self.validator.validate("/downloads/file1.pdf", "pdf")
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the PDF reader was created
        mock_pdf_reader.assert_called_once_with("/downloads/file1.pdf")
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('PyPDF2.PdfReader')
    def test_validate_invalid_pdf(self, mock_pdf_reader, mock_getsize, mock_exists):
        """Test the validate method with an invalid PDF file."""
        # Set up the mock os.path.exists to return True
        mock_exists.return_value = True
        
        # Set up the mock os.path.getsize to return a non-zero size
        mock_getsize.return_value = 1024
        
        # Set up the mock PdfReader to raise an exception
        mock_pdf_reader.side_effect = Exception("Invalid PDF")
        
        # Call the validate method
        result = self.validator.validate("/downloads/file1.pdf", "pdf")
        
        # Check the result
        self.assertFalse(result)
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('ebooklib.epub.read_epub')
    def test_validate_epub(self, mock_read_epub, mock_getsize, mock_exists):
        """Test the validate method with an EPUB file."""
        # Set up the mock os.path.exists to return True
        mock_exists.return_value = True
        
        # Set up the mock os.path.getsize to return a non-zero size
        mock_getsize.return_value = 1024
        
        # Set up the mock read_epub
        mock_book = MagicMock()
        mock_read_epub.return_value = mock_book
        
        # Call the validate method
        result = self.validator.validate("/downloads/file1.epub", "epub")
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the EPUB reader was created
        mock_read_epub.assert_called_once_with("/downloads/file1.epub")
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('ebooklib.epub.read_epub')
    def test_validate_invalid_epub(self, mock_read_epub, mock_getsize, mock_exists):
        """Test the validate method with an invalid EPUB file."""
        # Set up the mock os.path.exists to return True
        mock_exists.return_value = True
        
        # Set up the mock os.path.getsize to return a non-zero size
        mock_getsize.return_value = 1024
        
        # Set up the mock read_epub to raise an exception
        mock_read_epub.side_effect = Exception("Invalid EPUB")
        
        # Call the validate method
        result = self.validator.validate("/downloads/file1.epub", "epub")
        
        # Check the result
        self.assertFalse(result)
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_validate_txt(self, mock_getsize, mock_exists):
        """Test the validate method with a TXT file."""
        # Set up the mock os.path.exists to return True
        mock_exists.return_value = True
        
        # Set up the mock os.path.getsize to return a non-zero size
        mock_getsize.return_value = 1024
        
        # Mock the open function
        mock_file = MagicMock()
        with patch('builtins.open', mock_open(mock=mock_file)):
            # Call the validate method
            result = self.validator.validate("/downloads/file1.txt", "txt")
            
            # Check the result
            self.assertTrue(result)
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_validate_unsupported_file_type(self, mock_getsize, mock_exists):
        """Test the validate method with an unsupported file type."""
        # Set up the mock os.path.exists to return True
        mock_exists.return_value = True
        
        # Set up the mock os.path.getsize to return a non-zero size
        mock_getsize.return_value = 1024
        
        # Call the validate method
        result = self.validator.validate("/downloads/file1.xyz", "xyz")
        
        # Check the result
        # For unsupported file types, the validator should return True if the file exists and is not empty
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
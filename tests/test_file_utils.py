"""Tests for the file_utils module.

This module contains tests for the file utility functions.
"""

import os
import tempfile
import unittest
from pathlib import Path

from src.utils.file_utils import get_file_metadata, is_valid_pdf, scan_directory


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
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_get_file_metadata(self):
        """Test the get_file_metadata function."""
        metadata = get_file_metadata(str(self.test_file))
        
        self.assertEqual(metadata["name"], "test.txt")
        self.assertEqual(metadata["extension"], ".txt")
        self.assertTrue(metadata["size"] > 0)
        self.assertTrue(metadata["modified"] > 0)
    
    def test_is_valid_pdf(self):
        """Test the is_valid_pdf function."""
        # Create a fake PDF file
        pdf_file = self.test_dir / "test.pdf"
        with open(pdf_file, "w") as f:
            f.write("%PDF-1.5\nFake PDF content")
        
        # Test with a PDF file
        self.assertTrue(is_valid_pdf(str(pdf_file)))
        
        # Test with a non-PDF file
        self.assertFalse(is_valid_pdf(str(self.test_file)))
    
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
        all_files = scan_directory(str(self.test_dir))
        self.assertEqual(len(all_files), 3)  # test.txt, category1/test.pdf, category1/test.txt
        
        # Scan for PDF files only
        pdf_files = scan_directory(str(self.test_dir), extensions=[".pdf"])
        self.assertEqual(len(pdf_files), 1)
        self.assertEqual(pdf_files[0]["name"], "test.pdf")
        self.assertEqual(pdf_files[0]["category"], "category1")


if __name__ == "__main__":
    unittest.main()
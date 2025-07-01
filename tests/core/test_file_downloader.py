import unittest
from unittest.mock import patch, MagicMock, mock_open
import os

from src.core.file_downloader import FileDownloader


class TestFileDownloader(unittest.TestCase):
    """Test case for the FileDownloader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create the file downloader
        self.downloader = FileDownloader()
    
    def test_init(self):
        """Test the constructor."""
        # Check that the progress callback is None
        self.assertIsNone(self.downloader.progress_callback)
    
    @patch('requests.get')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_download(self, mock_makedirs, mock_exists, mock_get):
        """Test the download method."""
        # Set up the mock requests.get to return a response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_get.return_value = mock_response
        
        # Set up the mock os.path.exists to return False for the directory
        mock_exists.return_value = False
        
        # Mock the open function
        mock_file = MagicMock()
        with patch('builtins.open', mock_open(mock=mock_file)):
            # Call the download method
            result = self.downloader.download(
                "http://example.com/file1.pdf",
                "/downloads/file1.pdf"
            )
            
            # Check that the directory was created
            mock_makedirs.assert_called_once_with("/downloads", exist_ok=True)
            
            # Check that the file was downloaded
            mock_get.assert_called_once_with(
                "http://example.com/file1.pdf",
                stream=True
            )
            
            # Check that the file was written
            mock_file().write.assert_any_call(b'chunk1')
            mock_file().write.assert_any_call(b'chunk2')
            
            # Check the result
            self.assertEqual(result, "/downloads/file1.pdf")
    
    @patch('requests.get')
    @patch('os.path.exists')
    def test_download_with_existing_directory(self, mock_exists, mock_get):
        """Test the download method with an existing directory."""
        # Set up the mock requests.get to return a response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_get.return_value = mock_response
        
        # Set up the mock os.path.exists to return True for the directory
        mock_exists.return_value = True
        
        # Mock the open function
        mock_file = MagicMock()
        with patch('builtins.open', mock_open(mock=mock_file)):
            # Call the download method
            result = self.downloader.download(
                "http://example.com/file1.pdf",
                "/downloads/file1.pdf"
            )
            
            # Check that the directory was not created
            # (os.makedirs is not mocked in this test)
            
            # Check that the file was downloaded
            mock_get.assert_called_once_with(
                "http://example.com/file1.pdf",
                stream=True
            )
            
            # Check that the file was written
            mock_file().write.assert_any_call(b'chunk1')
            mock_file().write.assert_any_call(b'chunk2')
            
            # Check the result
            self.assertEqual(result, "/downloads/file1.pdf")
    
    @patch('requests.get')
    def test_download_with_http_error(self, mock_get):
        """Test the download method with an HTTP error."""
        # Set up the mock requests.get to return an error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Call the download method and check that it raises an exception
        with self.assertRaises(Exception):
            self.downloader.download(
                "http://example.com/file1.pdf",
                "/downloads/file1.pdf"
            )
    
    @patch('requests.get')
    def test_download_with_network_error(self, mock_get):
        """Test the download method with a network error."""
        # Set up the mock requests.get to raise an exception
        mock_get.side_effect = Exception("Network error")
        
        # Call the download method and check that it raises an exception
        with self.assertRaises(Exception):
            self.downloader.download(
                "http://example.com/file1.pdf",
                "/downloads/file1.pdf"
            )
    
    @patch('requests.get')
    @patch('os.path.exists')
    def test_download_with_progress_callback(self, mock_exists, mock_get):
        """Test the download method with a progress callback."""
        # Set up the mock requests.get to return a response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Length": "100"}  # 100 bytes total
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_get.return_value = mock_response
        
        # Set up the mock os.path.exists to return True for the directory
        mock_exists.return_value = True
        
        # Create a mock progress callback
        mock_callback = MagicMock()
        
        # Set the progress callback
        self.downloader.set_progress_callback(mock_callback)
        
        # Mock the open function
        mock_file = MagicMock()
        with patch('builtins.open', mock_open(mock=mock_file)):
            # Call the download method
            self.downloader.download(
                "http://example.com/file1.pdf",
                "/downloads/file1.pdf",
                download_id=1
            )
            
            # Check that the progress callback was called
            # The exact progress values depend on the implementation
            mock_callback.assert_called()
    
    def test_set_progress_callback(self):
        """Test the set_progress_callback method."""
        # Create a mock callback
        mock_callback = MagicMock()
        
        # Call the set_progress_callback method
        self.downloader.set_progress_callback(mock_callback)
        
        # Check that the callback was saved
        self.assertEqual(self.downloader.progress_callback, mock_callback)


if __name__ == "__main__":
    unittest.main()
import unittest
from unittest.mock import patch, MagicMock

from src.utils import network_utils


class TestNetworkUtils(unittest.TestCase):
    """Test case for the network_utils module."""
    
    def test_get(self):
        """Test the get function."""
        # Mock the requests.get function
        with patch('requests.get') as mock_get:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "Test content"
            mock_get.return_value = mock_response
            
            # Call the get function
            response = network_utils.get("http://example.com")
            
            # Check the result
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "Test content")
            
            # Check that requests.get was called correctly
            mock_get.assert_called_once_with(
                "http://example.com",
                headers=unittest.mock.ANY,
                timeout=unittest.mock.ANY
            )
    
    def test_get_with_headers(self):
        """Test the get function with custom headers."""
        # Mock the requests.get function
        with patch('requests.get') as mock_get:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            # Call the get function with custom headers
            headers = {"User-Agent": "Test Agent", "Accept": "text/html"}
            response = network_utils.get("http://example.com", headers=headers)
            
            # Check the result
            self.assertEqual(response.status_code, 200)
            
            # Check that requests.get was called with the custom headers
            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            self.assertEqual(kwargs["headers"]["User-Agent"], "Test Agent")
            self.assertEqual(kwargs["headers"]["Accept"], "text/html")
    
    def test_get_with_timeout(self):
        """Test the get function with a custom timeout."""
        # Mock the requests.get function
        with patch('requests.get') as mock_get:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            # Call the get function with a custom timeout
            response = network_utils.get("http://example.com", timeout=10)
            
            # Check the result
            self.assertEqual(response.status_code, 200)
            
            # Check that requests.get was called with the custom timeout
            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            self.assertEqual(kwargs["timeout"], 10)
    
    def test_get_with_session(self):
        """Test the get function with a session."""
        # Mock the requests.Session class
        with patch('requests.Session') as mock_session_class:
            # Set up the mock session
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_session.get.return_value = mock_response
            
            # Call the get function with a session
            response = network_utils.get("http://example.com", use_session=True)
            
            # Check the result
            self.assertEqual(response.status_code, 200)
            
            # Check that the session's get method was called correctly
            mock_session.get.assert_called_once_with(
                "http://example.com",
                headers=unittest.mock.ANY,
                timeout=unittest.mock.ANY
            )
    
    def test_post(self):
        """Test the post function."""
        # Mock the requests.post function
        with patch('requests.post') as mock_post:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_post.return_value = mock_response
            
            # Call the post function
            data = {"key": "value"}
            response = network_utils.post("http://example.com", data=data)
            
            # Check the result
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"success": True})
            
            # Check that requests.post was called correctly
            mock_post.assert_called_once_with(
                "http://example.com",
                data=data,
                headers=unittest.mock.ANY,
                timeout=unittest.mock.ANY
            )
    
    def test_post_with_json(self):
        """Test the post function with JSON data."""
        # Mock the requests.post function
        with patch('requests.post') as mock_post:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            # Call the post function with JSON data
            json_data = {"key": "value"}
            response = network_utils.post("http://example.com", json=json_data)
            
            # Check the result
            self.assertEqual(response.status_code, 200)
            
            # Check that requests.post was called with the JSON data
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertEqual(kwargs["json"], json_data)
    
    def test_download_file(self):
        """Test the download_file function."""
        # Mock the get function
        with patch('src.utils.network_utils.get') as mock_get:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
            mock_get.return_value.__enter__.return_value = mock_response
            
            # Mock the open function
            mock_open = unittest.mock.mock_open()
            with patch('builtins.open', mock_open):
                # Call the download_file function
                result = network_utils.download_file(
                    url="http://example.com/file.pdf",
                    file_path="/downloads/file.pdf"
                )
                
                # Check the result
                self.assertTrue(result["success"])
                self.assertEqual(result["file_path"], "/downloads/file.pdf")
                
                # Check that the file was written correctly
                mock_file = mock_open()
                mock_file.write.assert_any_call(b"chunk1")
                mock_file.write.assert_any_call(b"chunk2")
    
    def test_download_file_with_progress(self):
        """Test the download_file function with progress updates."""
        # Mock the get function
        with patch('src.utils.network_utils.get') as mock_get:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Length": "100"}
            mock_response.iter_content.return_value = [b"a" * 50, b"b" * 50]
            mock_get.return_value.__enter__.return_value = mock_response
            
            # Mock the open function
            mock_open = unittest.mock.mock_open()
            with patch('builtins.open', mock_open):
                # Create a mock progress callback
                mock_progress = MagicMock()
                
                # Call the download_file function with progress updates
                result = network_utils.download_file(
                    url="http://example.com/file.pdf",
                    file_path="/downloads/file.pdf",
                    progress_callback=mock_progress
                )
                
                # Check the result
                self.assertTrue(result["success"])
                
                # Check that the progress callback was called
                mock_progress.assert_any_call(0.5)  # After the first chunk
                mock_progress.assert_any_call(1.0)  # After the second chunk
    
    def test_download_file_error(self):
        """Test the download_file function with an error."""
        # Mock the get function to raise an exception
        with patch('src.utils.network_utils.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            # Call the download_file function
            result = network_utils.download_file(
                url="http://example.com/file.pdf",
                file_path="/downloads/file.pdf"
            )
            
            # Check the result
            self.assertFalse(result["success"])
            self.assertEqual(result["error"], "Network error")
    
    def test_is_url_valid(self):
        """Test the is_url_valid function."""
        # Test with valid URLs
        self.assertTrue(network_utils.is_url_valid("http://example.com"))
        self.assertTrue(network_utils.is_url_valid("https://example.com"))
        self.assertTrue(network_utils.is_url_valid("http://example.com/path/to/file.pdf"))
        
        # Test with invalid URLs
        self.assertFalse(network_utils.is_url_valid("not a url"))
        self.assertFalse(network_utils.is_url_valid("ftp://example.com"))  # Not HTTP/HTTPS
        self.assertFalse(network_utils.is_url_valid("http://"))  # No domain
    
    def test_get_domain(self):
        """Test the get_domain function."""
        # Test with various URLs
        self.assertEqual(network_utils.get_domain("http://example.com"), "example.com")
        self.assertEqual(network_utils.get_domain("https://example.com/path"), "example.com")
        self.assertEqual(network_utils.get_domain("http://sub.example.com"), "sub.example.com")
        
        # Test with invalid URLs
        self.assertIsNone(network_utils.get_domain("not a url"))


if __name__ == "__main__":
    unittest.main()
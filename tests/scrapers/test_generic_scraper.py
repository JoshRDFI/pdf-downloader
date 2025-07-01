import unittest
from unittest.mock import patch, MagicMock

from src.scrapers.generic_scraper import GenericScraper


class TestGenericScraper(unittest.TestCase):
    """Test case for the GenericScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create an instance of the generic scraper
        self.scraper = GenericScraper("http://example.com")
    
    def test_init(self):
        """Test the constructor."""
        # Check that the site URL was set correctly
        self.assertEqual(self.scraper.site_url, "http://example.com")
        
        # Check that the username and password are None by default
        self.assertIsNone(self.scraper.username)
        self.assertIsNone(self.scraper.password)
        
        # Create a scraper with username and password
        scraper = GenericScraper("http://example.com", "user", "pass")
        self.assertEqual(scraper.username, "user")
        self.assertEqual(scraper.password, "pass")
    
    def test_scan(self):
        """Test the scan method."""
        # Mock the requests.get function
        with patch('requests.get') as mock_get:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
                <body>
                    <a href="file1.pdf">File 1</a>
                    <a href="file2.pdf">File 2</a>
                    <a href="file3.txt">File 3</a>
                    <a href="http://example.com/file4.pdf">File 4</a>
                    <a href="https://another-site.com/file5.pdf">File 5</a>
                </body>
            </html>
            """
            mock_get.return_value = mock_response
            
            # Call the scan method
            files = self.scraper.scan()
            
            # Check the result
            self.assertEqual(len(files), 4)  # 3 PDF files + 1 TXT file
            
            # Check that the URLs are correctly formed
            urls = [file["url"] for file in files]
            self.assertIn("http://example.com/file1.pdf", urls)
            self.assertIn("http://example.com/file2.pdf", urls)
            self.assertIn("http://example.com/file3.txt", urls)
            self.assertIn("http://example.com/file4.pdf", urls)
            
            # Check that the external URL is not included
            self.assertNotIn("https://another-site.com/file5.pdf", urls)
    
    def test_scan_with_extensions(self):
        """Test the scan method with specific extensions."""
        # Mock the requests.get function
        with patch('requests.get') as mock_get:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
                <body>
                    <a href="file1.pdf">File 1</a>
                    <a href="file2.pdf">File 2</a>
                    <a href="file3.txt">File 3</a>
                    <a href="file4.epub">File 4</a>
                </body>
            </html>
            """
            mock_get.return_value = mock_response
            
            # Call the scan method with specific extensions
            files = self.scraper.scan(extensions=[".pdf"])
            
            # Check the result
            self.assertEqual(len(files), 2)  # Only PDF files
            
            # Check that only PDF files are included
            urls = [file["url"] for file in files]
            self.assertIn("http://example.com/file1.pdf", urls)
            self.assertIn("http://example.com/file2.pdf", urls)
            self.assertNotIn("http://example.com/file3.txt", urls)
            self.assertNotIn("http://example.com/file4.epub", urls)
    
    def test_scan_with_recursive(self):
        """Test the scan method with recursive scanning."""
        # Mock the requests.get function
        with patch('requests.get') as mock_get:
            # Set up the mock responses
            main_response = MagicMock()
            main_response.status_code = 200
            main_response.text = """
            <html>
                <body>
                    <a href="file1.pdf">File 1</a>
                    <a href="subdir/">Subdir</a>
                </body>
            </html>
            """
            
            subdir_response = MagicMock()
            subdir_response.status_code = 200
            subdir_response.text = """
            <html>
                <body>
                    <a href="file2.pdf">File 2</a>
                </body>
            </html>
            """
            
            # Set up the mock to return different responses for different URLs
            def get_response(url, **kwargs):
                if url == "http://example.com":
                    return main_response
                elif url == "http://example.com/subdir/":
                    return subdir_response
                else:
                    raise ValueError(f"Unexpected URL: {url}")
            
            mock_get.side_effect = get_response
            
            # Call the scan method with recursive scanning
            files = self.scraper.scan(recursive=True)
            
            # Check the result
            self.assertEqual(len(files), 2)  # 1 file in main dir + 1 file in subdir
            
            # Check that files from both directories are included
            urls = [file["url"] for file in files]
            self.assertIn("http://example.com/file1.pdf", urls)
            self.assertIn("http://example.com/subdir/file2.pdf", urls)
    
    def test_get_file_details(self):
        """Test the get_file_details method."""
        # Mock the requests.head function
        with patch('requests.head') as mock_head:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {
                "Content-Length": "1024",
                "Content-Type": "application/pdf"
            }
            mock_head.return_value = mock_response
            
            # Call the get_file_details method
            details = self.scraper.get_file_details("http://example.com/file.pdf")
            
            # Check the result
            self.assertEqual(details["url"], "http://example.com/file.pdf")
            self.assertEqual(details["name"], "file.pdf")
            self.assertEqual(details["type"], "pdf")
            self.assertEqual(details["size"], 1024)
            self.assertEqual(details["category"], "")  # No category for generic scraper
    
    def test_get_file_details_with_category(self):
        """Test the get_file_details method with a category."""
        # Mock the requests.head function
        with patch('requests.head') as mock_head:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {
                "Content-Length": "1024",
                "Content-Type": "application/pdf"
            }
            mock_head.return_value = mock_response
            
            # Call the get_file_details method with a category
            details = self.scraper.get_file_details(
                "http://example.com/category/file.pdf",
                category="category"
            )
            
            # Check the result
            self.assertEqual(details["url"], "http://example.com/category/file.pdf")
            self.assertEqual(details["name"], "file.pdf")
            self.assertEqual(details["type"], "pdf")
            self.assertEqual(details["size"], 1024)
            self.assertEqual(details["category"], "category")
    
    def test_login(self):
        """Test the login method."""
        # Mock the requests.post function
        with patch('requests.post') as mock_post:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            # Create a scraper with username and password
            scraper = GenericScraper("http://example.com", "user", "pass")
            
            # Call the login method
            scraper.login()
            
            # Check that requests.post was called with the correct arguments
            mock_post.assert_called_once_with(
                "http://example.com/login",
                data={"username": "user", "password": "pass"},
                headers=unittest.mock.ANY
            )
    
    def test_logout(self):
        """Test the logout method."""
        # Mock the requests.get function
        with patch('requests.get') as mock_get:
            # Set up the mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            # Call the logout method
            self.scraper.logout()
            
            # Check that requests.get was called with the correct arguments
            mock_get.assert_called_once_with(
                "http://example.com/logout",
                headers=unittest.mock.ANY
            )


if __name__ == "__main__":
    unittest.main()
import unittest
from unittest.mock import patch, MagicMock

from src.core.downloader import Downloader


class TestDownloader(unittest.TestCase):
    """Test case for the Downloader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock models
        self.mock_download_model = MagicMock()
        self.mock_category_model = MagicMock()
        self.mock_settings_model = MagicMock()
        
        # Create the downloader
        self.downloader = Downloader(
            self.mock_download_model,
            self.mock_category_model,
            self.mock_settings_model
        )
    
    def test_init(self):
        """Test the constructor."""
        # Check that the models were saved
        self.assertEqual(self.downloader.download_model, self.mock_download_model)
        self.assertEqual(self.downloader.category_model, self.mock_category_model)
        self.assertEqual(self.downloader.settings_model, self.mock_settings_model)
    
    @patch('src.core.file_downloader.FileDownloader')
    def test_download_file(self, mock_downloader_class):
        """Test the download_file method."""
        # Set up the mock file downloader
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        
        # Set up the mock downloader to return a file path
        mock_downloader.download.return_value = "/downloads/file1.pdf"
        
        # Set up the mock settings model to return settings
        self.mock_settings_model.get_setting.return_value = "/downloads"
        
        # Set up the mock category model to return a category
        self.mock_category_model.get_category.return_value = {
            "id": 1,
            "name": "Category 1",
            "parent_id": None
        }
        
        # Call the download_file method
        result = self.downloader.download_file(
            "http://example.com/file1.pdf",
            "file1.pdf",
            "pdf",
            1
        )
        
        # Check that the settings model was queried
        self.mock_settings_model.get_setting.assert_called_once_with(
            "download_dir",
            default="/downloads"
        )
        
        # Check that the category model was queried
        self.mock_category_model.get_category.assert_called_once_with(1)
        
        # Check that the downloader was created and used
        mock_downloader_class.assert_called_once()
        mock_downloader.download.assert_called_once_with(
            "http://example.com/file1.pdf",
            "/downloads/Category 1/file1.pdf"
        )
        
        # Check the result
        self.assertEqual(result, "/downloads/Category 1/file1.pdf")
    
    @patch('src.core.file_downloader.FileDownloader')
    def test_download_file_with_subcategory(self, mock_downloader_class):
        """Test the download_file method with a subcategory."""
        # Set up the mock file downloader
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        
        # Set up the mock downloader to return a file path
        mock_downloader.download.return_value = "/downloads/Category 1/Subcategory/file1.pdf"
        
        # Set up the mock settings model to return settings
        self.mock_settings_model.get_setting.return_value = "/downloads"
        
        # Set up the mock category model to return categories
        self.mock_category_model.get_category.side_effect = lambda category_id: {
            1: {"id": 1, "name": "Subcategory", "parent_id": 2},
            2: {"id": 2, "name": "Category 1", "parent_id": None}
        }.get(category_id)
        
        # Call the download_file method
        result = self.downloader.download_file(
            "http://example.com/file1.pdf",
            "file1.pdf",
            "pdf",
            1
        )
        
        # Check that the settings model was queried
        self.mock_settings_model.get_setting.assert_called_once_with(
            "download_dir",
            default="/downloads"
        )
        
        # Check that the category model was queried
        self.mock_category_model.get_category.assert_any_call(1)
        self.mock_category_model.get_category.assert_any_call(2)
        
        # Check that the downloader was created and used
        mock_downloader_class.assert_called_once()
        mock_downloader.download.assert_called_once_with(
            "http://example.com/file1.pdf",
            "/downloads/Category 1/Subcategory/file1.pdf"
        )
        
        # Check the result
        self.assertEqual(result, "/downloads/Category 1/Subcategory/file1.pdf")
    
    @patch('src.core.file_downloader.FileDownloader')
    def test_download_file_with_progress_callback(self, mock_downloader_class):
        """Test the download_file method with a progress callback."""
        # Set up the mock file downloader
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        
        # Set up the mock downloader to return a file path
        mock_downloader.download.return_value = "/downloads/file1.pdf"
        
        # Set up the mock settings model to return settings
        self.mock_settings_model.get_setting.return_value = "/downloads"
        
        # Set up the mock category model to return a category
        self.mock_category_model.get_category.return_value = {
            "id": 1,
            "name": "Category 1",
            "parent_id": None
        }
        
        # Create a mock progress callback
        mock_callback = MagicMock()
        
        # Call the download_file method with a progress callback
        result = self.downloader.download_file(
            "http://example.com/file1.pdf",
            "file1.pdf",
            "pdf",
            1,
            progress_callback=mock_callback,
            download_id=1
        )
        
        # Check that the progress callback was set
        mock_downloader.set_progress_callback.assert_called_once_with(mock_callback)
        
        # Check that the downloader was used with the download ID
        mock_downloader.download.assert_called_once_with(
            "http://example.com/file1.pdf",
            "/downloads/Category 1/file1.pdf",
            download_id=1
        )
    
    @patch('src.core.file_downloader.FileDownloader')
    def test_download_file_with_error(self, mock_downloader_class):
        """Test the download_file method with an error."""
        # Set up the mock file downloader
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        
        # Set up the mock downloader to raise an exception
        mock_downloader.download.side_effect = Exception("Download failed")
        
        # Set up the mock settings model to return settings
        self.mock_settings_model.get_setting.return_value = "/downloads"
        
        # Set up the mock category model to return a category
        self.mock_category_model.get_category.return_value = {
            "id": 1,
            "name": "Category 1",
            "parent_id": None
        }
        
        # Call the download_file method and check that it raises an exception
        with self.assertRaises(Exception):
            self.downloader.download_file(
                "http://example.com/file1.pdf",
                "file1.pdf",
                "pdf",
                1
            )


if __name__ == "__main__":
    unittest.main()
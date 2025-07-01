import unittest
from unittest.mock import patch, MagicMock
import threading

from src.core.download_manager import DownloadManager


class TestDownloadManager(unittest.TestCase):
    """Test case for the DownloadManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock models
        self.mock_download_model = MagicMock()
        self.mock_category_model = MagicMock()
        
        # Set up the mock download model to return downloads
        self.mock_download_model.get_queue.return_value = [
            {
                "id": 1,
                "url": "http://example.com/file1.pdf",
                "file_name": "file1.pdf",
                "file_type": "pdf",
                "category_id": 1,
                "priority": 1,
                "status": "queued",
                "created_at": 1609459200,
                "started_at": None,
                "completed_at": None
            },
            {
                "id": 2,
                "url": "http://example.com/file2.pdf",
                "file_name": "file2.pdf",
                "file_type": "pdf",
                "category_id": 1,
                "priority": 2,
                "status": "queued",
                "created_at": 1609459300,
                "started_at": None,
                "completed_at": None
            }
        ]
        
        # Set up the mock category model to return categories
        self.mock_category_model.get_category.return_value = {
            "id": 1,
            "name": "Category 1",
            "parent_id": None
        }
        
        # Create the download manager
        self.manager = DownloadManager(
            self.mock_download_model,
            self.mock_category_model
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Stop the download manager if it's running
        if self.manager.is_running:
            self.manager.stop()
    
    def test_init(self):
        """Test the constructor."""
        # Check that the models were saved
        self.assertEqual(self.manager.download_model, self.mock_download_model)
        self.assertEqual(self.manager.category_model, self.mock_category_model)
        
        # Check that the manager is not running
        self.assertFalse(self.manager.is_running)
        
        # Check that the thread is None
        self.assertIsNone(self.manager.thread)
    
    def test_start(self):
        """Test the start method."""
        # Mock the threading.Thread class
        with patch('threading.Thread') as mock_thread_class:
            # Set up the mock thread
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread
            
            # Call the start method
            self.manager.start()
            
            # Check that the thread was created and started
            mock_thread_class.assert_called_once_with(
                target=self.manager._download_thread,
                daemon=True
            )
            mock_thread.start.assert_called_once()
            
            # Check that the manager is running
            self.assertTrue(self.manager.is_running)
            
            # Check that the thread was saved
            self.assertEqual(self.manager.thread, mock_thread)
    
    def test_pause(self):
        """Test the pause method."""
        # Start the manager
        self.manager.is_running = True
        self.manager.thread = MagicMock()
        
        # Call the pause method
        self.manager.pause()
        
        # Check that the manager is not running
        self.assertFalse(self.manager.is_running)
    
    def test_stop(self):
        """Test the stop method."""
        # Start the manager
        self.manager.is_running = True
        self.manager.thread = MagicMock()
        
        # Call the stop method
        self.manager.stop()
        
        # Check that the manager is not running
        self.assertFalse(self.manager.is_running)
        
        # Check that the thread is None
        self.assertIsNone(self.manager.thread)
    
    @patch('src.core.file_downloader.FileDownloader')
    def test_download_thread(self, mock_downloader_class):
        """Test the _download_thread method."""
        # Set up the mock downloader
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        
        # Set up the mock downloader to return a file path
        mock_downloader.download.return_value = "/downloads/file1.pdf"
        
        # Set up the mock settings model to return settings
        self.manager.settings_model = MagicMock()
        self.manager.settings_model.get_setting.return_value = "/downloads"
        
        # Set up the mock file validator
        with patch('src.core.file_validator.FileValidator') as mock_validator_class:
            # Set up the mock validator
            mock_validator = MagicMock()
            mock_validator_class.return_value = mock_validator
            
            # Set up the mock validator to return True
            mock_validator.validate.return_value = True
            
            # Start the manager
            self.manager.is_running = True
            
            # Call the _download_thread method directly
            # We'll use a separate thread to call it and then stop it after a short time
            thread = threading.Thread(target=self._run_download_thread)
            thread.daemon = True
            thread.start()
            
            # Wait a short time for the thread to process at least one download
            import time
            time.sleep(0.1)
            
            # Stop the manager
            self.manager.is_running = False
            thread.join(timeout=1.0)
            
            # Check that the download model was queried
            self.mock_download_model.get_queue.assert_called()
            
            # Check that the download was started
            self.mock_download_model.update_status.assert_any_call(
                download_id=1,
                status="downloading"
            )
            
            # Check that the downloader was created and used
            mock_downloader_class.assert_called_once()
            mock_downloader.download.assert_called_once_with(
                "http://example.com/file1.pdf",
                "/downloads/file1.pdf"
            )
            
            # Check that the validator was created and used
            mock_validator_class.assert_called_once()
            mock_validator.validate.assert_called_once_with(
                "/downloads/file1.pdf",
                "pdf"
            )
            
            # Check that the download was completed
            self.mock_download_model.update_status.assert_any_call(
                download_id=1,
                status="completed"
            )
    
    def _run_download_thread(self):
        """Helper method to run the download thread."""
        try:
            self.manager._download_thread()
        except Exception as e:
            print(f"Error in download thread: {e}")
    
    @patch('src.core.file_downloader.FileDownloader')
    def test_download_thread_with_error(self, mock_downloader_class):
        """Test the _download_thread method with a download error."""
        # Set up the mock downloader
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        
        # Set up the mock downloader to raise an exception
        mock_downloader.download.side_effect = Exception("Download failed")
        
        # Set up the mock settings model to return settings
        self.manager.settings_model = MagicMock()
        self.manager.settings_model.get_setting.return_value = "/downloads"
        
        # Start the manager
        self.manager.is_running = True
        
        # Call the _download_thread method directly
        # We'll use a separate thread to call it and then stop it after a short time
        thread = threading.Thread(target=self._run_download_thread)
        thread.daemon = True
        thread.start()
        
        # Wait a short time for the thread to process at least one download
        import time
        time.sleep(0.1)
        
        # Stop the manager
        self.manager.is_running = False
        thread.join(timeout=1.0)
        
        # Check that the download was started
        self.mock_download_model.update_status.assert_any_call(
            download_id=1,
            status="downloading"
        )
        
        # Check that the download failed
        self.mock_download_model.update_status.assert_any_call(
            download_id=1,
            status="failed"
        )
    
    @patch('src.core.file_downloader.FileDownloader')
    def test_download_thread_with_validation_error(self, mock_downloader_class):
        """Test the _download_thread method with a validation error."""
        # Set up the mock downloader
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        
        # Set up the mock downloader to return a file path
        mock_downloader.download.return_value = "/downloads/file1.pdf"
        
        # Set up the mock settings model to return settings
        self.manager.settings_model = MagicMock()
        self.manager.settings_model.get_setting.return_value = "/downloads"
        
        # Set up the mock file validator
        with patch('src.core.file_validator.FileValidator') as mock_validator_class:
            # Set up the mock validator
            mock_validator = MagicMock()
            mock_validator_class.return_value = mock_validator
            
            # Set up the mock validator to return False
            mock_validator.validate.return_value = False
            
            # Start the manager
            self.manager.is_running = True
            
            # Call the _download_thread method directly
            # We'll use a separate thread to call it and then stop it after a short time
            thread = threading.Thread(target=self._run_download_thread)
            thread.daemon = True
            thread.start()
            
            # Wait a short time for the thread to process at least one download
            import time
            time.sleep(0.1)
            
            # Stop the manager
            self.manager.is_running = False
            thread.join(timeout=1.0)
            
            # Check that the download was started
            self.mock_download_model.update_status.assert_any_call(
                download_id=1,
                status="downloading"
            )
            
            # Check that the download failed validation
            self.mock_download_model.update_status.assert_any_call(
                download_id=1,
                status="validation_failed"
            )
    
    def test_on_progress(self):
        """Test the on_progress method."""
        # Create a mock progress callback
        self.manager.progress_callback = MagicMock()
        
        # Call the on_progress method
        self.manager.on_progress(1, 0.5)  # 50% progress for download ID 1
        
        # Check that the callback was called
        self.manager.progress_callback.assert_called_once_with(1, 0.5)
    
    def test_set_progress_callback(self):
        """Test the set_progress_callback method."""
        # Create a mock callback
        mock_callback = MagicMock()
        
        # Call the set_progress_callback method
        self.manager.set_progress_callback(mock_callback)
        
        # Check that the callback was saved
        self.assertEqual(self.manager.progress_callback, mock_callback)


if __name__ == "__main__":
    unittest.main()
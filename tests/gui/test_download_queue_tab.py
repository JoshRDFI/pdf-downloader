import unittest
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication, QWidget
from src.gui.download_queue_tab import DownloadQueueTab


# Create a QApplication instance for testing
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestDownloadQueueTab(unittest.TestCase):
    """Test case for the DownloadQueueTab class."""
    
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
                "status": "downloading",
                "created_at": 1609459300,
                "started_at": 1609459400,
                "completed_at": None
            }
        ]
        
        # Set up the mock category model to return categories
        self.mock_category_model.get_category.return_value = {
            "id": 1,
            "name": "Category 1",
            "parent_id": None
        }
        
        # Create the download queue tab
        self.tab = DownloadQueueTab(self.mock_download_model, self.mock_category_model)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Close the tab
        self.tab.close()
    
    def test_init(self):
        """Test the constructor."""
        # Check that the tab was created
        self.assertIsInstance(self.tab, QWidget)
        
        # Check that the models were saved
        self.assertEqual(self.tab.download_model, self.mock_download_model)
        self.assertEqual(self.tab.category_model, self.mock_category_model)
    
    def test_create_ui(self):
        """Test the create_ui method."""
        # Check that the queue table was created
        self.assertIsNotNone(self.tab.queue_table)
        
        # Check that the buttons were created
        self.assertIsNotNone(self.tab.start_button)
        self.assertIsNotNone(self.tab.pause_button)
        self.assertIsNotNone(self.tab.remove_button)
        self.assertIsNotNone(self.tab.clear_button)
    
    def test_refresh(self):
        """Test the refresh method."""
        # Call the refresh method
        self.tab.refresh()
        
        # Check that the download model was queried
        self.mock_download_model.get_queue.assert_called_once()
        
        # Check that the queue table was populated
        self.assertEqual(self.tab.queue_table.rowCount(), 2)
        self.assertEqual(self.tab.queue_table.item(0, 1).text(), "file1.pdf")
        self.assertEqual(self.tab.queue_table.item(1, 1).text(), "file2.pdf")
    
    def test_start_downloads(self):
        """Test the start_downloads method."""
        # Mock the DownloadManager class
        with patch('src.core.download_manager.DownloadManager') as mock_manager_class:
            # Set up the mock manager
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            
            # Call the start_downloads method
            self.tab.start_downloads()
            
            # Check that the download manager was created and started
            mock_manager_class.assert_called_once_with(
                self.mock_download_model,
                self.mock_category_model
            )
            mock_manager.start.assert_called_once()
            
            # Check that the download manager was saved
            self.assertEqual(self.tab.download_manager, mock_manager)
    
    def test_pause_downloads(self):
        """Test the pause_downloads method."""
        # Create a mock download manager
        self.tab.download_manager = MagicMock()
        
        # Call the pause_downloads method
        self.tab.pause_downloads()
        
        # Check that the download manager was paused
        self.tab.download_manager.pause.assert_called_once()
    
    def test_remove_selected(self):
        """Test the remove_selected method."""
        # Refresh the tab to populate the queue table
        self.tab.refresh()
        
        # Select a row in the queue table
        self.tab.queue_table.selectRow(0)
        
        # Call the remove_selected method
        self.tab.remove_selected()
        
        # Check that the download was removed from the queue
        self.mock_download_model.remove_from_queue.assert_called_once_with(1)
        
        # Check that the queue was refreshed
        self.assertEqual(self.mock_download_model.get_queue.call_count, 2)
    
    def test_clear_queue(self):
        """Test the clear_queue method."""
        # Mock the QMessageBox.question method to return Yes
        with patch('PyQt5.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.Yes
            
            # Call the clear_queue method
            self.tab.clear_queue()
            
            # Check that each download was removed from the queue
            self.mock_download_model.remove_from_queue.assert_any_call(1)
            self.mock_download_model.remove_from_queue.assert_any_call(2)
            
            # Check that the queue was refreshed
            self.assertEqual(self.mock_download_model.get_queue.call_count, 2)
    
    def test_update_progress(self):
        """Test the update_progress method."""
        # Refresh the tab to populate the queue table
        self.tab.refresh()
        
        # Call the update_progress method
        self.tab.update_progress(1, 0.5)  # 50% progress for download ID 1
        
        # Check that the progress bar was updated
        progress_bar = self.tab.queue_table.cellWidget(0, 5)
        self.assertEqual(progress_bar.value(), 50)  # 50% progress


if __name__ == "__main__":
    unittest.main()
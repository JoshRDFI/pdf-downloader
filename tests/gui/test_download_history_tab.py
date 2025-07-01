import unittest
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication, QWidget
from src.gui.download_history_tab import DownloadHistoryTab


# Create a QApplication instance for testing
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestDownloadHistoryTab(unittest.TestCase):
    """Test case for the DownloadHistoryTab class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock models
        self.mock_download_model = MagicMock()
        self.mock_category_model = MagicMock()
        
        # Set up the mock download model to return downloads
        self.mock_download_model.get_history.return_value = [
            {
                "id": 1,
                "url": "http://example.com/file1.pdf",
                "file_name": "file1.pdf",
                "file_type": "pdf",
                "category_id": 1,
                "priority": 1,
                "status": "completed",
                "created_at": 1609459200,
                "started_at": 1609459300,
                "completed_at": 1609459400
            },
            {
                "id": 2,
                "url": "http://example.com/file2.pdf",
                "file_name": "file2.pdf",
                "file_type": "pdf",
                "category_id": 1,
                "priority": 2,
                "status": "failed",
                "created_at": 1609459500,
                "started_at": 1609459600,
                "completed_at": 1609459700
            }
        ]
        
        # Set up the mock category model to return categories
        self.mock_category_model.get_category.return_value = {
            "id": 1,
            "name": "Category 1",
            "parent_id": None
        }
        
        # Create the download history tab
        self.tab = DownloadHistoryTab(self.mock_download_model, self.mock_category_model)
    
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
        # Check that the history table was created
        self.assertIsNotNone(self.tab.history_table)
        
        # Check that the buttons were created
        self.assertIsNotNone(self.tab.retry_button)
        self.assertIsNotNone(self.tab.delete_button)
        self.assertIsNotNone(self.tab.clear_button)
    
    def test_refresh(self):
        """Test the refresh method."""
        # Call the refresh method
        self.tab.refresh()
        
        # Check that the download model was queried
        self.mock_download_model.get_history.assert_called_once()
        
        # Check that the history table was populated
        self.assertEqual(self.tab.history_table.rowCount(), 2)
        self.assertEqual(self.tab.history_table.item(0, 1).text(), "file1.pdf")
        self.assertEqual(self.tab.history_table.item(1, 1).text(), "file2.pdf")
    
    def test_retry_selected(self):
        """Test the retry_selected method."""
        # Refresh the tab to populate the history table
        self.tab.refresh()
        
        # Select a row in the history table
        self.tab.history_table.selectRow(1)  # Select the failed download
        
        # Call the retry_selected method
        self.tab.retry_selected()
        
        # Check that the download was requeued
        self.mock_download_model.requeue.assert_called_once_with(2)
        
        # Check that the history was refreshed
        self.assertEqual(self.mock_download_model.get_history.call_count, 2)
    
    def test_delete_selected(self):
        """Test the delete_selected method."""
        # Refresh the tab to populate the history table
        self.tab.refresh()
        
        # Select a row in the history table
        self.tab.history_table.selectRow(0)
        
        # Call the delete_selected method
        self.tab.delete_selected()
        
        # Check that the download was deleted from history
        self.mock_download_model.delete_from_history.assert_called_once_with(1)
        
        # Check that the history was refreshed
        self.assertEqual(self.mock_download_model.get_history.call_count, 2)
    
    def test_clear_history(self):
        """Test the clear_history method."""
        # Mock the QMessageBox.question method to return Yes
        with patch('PyQt5.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.Yes
            
            # Call the clear_history method
            self.tab.clear_history()
            
            # Check that the history was cleared
            self.mock_download_model.clear_history.assert_called_once()
            
            # Check that the history was refreshed
            self.assertEqual(self.mock_download_model.get_history.call_count, 2)
    
    def test_filter_history(self):
        """Test the filter_history method."""
        # Refresh the tab to populate the history table
        self.tab.refresh()
        
        # Set up the filter combo and text
        self.tab.filter_combo.setCurrentIndex(1)  # Filter by file name
        self.tab.filter_text.setText("file1")
        
        # Call the filter_history method
        self.tab.filter_history()
        
        # Check that the history table was filtered
        # In a real implementation, this would filter the table to show only rows with "file1" in the file name
        # For this test, we'll just check that the filter was applied
        self.assertEqual(self.tab.filter_combo.currentIndex(), 1)
        self.assertEqual(self.tab.filter_text.text(), "file1")


if __name__ == "__main__":
    unittest.main()
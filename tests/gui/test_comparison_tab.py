import unittest
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication, QWidget
from src.gui.comparison_tab import ComparisonTab


# Create a QApplication instance for testing
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestComparisonTab(unittest.TestCase):
    """Test case for the ComparisonTab class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock models
        self.mock_local_file_model = MagicMock()
        self.mock_remote_file_model = MagicMock()
        self.mock_category_model = MagicMock()
        self.mock_download_model = MagicMock()
        
        # Set up the mock models to return data
        self.mock_local_file_model.get_all_files.return_value = [
            {
                "id": 1,
                "path": "/downloads/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 1,
                "hash": "abc123",
                "last_updated": 1609459200
            },
            {
                "id": 2,
                "path": "/downloads/file2.pdf",
                "name": "file2.pdf",
                "file_type": "pdf",
                "size": 2048,
                "category_id": 1,
                "hash": "def456",
                "last_updated": 1609459300
            }
        ]
        
        self.mock_remote_file_model.get_files_by_category.return_value = [
            {
                "id": 1,
                "site_id": 1,
                "url": "http://example.com/file1.pdf",
                "name": "file1.pdf",
                "file_type": "pdf",
                "size": 1024,
                "category_id": 1,
                "hash": "abc123",
                "last_updated": 1609459200
            },
            {
                "id": 2,
                "site_id": 1,
                "url": "http://example.com/file3.pdf",
                "name": "file3.pdf",
                "file_type": "pdf",
                "size": 3072,
                "category_id": 1,
                "hash": "ghi789",
                "last_updated": 1609459400
            }
        ]
        
        self.mock_category_model.get_all_categories.return_value = [
            {
                "id": 1,
                "name": "Category 1",
                "parent_id": None
            },
            {
                "id": 2,
                "name": "Category 2",
                "parent_id": None
            }
        ]
        
        # Create the comparison tab
        self.tab = ComparisonTab(
            self.mock_local_file_model,
            self.mock_remote_file_model,
            self.mock_category_model,
            self.mock_download_model
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Close the tab
        self.tab.close()
    
    def test_init(self):
        """Test the constructor."""
        # Check that the tab was created
        self.assertIsInstance(self.tab, QWidget)
        
        # Check that the models were saved
        self.assertEqual(self.tab.local_file_model, self.mock_local_file_model)
        self.assertEqual(self.tab.remote_file_model, self.mock_remote_file_model)
        self.assertEqual(self.tab.category_model, self.mock_category_model)
        self.assertEqual(self.tab.download_model, self.mock_download_model)
    
    def test_create_ui(self):
        """Test the create_ui method."""
        # Check that the category combo was created
        self.assertIsNotNone(self.tab.category_combo)
        
        # Check that the tables were created
        self.assertIsNotNone(self.tab.local_table)
        self.assertIsNotNone(self.tab.remote_table)
        self.assertIsNotNone(self.tab.missing_table)
        
        # Check that the buttons were created
        self.assertIsNotNone(self.tab.compare_button)
        self.assertIsNotNone(self.tab.queue_all_button)
    
    def test_refresh(self):
        """Test the refresh method."""
        # Call the refresh method
        self.tab.refresh()
        
        # Check that the category model was queried
        self.mock_category_model.get_all_categories.assert_called_once()
        
        # Check that the category combo was populated
        self.assertEqual(self.tab.category_combo.count(), 3)  # Including "All Categories"
        self.assertEqual(self.tab.category_combo.itemText(1), "Category 1")
        self.assertEqual(self.tab.category_combo.itemText(2), "Category 2")
    
    def test_compare_files(self):
        """Test the compare_files method."""
        # Mock the FileComparison class
        with patch('src.core.file_comparison.FileComparison') as mock_comparison_class:
            # Set up the mock comparison
            mock_comparison = MagicMock()
            mock_comparison_class.return_value = mock_comparison
            
            # Set up the comparison results
            mock_comparison.compare.return_value = {
                "matching": [
                    {
                        "local": {"name": "file1.pdf", "hash": "abc123"},
                        "remote": {"name": "file1.pdf", "hash": "abc123"}
                    }
                ],
                "missing": [
                    {"name": "file3.pdf", "hash": "ghi789"}
                ],
                "different": []
            }
            
            # Select a category
            self.tab.category_combo.setCurrentIndex(1)  # Category 1
            
            # Call the compare_files method
            self.tab.compare_files()
            
            # Check that the comparison was created and used
            mock_comparison_class.assert_called_once_with(
                self.mock_local_file_model,
                self.mock_remote_file_model
            )
            mock_comparison.compare.assert_called_once_with(category_id=1)
            
            # Check that the tables were populated
            self.assertEqual(self.tab.local_table.rowCount(), 1)  # Matching files
            self.assertEqual(self.tab.remote_table.rowCount(), 1)  # Matching files
            self.assertEqual(self.tab.missing_table.rowCount(), 1)  # Missing files
    
    def test_queue_all_missing(self):
        """Test the queue_all_missing method."""
        # Mock the FileComparison class
        with patch('src.core.file_comparison.FileComparison') as mock_comparison_class:
            # Set up the mock comparison
            mock_comparison = MagicMock()
            mock_comparison_class.return_value = mock_comparison
            
            # Set up the comparison results
            mock_comparison.compare.return_value = {
                "matching": [],
                "missing": [
                    {
                        "id": 2,
                        "site_id": 1,
                        "url": "http://example.com/file3.pdf",
                        "name": "file3.pdf",
                        "file_type": "pdf",
                        "size": 3072,
                        "category_id": 1,
                        "hash": "ghi789",
                        "last_updated": 1609459400
                    }
                ],
                "different": []
            }
            
            # Select a category
            self.tab.category_combo.setCurrentIndex(1)  # Category 1
            
            # Call the compare_files method to populate the tables
            self.tab.compare_files()
            
            # Call the queue_all_missing method
            self.tab.queue_all_missing()
            
            # Check that the download was added to the queue
            self.mock_download_model.add_to_queue.assert_called_once_with(
                url="http://example.com/file3.pdf",
                file_name="file3.pdf",
                file_type="pdf",
                category_id=1,
                priority=1,
                status="queued"
            )
    
    def test_queue_selected_missing(self):
        """Test the queue_selected_missing method."""
        # Mock the FileComparison class
        with patch('src.core.file_comparison.FileComparison') as mock_comparison_class:
            # Set up the mock comparison
            mock_comparison = MagicMock()
            mock_comparison_class.return_value = mock_comparison
            
            # Set up the comparison results
            mock_comparison.compare.return_value = {
                "matching": [],
                "missing": [
                    {
                        "id": 2,
                        "site_id": 1,
                        "url": "http://example.com/file3.pdf",
                        "name": "file3.pdf",
                        "file_type": "pdf",
                        "size": 3072,
                        "category_id": 1,
                        "hash": "ghi789",
                        "last_updated": 1609459400
                    }
                ],
                "different": []
            }
            
            # Select a category
            self.tab.category_combo.setCurrentIndex(1)  # Category 1
            
            # Call the compare_files method to populate the tables
            self.tab.compare_files()
            
            # Select a row in the missing table
            self.tab.missing_table.selectRow(0)
            
            # Call the queue_selected_missing method
            self.tab.queue_selected_missing()
            
            # Check that the download was added to the queue
            self.mock_download_model.add_to_queue.assert_called_once_with(
                url="http://example.com/file3.pdf",
                file_name="file3.pdf",
                file_type="pdf",
                category_id=1,
                priority=1,
                status="queued"
            )


if __name__ == "__main__":
    unittest.main()
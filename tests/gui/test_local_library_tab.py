import unittest
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication, QWidget
from src.gui.local_library_tab import LocalLibraryTab


# Create a QApplication instance for testing
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestLocalLibraryTab(unittest.TestCase):
    """Test case for the LocalLibraryTab class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock models
        self.mock_local_file_model = MagicMock()
        self.mock_category_model = MagicMock()
        self.mock_settings_model = MagicMock()
        
        # Set up the mock local file model to return files
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
                "category_id": 2,
                "hash": "def456",
                "last_updated": 1609459300
            }
        ]
        
        # Set up the mock category model to return categories
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
        
        self.mock_category_model.get_category.side_effect = lambda category_id: {
            1: {"id": 1, "name": "Category 1", "parent_id": None},
            2: {"id": 2, "name": "Category 2", "parent_id": None}
        }.get(category_id)
        
        # Set up the mock settings model to return settings
        self.mock_settings_model.get_setting.return_value = "/downloads"
        
        # Create the local library tab
        self.tab = LocalLibraryTab(
            self.mock_local_file_model,
            self.mock_category_model,
            self.mock_settings_model
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
        self.assertEqual(self.tab.category_model, self.mock_category_model)
        self.assertEqual(self.tab.settings_model, self.mock_settings_model)
    
    def test_create_ui(self):
        """Test the create_ui method."""
        # Check that the category tree was created
        self.assertIsNotNone(self.tab.category_tree)
        
        # Check that the file table was created
        self.assertIsNotNone(self.tab.file_table)
        
        # Check that the search box was created
        self.assertIsNotNone(self.tab.search_box)
        
        # Check that the scan button was created
        self.assertIsNotNone(self.tab.scan_button)
    
    def test_refresh(self):
        """Test the refresh method."""
        # Call the refresh method
        self.tab.refresh()
        
        # Check that the category model was queried
        self.mock_category_model.get_all_categories.assert_called_once()
        
        # Check that the category tree was populated
        self.assertEqual(self.tab.category_tree.topLevelItemCount(), 2)
        self.assertEqual(self.tab.category_tree.topLevelItem(0).text(0), "Category 1")
        self.assertEqual(self.tab.category_tree.topLevelItem(1).text(0), "Category 2")
    
    def test_category_selected(self):
        """Test the category_selected method."""
        # Refresh the tab to populate the category tree
        self.tab.refresh()
        
        # Select a category
        self.tab.category_tree.setCurrentItem(self.tab.category_tree.topLevelItem(0))
        
        # Call the category_selected method
        self.tab.category_selected()
        
        # Check that the local file model was queried
        self.mock_local_file_model.get_files_by_category.assert_called_once_with(1)
    
    def test_search_files(self):
        """Test the search_files method."""
        # Set up the search box
        self.tab.search_box.setText("file1")
        
        # Call the search_files method
        self.tab.search_files()
        
        # Check that the local file model was queried
        self.mock_local_file_model.search_files.assert_called_once_with("file1")
    
    def test_show_file_details(self):
        """Test the show_file_details method."""
        # Refresh the tab to populate the category tree
        self.tab.refresh()
        
        # Select a category
        self.tab.category_tree.setCurrentItem(self.tab.category_tree.topLevelItem(0))
        
        # Call the category_selected method to populate the file table
        self.tab.category_selected()
        
        # Select a file
        self.tab.file_table.selectRow(0)
        
        # Mock the QMessageBox.information method
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            # Call the show_file_details method
            self.tab.show_file_details()
            
            # Check that the message box was shown
            mock_info.assert_called_once()
    
    def test_scan_directory(self):
        """Test the scan_directory method."""
        # Mock the DirectoryScanner class
        with patch('src.core.directory_scanner.DirectoryScanner') as mock_scanner_class:
            # Set up the mock scanner
            mock_scanner = MagicMock()
            mock_scanner_class.return_value = mock_scanner
            mock_scanner.scan.return_value = [
                {"path": "/downloads/file1.pdf", "name": "file1.pdf"},
                {"path": "/downloads/file2.pdf", "name": "file2.pdf"}
            ]
            
            # Call the scan_directory method
            self.tab.scan_directory()
            
            # Check that the settings model was queried
            self.mock_settings_model.get_setting.assert_called_once_with(
                "download_dir",
                default="/downloads"
            )
            
            # Check that the scanner was created and used
            mock_scanner_class.assert_called_once_with(
                self.mock_local_file_model,
                self.mock_category_model
            )
            mock_scanner.scan.assert_called_once_with("/downloads")
            
            # Check that the file table was refreshed
            self.mock_local_file_model.get_all_files.assert_called()
    
    def test_open_file(self):
        """Test the open_file method."""
        # Refresh the tab to populate the category tree
        self.tab.refresh()
        
        # Select a category
        self.tab.category_tree.setCurrentItem(self.tab.category_tree.topLevelItem(0))
        
        # Call the category_selected method to populate the file table
        self.tab.category_selected()
        
        # Select a file
        self.tab.file_table.selectRow(0)
        
        # Mock the QDesktopServices.openUrl method
        with patch('PyQt5.QtGui.QDesktopServices.openUrl') as mock_open_url:
            # Call the open_file method
            self.tab.open_file()
            
            # Check that the file was opened
            mock_open_url.assert_called_once()
    
    def test_assign_category(self):
        """Test the assign_category method."""
        # Refresh the tab to populate the category tree
        self.tab.refresh()
        
        # Select a category
        self.tab.category_tree.setCurrentItem(self.tab.category_tree.topLevelItem(0))
        
        # Call the category_selected method to populate the file table
        self.tab.category_selected()
        
        # Select a file
        self.tab.file_table.selectRow(0)
        
        # Mock the QInputDialog.getItem method to return a category
        with patch('PyQt5.QtWidgets.QInputDialog.getItem') as mock_getItem:
            mock_getItem.return_value = ("Category 2", True)
            
            # Call the assign_category method
            self.tab.assign_category()
            
            # Check that the file's category was updated
            self.mock_local_file_model.update_category.assert_called_once_with(1, 2)
            
            # Check that the file table was refreshed
            self.mock_local_file_model.get_files_by_category.assert_called()


if __name__ == "__main__":
    unittest.main()
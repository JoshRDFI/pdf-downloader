import unittest
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication, QWidget
from src.gui.library_tab import LibraryTab


# Create a QApplication instance for testing
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestLibraryTab(unittest.TestCase):
    """Test case for the LibraryTab class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock models
        self.mock_remote_file_model = MagicMock()
        self.mock_category_model = MagicMock()
        self.mock_site_model = MagicMock()
        
        # Set up the mock remote file model to return files
        self.mock_remote_file_model.get_all_files.return_value = [
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
                "url": "http://example.com/file2.pdf",
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
        
        # Set up the mock site model to return sites
        self.mock_site_model.get_site.return_value = {
            "id": 1,
            "name": "Site 1",
            "url": "http://example.com",
            "scraper_type": "generic",
            "username": "user",
            "password": "pass",
            "last_scan": 1609459200
        }
        
        # Create the library tab
        self.tab = LibraryTab(
            self.mock_remote_file_model,
            self.mock_category_model,
            self.mock_site_model
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
        self.assertEqual(self.tab.remote_file_model, self.mock_remote_file_model)
        self.assertEqual(self.tab.category_model, self.mock_category_model)
        self.assertEqual(self.tab.site_model, self.mock_site_model)
    
    def test_create_ui(self):
        """Test the create_ui method."""
        # Check that the category tree was created
        self.assertIsNotNone(self.tab.category_tree)
        
        # Check that the file table was created
        self.assertIsNotNone(self.tab.file_table)
        
        # Check that the search box was created
        self.assertIsNotNone(self.tab.search_box)
    
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
        
        # Check that the remote file model was queried
        self.mock_remote_file_model.get_files_by_category.assert_called_once_with(1)
    
    def test_search_files(self):
        """Test the search_files method."""
        # Set up the search box
        self.tab.search_box.setText("file1")
        
        # Call the search_files method
        self.tab.search_files()
        
        # Check that the remote file model was queried
        self.mock_remote_file_model.search_files.assert_called_once_with("file1")
    
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
    
    def test_add_category(self):
        """Test the add_category method."""
        # Refresh the tab to populate the category tree
        self.tab.refresh()
        
        # Mock the QInputDialog.getText method to return a category name
        with patch('PyQt5.QtWidgets.QInputDialog.getText') as mock_getText:
            mock_getText.return_value = ("New Category", True)
            
            # Call the add_category method
            self.tab.add_category()
            
            # Check that the category was added
            self.mock_category_model.add_category.assert_called_once_with(
                name="New Category",
                parent_id=None
            )
            
            # Check that the category tree was refreshed
            self.assertEqual(self.mock_category_model.get_all_categories.call_count, 2)
    
    def test_add_subcategory(self):
        """Test the add_subcategory method."""
        # Refresh the tab to populate the category tree
        self.tab.refresh()
        
        # Select a category
        self.tab.category_tree.setCurrentItem(self.tab.category_tree.topLevelItem(0))
        
        # Mock the QInputDialog.getText method to return a category name
        with patch('PyQt5.QtWidgets.QInputDialog.getText') as mock_getText:
            mock_getText.return_value = ("New Subcategory", True)
            
            # Call the add_subcategory method
            self.tab.add_subcategory()
            
            # Check that the subcategory was added
            self.mock_category_model.add_category.assert_called_once_with(
                name="New Subcategory",
                parent_id=1
            )
            
            # Check that the category tree was refreshed
            self.assertEqual(self.mock_category_model.get_all_categories.call_count, 2)
    
    def test_edit_category(self):
        """Test the edit_category method."""
        # Refresh the tab to populate the category tree
        self.tab.refresh()
        
        # Select a category
        self.tab.category_tree.setCurrentItem(self.tab.category_tree.topLevelItem(0))
        
        # Mock the QInputDialog.getText method to return a new category name
        with patch('PyQt5.QtWidgets.QInputDialog.getText') as mock_getText:
            mock_getText.return_value = ("Updated Category", True)
            
            # Call the edit_category method
            self.tab.edit_category()
            
            # Check that the category was updated
            self.mock_category_model.update_category.assert_called_once_with(
                category_id=1,
                name="Updated Category"
            )
            
            # Check that the category tree was refreshed
            self.assertEqual(self.mock_category_model.get_all_categories.call_count, 2)
    
    def test_delete_category(self):
        """Test the delete_category method."""
        # Refresh the tab to populate the category tree
        self.tab.refresh()
        
        # Select a category
        self.tab.category_tree.setCurrentItem(self.tab.category_tree.topLevelItem(0))
        
        # Mock the QMessageBox.question method to return Yes
        with patch('PyQt5.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.Yes
            
            # Call the delete_category method
            self.tab.delete_category()
            
            # Check that the category was deleted
            self.mock_category_model.delete_category.assert_called_once_with(1)
            
            # Check that the category tree was refreshed
            self.assertEqual(self.mock_category_model.get_all_categories.call_count, 2)


if __name__ == "__main__":
    unittest.main()
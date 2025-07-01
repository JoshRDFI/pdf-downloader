import unittest
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication, QWidget
from src.gui.site_management import SiteManagementTab


# Create a QApplication instance for testing
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestSiteManagementTab(unittest.TestCase):
    """Test case for the SiteManagementTab class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock models
        self.mock_site_model = MagicMock()
        self.mock_remote_file_model = MagicMock()
        
        # Set up the mock site model to return sites
        self.mock_site_model.get_all_sites.return_value = [
            {
                "id": 1,
                "name": "Site 1",
                "url": "http://example1.com",
                "scraper_type": "generic",
                "username": "user1",
                "password": "pass1",
                "last_scan": 1609459200
            },
            {
                "id": 2,
                "name": "Site 2",
                "url": "http://example2.com",
                "scraper_type": "generic",
                "username": "user2",
                "password": "pass2",
                "last_scan": 1609459300
            }
        ]
        
        # Create the site management tab
        self.tab = SiteManagementTab(self.mock_site_model, self.mock_remote_file_model)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Close the tab
        self.tab.close()
    
    def test_init(self):
        """Test the constructor."""
        # Check that the tab was created
        self.assertIsInstance(self.tab, QWidget)
        
        # Check that the models were saved
        self.assertEqual(self.tab.site_model, self.mock_site_model)
        self.assertEqual(self.tab.remote_file_model, self.mock_remote_file_model)
    
    def test_create_ui(self):
        """Test the create_ui method."""
        # Check that the site list was created
        self.assertIsNotNone(self.tab.site_list)
        
        # Check that the form was created
        self.assertIsNotNone(self.tab.form_layout)
        
        # Check that the buttons were created
        self.assertIsNotNone(self.tab.add_button)
        self.assertIsNotNone(self.tab.edit_button)
        self.assertIsNotNone(self.tab.delete_button)
        self.assertIsNotNone(self.tab.scan_button)
    
    def test_refresh(self):
        """Test the refresh method."""
        # Call the refresh method
        self.tab.refresh()
        
        # Check that the site model was queried
        self.mock_site_model.get_all_sites.assert_called_once()
        
        # Check that the site list was populated
        self.assertEqual(self.tab.site_list.count(), 2)
        self.assertEqual(self.tab.site_list.item(0).text(), "Site 1")
        self.assertEqual(self.tab.site_list.item(1).text(), "Site 2")
    
    def test_site_selected(self):
        """Test the site_selected method."""
        # Select a site
        self.tab.site_list.setCurrentRow(0)
        
        # Call the site_selected method
        self.tab.site_selected()
        
        # Check that the form was populated
        self.assertEqual(self.tab.name_edit.text(), "Site 1")
        self.assertEqual(self.tab.url_edit.text(), "http://example1.com")
        self.assertEqual(self.tab.scraper_type_combo.currentText(), "generic")
        self.assertEqual(self.tab.username_edit.text(), "user1")
        self.assertEqual(self.tab.password_edit.text(), "pass1")
    
    def test_add_site(self):
        """Test the add_site method."""
        # Set up the form for a new site
        self.tab.name_edit.setText("New Site")
        self.tab.url_edit.setText("http://example.com")
        self.tab.scraper_type_combo.setCurrentText("generic")
        self.tab.username_edit.setText("user")
        self.tab.password_edit.setText("pass")
        
        # Set up the mock site model to return a site ID
        self.mock_site_model.add_site.return_value = 3
        
        # Call the add_site method
        self.tab.add_site()
        
        # Check that the site was added
        self.mock_site_model.add_site.assert_called_once_with(
            name="New Site",
            url="http://example.com",
            scraper_type="generic",
            username="user",
            password="pass"
        )
        
        # Check that the site list was refreshed
        self.mock_site_model.get_all_sites.assert_called()
    
    def test_edit_site(self):
        """Test the edit_site method."""
        # Select a site
        self.tab.site_list.setCurrentRow(0)
        self.tab.site_selected()
        
        # Change the site details
        self.tab.name_edit.setText("Updated Site")
        self.tab.url_edit.setText("http://updated.com")
        
        # Call the edit_site method
        self.tab.edit_site()
        
        # Check that the site was updated
        self.mock_site_model.update_site.assert_called_once_with(
            site_id=1,
            name="Updated Site",
            url="http://updated.com",
            scraper_type="generic",
            username="user1",
            password="pass1"
        )
        
        # Check that the site list was refreshed
        self.mock_site_model.get_all_sites.assert_called()
    
    def test_delete_site(self):
        """Test the delete_site method."""
        # Select a site
        self.tab.site_list.setCurrentRow(0)
        
        # Mock the QMessageBox.question method to return Yes
        with patch('PyQt5.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.Yes
            
            # Call the delete_site method
            self.tab.delete_site()
            
            # Check that the site was deleted
            self.mock_site_model.delete_site.assert_called_once_with(1)
            
            # Check that the site list was refreshed
            self.mock_site_model.get_all_sites.assert_called()
    
    def test_scan_site(self):
        """Test the scan_site method."""
        # Select a site
        self.tab.site_list.setCurrentRow(0)
        
        # Mock the SiteScanner class
        with patch('src.core.site_scanner.SiteScanner') as mock_scanner_class:
            # Set up the mock scanner
            mock_scanner = MagicMock()
            mock_scanner_class.return_value = mock_scanner
            mock_scanner.scan.return_value = [
                {"url": "http://example1.com/file1.pdf", "name": "file1.pdf"},
                {"url": "http://example1.com/file2.pdf", "name": "file2.pdf"}
            ]
            
            # Call the scan_site method
            self.tab.scan_site()
            
            # Check that the scanner was created and used
            mock_scanner_class.assert_called_once_with(
                self.mock_site_model,
                self.mock_remote_file_model
            )
            mock_scanner.scan.assert_called_once_with(1)
            
            # Check that the last scan time was updated
            self.mock_site_model.update_last_scan.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
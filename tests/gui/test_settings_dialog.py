import unittest
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication, QDialog
from src.gui.settings_dialog import SettingsDialog


# Create a QApplication instance for testing
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestSettingsDialog(unittest.TestCase):
    """Test case for the SettingsDialog class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock settings model
        self.mock_settings_model = MagicMock()
        
        # Set up the mock settings model to return settings
        self.mock_settings_model.get_all_settings.return_value = {
            "download_dir": "/downloads",
            "max_downloads": 5,
            "auto_validate": True,
            "network_timeout": 30
        }
        
        # Create the settings dialog
        self.dialog = SettingsDialog(self.mock_settings_model)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Close the dialog
        self.dialog.close()
    
    def test_init(self):
        """Test the constructor."""
        # Check that the dialog was created
        self.assertIsInstance(self.dialog, QDialog)
        
        # Check that the dialog has a title
        self.assertTrue(self.dialog.windowTitle())
        
        # Check that the settings model was saved
        self.assertEqual(self.dialog.settings_model, self.mock_settings_model)
        
        # Check that the settings were loaded
        self.mock_settings_model.get_all_settings.assert_called_once()
    
    def test_create_ui(self):
        """Test the create_ui method."""
        # Check that the form layout was created
        self.assertIsNotNone(self.dialog.form_layout)
        
        # Check that the button box was created
        self.assertIsNotNone(self.dialog.button_box)
    
    def test_load_settings(self):
        """Test the load_settings method."""
        # Check that the settings were loaded into the form
        self.assertEqual(self.dialog.download_dir_edit.text(), "/downloads")
        self.assertEqual(self.dialog.max_downloads_spin.value(), 5)
        self.assertEqual(self.dialog.auto_validate_check.isChecked(), True)
        self.assertEqual(self.dialog.network_timeout_spin.value(), 30)
    
    def test_save_settings(self):
        """Test the save_settings method."""
        # Change the settings in the form
        self.dialog.download_dir_edit.setText("/new_downloads")
        self.dialog.max_downloads_spin.setValue(10)
        self.dialog.auto_validate_check.setChecked(False)
        self.dialog.network_timeout_spin.setValue(60)
        
        # Call the save_settings method
        self.dialog.save_settings()
        
        # Check that the settings were saved
        self.mock_settings_model.set_setting.assert_any_call("download_dir", "/new_downloads")
        self.mock_settings_model.set_setting.assert_any_call("max_downloads", 10)
        self.mock_settings_model.set_setting.assert_any_call("auto_validate", False)
        self.mock_settings_model.set_setting.assert_any_call("network_timeout", 60)
    
    def test_browse_download_dir(self):
        """Test the browse_download_dir method."""
        # Mock the QFileDialog.getExistingDirectory method
        with patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory') as mock_get_dir:
            # Set up the mock to return a directory
            mock_get_dir.return_value = "/selected_dir"
            
            # Call the browse_download_dir method
            self.dialog.browse_download_dir()
            
            # Check that the directory was set in the form
            self.assertEqual(self.dialog.download_dir_edit.text(), "/selected_dir")
    
    def test_accept(self):
        """Test the accept method."""
        # Mock the save_settings method
        self.dialog.save_settings = MagicMock()
        
        # Call the accept method
        self.dialog.accept()
        
        # Check that the settings were saved
        self.dialog.save_settings.assert_called_once()


if __name__ == "__main__":
    unittest.main()
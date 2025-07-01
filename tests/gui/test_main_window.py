import unittest
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication, QMainWindow
from src.gui.main_window import MainWindow


# Create a QApplication instance for testing
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestMainWindow(unittest.TestCase):
    """Test case for the MainWindow class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the database and models
        self.mock_db = MagicMock()
        self.mock_site_model = MagicMock()
        self.mock_category_model = MagicMock()
        self.mock_remote_file_model = MagicMock()
        self.mock_local_file_model = MagicMock()
        self.mock_download_model = MagicMock()
        self.mock_settings_model = MagicMock()
        
        # Mock the database connection
        with patch('src.db.database.Database') as mock_db_class:
            mock_db_class.return_value = self.mock_db
            
            # Mock the models
            with patch('src.db.site_model.SiteModel') as mock_site_model_class, \
                 patch('src.db.category_model.CategoryModel') as mock_category_model_class, \
                 patch('src.db.remote_file_model.RemoteFileModel') as mock_remote_file_model_class, \
                 patch('src.db.local_file_model.LocalFileModel') as mock_local_file_model_class, \
                 patch('src.db.download_model.DownloadModel') as mock_download_model_class, \
                 patch('src.db.settings_model.SettingsModel') as mock_settings_model_class:
                
                mock_site_model_class.return_value = self.mock_site_model
                mock_category_model_class.return_value = self.mock_category_model
                mock_remote_file_model_class.return_value = self.mock_remote_file_model
                mock_local_file_model_class.return_value = self.mock_local_file_model
                mock_download_model_class.return_value = self.mock_download_model
                mock_settings_model_class.return_value = self.mock_settings_model
                
                # Create the main window
                self.window = MainWindow()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Close the main window
        self.window.close()
    
    def test_init(self):
        """Test the constructor."""
        # Check that the window was created
        self.assertIsInstance(self.window, QMainWindow)
        
        # Check that the window has a title
        self.assertTrue(self.window.windowTitle())
        
        # Check that the tabs were created
        self.assertIsNotNone(self.window.tabs)
        
        # Check that the database was connected
        self.mock_db.connect.assert_called_once()
    
    def test_create_tabs(self):
        """Test the create_tabs method."""
        # Check that the tabs were created
        self.assertIsNotNone(self.window.site_management_tab)
        self.assertIsNotNone(self.window.local_library_tab)
        self.assertIsNotNone(self.window.library_tab)
        self.assertIsNotNone(self.window.comparison_tab)
        self.assertIsNotNone(self.window.download_queue_tab)
        self.assertIsNotNone(self.window.download_history_tab)
    
    def test_create_menu(self):
        """Test the create_menu method."""
        # Check that the menu bar was created
        self.assertIsNotNone(self.window.menuBar())
        
        # Check that the file menu was created
        file_menu = self.window.menuBar().findChild(QMenu, "fileMenu")
        self.assertIsNotNone(file_menu)
        
        # Check that the settings menu was created
        settings_menu = self.window.menuBar().findChild(QMenu, "settingsMenu")
        self.assertIsNotNone(settings_menu)
        
        # Check that the help menu was created
        help_menu = self.window.menuBar().findChild(QMenu, "helpMenu")
        self.assertIsNotNone(help_menu)
    
    def test_create_status_bar(self):
        """Test the create_status_bar method."""
        # Check that the status bar was created
        self.assertIsNotNone(self.window.statusBar())
    
    def test_open_settings(self):
        """Test the open_settings method."""
        # Mock the SettingsDialog class
        with patch('src.gui.settings_dialog.SettingsDialog') as mock_settings_dialog_class:
            # Set up the mock dialog
            mock_dialog = MagicMock()
            mock_settings_dialog_class.return_value = mock_dialog
            
            # Call the open_settings method
            self.window.open_settings()
            
            # Check that the dialog was created and executed
            mock_settings_dialog_class.assert_called_once_with(
                self.mock_settings_model,
                self.window
            )
            mock_dialog.exec_.assert_called_once()
    
    def test_refresh_all_tabs(self):
        """Test the refresh_all_tabs method."""
        # Mock the tab refresh methods
        self.window.site_management_tab.refresh = MagicMock()
        self.window.local_library_tab.refresh = MagicMock()
        self.window.library_tab.refresh = MagicMock()
        self.window.comparison_tab.refresh = MagicMock()
        self.window.download_queue_tab.refresh = MagicMock()
        self.window.download_history_tab.refresh = MagicMock()
        
        # Call the refresh_all_tabs method
        self.window.refresh_all_tabs()
        
        # Check that all tab refresh methods were called
        self.window.site_management_tab.refresh.assert_called_once()
        self.window.local_library_tab.refresh.assert_called_once()
        self.window.library_tab.refresh.assert_called_once()
        self.window.comparison_tab.refresh.assert_called_once()
        self.window.download_queue_tab.refresh.assert_called_once()
        self.window.download_history_tab.refresh.assert_called_once()
    
    def test_closeEvent(self):
        """Test the closeEvent method."""
        # Create a mock close event
        mock_event = MagicMock()
        
        # Call the closeEvent method
        self.window.closeEvent(mock_event)
        
        # Check that the database was closed
        self.mock_db.close.assert_called_once()
        
        # Check that the event was accepted
        mock_event.accept.assert_called_once()


if __name__ == "__main__":
    unittest.main()
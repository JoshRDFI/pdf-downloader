import unittest
from unittest.mock import patch, MagicMock

from src.db.settings_model import SettingsModel
from src.db.database import Database


class TestSettingsModel(unittest.TestCase):
    """Test case for the SettingsModel class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock database
        self.mock_db = MagicMock(spec=Database)
        
        # Create the settings model with the mock database
        self.settings_model = SettingsModel(self.mock_db)
    
    def test_get_setting(self):
        """Test getting a setting."""
        # Set up the mock database to return a setting
        self.mock_db.execute_query.return_value = [{
            "id": 1,
            "key": "download_dir",
            "value": "/downloads",
            "type": "string"
        }]
        
        # Get a setting
        setting = self.settings_model.get_setting("download_dir")
        
        # Check the result
        self.assertEqual(setting, "/downloads")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM settings WHERE key" in args[0])
        self.assertEqual(kwargs["params"][0], "download_dir")
    
    def test_get_setting_not_found(self):
        """Test getting a setting that doesn't exist."""
        # Set up the mock database to return no settings
        self.mock_db.execute_query.return_value = []
        
        # Get a setting that doesn't exist
        setting = self.settings_model.get_setting("nonexistent", default="default_value")
        
        # Check the result
        self.assertEqual(setting, "default_value")
    
    def test_get_setting_with_type(self):
        """Test getting a setting with type conversion."""
        # Set up the mock database to return settings for different types
        def mock_execute_query(query, params=None, fetch=False):
            if params[0] == "int_setting":
                return [{
                    "id": 1,
                    "key": "int_setting",
                    "value": "42",
                    "type": "int"
                }]
            elif params[0] == "float_setting":
                return [{
                    "id": 2,
                    "key": "float_setting",
                    "value": "3.14",
                    "type": "float"
                }]
            elif params[0] == "bool_setting":
                return [{
                    "id": 3,
                    "key": "bool_setting",
                    "value": "true",
                    "type": "bool"
                }]
            else:
                return []
        
        self.mock_db.execute_query.side_effect = mock_execute_query
        
        # Get settings with different types
        int_setting = self.settings_model.get_setting("int_setting")
        float_setting = self.settings_model.get_setting("float_setting")
        bool_setting = self.settings_model.get_setting("bool_setting")
        
        # Check the results
        self.assertEqual(int_setting, 42)
        self.assertEqual(float_setting, 3.14)
        self.assertEqual(bool_setting, True)
    
    def test_set_setting(self):
        """Test setting a setting."""
        # Set up the mock database to return no settings (setting doesn't exist)
        self.mock_db.execute_query.return_value = []
        
        # Set a setting
        self.settings_model.set_setting("download_dir", "/downloads")
        
        # Check that the database was called correctly
        self.assertEqual(self.mock_db.execute_query.call_count, 2)  # get + insert
        
        # Check the insert call
        args, kwargs = self.mock_db.execute_query.call_args_list[1]
        self.assertTrue("INSERT INTO settings" in args[0])
        self.assertEqual(kwargs["params"][0], "download_dir")
        self.assertEqual(kwargs["params"][1], "/downloads")
        self.assertEqual(kwargs["params"][2], "string")
    
    def test_set_setting_update(self):
        """Test updating an existing setting."""
        # Set up the mock database to return a setting (setting exists)
        self.mock_db.execute_query.return_value = [{
            "id": 1,
            "key": "download_dir",
            "value": "/old_downloads",
            "type": "string"
        }]
        
        # Update a setting
        self.settings_model.set_setting("download_dir", "/new_downloads")
        
        # Check that the database was called correctly
        self.assertEqual(self.mock_db.execute_query.call_count, 2)  # get + update
        
        # Check the update call
        args, kwargs = self.mock_db.execute_query.call_args_list[1]
        self.assertTrue("UPDATE settings" in args[0])
        self.assertEqual(kwargs["params"][0], "/new_downloads")
        self.assertEqual(kwargs["params"][1], "string")
        self.assertEqual(kwargs["params"][2], "download_dir")
    
    def test_set_setting_with_type(self):
        """Test setting a setting with a specific type."""
        # Set up the mock database to return no settings (setting doesn't exist)
        self.mock_db.execute_query.return_value = []
        
        # Set settings with different types
        self.settings_model.set_setting("int_setting", 42)
        self.settings_model.set_setting("float_setting", 3.14)
        self.settings_model.set_setting("bool_setting", True)
        
        # Check the insert calls
        args, kwargs = self.mock_db.execute_query.call_args_list[1]
        self.assertEqual(kwargs["params"][1], "42")
        self.assertEqual(kwargs["params"][2], "int")
        
        args, kwargs = self.mock_db.execute_query.call_args_list[3]
        self.assertEqual(kwargs["params"][1], "3.14")
        self.assertEqual(kwargs["params"][2], "float")
        
        args, kwargs = self.mock_db.execute_query.call_args_list[5]
        self.assertEqual(kwargs["params"][1], "true")
        self.assertEqual(kwargs["params"][2], "bool")
    
    def test_delete_setting(self):
        """Test deleting a setting."""
        # Delete a setting
        self.settings_model.delete_setting("download_dir")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("DELETE FROM settings" in args[0])
        self.assertEqual(kwargs["params"][0], "download_dir")
    
    def test_get_all_settings(self):
        """Test getting all settings."""
        # Set up the mock database to return settings
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "key": "download_dir",
                "value": "/downloads",
                "type": "string"
            },
            {
                "id": 2,
                "key": "max_downloads",
                "value": "5",
                "type": "int"
            },
            {
                "id": 3,
                "key": "auto_validate",
                "value": "true",
                "type": "bool"
            }
        ]
        
        # Get all settings
        settings = self.settings_model.get_all_settings()
        
        # Check the result
        self.assertEqual(len(settings), 3)
        self.assertEqual(settings["download_dir"], "/downloads")
        self.assertEqual(settings["max_downloads"], 5)
        self.assertEqual(settings["auto_validate"], True)
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM settings" in args[0])
    
    def test_get_settings_by_prefix(self):
        """Test getting settings by prefix."""
        # Set up the mock database to return settings
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "key": "download_dir",
                "value": "/downloads",
                "type": "string"
            },
            {
                "id": 2,
                "key": "download_max",
                "value": "5",
                "type": "int"
            }
        ]
        
        # Get settings by prefix
        settings = self.settings_model.get_settings_by_prefix("download")
        
        # Check the result
        self.assertEqual(len(settings), 2)
        self.assertEqual(settings["download_dir"], "/downloads")
        self.assertEqual(settings["download_max"], 5)
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM settings WHERE key LIKE" in args[0])
        self.assertEqual(kwargs["params"][0], "download%")


if __name__ == "__main__":
    unittest.main()
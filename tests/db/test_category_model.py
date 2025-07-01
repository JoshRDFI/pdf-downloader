import unittest
from unittest.mock import patch, MagicMock

from src.db.category_model import CategoryModel
from src.db.database import Database


class TestCategoryModel(unittest.TestCase):
    """Test case for the CategoryModel class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock database
        self.mock_db = MagicMock(spec=Database)
        
        # Create the category model with the mock database
        self.category_model = CategoryModel(self.mock_db)
    
    def test_add_category(self):
        """Test adding a category."""
        # Set up the mock database to return a category ID
        self.mock_db.execute_query.return_value = [{"id": 1}]
        
        # Add a category
        category_id = self.category_model.add_category(
            name="Test Category",
            parent_id=None
        )
        
        # Check the result
        self.assertEqual(category_id, 1)
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("INSERT INTO categories" in args[0])
        self.assertEqual(kwargs["params"][0], "Test Category")
        self.assertIsNone(kwargs["params"][1])  # parent_id
    
    def test_add_subcategory(self):
        """Test adding a subcategory."""
        # Set up the mock database to return a category ID
        self.mock_db.execute_query.return_value = [{"id": 2}]
        
        # Add a subcategory
        category_id = self.category_model.add_category(
            name="Test Subcategory",
            parent_id=1
        )
        
        # Check the result
        self.assertEqual(category_id, 2)
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("INSERT INTO categories" in args[0])
        self.assertEqual(kwargs["params"][0], "Test Subcategory")
        self.assertEqual(kwargs["params"][1], 1)  # parent_id
    
    def test_update_category(self):
        """Test updating a category."""
        # Update a category
        self.category_model.update_category(
            category_id=1,
            name="Updated Category",
            parent_id=2
        )
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("UPDATE categories" in args[0])
        self.assertEqual(kwargs["params"][0], "Updated Category")
        self.assertEqual(kwargs["params"][1], 2)  # parent_id
        self.assertEqual(kwargs["params"][2], 1)  # category_id
    
    def test_delete_category(self):
        """Test deleting a category."""
        # Delete a category
        self.category_model.delete_category(1)
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("DELETE FROM categories" in args[0])
        self.assertEqual(kwargs["params"][0], 1)
    
    def test_get_category(self):
        """Test getting a category."""
        # Set up the mock database to return a category
        self.mock_db.execute_query.return_value = [{
            "id": 1,
            "name": "Test Category",
            "parent_id": None
        }]
        
        # Get a category
        category = self.category_model.get_category(1)
        
        # Check the result
        self.assertEqual(category["id"], 1)
        self.assertEqual(category["name"], "Test Category")
        self.assertIsNone(category["parent_id"])
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM categories" in args[0])
        self.assertEqual(kwargs["params"][0], 1)
    
    def test_get_category_not_found(self):
        """Test getting a category that doesn't exist."""
        # Set up the mock database to return no categories
        self.mock_db.execute_query.return_value = []
        
        # Get a category that doesn't exist
        category = self.category_model.get_category(999)
        
        # Check the result
        self.assertIsNone(category)
    
    def test_get_all_categories(self):
        """Test getting all categories."""
        # Set up the mock database to return categories
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "name": "Category 1",
                "parent_id": None
            },
            {
                "id": 2,
                "name": "Category 2",
                "parent_id": None
            },
            {
                "id": 3,
                "name": "Subcategory 1",
                "parent_id": 1
            }
        ]
        
        # Get all categories
        categories = self.category_model.get_all_categories()
        
        # Check the result
        self.assertEqual(len(categories), 3)
        self.assertEqual(categories[0]["name"], "Category 1")
        self.assertEqual(categories[1]["name"], "Category 2")
        self.assertEqual(categories[2]["name"], "Subcategory 1")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM categories" in args[0])
    
    def test_get_subcategories(self):
        """Test getting subcategories."""
        # Set up the mock database to return subcategories
        self.mock_db.execute_query.return_value = [
            {
                "id": 3,
                "name": "Subcategory 1",
                "parent_id": 1
            },
            {
                "id": 4,
                "name": "Subcategory 2",
                "parent_id": 1
            }
        ]
        
        # Get subcategories
        subcategories = self.category_model.get_subcategories(1)
        
        # Check the result
        self.assertEqual(len(subcategories), 2)
        self.assertEqual(subcategories[0]["name"], "Subcategory 1")
        self.assertEqual(subcategories[1]["name"], "Subcategory 2")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM categories WHERE parent_id" in args[0])
        self.assertEqual(kwargs["params"][0], 1)
    
    def test_get_category_by_name(self):
        """Test getting a category by name."""
        # Set up the mock database to return a category
        self.mock_db.execute_query.return_value = [{
            "id": 1,
            "name": "Test Category",
            "parent_id": None
        }]
        
        # Get a category by name
        category = self.category_model.get_category_by_name("Test Category")
        
        # Check the result
        self.assertEqual(category["id"], 1)
        self.assertEqual(category["name"], "Test Category")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM categories WHERE name" in args[0])
        self.assertEqual(kwargs["params"][0], "Test Category")
    
    def test_get_category_by_name_not_found(self):
        """Test getting a category by name that doesn't exist."""
        # Set up the mock database to return no categories
        self.mock_db.execute_query.return_value = []
        
        # Get a category by name that doesn't exist
        category = self.category_model.get_category_by_name("Nonexistent")
        
        # Check the result
        self.assertIsNone(category)
    
    def test_get_category_path(self):
        """Test getting the path of a category."""
        # Set up the mock database to return categories for different queries
        def mock_execute_query(query, params=None, fetch=False):
            if "WHERE id = ?" in query and params[0] == 3:
                return [{
                    "id": 3,
                    "name": "Subcategory",
                    "parent_id": 2
                }]
            elif "WHERE id = ?" in query and params[0] == 2:
                return [{
                    "id": 2,
                    "name": "Category",
                    "parent_id": None
                }]
            else:
                return []
        
        self.mock_db.execute_query.side_effect = mock_execute_query
        
        # Get the path of a category
        path = self.category_model.get_category_path(3)
        
        # Check the result
        self.assertEqual(path, "Category/Subcategory")
    
    def test_get_category_path_root(self):
        """Test getting the path of a root category."""
        # Set up the mock database to return a root category
        self.mock_db.execute_query.return_value = [{
            "id": 1,
            "name": "Root Category",
            "parent_id": None
        }]
        
        # Get the path of a root category
        path = self.category_model.get_category_path(1)
        
        # Check the result
        self.assertEqual(path, "Root Category")


if __name__ == "__main__":
    unittest.main()
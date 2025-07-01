import os
import unittest
import tempfile
from unittest.mock import patch, MagicMock

from src.db.database import Database


class TestDatabase(unittest.TestCase):
    """Test case for the Database class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for the test database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        
        # Patch the config to use the test database
        self.config_patcher = patch('src.db.database.config')
        self.mock_config = self.config_patcher.start()
        self.mock_config.get.side_effect = lambda section, key, default=None: {
            ("database", "path"): self.db_path
        }.get((section, key), default)
        
        # Create the database
        self.db = Database()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Stop the config patcher
        self.config_patcher.stop()
        
        # Close the database connection
        if hasattr(self.db, "conn") and self.db.conn is not None:
            self.db.conn.close()
        
        # Remove the temporary directory
        self.temp_dir.cleanup()
    
    def test_connect(self):
        """Test connecting to the database."""
        # Connect to the database
        self.db.connect()
        
        # Check that the connection was established
        self.assertIsNotNone(self.db.conn)
        
        # Check that the database file was created
        self.assertTrue(os.path.exists(self.db_path))
    
    def test_close(self):
        """Test closing the database connection."""
        # Connect to the database
        self.db.connect()
        
        # Close the connection
        self.db.close()
        
        # Check that the connection was closed
        self.assertIsNone(self.db.conn)
    
    def test_execute_query(self):
        """Test executing a query."""
        # Connect to the database
        self.db.connect()
        
        # Execute a query to create a table
        self.db.execute_query(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )
        
        # Execute a query to insert data
        self.db.execute_query(
            "INSERT INTO test (name) VALUES (?)",
            ("Test Name",)
        )
        
        # Execute a query to select data
        result = self.db.execute_query(
            "SELECT * FROM test",
            fetch=True
        )
        
        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Test Name")
    
    def test_execute_query_with_error(self):
        """Test executing a query that causes an error."""
        # Connect to the database
        self.db.connect()
        
        # Execute a query with invalid SQL
        with self.assertRaises(Exception):
            self.db.execute_query("INVALID SQL")
    
    def test_transaction(self):
        """Test executing queries in a transaction."""
        # Connect to the database
        self.db.connect()
        
        # Create a test table
        self.db.execute_query(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )
        
        # Execute queries in a transaction
        with self.db.transaction():
            self.db.execute_query(
                "INSERT INTO test (name) VALUES (?)",
                ("Name 1",)
            )
            self.db.execute_query(
                "INSERT INTO test (name) VALUES (?)",
                ("Name 2",)
            )
        
        # Check that both inserts were committed
        result = self.db.execute_query(
            "SELECT * FROM test ORDER BY id",
            fetch=True
        )
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Name 1")
        self.assertEqual(result[1]["name"], "Name 2")
    
    def test_transaction_rollback(self):
        """Test rolling back a transaction."""
        # Connect to the database
        self.db.connect()
        
        # Create a test table
        self.db.execute_query(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )
        
        # Insert initial data
        self.db.execute_query(
            "INSERT INTO test (name) VALUES (?)",
            ("Initial",)
        )
        
        # Try to execute queries in a transaction that will fail
        try:
            with self.db.transaction():
                self.db.execute_query(
                    "INSERT INTO test (name) VALUES (?)",
                    ("Name 1",)
                )
                # This will cause an error
                self.db.execute_query("INVALID SQL")
        except Exception:
            pass
        
        # Check that the transaction was rolled back
        result = self.db.execute_query(
            "SELECT * FROM test",
            fetch=True
        )
        
        self.assertEqual(len(result), 1)  # Only the initial insert should be there
        self.assertEqual(result[0]["name"], "Initial")
    
    def test_initialize_schema(self):
        """Test initializing the database schema."""
        # Mock the schema file
        schema_content = """
        CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO test (name) VALUES ('Schema Test');
        """
        
        # Patch the open function to return the mock schema
        with patch('builtins.open', unittest.mock.mock_open(read_data=schema_content)):
            # Connect to the database and initialize the schema
            self.db.connect()
            self.db.initialize_schema()
            
            # Check that the schema was applied
            result = self.db.execute_query(
                "SELECT * FROM test",
                fetch=True
            )
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["name"], "Schema Test")


if __name__ == "__main__":
    unittest.main()
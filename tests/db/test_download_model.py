import unittest
from unittest.mock import patch, MagicMock

from src.db.download_model import DownloadModel
from src.db.database import Database


class TestDownloadModel(unittest.TestCase):
    """Test case for the DownloadModel class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock database
        self.mock_db = MagicMock(spec=Database)
        
        # Create the download model with the mock database
        self.download_model = DownloadModel(self.mock_db)
    
    def test_add_to_queue(self):
        """Test adding a download to the queue."""
        # Set up the mock database to return a download ID
        self.mock_db.execute_query.return_value = [{"id": 1}]
        
        # Add a download to the queue
        download_id = self.download_model.add_to_queue(
            url="http://example.com/test.pdf",
            file_name="test.pdf",
            file_type="pdf",
            category_id=2,
            priority=1,
            status="queued"
        )
        
        # Check the result
        self.assertEqual(download_id, 1)
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("INSERT INTO downloads" in args[0])
        self.assertEqual(kwargs["params"][0], "http://example.com/test.pdf")
        self.assertEqual(kwargs["params"][1], "test.pdf")
        self.assertEqual(kwargs["params"][2], "pdf")
        self.assertEqual(kwargs["params"][3], 2)  # category_id
        self.assertEqual(kwargs["params"][4], 1)  # priority
        self.assertEqual(kwargs["params"][5], "queued")  # status
    
    def test_get_queue(self):
        """Test getting the download queue."""
        # Set up the mock database to return downloads
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "url": "http://example.com/file1.pdf",
                "file_name": "file1.pdf",
                "file_type": "pdf",
                "category_id": 1,
                "priority": 1,
                "status": "queued",
                "created_at": 1609459200,
                "started_at": None,
                "completed_at": None
            },
            {
                "id": 2,
                "url": "http://example.com/file2.pdf",
                "file_name": "file2.pdf",
                "file_type": "pdf",
                "category_id": 1,
                "priority": 2,
                "status": "queued",
                "created_at": 1609459300,
                "started_at": None,
                "completed_at": None
            }
        ]
        
        # Get the download queue
        queue = self.download_model.get_queue()
        
        # Check the result
        self.assertEqual(len(queue), 2)
        self.assertEqual(queue[0]["file_name"], "file1.pdf")
        self.assertEqual(queue[1]["file_name"], "file2.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM downloads WHERE status IN" in args[0])
    
    def test_get_queue_by_status(self):
        """Test getting the download queue filtered by status."""
        # Set up the mock database to return downloads
        self.mock_db.execute_query.return_value = [
            {
                "id": 1,
                "url": "http://example.com/file1.pdf",
                "file_name": "file1.pdf",
                "file_type": "pdf",
                "category_id": 1,
                "priority": 1,
                "status": "downloading",
                "created_at": 1609459200,
                "started_at": 1609459300,
                "completed_at": None
            }
        ]
        
        # Get the download queue filtered by status
        queue = self.download_model.get_queue_by_status("downloading")
        
        # Check the result
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["status"], "downloading")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM downloads WHERE status = ?" in args[0])
        self.assertEqual(kwargs["params"][0], "downloading")
    
    def test_get_download(self):
        """Test getting a specific download."""
        # Set up the mock database to return a download
        self.mock_db.execute_query.return_value = [{
            "id": 1,
            "url": "http://example.com/file1.pdf",
            "file_name": "file1.pdf",
            "file_type": "pdf",
            "category_id": 1,
            "priority": 1,
            "status": "queued",
            "created_at": 1609459200,
            "started_at": None,
            "completed_at": None
        }]
        
        # Get a specific download
        download = self.download_model.get_download(1)
        
        # Check the result
        self.assertEqual(download["id"], 1)
        self.assertEqual(download["file_name"], "file1.pdf")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM downloads WHERE id = ?" in args[0])
        self.assertEqual(kwargs["params"][0], 1)
    
    def test_get_download_not_found(self):
        """Test getting a download that doesn't exist."""
        # Set up the mock database to return no downloads
        self.mock_db.execute_query.return_value = []
        
        # Get a download that doesn't exist
        download = self.download_model.get_download(999)
        
        # Check the result
        self.assertIsNone(download)
    
    def test_update_status(self):
        """Test updating the status of a download."""
        # Update the status of a download
        self.download_model.update_status(1, "downloading")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("UPDATE downloads SET status = ?" in args[0])
        self.assertEqual(kwargs["params"][0], "downloading")
        self.assertEqual(kwargs["params"][2], 1)  # download_id
    
    def test_update_status_completed(self):
        """Test updating the status of a download to completed."""
        # Update the status of a download to completed
        self.download_model.update_status(1, "completed")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("UPDATE downloads SET status = ?" in args[0])
        self.assertEqual(kwargs["params"][0], "completed")
        self.assertEqual(kwargs["params"][2], 1)  # download_id
    
    def test_remove_from_queue(self):
        """Test removing a download from the queue."""
        # Remove a download from the queue
        self.download_model.remove_from_queue(1)
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("DELETE FROM downloads WHERE id = ?" in args[0])
        self.assertEqual(kwargs["params"][0], 1)
    
    def test_get_history(self):
        """Test getting the download history."""
        # Set up the mock database to return downloads
        self.mock_db.execute_query.return_value = [
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
        
        # Get the download history
        history = self.download_model.get_history()
        
        # Check the result
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["status"], "completed")
        self.assertEqual(history[1]["status"], "failed")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM downloads WHERE status IN" in args[0])
    
    def test_get_history_by_status(self):
        """Test getting the download history filtered by status."""
        # Set up the mock database to return downloads
        self.mock_db.execute_query.return_value = [
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
            }
        ]
        
        # Get the download history filtered by status
        history = self.download_model.get_history_by_status("completed")
        
        # Check the result
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["status"], "completed")
        
        # Check that the database was called correctly
        self.mock_db.execute_query.assert_called_once()
        args, kwargs = self.mock_db.execute_query.call_args
        self.assertTrue("SELECT * FROM downloads WHERE status = ?" in args[0])
        self.assertEqual(kwargs["params"][0], "completed")


if __name__ == "__main__":
    unittest.main()
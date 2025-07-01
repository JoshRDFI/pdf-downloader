"""Download model for the PDF Downloader application.

This module contains the DownloadModel class for managing download records.
"""

import logging
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.db.database import Database


logger = logging.getLogger(__name__)


class DownloadModel:
    """Model for managing download records in the database.
    
    This class provides methods for creating, retrieving, updating, and deleting
    download records in the database.
    """
    
    def __init__(self):
        """Initialize the download model."""
        self.db = Database()
    
    def create_download(self, remote_file_id: int) -> int:
        """Create a new download record.
        
        Args:
            remote_file_id: ID of the remote file to download
            
        Returns:
            ID of the created download record
        """
        try:
            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert the download record
            query = """
            INSERT INTO downloads (remote_file_id, status, created_at)
            VALUES (?, ?, ?)
            """
            params = (remote_file_id, "pending", timestamp)
            
            # Execute the query
            cursor = self.db.execute_query(query, params)
            download_id = cursor.lastrowid
            
            logger.info(f"Created download record {download_id} for remote file {remote_file_id}")
            return download_id
        except sqlite3.Error as e:
            logger.error(f"Error creating download record: {e}")
            raise
    
    def update_download_started(self, download_id: int) -> bool:
        """Update a download record when the download starts.
        
        Args:
            download_id: ID of the download record
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Update the download record
            query = """
            UPDATE downloads
            SET status = ?, started_at = ?
            WHERE id = ?
            """
            params = ("in_progress", timestamp, download_id)
            
            # Execute the query
            self.db.execute_query(query, params)
            
            logger.info(f"Updated download record {download_id} as started")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating download record: {e}")
            return False
    
    def update_download_completed(self, download_id: int, local_file_id: int) -> bool:
        """Update a download record when the download completes.
        
        Args:
            download_id: ID of the download record
            local_file_id: ID of the local file
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Update the download record
            query = """
            UPDATE downloads
            SET status = ?, completed_at = ?, local_file_id = ?
            WHERE id = ?
            """
            params = ("completed", timestamp, local_file_id, download_id)
            
            # Execute the query
            self.db.execute_query(query, params)
            
            logger.info(f"Updated download record {download_id} as completed")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating download record: {e}")
            return False
    
    def update_download_failed(self, download_id: int, error_message: str) -> bool:
        """Update a download record when the download fails.
        
        Args:
            download_id: ID of the download record
            error_message: Error message
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Update the download record
            query = """
            UPDATE downloads
            SET status = ?, completed_at = ?, error_message = ?
            WHERE id = ?
            """
            params = ("failed", timestamp, error_message, download_id)
            
            # Execute the query
            self.db.execute_query(query, params)
            
            logger.info(f"Updated download record {download_id} as failed")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating download record: {e}")
            return False
    
    def get_download_by_id(self, download_id: int) -> Optional[Dict[str, Any]]:
        """Get a download record by ID.
        
        Args:
            download_id: ID of the download record
            
        Returns:
            Download record as a dictionary, or None if not found
        """
        try:
            # Get the download record
            query = "SELECT * FROM downloads WHERE id = ?"
            params = (download_id,)
            
            # Execute the query
            result = self.db.fetch_one(query, params)
            
            if result:
                # Get the file name from the remote file
                from src.db.remote_file_model import RemoteFileModel
                remote_file_model = RemoteFileModel()
                remote_file = remote_file_model.get_file_by_id(result["remote_file_id"])
                
                if remote_file:
                    result["file_name"] = remote_file["name"]
                else:
                    result["file_name"] = "Unknown"
            
            return result
        except sqlite3.Error as e:
            logger.error(f"Error getting download record: {e}")
            return None
    
    def get_download_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get the download history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of download records as dictionaries
        """
        try:
            # Get the download records
            query = """
            SELECT * FROM downloads
            ORDER BY created_at DESC
            LIMIT ?
            """
            params = (limit,)
            
            # Execute the query
            results = self.db.fetch_all(query, params)
            
            # Get the file names from the remote files
            from src.db.remote_file_model import RemoteFileModel
            remote_file_model = RemoteFileModel()
            
            for result in results:
                remote_file = remote_file_model.get_file_by_id(result["remote_file_id"])
                
                if remote_file:
                    result["file_name"] = remote_file["name"]
                else:
                    result["file_name"] = "Unknown"
            
            return results
        except sqlite3.Error as e:
            logger.error(f"Error getting download history: {e}")
            return []
    
    def get_pending_downloads(self) -> List[Dict[str, Any]]:
        """Get pending download records.
        
        Returns:
            List of pending download records as dictionaries
        """
        try:
            # Get the download records
            query = "SELECT * FROM downloads WHERE status = 'pending' ORDER BY created_at ASC"
            
            # Execute the query
            results = self.db.fetch_all(query)
            
            return results
        except sqlite3.Error as e:
            logger.error(f"Error getting pending downloads: {e}")
            return []
    
    def get_in_progress_downloads(self) -> List[Dict[str, Any]]:
        """Get in-progress download records.
        
        Returns:
            List of in-progress download records as dictionaries
        """
        try:
            # Get the download records
            query = "SELECT * FROM downloads WHERE status = 'in_progress' ORDER BY started_at ASC"
            
            # Execute the query
            results = self.db.fetch_all(query)
            
            return results
        except sqlite3.Error as e:
            logger.error(f"Error getting in-progress downloads: {e}")
            return []
    
    def delete_download(self, download_id: int) -> bool:
        """Delete a download record.
        
        Args:
            download_id: ID of the download record
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        try:
            # Delete the download record
            query = "DELETE FROM downloads WHERE id = ?"
            params = (download_id,)
            
            # Execute the query
            self.db.execute_query(query, params)
            
            logger.info(f"Deleted download record {download_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error deleting download record: {e}")
            return False
    
    def count_downloads_by_status(self, status: str) -> int:
        """Count download records by status.
        
        Args:
            status: Status to count (pending, in_progress, completed, failed)
            
        Returns:
            Number of download records with the specified status
        """
        try:
            # Count the download records
            query = "SELECT COUNT(*) FROM downloads WHERE status = ?"
            params = (status,)
            
            # Execute the query
            result = self.db.fetch_one(query, params)
            
            return result["COUNT(*)"] if result else 0
        except sqlite3.Error as e:
            logger.error(f"Error counting downloads by status: {e}")
            return 0
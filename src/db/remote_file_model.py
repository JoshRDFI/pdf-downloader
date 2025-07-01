"""Database models for remote files in the PDF Downloader application.

This module provides database models and operations for managing remote files.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.db.database import DatabaseManager


class RemoteFileModel:
    """Model for managing remote file data in the database.
    
    This class provides methods for CRUD operations on remote file data.
    """
    
    def __init__(self):
        """Initialize the remote file model with a database connection."""
        self.db_manager = DatabaseManager()
    
    def get_files_by_site(self, site_id: int) -> List[Dict[str, Any]]:
        """Get all remote files for a site from the database.
        
        Args:
            site_id: ID of the site to get files for
            
        Returns:
            List of dictionaries containing file information
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, site_id, category_id, name, url, size, file_type, last_checked, created_at, updated_at
            FROM remote_files
            WHERE site_id = ?
            ORDER BY name
        """, (site_id,))
        
        # Convert row objects to dictionaries
        files = [dict(row) for row in cursor.fetchall()]
        
        return files
    
    def get_files_by_category(self, category_id: int) -> List[Dict[str, Any]]:
        """Get all remote files for a category from the database.
        
        Args:
            category_id: ID of the category to get files for
            
        Returns:
            List of dictionaries containing file information
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, site_id, category_id, name, url, size, file_type, last_checked, created_at, updated_at
            FROM remote_files
            WHERE category_id = ?
            ORDER BY name
        """, (category_id,))
        
        # Convert row objects to dictionaries
        files = [dict(row) for row in cursor.fetchall()]
        
        return files
    
    def get_file_by_id(self, file_id: int) -> Optional[Dict[str, Any]]:
        """Get a remote file by its ID.
        
        Args:
            file_id: ID of the file to get
            
        Returns:
            Dictionary containing file information, or None if not found
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, site_id, category_id, name, url, size, file_type, last_checked, created_at, updated_at
            FROM remote_files
            WHERE id = ?
        """, (file_id,))
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return dict(row)
    
    def add_file(self, site_id: int, name: str, url: str, category_id: Optional[int] = None,
                size: Optional[int] = None, file_type: Optional[str] = None) -> int:
        """Add a new remote file to the database.
        
        Args:
            site_id: ID of the site the file belongs to
            name: Name of the file
            url: URL of the file
            category_id: ID of the category the file belongs to (optional)
            size: Size of the file in bytes (optional)
            file_type: Type of the file (e.g., 'pdf', 'epub') (optional)
            
        Returns:
            ID of the newly added file
            
        Raises:
            sqlite3.IntegrityError: If a file with the same site_id and URL already exists
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO remote_files (site_id, category_id, name, url, size, file_type, last_checked)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (site_id, category_id, name, url, size, file_type, now))
        
        conn.commit()
        return cursor.lastrowid
    
    def update_file(self, file_id: int, name: str, url: str, category_id: Optional[int] = None,
                   size: Optional[int] = None, file_type: Optional[str] = None) -> bool:
        """Update an existing remote file in the database.
        
        Args:
            file_id: ID of the file to update
            name: New name for the file
            url: New URL for the file
            category_id: New category ID for the file (optional)
            size: New size for the file in bytes (optional)
            file_type: New type for the file (optional)
            
        Returns:
            True if the file was updated, False if the file was not found
            
        Raises:
            sqlite3.IntegrityError: If another file with the same site_id and URL already exists
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE remote_files
            SET name = ?, url = ?, category_id = ?, size = ?, file_type = ?, last_checked = ?
            WHERE id = ?
        """, (name, url, category_id, size, file_type, now, file_id))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_file(self, file_id: int) -> bool:
        """Delete a remote file from the database.
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            True if the file was deleted, False if the file was not found
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM remote_files
            WHERE id = ?
        """, (file_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_files_by_site(self, site_id: int) -> int:
        """Delete all remote files for a site from the database.
        
        Args:
            site_id: ID of the site to delete files for
            
        Returns:
            Number of files deleted
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM remote_files
            WHERE site_id = ?
        """, (site_id,))
        
        conn.commit()
        return cursor.rowcount
    
    def delete_files_by_category(self, category_id: int) -> int:
        """Delete all remote files for a category from the database.
        
        Args:
            category_id: ID of the category to delete files for
            
        Returns:
            Number of files deleted
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM remote_files
            WHERE category_id = ?
        """, (category_id,))
        
        conn.commit()
        return cursor.rowcount
    
    def add_or_update_files(self, site_id: int, files: List[Dict[str, Any]]) -> Dict[str, int]:
        """Add or update multiple remote files for a site.
        
        This method first deletes all existing files for the site,
        then adds the new files.
        
        Args:
            site_id: ID of the site the files belong to
            files: List of dictionaries containing file information
            
        Returns:
            Dictionary with counts of added and updated files
        """
        # Delete existing files for the site
        deleted = self.delete_files_by_site(site_id)
        
        # Add the new files
        added = 0
        for file in files:
            try:
                self.add_file(
                    site_id=site_id,
                    name=file["name"],
                    url=file["url"],
                    category_id=file.get("category_id"),
                    size=file.get("size"),
                    file_type=file.get("file_type")
                )
                added += 1
            except Exception as e:
                # Log the error but continue with other files
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error adding file {file.get('name')}: {e}")
        
        return {
            "deleted": deleted,
            "added": added
        }
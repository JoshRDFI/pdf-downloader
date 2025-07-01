"""Database models for local files in the PDF Downloader application.

This module provides database models and operations for managing local files.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from src.db.database import DatabaseManager


class LocalFileModel:
    """Model for managing local file data in the database.
    
    This class provides methods for CRUD operations on local file data.
    """
    
    def __init__(self):
        """Initialize the local file model with a database connection."""
        self.db_manager = DatabaseManager()
    
    def get_all_files(self) -> List[Dict[str, Any]]:
        """Get all local files from the database.
        
        Returns:
            List of dictionaries containing file information
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, remote_file_id, path, size, file_type, last_checked, created_at, updated_at
            FROM local_files
            ORDER BY path
        """)
        
        # Convert row objects to dictionaries
        files = [dict(row) for row in cursor.fetchall()]
        
        return files
    
    def get_file_by_id(self, file_id: int) -> Optional[Dict[str, Any]]:
        """Get a local file by its ID.
        
        Args:
            file_id: ID of the file to get
            
        Returns:
            Dictionary containing file information, or None if not found
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, remote_file_id, path, size, file_type, last_checked, created_at, updated_at
            FROM local_files
            WHERE id = ?
        """, (file_id,))
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return dict(row)
    
    def get_file_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        """Get a local file by its path.
        
        Args:
            path: Path of the file to get
            
        Returns:
            Dictionary containing file information, or None if not found
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, remote_file_id, path, size, file_type, last_checked, created_at, updated_at
            FROM local_files
            WHERE path = ?
        """, (path,))
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return dict(row)
    
    def add_file(self, path: str, size: int, file_type: str, 
                remote_file_id: Optional[int] = None) -> int:
        """Add a new local file to the database.
        
        Args:
            path: Path of the file
            size: Size of the file in bytes
            file_type: Type of the file (e.g., 'pdf', 'epub')
            remote_file_id: ID of the corresponding remote file (optional)
            
        Returns:
            ID of the newly added file
            
        Raises:
            sqlite3.IntegrityError: If a file with the same path already exists
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO local_files (remote_file_id, path, size, file_type, last_checked)
            VALUES (?, ?, ?, ?, ?)
        """, (remote_file_id, path, size, file_type, now))
        
        conn.commit()
        return cursor.lastrowid
    
    def update_file(self, file_id: int, path: str, size: int, file_type: str,
                   remote_file_id: Optional[int] = None) -> bool:
        """Update an existing local file in the database.
        
        Args:
            file_id: ID of the file to update
            path: New path for the file
            size: New size for the file in bytes
            file_type: New type for the file
            remote_file_id: New ID of the corresponding remote file (optional)
            
        Returns:
            True if the file was updated, False if the file was not found
            
        Raises:
            sqlite3.IntegrityError: If another file with the same path already exists
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE local_files
            SET remote_file_id = ?, path = ?, size = ?, file_type = ?, last_checked = ?
            WHERE id = ?
        """, (remote_file_id, path, size, file_type, now, file_id))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_file(self, file_id: int) -> bool:
        """Delete a local file from the database.
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            True if the file was deleted, False if the file was not found
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM local_files
            WHERE id = ?
        """, (file_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_all_files(self) -> int:
        """Delete all local files from the database.
        
        Returns:
            Number of files deleted
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM local_files
        """)
        
        conn.commit()
        return cursor.rowcount
    
    def get_files_by_type(self, file_type: str) -> List[Dict[str, Any]]:
        """Get all local files of a specific type.
        
        Args:
            file_type: Type of files to get (e.g., 'pdf', 'epub')
            
        Returns:
            List of dictionaries containing file information
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, remote_file_id, path, size, file_type, last_checked, created_at, updated_at
            FROM local_files
            WHERE file_type = ?
            ORDER BY path
        """, (file_type,))
        
        # Convert row objects to dictionaries
        files = [dict(row) for row in cursor.fetchall()]
        
        return files
    
    def get_file_count(self) -> int:
        """Get the total number of local files in the database.
        
        Returns:
            Number of files
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM local_files
        """)
        
        return cursor.fetchone()[0]
    
    def get_file_count_by_type(self) -> Dict[str, int]:
        """Get the number of local files by type.
        
        Returns:
            Dictionary mapping file types to counts
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT file_type, COUNT(*) as count
            FROM local_files
            GROUP BY file_type
        """)
        
        # Convert rows to a dictionary
        counts = {row["file_type"]: row["count"] for row in cursor.fetchall()}
        
        return counts
    
    def add_or_update_file(self, path: str, size: int, file_type: str,
                          remote_file_id: Optional[int] = None) -> int:
        """Add a new local file or update an existing one.
        
        Args:
            path: Path of the file
            size: Size of the file in bytes
            file_type: Type of the file (e.g., 'pdf', 'epub')
            remote_file_id: ID of the corresponding remote file (optional)
            
        Returns:
            ID of the added or updated file
        """
        # Check if the file already exists
        existing_file = self.get_file_by_path(path)
        
        if existing_file is not None:
            # Update the existing file
            self.update_file(
                file_id=existing_file["id"],
                path=path,
                size=size,
                file_type=file_type,
                remote_file_id=remote_file_id
            )
            return existing_file["id"]
        else:
            # Add a new file
            return self.add_file(
                path=path,
                size=size,
                file_type=file_type,
                remote_file_id=remote_file_id
            )

    def get_file_by_remote_id(self, remote_file_id: int) -> Optional[Dict[str, Any]]:
        """Get a local file by its remote file ID.

        Args:
            remote_file_id: ID of the remote file

        Returns:
            Dictionary containing file information, or None if not found
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, remote_file_id, path, size, file_type, last_checked, created_at, updated_at
            FROM local_files
            WHERE remote_file_id = ?
        """, (remote_file_id,))

        row = cursor.fetchone()
        if row is None:
            return None

        return dict(row)

    def get_files_without_remote_id(self) -> List[Dict[str, Any]]:
        """Get all local files that are not linked to a remote file.

        Returns:
            List of dictionaries containing file information
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, remote_file_id, path, size, file_type, last_checked, created_at, updated_at
            FROM local_files
            WHERE remote_file_id IS NULL
            ORDER BY path
        """)

        # Convert row objects to dictionaries
        files = [dict(row) for row in cursor.fetchall()]

        return files
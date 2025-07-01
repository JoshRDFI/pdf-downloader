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
    
    def get_all_files(self) -> List[Dict[str, Any]]:
        """Get all remote files from the database.
        
        Returns:
            List of dictionaries containing file information
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, site_id, url, name, size, file_type, category, last_checked, created_at, updated_at
            FROM remote_files
            ORDER BY name
        """)
        
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
            SELECT id, site_id, url, name, size, file_type, category, last_checked, created_at, updated_at
            FROM remote_files
            WHERE id = ?
        """, (file_id,))
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return dict(row)
    
    def get_file_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Get a remote file by its URL.
        
        Args:
            url: URL of the file to get
            
        Returns:
            Dictionary containing file information, or None if not found
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, site_id, url, name, size, file_type, category, last_checked, created_at, updated_at
            FROM remote_files
            WHERE url = ?
        """, (url,))
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return dict(row)
    
    def get_files_by_site(self, site_id: int) -> List[Dict[str, Any]]:
        """Get all remote files for a specific site.
        
        Args:
            site_id: ID of the site to get files for
            
        Returns:
            List of dictionaries containing file information
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, site_id, url, name, size, file_type, category, last_checked, created_at, updated_at
            FROM remote_files
            WHERE site_id = ?
            ORDER BY name
        """, (site_id,))
        
        # Convert row objects to dictionaries
        files = [dict(row) for row in cursor.fetchall()]
        
        return files
    
    def add_file(self, site_id: int, url: str, name: str, size: int, file_type: str,
                category: str = "") -> int:
        """Add a new remote file to the database.
        
        Args:
            site_id: ID of the site the file belongs to
            url: URL of the file
            name: Name of the file
            size: Size of the file in bytes
            file_type: Type of the file (e.g., 'pdf', 'epub')
            category: Category of the file (optional)
            
        Returns:
            ID of the newly added file
            
        Raises:
            sqlite3.IntegrityError: If a file with the same URL already exists
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO remote_files (site_id, url, name, size, file_type, category, last_checked)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (site_id, url, name, size, file_type, category, now))
        
        conn.commit()
        return cursor.lastrowid
    
    def update_file(self, file_id: int, site_id: int, url: str, name: str, size: int,
                   file_type: str, category: str = "") -> bool:
        """Update an existing remote file in the database.
        
        Args:
            file_id: ID of the file to update
            site_id: New site ID for the file
            url: New URL for the file
            name: New name for the file
            size: New size for the file in bytes
            file_type: New type for the file
            category: New category for the file (optional)
            
        Returns:
            True if the file was updated, False if the file was not found
            
        Raises:
            sqlite3.IntegrityError: If another file with the same URL already exists
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE remote_files
            SET site_id = ?, url = ?, name = ?, size = ?, file_type = ?, category = ?, last_checked = ?
            WHERE id = ?
        """, (site_id, url, name, size, file_type, category, now, file_id))
        
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
        """Delete all remote files for a specific site.
        
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
    
    def get_file_count(self) -> int:
        """Get the total number of remote files in the database.
        
        Returns:
            Number of files
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM remote_files
        """)
        
        return cursor.fetchone()[0]
    
    def get_file_count_by_site(self, site_id: int) -> int:
        """Get the number of remote files for a specific site.
        
        Args:
            site_id: ID of the site to get the count for
            
        Returns:
            Number of files
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM remote_files
            WHERE site_id = ?
        """, (site_id,))
        
        return cursor.fetchone()[0]
    
    def get_file_count_by_type(self) -> Dict[str, int]:
        """Get the number of remote files by type.
        
        Returns:
            Dictionary mapping file types to counts
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT file_type, COUNT(*) as count
            FROM remote_files
            GROUP BY file_type
        """)
        
        # Convert rows to a dictionary
        counts = {row["file_type"]: row["count"] for row in cursor.fetchall()}
        
        return counts
    
    def add_or_update_file(self, site_id: int, url: str, name: str, size: int,
                          file_type: str, category: str = "") -> int:
        """Add a new remote file or update an existing one.
        
        Args:
            site_id: ID of the site the file belongs to
            url: URL of the file
            name: Name of the file
            size: Size of the file in bytes
            file_type: Type of the file (e.g., 'pdf', 'epub')
            category: Category of the file (optional)
            
        Returns:
            ID of the added or updated file
        """
        # Check if the file already exists
        existing_file = self.get_file_by_url(url)
        
        if existing_file is not None:
            # Update the existing file
            self.update_file(
                file_id=existing_file["id"],
                site_id=site_id,
                url=url,
                name=name,
                size=size,
                file_type=file_type,
                category=category
            )
            return existing_file["id"]
        else:
            # Add a new file
            return self.add_file(
                site_id=site_id,
                url=url,
                name=name,
                size=size,
                file_type=file_type,
                category=category
            )
    
    def get_all_sites(self) -> List[Dict[str, Any]]:
        """Get all sites from the database.
        
        Returns:
            List of dictionaries containing site information
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, url, scraper_module, last_scanned, created_at, updated_at
            FROM sites
            ORDER BY name
        """)
        
        # Convert row objects to dictionaries
        sites = [dict(row) for row in cursor.fetchall()]
        
        return sites
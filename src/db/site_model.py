"""Database models for sites in the PDF Downloader application.

This module provides database models and operations for managing sites.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.db.database import DatabaseManager


class SiteModel:
    """Model for managing site data in the database.
    
    This class provides methods for CRUD operations on site data.
    """
    
    def __init__(self):
        """Initialize the site model with a database connection."""
        self.db_manager = DatabaseManager()
    
    def get_all_sites(self) -> List[Dict[str, Any]]:
        """Get all sites from the database.
        
        Returns:
            List of dictionaries containing site information
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, url, scraper_type, last_scan_date, created_at, updated_at
            FROM sites
            ORDER BY name
        """)
        
        # Convert row objects to dictionaries
        sites = [dict(row) for row in cursor.fetchall()]
        
        return sites
    
    def get_site_by_id(self, site_id: int) -> Optional[Dict[str, Any]]:
        """Get a site by its ID.
        
        Args:
            site_id: ID of the site to get
            
        Returns:
            Dictionary containing site information, or None if not found
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, url, scraper_type, last_scan_date, created_at, updated_at
            FROM sites
            WHERE id = ?
        """, (site_id,))
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return dict(row)
    
    def add_site(self, name: str, url: str, scraper_type: str) -> int:
        """Add a new site to the database.
        
        Args:
            name: Name of the site
            url: URL of the site
            scraper_type: Type of scraper to use for the site
            
        Returns:
            ID of the newly added site
            
        Raises:
            sqlite3.IntegrityError: If a site with the same URL already exists
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sites (name, url, scraper_type)
            VALUES (?, ?, ?)
        """, (name, url, scraper_type))
        
        conn.commit()
        return cursor.lastrowid
    
    def update_site(self, site_id: int, name: str, url: str, scraper_type: str) -> bool:
        """Update an existing site in the database.
        
        Args:
            site_id: ID of the site to update
            name: New name for the site
            url: New URL for the site
            scraper_type: New scraper type for the site
            
        Returns:
            True if the site was updated, False if the site was not found
            
        Raises:
            sqlite3.IntegrityError: If another site with the same URL already exists
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sites
            SET name = ?, url = ?, scraper_type = ?
            WHERE id = ?
        """, (name, url, scraper_type, site_id))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_site(self, site_id: int) -> bool:
        """Delete a site from the database.
        
        Args:
            site_id: ID of the site to delete
            
        Returns:
            True if the site was deleted, False if the site was not found
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM sites
            WHERE id = ?
        """, (site_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def update_last_scan_date(self, site_id: int, scan_date: Optional[datetime] = None) -> bool:
        """Update the last scan date for a site.
        
        Args:
            site_id: ID of the site to update
            scan_date: Date of the scan (defaults to current time if None)
            
        Returns:
            True if the site was updated, False if the site was not found
        """
        if scan_date is None:
            scan_date = datetime.now()
        
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sites
            SET last_scan_date = ?
            WHERE id = ?
        """, (scan_date.isoformat(), site_id))
        
        conn.commit()
        return cursor.rowcount > 0
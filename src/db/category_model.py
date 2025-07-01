"""Database models for categories in the PDF Downloader application.

This module provides database models and operations for managing categories.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.db.database import DatabaseManager


class CategoryModel:
    """Model for managing category data in the database.
    
    This class provides methods for CRUD operations on category data.
    """
    
    def __init__(self):
        """Initialize the category model with a database connection."""
        self.db_manager = DatabaseManager()
    
    def get_categories_by_site(self, site_id: int) -> List[Dict[str, Any]]:
        """Get all categories for a site from the database.
        
        Args:
            site_id: ID of the site to get categories for
            
        Returns:
            List of dictionaries containing category information
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, site_id, name, url, parent_id, created_at, updated_at
            FROM categories
            WHERE site_id = ?
            ORDER BY name
        """, (site_id,))
        
        # Convert row objects to dictionaries
        categories = [dict(row) for row in cursor.fetchall()]
        
        return categories
    
    def get_category_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        """Get a category by its ID.
        
        Args:
            category_id: ID of the category to get
            
        Returns:
            Dictionary containing category information, or None if not found
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, site_id, name, url, parent_id, created_at, updated_at
            FROM categories
            WHERE id = ?
        """, (category_id,))
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return dict(row)
    
    def add_category(self, site_id: int, name: str, url: Optional[str] = None, 
                    parent_id: Optional[int] = None) -> int:
        """Add a new category to the database.
        
        Args:
            site_id: ID of the site the category belongs to
            name: Name of the category
            url: URL of the category (optional)
            parent_id: ID of the parent category (optional)
            
        Returns:
            ID of the newly added category
            
        Raises:
            sqlite3.IntegrityError: If a category with the same site_id and URL already exists
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO categories (site_id, name, url, parent_id)
            VALUES (?, ?, ?, ?)
        """, (site_id, name, url, parent_id))
        
        conn.commit()
        return cursor.lastrowid
    
    def update_category(self, category_id: int, name: str, url: Optional[str] = None,
                       parent_id: Optional[int] = None) -> bool:
        """Update an existing category in the database.
        
        Args:
            category_id: ID of the category to update
            name: New name for the category
            url: New URL for the category (optional)
            parent_id: New parent ID for the category (optional)
            
        Returns:
            True if the category was updated, False if the category was not found
            
        Raises:
            sqlite3.IntegrityError: If another category with the same site_id and URL already exists
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE categories
            SET name = ?, url = ?, parent_id = ?
            WHERE id = ?
        """, (name, url, parent_id, category_id))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_category(self, category_id: int) -> bool:
        """Delete a category from the database.
        
        Args:
            category_id: ID of the category to delete
            
        Returns:
            True if the category was deleted, False if the category was not found
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM categories
            WHERE id = ?
        """, (category_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_categories_by_site(self, site_id: int) -> int:
        """Delete all categories for a site from the database.
        
        Args:
            site_id: ID of the site to delete categories for
            
        Returns:
            Number of categories deleted
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM categories
            WHERE site_id = ?
        """, (site_id,))
        
        conn.commit()
        return cursor.rowcount
    
    def add_or_update_categories(self, site_id: int, categories: List[Dict[str, Any]]) -> Dict[str, int]:
        """Add or update multiple categories for a site.
        
        This method first deletes all existing categories for the site,
        then adds the new categories.
        
        Args:
            site_id: ID of the site the categories belong to
            categories: List of dictionaries containing category information
            
        Returns:
            Dictionary with counts of added and updated categories
        """
        # Delete existing categories for the site
        deleted = self.delete_categories_by_site(site_id)
        
        # Add the new categories
        added = 0
        for category in categories:
            try:
                self.add_category(
                    site_id=site_id,
                    name=category["name"],
                    url=category.get("url"),
                    parent_id=category.get("parent_id")
                )
                added += 1
            except Exception as e:
                # Log the error but continue with other categories
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error adding category {category.get('name')}: {e}")
        
        return {
            "deleted": deleted,
            "added": added
        }
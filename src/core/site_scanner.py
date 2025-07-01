"""Site scanner implementation for the PDF Downloader application.

This module provides functionality for scanning sites and extracting file information.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.db.site_model import SiteModel
from src.db.category_model import CategoryModel
from src.db.remote_file_model import RemoteFileModel
from src.scrapers.registry import ScraperRegistry


logger = logging.getLogger(__name__)


class SiteScanner:
    """Scanner for extracting file information from sites.
    
    This class handles the scanning of sites using the appropriate scraper,
    and updates the database with the extracted information.
    """
    
    def __init__(self):
        """Initialize the site scanner."""
        self.site_model = SiteModel()
        self.category_model = CategoryModel()
        self.remote_file_model = RemoteFileModel()
        self.scraper_registry = ScraperRegistry()
    
    def scan_site(self, site_id: int) -> Dict[str, Any]:
        """Scan a site for available files and categories.
        
        Args:
            site_id: ID of the site to scan
            
        Returns:
            Dictionary containing scan results
        """
        result = {
            "success": False,
            "site_id": site_id,
            "categories": [],
            "files": [],
            "error": None,
            "stats": {
                "categories_added": 0,
                "files_added": 0
            }
        }
        
        try:
            # Get the site information
            site = self.site_model.get_site_by_id(site_id)
            if site is None:
                result["error"] = f"Site with ID {site_id} not found"
                return result
            
            # Create a scraper for the site
            scraper = self.scraper_registry.create_scraper(
                site["scraper_type"],
                site["url"]
            )
            
            if scraper is None:
                result["error"] = f"No scraper available for type: {site['scraper_type']}"
                return result
            
            # Get categories from the site
            categories = scraper.get_categories()
            result["categories"] = categories
            
            # Process categories and build a mapping of category IDs
            category_id_map = {}
            db_categories = []
            
            for category in categories:
                # Create a database-friendly category object
                db_category = {
                    "name": category["name"],
                    "url": category.get("url"),
                    # Parent ID will be updated after all categories are added
                    "parent_id": None
                }
                
                db_categories.append(db_category)
                
                # Map the scraper's category ID to the index in our list
                category_id_map[category["id"]] = len(db_categories) - 1
            
            # Update parent IDs now that we have all categories
            for i, category in enumerate(categories):
                parent_id = category.get("parent_id")
                if parent_id is not None and parent_id in category_id_map:
                    # The parent ID in the database will be set after insertion
                    db_categories[i]["parent_id_ref"] = parent_id
            
            # Add categories to the database
            category_result = self.category_model.add_or_update_categories(site_id, db_categories)
            result["stats"]["categories_added"] = category_result["added"]
            
            # Get the newly added categories to map scraper IDs to database IDs
            db_categories = self.category_model.get_categories_by_site(site_id)
            
            # Create a mapping of category names to database IDs
            category_name_to_id = {cat["name"]: cat["id"] for cat in db_categories}
            
            # Get files for each category
            all_files = []
            for category in categories:
                category_id = category["id"]
                category_name = category["name"]
                
                # Get the database ID for this category
                db_category_id = category_name_to_id.get(category_name)
                
                # Get files for this category
                files = scraper.get_files_in_category(category_id)
                
                # Add the database category ID to each file
                for file in files:
                    file["category_id"] = db_category_id
                
                all_files.extend(files)
            
            # Process files for database storage
            db_files = []
            for file in all_files:
                # Create a database-friendly file object
                db_file = {
                    "name": file["name"],
                    "url": file["url"],
                    "category_id": file.get("category_id"),
                    "size": file.get("size"),
                    "file_type": file.get("file_type")
                }
                
                db_files.append(db_file)
            
            # Add files to the database
            file_result = self.remote_file_model.add_or_update_files(site_id, db_files)
            result["stats"]["files_added"] = file_result["added"]
            
            result["files"] = all_files
            result["success"] = True
            
            # Update the last scan date
            self.site_model.update_last_scan_date(site_id)
            
            logger.info(f"Scanned site {site_id}: {len(categories)} categories, {len(all_files)} files")
        except Exception as e:
            logger.error(f"Error scanning site {site_id}: {e}")
            result["error"] = str(e)
        
        return result
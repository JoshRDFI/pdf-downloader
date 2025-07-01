"""File comparison service for the PDF Downloader application.

This module provides functionality for comparing local and remote files.
"""

import logging
from typing import Dict, Any, List, Optional

from src.db.local_file_model import LocalFileModel
from src.db.remote_file_model import RemoteFileModel
from src.core.file_validator import FileValidator


logger = logging.getLogger(__name__)


class FileComparisonService:
    """Service for comparing local and remote files.
    
    This class provides methods for comparing local and remote files,
    identifying new, updated, and corrupted files, and building a download queue.
    """
    
    def __init__(self):
        """Initialize the file comparison service."""
        self.local_file_model = LocalFileModel()
        self.remote_file_model = RemoteFileModel()
        self.file_validator = FileValidator()
    
    def compare_files(self, site_id: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Compare local and remote files.
        
        Args:
            site_id: ID of the site to compare files for (optional)
                    If not provided, all sites will be compared
            
        Returns:
            Dictionary with lists of new, updated, and corrupted files
        """
        result = {
            "new_files": [],
            "updated_files": [],
            "corrupted_files": [],
            "ok_files": []
        }
        
        try:
            # Get all remote files, optionally filtered by site
            if site_id is not None:
                remote_files = self.remote_file_model.get_files_by_site(site_id)
            else:
                remote_files = self.remote_file_model.get_all_files()
            
            logger.info(f"Comparing {len(remote_files)} remote files")
            
            for remote_file in remote_files:
                # Check if the file exists locally by remote ID
                local_file = self.local_file_model.get_file_by_remote_id(remote_file["id"])
                
                if local_file is None:
                    # File doesn't exist locally, add to new files
                    result["new_files"].append(remote_file)
                else:
                    # File exists locally, check if it needs updating
                    if local_file["size"] != remote_file["size"]:
                        # File sizes don't match, add to updated files
                        result["updated_files"].append({
                            "remote": remote_file,
                            "local": local_file
                        })
                    else:
                        # File sizes match, check if the file is valid
                        validation_result = self.file_validator.validate_file(
                            local_file["path"], local_file["file_type"]
                        )
                        
                        if not validation_result["valid"]:
                            # File is corrupted, add to corrupted files
                            result["corrupted_files"].append({
                                "remote": remote_file,
                                "local": local_file,
                                "error": validation_result["error"]
                            })
                        else:
                            # File is OK, add to OK files
                            result["ok_files"].append({
                                "remote": remote_file,
                                "local": local_file
                            })
            
            logger.info(f"Comparison results: "
                       f"{len(result['new_files'])} new, "
                       f"{len(result['updated_files'])} updated, "
                       f"{len(result['corrupted_files'])} corrupted, "
                       f"{len(result['ok_files'])} OK")
        except Exception as e:
            logger.error(f"Error comparing files: {e}")
        
        return result
    
    def compare_files_by_site(self) -> Dict[int, Dict[str, List[Dict[str, Any]]]]:
        """Compare local and remote files, grouped by site.
        
        Returns:
            Dictionary mapping site IDs to comparison results
        """
        result = {}
        
        try:
            # Get all sites
            sites = self.remote_file_model.get_all_sites()
            
            for site in sites:
                # Compare files for this site
                site_result = self.compare_files(site["id"])
                result[site["id"]] = site_result
        except Exception as e:
            logger.error(f"Error comparing files by site: {e}")
        
        return result
    
    def build_download_queue(self, site_id: Optional[int] = None, 
                           include_new: bool = True,
                           include_updated: bool = True,
                           include_corrupted: bool = True) -> List[Dict[str, Any]]:
        """Build a download queue based on comparison results.
        
        Args:
            site_id: ID of the site to build the queue for (optional)
            include_new: Whether to include new files in the queue
            include_updated: Whether to include updated files in the queue
            include_corrupted: Whether to include corrupted files in the queue
            
        Returns:
            List of files to download
        """
        queue = []
        
        try:
            # Compare files
            comparison = self.compare_files(site_id)
            
            # Add new files to the queue
            if include_new:
                queue.extend(comparison["new_files"])
            
            # Add updated files to the queue
            if include_updated:
                for item in comparison["updated_files"]:
                    queue.append(item["remote"])
            
            # Add corrupted files to the queue
            if include_corrupted:
                for item in comparison["corrupted_files"]:
                    queue.append(item["remote"])
            
            logger.info(f"Built download queue with {len(queue)} files")
        except Exception as e:
            logger.error(f"Error building download queue: {e}")
        
        return queue
    
    def link_local_to_remote(self, local_file_id: int, remote_file_id: int) -> bool:
        """Link a local file to a remote file.
        
        Args:
            local_file_id: ID of the local file
            remote_file_id: ID of the remote file
            
        Returns:
            True if the link was created successfully, False otherwise
        """
        try:
            # Get the local file
            local_file = self.local_file_model.get_file_by_id(local_file_id)
            
            if local_file is None:
                logger.error(f"Local file with ID {local_file_id} not found")
                return False
            
            # Get the remote file
            remote_file = self.remote_file_model.get_file_by_id(remote_file_id)
            
            if remote_file is None:
                logger.error(f"Remote file with ID {remote_file_id} not found")
                return False
            
            # Update the local file with the remote file ID
            success = self.local_file_model.update_remote_file_id(
                file_id=local_file_id,
                remote_file_id=remote_file_id
            )

            if success:
                logger.info(f"Linked local file {local_file_id} to remote file {remote_file_id}")
            else:
                logger.error(f"Failed to link local file {local_file_id} to remote file {remote_file_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error linking local file to remote file: {e}")
            return False
    
    def unlink_local_from_remote(self, local_file_id: int) -> bool:
        """Unlink a local file from its remote file.
        
        Args:
            local_file_id: ID of the local file
            
        Returns:
            True if the link was removed successfully, False otherwise
        """
        try:
            # Get the local file
            local_file = self.local_file_model.get_file_by_id(local_file_id)
            
            if local_file is None:
                logger.error(f"Local file with ID {local_file_id} not found")
                return False
            
            # Update the local file to remove the remote file ID
            success = self.local_file_model.update_file(
                file_id=local_file_id,
                path=local_file["path"],
                size=local_file["size"],
                file_type=local_file["file_type"],
                remote_file_id=None
            )
            
            if success:
                logger.info(f"Unlinked local file {local_file_id} from remote file")
            else:
                logger.error(f"Failed to unlink local file {local_file_id} from remote file")
            
            return success
        except Exception as e:
            logger.error(f"Error unlinking local file from remote file: {e}")
            return False
"""Directory scanner implementation for the PDF Downloader application.

This module provides functionality for scanning local directories and extracting file information.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime

from src.db.local_file_model import LocalFileModel
from src.core.file_validator import FileValidator


logger = logging.getLogger(__name__)


class DirectoryScanner:
    """Scanner for extracting file information from local directories.
    
    This class handles the scanning of local directories, extracting file metadata,
    and updating the database with the extracted information.
    """
    
    # Supported file types
    SUPPORTED_EXTENSIONS = {
        ".pdf": "pdf",
        ".epub": "epub",
        ".txt": "txt",
        ".text": "txt"
    }
    
    def __init__(self):
        """Initialize the directory scanner."""
        self.local_file_model = LocalFileModel()
        self.file_validator = FileValidator()
        self.cancel_requested = False
    
    def scan_directory(self, root_dir: str, 
                      progress_callback: Optional[Callable[[int, int, str], None]] = None) -> Dict[str, Any]:
        """Scan a directory for files and update the database.
        
        Args:
            root_dir: Root directory to scan
            progress_callback: Callback function for progress updates (optional)
                The callback receives (files_processed, total_files, current_file)
            
        Returns:
            Dictionary containing scan results
        """
        result = {
            "success": False,
            "root_dir": root_dir,
            "files_found": 0,
            "files_added": 0,
            "files_updated": 0,
            "files_by_type": {},
            "error": None,
            "cancelled": False
        }
        
        try:
            # Reset the cancel flag
            self.cancel_requested = False
            
            # Check if the directory exists
            if not os.path.isdir(root_dir):
                result["error"] = f"Directory {root_dir} does not exist"
                return result
            
            # Get a list of all files in the directory and subdirectories
            all_files = []
            for dirpath, dirnames, filenames in os.walk(root_dir):
                for filename in filenames:
                    # Check if the file has a supported extension
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in self.SUPPORTED_EXTENSIONS:
                        file_path = os.path.join(dirpath, filename)
                        all_files.append(file_path)
            
            # Update the result with the number of files found
            result["files_found"] = len(all_files)
            
            # Initialize file type counts
            for ext_type in self.SUPPORTED_EXTENSIONS.values():
                result["files_by_type"][ext_type] = 0
            
            # Process each file
            for i, file_path in enumerate(all_files):
                # Check if cancellation was requested
                if self.cancel_requested:
                    result["cancelled"] = True
                    break
                
                # Update progress
                if progress_callback:
                    progress_callback(i, len(all_files), file_path)
                
                try:
                    # Get the file extension and type
                    _, ext = os.path.splitext(file_path)
                    file_type = self.SUPPORTED_EXTENSIONS.get(ext.lower())
                    
                    # Get the file size
                    file_size = os.path.getsize(file_path)
                    
                    # Validate the file
                    validation_result = self.file_validator.validate_file(file_path, file_type)
                    
                    # Only add valid files to the database
                    if validation_result["valid"]:
                        # Get the relative path from the root directory
                        rel_path = os.path.relpath(file_path, root_dir)
                        
                        # Add or update the file in the database
                        existing_file = self.local_file_model.get_file_by_path(file_path)
                        
                        if existing_file is None:
                            # Add a new file
                            self.local_file_model.add_file(
                                path=file_path,
                                size=file_size,
                                file_type=file_type
                            )
                            result["files_added"] += 1
                        else:
                            # Update an existing file
                            self.local_file_model.update_file(
                                file_id=existing_file["id"],
                                path=file_path,
                                size=file_size,
                                file_type=file_type,
                                remote_file_id=existing_file.get("remote_file_id")
                            )
                            result["files_updated"] += 1
                        
                        # Update the file type count
                        result["files_by_type"][file_type] = result["files_by_type"].get(file_type, 0) + 1
                    else:
                        logger.warning(f"Invalid file: {file_path} - {validation_result['error']}")
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
            
            # Update the final progress
            if progress_callback and not result["cancelled"]:
                progress_callback(len(all_files), len(all_files), "")
            
            result["success"] = True
        except Exception as e:
            logger.error(f"Error scanning directory {root_dir}: {e}")
            result["error"] = str(e)
        
        return result
    
    def cancel_scan(self):
        """Cancel the current scan operation."""
        self.cancel_requested = True
        logger.info("Directory scan cancellation requested")
    
    def get_file_count_by_type(self) -> Dict[str, int]:
        """Get the number of local files by type from the database.
        
        Returns:
            Dictionary mapping file types to counts
        """
        return self.local_file_model.get_file_count_by_type()
    
    def get_total_file_count(self) -> int:
        """Get the total number of local files from the database.
        
        Returns:
            Total number of files
        """
        return self.local_file_model.get_file_count()
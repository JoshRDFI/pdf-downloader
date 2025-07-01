"""Example file type plugin for the PDF Downloader application.

This module demonstrates how to create a custom file type plugin.
"""

import os
import logging
from typing import Dict, Any

from src.plugins.file_types import FileTypeValidator


logger = logging.getLogger(__name__)


class MarkdownValidator(FileTypeValidator):
    """Validator for Markdown files.
    
    This validator demonstrates how to create a custom file type validator.
    """
    
    FILE_TYPE = "markdown"
    EXTENSIONS = [".md", ".markdown"]
    
    def validate(self, file_path: str) -> Dict[str, Any]:
        """Validate a Markdown file.
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            Dictionary containing validation results
        """
        result = {
            "valid": False,
            "file_path": file_path,
            "file_type": self.FILE_TYPE,
            "error": None,
            "metadata": {}
        }
        
        try:
            # Try to open the file to check if it's readable
            with open(file_path, "r", encoding="utf-8") as f:
                # Read the first few lines to extract metadata
                lines = [f.readline().strip() for _ in range(10) if f.readline()]
                
                # Look for a title (# Title)
                title = None
                for line in lines:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
                
                # Count the number of headers
                header_count = 0
                with open(file_path, "r", encoding="utf-8") as f2:
                    for line in f2:
                        if line.strip().startswith("#"):
                            header_count += 1
                
                # Add metadata to the result
                result["metadata"] = {
                    "title": title,
                    "header_count": header_count,
                    "size": os.path.getsize(file_path)
                }
                
                # Mark the file as valid
                result["valid"] = True
        except Exception as e:
            logger.error(f"Error validating Markdown file {file_path}: {e}")
            result["error"] = str(e)
        
        return result
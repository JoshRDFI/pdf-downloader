"""Utility functions for file operations in the PDF Downloader application.

This module provides utility functions for file validation, metadata extraction,
and other file-related operations.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import mimetypes


def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from a file.
    
    Args:
        file_path: Path to the file to extract metadata from
        
    Returns:
        Dictionary containing file metadata
    """
    path = Path(file_path)
    
    metadata = {
        "name": path.name,
        "path": str(path),
        "size": path.stat().st_size if path.exists() else 0,
        "modified": path.stat().st_mtime if path.exists() else 0,
        "extension": path.suffix.lower(),
        "mime_type": mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    }
    
    return metadata


def is_valid_pdf(file_path: str) -> bool:
    """Check if a file is a valid PDF.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file is a valid PDF, False otherwise
    """
    # TODO: Implement PDF validation using PyPDF2 or pdfminer
    # For now, just check the extension and file existence
    path = Path(file_path)
    return path.exists() and path.suffix.lower() == ".pdf"


def scan_directory(directory: str, extensions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Scan a directory for files with the given extensions.
    
    Args:
        directory: Directory to scan
        extensions: List of file extensions to include (e.g., [".pdf", ".epub"])
                   If None, all files are included
        
    Returns:
        List of dictionaries containing file metadata
    """
    results = []
    directory_path = Path(directory)
    
    if not directory_path.exists() or not directory_path.is_dir():
        return results
    
    for root, _, files in os.walk(directory_path):
        for filename in files:
            file_path = Path(root) / filename
            
            # Skip files with unwanted extensions
            if extensions and file_path.suffix.lower() not in extensions:
                continue
            
            # Get file metadata
            metadata = get_file_metadata(str(file_path))
            
            # Add relative path from base directory
            rel_path = file_path.relative_to(directory_path)
            metadata["relative_path"] = str(rel_path)
            
            # Add category based on parent directory
            parent_dir = rel_path.parent
            metadata["category"] = str(parent_dir) if str(parent_dir) != "." else ""
            
            results.append(metadata)
    
    return results
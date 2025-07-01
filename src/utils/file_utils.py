"""Utility functions for file operations in the PDF Downloader application.

This module provides utility functions for file validation, metadata extraction,
and other file-related operations.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import mimetypes
import logging

# Import file-specific validation libraries
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import ebooklib
    from ebooklib import epub
    HAS_EBOOKLIB = True
except ImportError:
    HAS_EBOOKLIB = False

try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False


logger = logging.getLogger(__name__)


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
    
    # Extract additional metadata based on file type
    if path.suffix.lower() == ".pdf" and HAS_PYPDF2:
        try:
            pdf_metadata = extract_pdf_metadata(file_path)
            metadata.update(pdf_metadata)
        except Exception as e:
            logger.warning(f"Error extracting PDF metadata from {file_path}: {e}")
    elif path.suffix.lower() == ".epub" and HAS_EBOOKLIB:
        try:
            epub_metadata = extract_epub_metadata(file_path)
            metadata.update(epub_metadata)
        except Exception as e:
            logger.warning(f"Error extracting EPUB metadata from {file_path}: {e}")
    elif path.suffix.lower() in [".txt", ".text"] and HAS_CHARDET:
        try:
            text_metadata = extract_text_metadata(file_path)
            metadata.update(text_metadata)
        except Exception as e:
            logger.warning(f"Error extracting text metadata from {file_path}: {e}")
    
    return metadata


def extract_pdf_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary containing PDF metadata
    """
    metadata = {}
    
    try:
        with open(file_path, "rb") as f:
            pdf = PyPDF2.PdfReader(f)
            
            # Get the number of pages
            metadata["num_pages"] = len(pdf.pages)
            
            # Get the document info
            info = pdf.metadata
            
            if info:
                # Extract common metadata fields
                if hasattr(info, "title") and info.title:
                    metadata["title"] = info.title
                if hasattr(info, "author") and info.author:
                    metadata["author"] = info.author
                if hasattr(info, "subject") and info.subject:
                    metadata["subject"] = info.subject
                if hasattr(info, "creator") and info.creator:
                    metadata["creator"] = info.creator
                if hasattr(info, "producer") and info.producer:
                    metadata["producer"] = info.producer
    except Exception as e:
        logger.error(f"Error extracting PDF metadata from {file_path}: {e}")
    
    return metadata


def extract_epub_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from an EPUB file.
    
    Args:
        file_path: Path to the EPUB file
        
    Returns:
        Dictionary containing EPUB metadata
    """
    metadata = {}
    
    try:
        book = epub.read_epub(file_path)
        
        # Get the metadata
        title = book.get_metadata("DC", "title")
        creator = book.get_metadata("DC", "creator")
        language = book.get_metadata("DC", "language")
        
        if title and len(title) > 0:
            metadata["title"] = title[0][0]
        if creator and len(creator) > 0:
            metadata["author"] = creator[0][0]
        if language and len(language) > 0:
            metadata["language"] = language[0][0]
    except Exception as e:
        logger.error(f"Error extracting EPUB metadata from {file_path}: {e}")
    
    return metadata


def extract_text_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from a text file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Dictionary containing text file metadata
    """
    metadata = {}
    
    try:
        with open(file_path, "rb") as f:
            # Read a sample of the file
            sample = f.read(4096)  # Read the first 4KB
            
            # Try to detect the encoding
            encoding_result = chardet.detect(sample)
            metadata["encoding"] = encoding_result["encoding"]
            metadata["encoding_confidence"] = encoding_result["confidence"]
            
            # Try to read the first few lines to extract potential title
            try:
                with open(file_path, "r", encoding=metadata["encoding"]) as text_file:
                    lines = [line.strip() for line in text_file.readlines(10) if line.strip()]
                    
                    if lines:
                        # Use the first non-empty line as the title
                        metadata["title"] = lines[0]
            except Exception as e:
                logger.warning(f"Error reading text file {file_path}: {e}")
    except Exception as e:
        logger.error(f"Error extracting text metadata from {file_path}: {e}")
    
    return metadata


def is_valid_pdf(file_path: str) -> Tuple[bool, Optional[str]]:
    """Check if a file is a valid PDF.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(file_path)
    
    # Check if the file exists
    if not path.exists():
        return False, "File does not exist"
    
    # Check if the file has a PDF extension
    if path.suffix.lower() != ".pdf":
        return False, "File does not have a PDF extension"
    
    # Check if PyPDF2 is available
    if not HAS_PYPDF2:
        return True, None  # Can't validate further without PyPDF2
    
    # Try to open the PDF file
    try:
        with open(file_path, "rb") as f:
            pdf = PyPDF2.PdfReader(f)
            # Try to access the first page to verify it's readable
            if len(pdf.pages) > 0:
                _ = pdf.pages[0]
                return True, None
            else:
                return False, "PDF file has no pages"
    except Exception as e:
        return False, f"Invalid PDF file: {str(e)}"


def is_valid_epub(file_path: str) -> Tuple[bool, Optional[str]]:
    """Check if a file is a valid EPUB.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(file_path)
    
    # Check if the file exists
    if not path.exists():
        return False, "File does not exist"
    
    # Check if the file has an EPUB extension
    if path.suffix.lower() != ".epub":
        return False, "File does not have an EPUB extension"
    
    # Check if ebooklib is available
    if not HAS_EBOOKLIB:
        return True, None  # Can't validate further without ebooklib
    
    # Try to open the EPUB file
    try:
        book = epub.read_epub(file_path)
        return True, None
    except Exception as e:
        return False, f"Invalid EPUB file: {str(e)}"


def is_valid_text(file_path: str) -> Tuple[bool, Optional[str]]:
    """Check if a file is a valid text file.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(file_path)
    
    # Check if the file exists
    if not path.exists():
        return False, "File does not exist"
    
    # Check if the file has a text extension
    if path.suffix.lower() not in [".txt", ".text"]:
        return False, "File does not have a text extension"
    
    # Try to open the text file
    try:
        # Try to read the file as binary first
        with open(file_path, "rb") as f:
            sample = f.read(1024)  # Read the first 1KB
        
        # Try to detect the encoding if chardet is available
        if HAS_CHARDET:
            encoding_result = chardet.detect(sample)
            encoding = encoding_result["encoding"]
        else:
            encoding = "utf-8"  # Default to UTF-8
        
        # Try to read the file with the detected encoding
        with open(file_path, "r", encoding=encoding) as f:
            _ = f.read(1024)  # Try to read some text
            return True, None
    except Exception as e:
        return False, f"Invalid text file: {str(e)}"


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


def get_file_type(file_path: str) -> str:
    """Get the type of a file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File type ("pdf", "epub", "txt", or "unknown")
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    
    if extension == ".pdf":
        return "pdf"
    elif extension == ".epub":
        return "epub"
    elif extension in [".txt", ".text"]:
        return "txt"
    else:
        return "unknown"
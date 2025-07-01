"""File validator implementation for the PDF Downloader application.

This module provides functionality for validating downloaded files.
"""

import os
import logging
from typing import Dict, Any, Optional

# Import file-specific libraries
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


class FileValidator:
    """Validator for checking downloaded files.
    
    This class provides methods for validating different types of files,
    such as PDFs, EPUBs, and text files.
    """
    
    def __init__(self):
        """Initialize the file validator."""
        pass
    
    def validate_file(self, file_path: str, file_type: Optional[str] = None) -> Dict[str, Any]:
        """Validate a file.
        
        Args:
            file_path: Path to the file to validate
            file_type: Type of the file (optional, will be inferred from the file extension if not provided)
            
        Returns:
            Dictionary containing validation results
        """
        result = {
            "valid": False,
            "file_path": file_path,
            "file_type": file_type,
            "error": None,
            "metadata": {}
        }
        
        # Check if the file exists
        if not os.path.exists(file_path):
            result["error"] = f"File {file_path} does not exist"
            return result
        
        # Determine the file type if not provided
        if file_type is None:
            file_type = os.path.splitext(file_path)[1].lower().lstrip('.')
            result["file_type"] = file_type
        
        # Validate the file based on its type
        try:
            if file_type == "pdf":
                self._validate_pdf(file_path, result)
            elif file_type == "epub":
                self._validate_epub(file_path, result)
            elif file_type in ["txt", "text"]:
                self._validate_text(file_path, result)
            else:
                # For unknown file types, just check if the file is not empty
                self._validate_generic(file_path, result)
        except Exception as e:
            logger.error(f"Error validating file {file_path}: {e}")
            result["error"] = str(e)
        
        return result
    
    def _validate_pdf(self, file_path: str, result: Dict[str, Any]) -> None:
        """Validate a PDF file.
        
        Args:
            file_path: Path to the PDF file
            result: Dictionary to store validation results
        """
        if not HAS_PYPDF2:
            result["error"] = "PyPDF2 library not available for PDF validation"
            return
        
        try:
            # Open the PDF file
            with open(file_path, "rb") as f:
                # Create a PDF reader object
                pdf = PyPDF2.PdfReader(f)
                
                # Check if the PDF has pages
                if len(pdf.pages) == 0:
                    result["error"] = "PDF file has no pages"
                    return
                
                # Get metadata
                result["metadata"] = {
                    "pages": len(pdf.pages),
                    "title": pdf.metadata.get("/Title", ""),
                    "author": pdf.metadata.get("/Author", ""),
                    "subject": pdf.metadata.get("/Subject", ""),
                    "creator": pdf.metadata.get("/Creator", "")
                }
                
                # Mark as valid
                result["valid"] = True
        except Exception as e:
            result["error"] = f"Error validating PDF: {str(e)}"
    
    def _validate_epub(self, file_path: str, result: Dict[str, Any]) -> None:
        """Validate an EPUB file.
        
        Args:
            file_path: Path to the EPUB file
            result: Dictionary to store validation results
        """
        if not HAS_EBOOKLIB:
            result["error"] = "ebooklib library not available for EPUB validation"
            return
        
        try:
            # Open the EPUB file
            book = epub.read_epub(file_path)
            
            # Check if the EPUB has items
            if len(book.items) == 0:
                result["error"] = "EPUB file has no items"
                return
            
            # Get metadata
            result["metadata"] = {
                "title": book.title,
                "language": book.language,
                "author": ", ".join(book.get_metadata("DC", "creator")),
                "items": len(book.items)
            }
            
            # Mark as valid
            result["valid"] = True
        except Exception as e:
            result["error"] = f"Error validating EPUB: {str(e)}"
    
    def _validate_text(self, file_path: str, result: Dict[str, Any]) -> None:
        """Validate a text file.
        
        Args:
            file_path: Path to the text file
            result: Dictionary to store validation results
        """
        try:
            # Get the file size
            file_size = os.path.getsize(file_path)
            
            # Check if the file is empty
            if file_size == 0:
                result["error"] = "Text file is empty"
                return
            
            # Try to detect the encoding
            encoding = "utf-8"
            if HAS_CHARDET:
                with open(file_path, "rb") as f:
                    raw_data = f.read(min(file_size, 1024 * 1024))  # Read up to 1 MB
                    encoding_result = chardet.detect(raw_data)
                    encoding = encoding_result["encoding"]
            
            # Try to read the file with the detected encoding
            with open(file_path, "r", encoding=encoding) as f:
                # Read the first few lines
                lines = []
                for i, line in enumerate(f):
                    if i >= 10:
                        break
                    lines.append(line.strip())
            
            # Get metadata
            result["metadata"] = {
                "size": file_size,
                "encoding": encoding,
                "lines": len(lines),
                "preview": "\n".join(lines[:3])
            }
            
            # Mark as valid
            result["valid"] = True
        except Exception as e:
            result["error"] = f"Error validating text file: {str(e)}"
    
    def _validate_generic(self, file_path: str, result: Dict[str, Any]) -> None:
        """Validate a generic file.
        
        Args:
            file_path: Path to the file
            result: Dictionary to store validation results
        """
        try:
            # Get the file size
            file_size = os.path.getsize(file_path)
            
            # Check if the file is empty
            if file_size == 0:
                result["error"] = "File is empty"
                return
            
            # Get metadata
            result["metadata"] = {
                "size": file_size,
                "extension": os.path.splitext(file_path)[1].lower().lstrip('.')
            }
            
            # Mark as valid
            result["valid"] = True
        except Exception as e:
            result["error"] = f"Error validating file: {str(e)}"
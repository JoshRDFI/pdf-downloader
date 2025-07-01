"""File validator for the PDF Downloader application.

This module provides functionality for validating different types of files.
"""

import os
import logging
from typing import Dict, Any, Optional, List

from src.plugins.file_types import file_type_plugin_manager, FileTypeValidator

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


# Define built-in file type validators
class PDFValidator(FileTypeValidator):
    """Validator for PDF files."""
    
    FILE_TYPE = "pdf"
    EXTENSIONS = [".pdf"]
    
    def validate(self, file_path: str) -> Dict[str, Any]:
        """Validate a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
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
            # Check if PyPDF2 is available
            if not HAS_PYPDF2:
                result["error"] = "PyPDF2 library not available"
                return result
            
            # Open the PDF file
            with open(file_path, "rb") as f:
                # Try to read the PDF file
                pdf = PyPDF2.PdfReader(f)
                
                # Get the number of pages
                num_pages = len(pdf.pages)
                
                # Get the document info
                info = pdf.metadata
                
                # Add metadata to the result
                result["metadata"] = {
                    "num_pages": num_pages,
                    "title": info.title if info and hasattr(info, "title") else None,
                    "author": info.author if info and hasattr(info, "author") else None,
                    "subject": info.subject if info and hasattr(info, "subject") else None,
                    "creator": info.creator if info and hasattr(info, "creator") else None,
                    "producer": info.producer if info and hasattr(info, "producer") else None
                }
                
                # Mark the file as valid
                result["valid"] = True
        except Exception as e:
            logger.error(f"Error validating PDF file {file_path}: {e}")
            result["error"] = str(e)
        
        return result


class EPUBValidator(FileTypeValidator):
    """Validator for EPUB files."""
    
    FILE_TYPE = "epub"
    EXTENSIONS = [".epub"]
    
    def validate(self, file_path: str) -> Dict[str, Any]:
        """Validate an EPUB file.
        
        Args:
            file_path: Path to the EPUB file
            
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
            # Check if ebooklib is available
            if not HAS_EBOOKLIB:
                result["error"] = "ebooklib library not available"
                return result
            
            # Open the EPUB file
            book = epub.read_epub(file_path)
            
            # Get the metadata
            title = book.get_metadata("DC", "title")
            creator = book.get_metadata("DC", "creator")
            language = book.get_metadata("DC", "language")
            
            # Add metadata to the result
            result["metadata"] = {
                "title": title[0][0] if title and len(title) > 0 else None,
                "author": creator[0][0] if creator and len(creator) > 0 else None,
                "language": language[0][0] if language and len(language) > 0 else None
            }
            
            # Mark the file as valid
            result["valid"] = True
        except Exception as e:
            logger.error(f"Error validating EPUB file {file_path}: {e}")
            result["error"] = str(e)
        
        return result


class TextValidator(FileTypeValidator):
    """Validator for text files."""
    
    FILE_TYPE = "txt"
    EXTENSIONS = [".txt", ".text"]
    
    def validate(self, file_path: str) -> Dict[str, Any]:
        """Validate a text file.
        
        Args:
            file_path: Path to the text file
            
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
            with open(file_path, "rb") as f:
                # Read a sample of the file
                sample = f.read(1024)  # Read the first 1KB
                
                # Try to detect the encoding
                if HAS_CHARDET:
                    encoding_result = chardet.detect(sample)
                    encoding = encoding_result["encoding"]
                    confidence = encoding_result["confidence"]
                else:
                    encoding = "utf-8"  # Default to UTF-8
                    confidence = 0.0
                
                # Add metadata to the result
                result["metadata"] = {
                    "encoding": encoding,
                    "confidence": confidence,
                    "size": os.path.getsize(file_path)
                }
                
                # Mark the file as valid
                result["valid"] = True
        except Exception as e:
            logger.error(f"Error validating text file {file_path}: {e}")
            result["error"] = str(e)
        
        return result


# Register built-in validators
file_type_plugin_manager.register_plugin("pdf", PDFValidator)
file_type_plugin_manager.register_plugin("epub", EPUBValidator)
file_type_plugin_manager.register_plugin("txt", TextValidator)


class FileValidator:
    """Validator for checking file integrity and type.
    
    This class provides methods for validating different types of files,
    such as PDFs, EPUBs, and text files.
    """
    
    def __init__(self):
        """Initialize the file validator."""
        # Discover file type plugins
        file_type_plugin_manager.discover_plugins()
    
    def validate_file(self, file_path: str, file_type: Optional[str] = None) -> Dict[str, Any]:
        """Validate a file based on its type.
        
        Args:
            file_path: Path to the file to validate
            file_type: Type of the file (optional, will be inferred from extension if not provided)
            
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
        
        try:
            # Check if the file exists
            if not os.path.isfile(file_path):
                result["error"] = "File does not exist"
                return result
            
            # Get a validator for the file
            validator = None
            
            if file_type is not None:
                # Use the specified file type
                validator = file_type_plugin_manager.get_validator_for_type(file_type)
            else:
                # Infer the file type from the extension
                validator = file_type_plugin_manager.get_validator_for_file(file_path)
                
                if validator is None:
                    # Try to infer the file type from the extension
                    _, ext = os.path.splitext(file_path)
                    ext = ext.lower()
                    
                    result["error"] = f"Unsupported file extension: {ext}"
                    return result
            
            if validator is None:
                result["error"] = f"No validator found for file type: {file_type}"
                return result
            
            # Update the file type in the result
            result["file_type"] = validator.FILE_TYPE
            
            # Validate the file
            return validator.validate(file_path)
        except Exception as e:
            logger.error(f"Error validating file {file_path}: {e}")
            result["error"] = str(e)
            return result
    
    def get_supported_extensions(self) -> List[str]:
        """Get a list of supported file extensions.
        
        Returns:
            List of supported file extensions
        """
        return file_type_plugin_manager.get_supported_extensions()
    
    def get_supported_types(self) -> List[str]:
        """Get a list of supported file types.
        
        Returns:
            List of supported file types
        """
        return file_type_plugin_manager.get_supported_types()
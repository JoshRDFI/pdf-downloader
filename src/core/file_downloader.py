"""File downloader implementation for the PDF Downloader application.

This module provides functionality for downloading files from remote sites.
"""

import os
import logging
import requests
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from urllib.parse import urlparse

from config import config


logger = logging.getLogger(__name__)


class FileDownloader:
    """Downloader for retrieving files from remote sites.
    
    This class handles the downloading of files, including error handling,
    retries, progress tracking, and rate limiting.
    """
    
    def __init__(self):
        """Initialize the file downloader."""
        self.download_dir = config.get("download", "directory", "downloads")
        self.retry_count = config.get("download", "retry_count", 3)
        self.timeout = config.get("download", "timeout", 30)
        self.user_agent = config.get("network", "user_agent", 
                                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.proxy = config.get("network", "proxy", None)
        
        # Create the download directory if it doesn't exist
        os.makedirs(self.download_dir, exist_ok=True)
    
    def download_file(self, url: str, file_name: Optional[str] = None, 
                     file_type: Optional[str] = None,
                     category_id: Optional[int] = None,
                     progress_callback: Optional[Callable[[float], None]] = None,
                     rate_limit: Optional[int] = None) -> Dict[str, Any]:
        """Download a file from a URL.
        
        Args:
            url: URL of the file to download
            file_name: Name to save the file as (optional, defaults to URL filename)
            file_type: Type of the file (e.g., 'pdf', 'epub')
            category_id: ID of the category to save the file in (optional)
            progress_callback: Callback function for progress updates (optional)
            rate_limit: Rate limit in KB/s (optional)
            
        Returns:
            Dictionary containing download results
        """
        result = {
            "success": False,
            "url": url,
            "file_path": None,
            "file_size": None,
            "error": None
        }
        
        try:
            # Determine the file name if not provided
            if file_name is None:
                file_name = os.path.basename(urlparse(url).path)
                if not file_name:
                    file_name = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_type or 'pdf'}"
            
            # Determine the save directory
            save_dir = self.download_dir
            if category_id:
                # Use category_id as a subdirectory
                category_dir = f"category_{category_id}"
                save_dir = os.path.join(save_dir, category_dir)
                os.makedirs(save_dir, exist_ok=True)
            
            # Determine the file path
            file_path = os.path.join(save_dir, file_name)
            result["file_path"] = file_path
            
            # Set up the request headers
            headers = {
                "User-Agent": self.user_agent
            }
            
            # Set up the proxies
            proxies = None
            if self.proxy:
                proxies = {
                    "http": self.proxy,
                    "https": self.proxy
                }
            
            # Download the file with retries
            for attempt in range(self.retry_count + 1):
                try:
                    # Start the download
                    with requests.get(url, headers=headers, proxies=proxies, 
                                     stream=True, timeout=self.timeout) as response:
                        # Check if the request was successful
                        response.raise_for_status()
                        
                        # Get the file size
                        file_size = int(response.headers.get("Content-Length", 0))
                        result["file_size"] = file_size
                        
                        # Download the file in chunks with rate limiting
                        downloaded = 0
                        start_time = time.time()
                        chunk_size = 8192  # 8 KB chunks
                        
                        with open(file_path, "wb") as f:
                            for chunk in response.iter_content(chunk_size=chunk_size):
                                if chunk:
                                    # Apply rate limiting if specified
                                    if rate_limit:
                                        # Calculate the expected time for this chunk at the rate limit
                                        chunk_size_kb = len(chunk) / 1024
                                        expected_time = chunk_size_kb / rate_limit
                                        
                                        # Calculate the elapsed time
                                        elapsed = time.time() - start_time
                                        
                                        # Sleep if we're going too fast
                                        if elapsed < expected_time:
                                            time.sleep(expected_time - elapsed)
                                        
                                        # Reset the start time
                                        start_time = time.time()
                                    
                                    # Write the chunk
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    
                                    # Update progress
                                    if progress_callback and file_size > 0:
                                        progress = (downloaded / file_size) * 100
                                        progress_callback(progress)
                    
                    # Download successful
                    result["success"] = True
                    logger.info(f"Downloaded {url} to {file_path}")
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < self.retry_count:
                        logger.warning(f"Download attempt {attempt + 1} failed for {url}: {e}")
                    else:
                        raise
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            result["error"] = str(e)
            
            # Remove the file if it was partially downloaded
            if result["file_path"] and os.path.exists(result["file_path"]):
                try:
                    os.remove(result["file_path"])
                except Exception as remove_error:
                    logger.error(f"Error removing partial download {result['file_path']}: {remove_error}")
        
        return result
"""Download manager implementation for the PDF Downloader application.

This module provides functionality for managing multiple file downloads.
"""

import logging
import threading
from queue import Queue
from typing import Dict, Any, List, Optional, Callable

from config import config
from src.core.file_downloader import FileDownloader
from src.db.remote_file_model import RemoteFileModel


logger = logging.getLogger(__name__)


class DownloadManager:
    """Manager for handling multiple file downloads.
    
    This class manages a queue of downloads and processes them using
    multiple worker threads.
    """
    
    def __init__(self):
        """Initialize the download manager."""
        self.file_downloader = FileDownloader()
        self.remote_file_model = RemoteFileModel()
        self.download_queue = Queue()
        self.active_downloads = {}
        self.workers = []
        self.max_workers = config.get("download", "concurrent_downloads", 3)
        self.running = False
        self.lock = threading.Lock()
    
    def start(self):
        """Start the download manager.
        
        This method starts the worker threads to process the download queue.
        """
        if self.running:
            return
        
        self.running = True
        
        # Create and start the worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker,
                name=f"DownloadWorker-{i}",
                daemon=True
            )
            self.workers.append(worker)
            worker.start()
        
        logger.info(f"Started download manager with {self.max_workers} workers")
    
    def stop(self):
        """Stop the download manager.
        
        This method stops the worker threads and clears the download queue.
        """
        if not self.running:
            return
        
        self.running = False
        
        # Clear the download queue
        while not self.download_queue.empty():
            try:
                self.download_queue.get_nowait()
                self.download_queue.task_done()
            except Exception:
                pass
        
        # Wait for the worker threads to finish
        for worker in self.workers:
            if worker.is_alive():
                worker.join(1.0)
        
        self.workers = []
        
        logger.info("Stopped download manager")
    
    def queue_download(self, file_id: int, progress_callback: Optional[Callable[[int, float], None]] = None) -> bool:
        """Queue a file for download.
        
        Args:
            file_id: ID of the remote file to download
            progress_callback: Callback function for progress updates (optional)
            
        Returns:
            True if the file was queued successfully, False otherwise
        """
        # Check if the file is already in the queue or being downloaded
        with self.lock:
            if file_id in self.active_downloads:
                logger.warning(f"File {file_id} is already in the download queue")
                return False
        
        # Get the file information
        file = self.remote_file_model.get_file_by_id(file_id)
        if file is None:
            logger.warning(f"File with ID {file_id} not found")
            return False
        
        # Add the file to the active downloads
        with self.lock:
            self.active_downloads[file_id] = {
                "file": file,
                "progress": 0.0,
                "status": "queued",
                "progress_callback": progress_callback
            }
        
        # Add the file to the download queue
        self.download_queue.put(file_id)
        
        logger.info(f"Queued file {file_id} for download")
        return True
    
    def get_download_status(self, file_id: int) -> Dict[str, Any]:
        """Get the status of a download.
        
        Args:
            file_id: ID of the remote file
            
        Returns:
            Dictionary containing download status information
        """
        with self.lock:
            if file_id in self.active_downloads:
                return self.active_downloads[file_id].copy()
        
        return {
            "file": None,
            "progress": 0.0,
            "status": "not_queued",
            "progress_callback": None
        }
    
    def get_all_downloads(self) -> List[Dict[str, Any]]:
        """Get the status of all downloads.
        
        Returns:
            List of dictionaries containing download status information
        """
        with self.lock:
            downloads = []
            for file_id, download in self.active_downloads.items():
                download_copy = download.copy()
                download_copy["file_id"] = file_id
                downloads.append(download_copy)
        
        return downloads
    
    def _worker(self):
        """Worker thread for processing downloads.
        
        This method runs in a separate thread and processes downloads from the queue.
        """
        while self.running:
            try:
                # Get a file ID from the queue
                file_id = self.download_queue.get(timeout=1.0)
                
                # Get the download information
                with self.lock:
                    if file_id not in self.active_downloads:
                        self.download_queue.task_done()
                        continue
                    
                    download = self.active_downloads[file_id]
                    download["status"] = "downloading"
                
                # Get the file information
                file = download["file"]
                progress_callback = download["progress_callback"]
                
                # Create a progress callback for this download
                def update_progress(progress):
                    with self.lock:
                        if file_id in self.active_downloads:
                            self.active_downloads[file_id]["progress"] = progress
                            if progress_callback:
                                progress_callback(file_id, progress)
                
                # Download the file
                result = self.file_downloader.download_file(
                    url=file["url"],
                    file_name=file["name"],
                    category=None,  # TODO: Get category name
                    progress_callback=update_progress
                )
                
                # Update the download status
                with self.lock:
                    if file_id in self.active_downloads:
                        if result["success"]:
                            self.active_downloads[file_id]["status"] = "completed"
                            self.active_downloads[file_id]["progress"] = 1.0
                            self.active_downloads[file_id]["result"] = result
                        else:
                            self.active_downloads[file_id]["status"] = "failed"
                            self.active_downloads[file_id]["error"] = result["error"]
                            self.active_downloads[file_id]["result"] = result
                
                # Mark the task as done
                self.download_queue.task_done()
            except Exception as e:
                logger.error(f"Error in download worker: {e}")
    
    def remove_download(self, file_id: int) -> bool:
        """Remove a download from the active downloads.
        
        Args:
            file_id: ID of the remote file
            
        Returns:
            True if the download was removed, False otherwise
        """
        with self.lock:
            if file_id in self.active_downloads:
                status = self.active_downloads[file_id]["status"]
                if status in ["completed", "failed"]:
                    del self.active_downloads[file_id]
                    return True
        
        return False
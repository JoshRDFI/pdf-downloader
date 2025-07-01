"""Download manager implementation for the PDF Downloader application.

This module provides functionality for managing multiple file downloads.
"""

import logging
import threading
import time
from queue import Queue, PriorityQueue
from typing import Dict, Any, List, Optional, Callable, Tuple

from PyQt5.QtCore import QObject, pyqtSignal

from config import config
from src.core.file_downloader import FileDownloader
from src.db.remote_file_model import RemoteFileModel
from src.db.download_model import DownloadModel


logger = logging.getLogger(__name__)


class DownloadManager(QObject):
    """Manager for handling multiple file downloads.

    This class manages a queue of downloads and processes them using
    multiple worker threads with rate limiting.
    """

    # Signals for download events
    download_started = pyqtSignal(int)  # file_id
    download_progress = pyqtSignal(int, float)  # file_id, progress
    download_completed = pyqtSignal(int)  # file_id
    download_failed = pyqtSignal(int, str)  # file_id, error

    def __init__(self):
        """Initialize the download manager."""
        super().__init__()
        self.file_downloader = FileDownloader()
        self.remote_file_model = RemoteFileModel()
        self.download_model = DownloadModel()
        self.download_queue = PriorityQueue()  # Priority queue for downloads
        self.active_downloads = {}  # Map of file_id to download info
        self.workers = []  # List of worker threads
        self.running = False
        self.lock = threading.Lock()
        self.queue_items = []  # List of queue items for UI display

        # Load settings
        self.load_settings()

    def load_settings(self):
        """Load settings from the configuration."""
        self.max_workers = config.get("download", "concurrent_downloads", 3)
        self.rate_limit = config.get("download", "rate_limit_kbps", 500)  # KB/s

        # If rate limit is 0, disable rate limiting
        if self.rate_limit == 0:
            self.rate_limit = None

    def reload_settings(self):
        """Reload settings from the configuration.

        This method should be called when settings are changed.
        """
        with self.lock:
            old_max_workers = self.max_workers
            self.load_settings()

            # If the number of workers has decreased, we need to stop some workers
            if self.max_workers < old_max_workers and self.running:
                # Stop the manager and restart it
                self.stop()
                self.start()

            logger.info(f"Reloaded download manager settings: max_workers={self.max_workers}, rate_limit={self.rate_limit}")

    def start(self):
        """Start the download manager.

        This method starts the worker threads for processing downloads.
        """
        if self.running:
            logger.warning("Download manager is already running")
            return

        self.running = True

        # Start worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker,
                daemon=True,
                name=f"DownloadWorker-{i}"
            )
            worker.start()
            self.workers.append(worker)

        logger.info(f"Started download manager with {self.max_workers} workers")

    def stop(self):
        """Stop the download manager.

        This method stops all worker threads and clears the download queue.
        """
        if not self.running:
            logger.warning("Download manager is not running")
            return

        self.running = False

        # Wait for worker threads to finish
        for worker in self.workers:
            if worker.is_alive():
                worker.join(timeout=1.0)

        # Clear the workers list
        self.workers.clear()

        logger.info("Stopped download manager")

    def restart(self):
        """Restart the download manager.

        This method stops and then starts the download manager.
        """
        self.stop()
        self.start()

    def is_running(self) -> bool:
        """Check if the download manager is running.

        Returns:
            True if the download manager is running, False otherwise
        """
        return self.running

    def get_queue_size(self) -> int:
        """Get the number of items in the download queue.

        Returns:
            Number of items in the download queue
        """
        return len(self.queue_items)

    def get_active_downloads_count(self) -> int:
        """Get the number of active downloads.

        Returns:
            Number of active downloads
        """
        return len(self.active_downloads)

    def get_queue_items(self) -> List[Dict[str, Any]]:
        """Get the items in the download queue.

        Returns:
            List of items in the download queue
        """
        with self.lock:
            return self.queue_items.copy()

    def get_active_downloads(self) -> Dict[int, Dict[str, Any]]:
        """Get the active downloads.

        Returns:
            Dictionary of active downloads
        """
        with self.lock:
            return self.active_downloads.copy()

    def queue_download(self, file_id: int, priority: int = 100) -> bool:
        """Add a file to the download queue.

        Args:
            file_id: ID of the file to download
            priority: Priority of the download (lower values have higher priority)

        Returns:
            True if the file was added to the queue, False otherwise
        """
        try:
            # Check if the file exists
            file_info = self.remote_file_model.get_file_by_id(file_id)
            if not file_info:
                logger.error(f"File with ID {file_id} not found")
                return False

            # Check if the file is already in the queue
            with self.lock:
                for item in self.queue_items:
                    if item["file_id"] == file_id:
                        logger.warning(f"File with ID {file_id} is already in the queue")
                        return False

                # Check if the file is already being downloaded
                if file_id in self.active_downloads:
                    logger.warning(f"File with ID {file_id} is already being downloaded")
                    return False

            # Add the file to the queue
            self.download_queue.put((priority, file_id))

            # Add the file to the queue items list
            with self.lock:
                self.queue_items.append({
                    "file_id": file_id,
                    "name": file_info["name"],
                    "url": file_info["url"],
                    "size": file_info["size"],
                    "priority": priority
                })

            # Add the file to the downloads table
            self.download_model.create_download(file_id)

            logger.info(f"Added file {file_id} to download queue with priority {priority}")
            return True
        except Exception as e:
            logger.error(f"Error adding file {file_id} to download queue: {e}")
            return False

    def remove_from_queue(self, file_id: int) -> bool:
        """Remove a file from the download queue.

        Args:
            file_id: ID of the file to remove

        Returns:
            True if the file was removed from the queue, False otherwise
        """
        try:
            # Remove the file from the queue items list
            with self.lock:
                for i, item in enumerate(self.queue_items):
                    if item["file_id"] == file_id:
                        self.queue_items.pop(i)
                        break
                else:
                    logger.warning(f"File with ID {file_id} not found in queue")
                    return False

            # Note: We can't remove items from a priority queue directly,
            # so we'll just skip them when we process the queue

            logger.info(f"Removed file {file_id} from download queue")
            return True
        except Exception as e:
            logger.error(f"Error removing file {file_id} from download queue: {e}")
            return False

    def clear_queue(self) -> bool:
        """Clear the download queue.

        Returns:
            True if the queue was cleared, False otherwise
        """
        try:
            # Clear the queue
            while not self.download_queue.empty():
                try:
                    self.download_queue.get_nowait()
                    self.download_queue.task_done()
                except Exception:
                    pass

            # Clear the queue items list
            with self.lock:
                self.queue_items.clear()

            logger.info("Cleared download queue")
            return True
        except Exception as e:
            logger.error(f"Error clearing download queue: {e}")
            return False

    def pause_download(self, file_id: int) -> bool:
        """Pause a download.

        Args:
            file_id: ID of the file to pause

        Returns:
            True if the download was paused, False otherwise
        """
        try:
            # Check if the file is being downloaded
            with self.lock:
                if file_id not in self.active_downloads:
                    logger.warning(f"File with ID {file_id} is not being downloaded")
                    return False

                # Update the status
                self.active_downloads[file_id]["status"] = "Paused"

            logger.info(f"Paused download of file {file_id}")
            return True
        except Exception as e:
            logger.error(f"Error pausing download of file {file_id}: {e}")
            return False

    def resume_download(self, file_id: int) -> bool:
        """Resume a paused download.

        Args:
            file_id: ID of the file to resume

        Returns:
            True if the download was resumed, False otherwise
        """
        try:
            # Check if the file is being downloaded
            with self.lock:
                if file_id not in self.active_downloads:
                    logger.warning(f"File with ID {file_id} is not being downloaded")
                    return False

                # Check if the download is paused
                if self.active_downloads[file_id]["status"] != "Paused":
                    logger.warning(f"Download of file {file_id} is not paused")
                    return False

                # Update the status
                self.active_downloads[file_id]["status"] = "Downloading"

            logger.info(f"Resumed download of file {file_id}")
            return True
        except Exception as e:
            logger.error(f"Error resuming download of file {file_id}: {e}")
            return False

    def cancel_download(self, file_id: int) -> bool:
        """Cancel a download.

        Args:
            file_id: ID of the file to cancel

        Returns:
            True if the download was canceled, False otherwise
        """
        try:
            # Check if the file is being downloaded
            with self.lock:
                if file_id not in self.active_downloads:
                    logger.warning(f"File with ID {file_id} is not being downloaded")
                    return False

                # Update the status
                self.active_downloads[file_id]["status"] = "Canceled"

                # Remove the file from the active downloads map
                self.active_downloads.pop(file_id)

            logger.info(f"Canceled download of file {file_id}")
            return True
        except Exception as e:
            logger.error(f"Error canceling download of file {file_id}: {e}")
            return False

    def get_download_progress(self, file_id: int) -> float:
        """Get the progress of a download.

        Args:
            file_id: ID of the file

        Returns:
            Progress of the download as a percentage (0-100)
        """
        with self.lock:
            if file_id in self.active_downloads:
                return self.active_downloads[file_id].get("progress", 0.0)
            return 0.0

    def get_download_status(self, file_id: int) -> str:
        """Get the status of a download.

        Args:
            file_id: ID of the file

        Returns:
            Status of the download
        """
        with self.lock:
            if file_id in self.active_downloads:
                return self.active_downloads[file_id].get("status", "Unknown")
            return "Not Found"

    def get_download_speed(self, file_id: int) -> float:
        """Get the download speed.

        Args:
            file_id: ID of the file

        Returns:
            Download speed in KB/s
        """
        with self.lock:
            if file_id in self.active_downloads:
                return self.active_downloads[file_id].get("speed", 0.0)
            return 0.0

    def _progress_callback(self, file_id: int, progress: float):
        """Callback for download progress updates.

        Args:
            file_id: ID of the file
            progress: Progress of the download as a percentage (0-100)
        """
        # Update the progress in the active downloads map
        with self.lock:
            if file_id in self.active_downloads:
                self.active_downloads[file_id]["progress"] = progress

        # Emit the progress signal
        self.download_progress.emit(file_id, progress)

    def _worker(self):
        """Worker thread for processing downloads."""
        while self.running:
            try:
                # Get the next file from the queue
                priority, file_id = self.download_queue.get(timeout=1.0)

                # Check if the file is still in the active downloads map
                with self.lock:
                    if file_id not in self.active_downloads:
                        self.download_queue.task_done()
                        continue

                    # Update the status
                    self.active_downloads[file_id]["status"] = "Downloading"

                    # Get the file information
                    file = self.active_downloads[file_id]

                # Emit the download started signal
                self.download_started.emit(file_id)
                
                # Update the download record in the database
                # Get the download record for this file
                downloads = self.download_model.get_pending_downloads()
                download_id = None
                
                for download in downloads:
                    if download["remote_file_id"] == file_id:
                        download_id = download["id"]
                        break
                
                if download_id:
                    self.download_model.update_download_started(download_id)

                # Download the file with rate limiting
                try:
                    result = self.file_downloader.download_file(
                        file["url"],
                        file["name"],
                        file["file_type"],
                        file["category_id"],
                        lambda progress: self._progress_callback(file_id, progress),
                        rate_limit=self.rate_limit
                    )

                    if result["success"]:
                        # Update the status
                        with self.lock:
                            self.active_downloads[file_id]["status"] = "Completed"
                            self.active_downloads[file_id]["progress"] = 100

                        # Emit the download completed signal
                        self.download_completed.emit(file_id)
                        
                        # Update the download record in the database
                        if download_id and "local_file_id" in result:
                            self.download_model.update_download_completed(download_id, result["local_file_id"])

                        logger.info(f"Downloaded file {file_id}")
                    else:
                        # Update the status
                        with self.lock:
                            self.active_downloads[file_id]["status"] = "Failed"

                        # Emit the download failed signal
                        self.download_failed.emit(file_id, result["error"])
                        
                        # Update the download record in the database
                        if download_id:
                            self.download_model.update_download_failed(download_id, result["error"])

                        logger.error(f"Failed to download file {file_id}: {result['error']}")
                except Exception as e:
                    # Update the status
                    with self.lock:
                        self.active_downloads[file_id]["status"] = "Failed"

                    # Emit the download failed signal
                    self.download_failed.emit(file_id, str(e))
                    
                    # Update the download record in the database
                    if download_id:
                        self.download_model.update_download_failed(download_id, str(e))

                    logger.error(f"Error downloading file {file_id}: {e}")

                # Mark the task as done
                self.download_queue.task_done()
            except Exception as e:
                if self.running:
                    logger.error(f"Error in download worker: {e}")

        logger.info("Download worker stopped")
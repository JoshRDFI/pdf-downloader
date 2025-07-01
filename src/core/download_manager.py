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
        self.download_queue = PriorityQueue()  # Priority queue for downloads
        self.active_downloads = {}  # Map of file_id to download info
        self.workers = []  # List of worker threads
        self.max_workers = config.get("download", "concurrent_downloads", 3)
        self.rate_limit = config.get("download", "rate_limit_kbps", 500)  # KB/s
        self.running = False
        self.lock = threading.Lock()
        self.queue_items = []  # List of queue items for UI display

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

    def is_running(self) -> bool:
        """Check if the download manager is running.

        Returns:
            True if the download manager is running, False otherwise
        """
        return self.running

    def queue_download(self, file_id: int, priority: int = 100) -> bool:
        """Queue a file for download.

        Args:
            file_id: ID of the remote file to download
            priority: Priority of the download (lower values = higher priority)

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
            logger.error(f"File {file_id} not found")
            return False

        # Add the file to the queue
        with self.lock:
            # Create a queue item
            queue_item = {
                "id": file_id,
                "name": file["name"],
                "url": file["url"],
                "size": file["size"],
                "file_type": file["file_type"],
                "category_id": file["category_id"],
                "status": "Queued",
                "progress": 0,
                "priority": priority
            }

            # Add to the active downloads map
            self.active_downloads[file_id] = queue_item

            # Add to the queue items list
            self.queue_items.append(queue_item)

            # Add to the priority queue
            self.download_queue.put((priority, file_id))

        logger.info(f"Queued file {file_id} for download")
        return True

    def remove_from_queue(self, file_id: int) -> bool:
        """Remove a file from the download queue.

        Args:
            file_id: ID of the file to remove

        Returns:
            True if the file was removed, False otherwise
        """
        with self.lock:
            if file_id not in self.active_downloads:
                logger.warning(f"File {file_id} is not in the download queue")
                return False

            # Remove from the active downloads map
            del self.active_downloads[file_id]

            # Remove from the queue items list
            self.queue_items = [item for item in self.queue_items if item["id"] != file_id]

        logger.info(f"Removed file {file_id} from the download queue")
        return True

    def prioritize_file(self, file_id: int) -> bool:
        """Move a file to the top of the download queue.

        Args:
            file_id: ID of the file to prioritize

        Returns:
            True if the file was prioritized, False otherwise
        """
        with self.lock:
            if file_id not in self.active_downloads:
                logger.warning(f"File {file_id} is not in the download queue")
                return False

            # Get the queue item
            queue_item = self.active_downloads[file_id]

            # If the file is already downloading, we can't prioritize it
            if queue_item["status"] == "Downloading":
                logger.warning(f"File {file_id} is already downloading")
                return False

            # Update the priority
            queue_item["priority"] = 0

            # Re-queue the file with the new priority
            self.download_queue.put((0, file_id))

        logger.info(f"Prioritized file {file_id}")
        return True

    def clear_queue(self) -> int:
        """Clear the download queue.

        Returns:
            Number of items removed from the queue
        """
        with self.lock:
            # Count the number of items in the queue
            count = len(self.queue_items)

            # Clear the queue
            self.active_downloads = {}
            self.queue_items = []

            # Clear the priority queue
            while not self.download_queue.empty():
                try:
                    self.download_queue.get_nowait()
                    self.download_queue.task_done()
                except Exception:
                    pass

        logger.info(f"Cleared download queue ({count} items)")
        return count

    def get_queue_items(self) -> List[Dict[str, Any]]:
        """Get the items in the download queue.

        Returns:
            List of queue items
        """
        with self.lock:
            return self.queue_items.copy()

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

                        logger.info(f"Downloaded file {file_id}")
                    else:
                        # Update the status
                        with self.lock:
                            self.active_downloads[file_id]["status"] = "Failed"

                        # Emit the download failed signal
                        self.download_failed.emit(file_id, result["error"])

                        logger.error(f"Failed to download file {file_id}: {result['error']}")
                except Exception as e:
                    # Update the status
                    with self.lock:
                        self.active_downloads[file_id]["status"] = "Failed"

                    # Emit the download failed signal
                    self.download_failed.emit(file_id, str(e))

                    logger.error(f"Error downloading file {file_id}: {e}")

                # Mark the task as done
                self.download_queue.task_done()
            except Exception as e:
                if self.running:
                    logger.error(f"Error in download worker: {e}")

    def _progress_callback(self, file_id: int, progress: float):
        """Callback for download progress updates.

        Args:
            file_id: ID of the file being downloaded
            progress: Download progress (0-100)
        """
        # Update the progress in the active downloads map
        with self.lock:
            if file_id in self.active_downloads:
                self.active_downloads[file_id]["progress"] = progress

        # Emit the progress signal
        self.download_progress.emit(file_id, progress)
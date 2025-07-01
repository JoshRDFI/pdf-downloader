"""Download queue tab for the PDF Downloader application.

This module provides a tab for managing the download queue.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
                             QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QColor

import logging
from typing import Dict, Any, List, Optional

from src.core.download_manager import DownloadManager


logger = logging.getLogger(__name__)


class DownloadQueueTab(QWidget):
    """Tab for managing the download queue.
    
    This tab allows users to view, prioritize, reorder, and remove items from the download queue.
    """
    
    def __init__(self, parent=None):
        """Initialize the download queue tab."""
        super().__init__(parent)
        self.download_manager = DownloadManager()
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Start/Stop button
        self.start_stop_button = QPushButton("Start Downloads")
        self.start_stop_button.clicked.connect(self.toggle_downloads)
        
        # Clear button
        self.clear_button = QPushButton("Clear Queue")
        self.clear_button.clicked.connect(self.clear_queue)
        
        # Add to controls layout
        controls_layout.addWidget(self.start_stop_button)
        controls_layout.addWidget(self.clear_button)
        controls_layout.addStretch()

        # Add controls layout to main layout
        main_layout.addLayout(controls_layout)

        # Queue table
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(5)
        self.queue_table.setHorizontalHeaderLabels(["ID", "Name", "Size", "Status", "Progress"])
        self.queue_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.queue_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.queue_table.setSelectionMode(QTableWidget.SingleSelection)
        self.queue_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.queue_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.queue_table.customContextMenuRequested.connect(self.show_context_menu)

        # Add queue table to main layout
        main_layout.addWidget(self.queue_table)

        # Connect signals from download manager
        self.download_manager.download_started.connect(self.on_download_started)
        self.download_manager.download_progress.connect(self.on_download_progress)
        self.download_manager.download_completed.connect(self.on_download_completed)
        self.download_manager.download_failed.connect(self.on_download_failed)

        # Start the download manager
        self.download_manager.start()

        # Update the queue table
        self.update_queue_table()

    def toggle_downloads(self):
        """Toggle the download manager between running and paused states."""
        if self.download_manager.is_running():
            self.download_manager.stop()
            self.start_stop_button.setText("Start Downloads")
        else:
            self.download_manager.start()
            self.start_stop_button.setText("Pause Downloads")

    def clear_queue(self):
        """Clear the download queue."""
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Clear Queue",
            "Are you sure you want to clear the download queue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.download_manager.clear_queue()
            self.update_queue_table()

    def update_queue_table(self):
        """Update the queue table with the current download queue."""
        # Get the queue items
        queue_items = self.download_manager.get_queue_items()
        active_downloads = self.download_manager.get_active_downloads()

        # Clear the table
        self.queue_table.setRowCount(0)

        # Add active downloads first
        for file_id, download in active_downloads.items():
            row = self.queue_table.rowCount()
            self.queue_table.insertRow(row)

            # ID
            id_item = QTableWidgetItem(str(file_id))
            id_item.setData(Qt.UserRole, file_id)
            self.queue_table.setItem(row, 0, id_item)

            # Name
            name_item = QTableWidgetItem(download.get("name", ""))
            self.queue_table.setItem(row, 1, name_item)

            # Size
            size = download.get("size", 0)
            size_item = QTableWidgetItem(self._format_size(size) if size else "")
            self.queue_table.setItem(row, 2, size_item)

            # Status
            status = download.get("status", "")
            status_item = QTableWidgetItem(status.capitalize())
            if status == "completed":
                status_item.setForeground(QColor(0, 128, 0))  # Green
            elif status == "failed":
                status_item.setForeground(QColor(255, 0, 0))  # Red
            self.queue_table.setItem(row, 3, status_item)

            # Progress
            progress = download.get("progress", 0.0)
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(int(progress * 100))
            self.queue_table.setCellWidget(row, 4, progress_bar)

        # Add queued items
        for item in queue_items:
            row = self.queue_table.rowCount()
            self.queue_table.insertRow(row)

            # ID
            file_id = item.get("file_id", 0)
            id_item = QTableWidgetItem(str(file_id))
            id_item.setData(Qt.UserRole, file_id)
            self.queue_table.setItem(row, 0, id_item)

            # Name
            name_item = QTableWidgetItem(item.get("name", ""))
            self.queue_table.setItem(row, 1, name_item)

            # Size
            size = item.get("size", 0)
            size_item = QTableWidgetItem(self._format_size(size) if size else "")
            self.queue_table.setItem(row, 2, size_item)

            # Status
            status_item = QTableWidgetItem("Queued")
            self.queue_table.setItem(row, 3, status_item)

            # Progress
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            self.queue_table.setCellWidget(row, 4, progress_bar)

    def _format_size(self, size_bytes):
        """Format a size in bytes to a human-readable string.

        Args:
            size_bytes: Size in bytes

        Returns:
            Human-readable size string
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def show_context_menu(self, position):
        """Show context menu for the queue table.

        Args:
            position: Position where the context menu should be shown
        """
        # Get the selected row
        row = self.queue_table.rowAt(position.y())
        if row < 0:
            return

        # Get the file ID
        file_id = self.queue_table.item(row, 0).data(Qt.UserRole)

        # Create menu
        menu = QMenu()

        # Add actions
        remove_action = QAction("Remove from Queue", self)
        menu.addAction(remove_action)

        # Show menu and handle action
        action = menu.exec_(self.queue_table.mapToGlobal(position))

        if action == remove_action:
            self.download_manager.remove_from_queue(file_id)
            self.update_queue_table()

    def on_download_started(self, file_id):
        """Handle download started event.

        Args:
            file_id: ID of the file being downloaded
        """
        self.update_queue_table()

    def on_download_progress(self, file_id, progress):
        """Handle download progress event.

        Args:
            file_id: ID of the file being downloaded
            progress: Download progress (0.0 to 1.0)
        """
        # Find the row with the file ID
        for row in range(self.queue_table.rowCount()):
            if self.queue_table.item(row, 0).data(Qt.UserRole) == file_id:
                # Update the progress bar
                progress_bar = self.queue_table.cellWidget(row, 4)
                if progress_bar:
                    progress_bar.setValue(int(progress * 100))
                break

    def on_download_completed(self, file_id):
        """Handle download completed event.

        Args:
            file_id: ID of the file that was downloaded
        """
        self.update_queue_table()

    def on_download_failed(self, file_id, error):
        """Handle download failed event.

        Args:
            file_id: ID of the file that failed to download
            error: Error message
        """
        self.update_queue_table()

        # Show error message
        QMessageBox.warning(
            self, "Download Failed",
            f"Failed to download file {file_id}: {error}"
        )
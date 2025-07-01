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
        
        # Status label
        self.status_label = QLabel("Ready")
        
        # Queue table
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(5)
        self.queue_table.setHorizontalHeaderLabels(["ID", "Name", "Size", "Status", "Progress"])
        self.queue_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.queue_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.queue_table.setSelectionMode(QTableWidget.SingleSelection)
        self.queue_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.queue_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Add to main layout
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.queue_table)
        
        # Initialize the download manager
        self.download_manager.start()
        
        # Connect signals
        self.download_manager.download_started.connect(self.on_download_started)
        self.download_manager.download_progress.connect(self.on_download_progress)
        self.download_manager.download_completed.connect(self.on_download_completed)
        self.download_manager.download_failed.connect(self.on_download_failed)
        
        # Load the queue
        self.load_queue()
        
    def load_queue(self):
        """Load the download queue into the table."""
        # Clear the table
        self.queue_table.setRowCount(0)
        
        # Get the queue items
        queue_items = self.download_manager.get_queue_items()
        
        # Add items to the table
        for i, item in enumerate(queue_items):
            self.queue_table.insertRow(i)
            
            # ID
            id_item = QTableWidgetItem(str(item["id"]))
            id_item.setData(Qt.UserRole, item["id"])
            self.queue_table.setItem(i, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(item["name"])
            self.queue_table.setItem(i, 1, name_item)
            
            # Size
            size_item = QTableWidgetItem(self.format_size(item["size"]))
            self.queue_table.setItem(i, 2, size_item)
            
            # Status
            status_item = QTableWidgetItem(item["status"])
            self.queue_table.setItem(i, 3, status_item)
            
            # Progress
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(item["progress"])
            self.queue_table.setCellWidget(i, 4, progress_bar)
        
        # Update the status label
        self.update_status_label()
        
    def update_status_label(self):
        """Update the status label with queue information."""
        queue_items = self.download_manager.get_queue_items()
        active = sum(1 for item in queue_items if item["status"] == "Downloading")
        queued = sum(1 for item in queue_items if item["status"] == "Queued")
        completed = sum(1 for item in queue_items if item["status"] == "Completed")
        failed = sum(1 for item in queue_items if item["status"] == "Failed")
        
        self.status_label.setText(
            f"Queue: {len(queue_items)} items | "
            f"Active: {active} | "
            f"Queued: {queued} | "
            f"Completed: {completed} | "
            f"Failed: {failed}"
        )
        
    def toggle_downloads(self):
        """Start or stop the download process."""
        if self.download_manager.is_running():
            self.download_manager.stop()
            self.start_stop_button.setText("Start Downloads")
        else:
            self.download_manager.start()
            self.start_stop_button.setText("Stop Downloads")
        
    def clear_queue(self):
        """Clear the download queue."""
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Clear Queue",
            "Are you sure you want to clear the download queue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.download_manager.clear_queue()
            self.load_queue()
        
    def show_context_menu(self, position: QPoint):
        """Show the context menu for the queue table.
        
        Args:
            position: Position where the context menu should be shown
        """
        # Get the selected row
        row = self.queue_table.indexAt(position).row()
        if row < 0:
            return
        
        # Get the file ID
        file_id = self.queue_table.item(row, 0).data(Qt.UserRole)
        
        # Create the context menu
        menu = QMenu(self)
        
        # Add actions
        remove_action = QAction("Remove from Queue", self)
        remove_action.triggered.connect(lambda: self.remove_from_queue(file_id))
        menu.addAction(remove_action)
        
        prioritize_action = QAction("Move to Top", self)
        prioritize_action.triggered.connect(lambda: self.prioritize_file(file_id))
        menu.addAction(prioritize_action)
        
        # Show the menu
        menu.exec_(self.queue_table.mapToGlobal(position))
        
    def remove_from_queue(self, file_id: int):
        """Remove a file from the download queue.
        
        Args:
            file_id: ID of the file to remove
        """
        self.download_manager.remove_from_queue(file_id)
        self.load_queue()
        
    def prioritize_file(self, file_id: int):
        """Move a file to the top of the download queue.
        
        Args:
            file_id: ID of the file to prioritize
        """
        self.download_manager.prioritize_file(file_id)
        self.load_queue()
        
    def on_download_started(self, file_id: int):
        """Handle the download started signal.
        
        Args:
            file_id: ID of the file that started downloading
        """
        # Find the row for this file
        for row in range(self.queue_table.rowCount()):
            if self.queue_table.item(row, 0).data(Qt.UserRole) == file_id:
                # Update the status
                self.queue_table.item(row, 3).setText("Downloading")
                break
        
        # Update the status label
        self.update_status_label()
        
    def on_download_progress(self, file_id: int, progress: float):
        """Handle the download progress signal.
        
        Args:
            file_id: ID of the file being downloaded
            progress: Download progress (0-100)
        """
        # Find the row for this file
        for row in range(self.queue_table.rowCount()):
            if self.queue_table.item(row, 0).data(Qt.UserRole) == file_id:
                # Update the progress bar
                progress_bar = self.queue_table.cellWidget(row, 4)
                progress_bar.setValue(int(progress))
                break
        
    def on_download_completed(self, file_id: int):
        """Handle the download completed signal.
        
        Args:
            file_id: ID of the file that completed downloading
        """
        # Find the row for this file
        for row in range(self.queue_table.rowCount()):
            if self.queue_table.item(row, 0).data(Qt.UserRole) == file_id:
                # Update the status
                self.queue_table.item(row, 3).setText("Completed")
                # Set progress to 100%
                progress_bar = self.queue_table.cellWidget(row, 4)
                progress_bar.setValue(100)
                break
        
        # Update the status label
        self.update_status_label()
        
    def on_download_failed(self, file_id: int, error: str):
        """Handle the download failed signal.
        
        Args:
            file_id: ID of the file that failed to download
            error: Error message
        """
        # Find the row for this file
        for row in range(self.queue_table.rowCount()):
            if self.queue_table.item(row, 0).data(Qt.UserRole) == file_id:
                # Update the status
                self.queue_table.item(row, 3).setText("Failed")
                # Set progress to 0%
                progress_bar = self.queue_table.cellWidget(row, 4)
                progress_bar.setValue(0)
                break
        
        # Update the status label
        self.update_status_label()
        
        # Show an error message
        QMessageBox.warning(self, "Download Failed", f"Failed to download file {file_id}: {error}")
        
    @staticmethod
    def format_size(size: int) -> str:
        """Format a file size in bytes to a human-readable string.
        
        Args:
            size: File size in bytes
            
        Returns:
            Human-readable file size string
        """
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
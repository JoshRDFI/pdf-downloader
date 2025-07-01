"""Download history tab for the PDF Downloader application.

This module contains the DownloadHistoryTab class for viewing download history.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QMenu, QAction, QMessageBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor

from src.db.download_model import DownloadModel


logger = logging.getLogger(__name__)


class DownloadHistoryTab(QWidget):
    """Tab for viewing download history.
    
    This tab allows users to view their download history and filter by various criteria.
    """
    
    def __init__(self, parent=None):
        """Initialize the download history tab."""
        super().__init__(parent)
        self.download_model = DownloadModel()
        self.init_ui()
        self.load_history()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses", None)
        self.status_filter.addItem("Completed", "completed")
        self.status_filter.addItem("Failed", "failed")
        self.status_filter.addItem("In Progress", "in_progress")
        self.status_filter.addItem("Pending", "pending")
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        
        # Date range filter
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))  # Default to 1 month ago
        self.date_from.dateChanged.connect(self.apply_filters)
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self.apply_filters)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by filename...")
        self.search_box.textChanged.connect(self.apply_filters)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_history)
        
        # Add widgets to filter layout
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_box)
        filter_layout.addWidget(self.refresh_button)
        
        # Add filter layout to main layout
        main_layout.addLayout(filter_layout)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Filename", "Status", "Started", "Completed", "Error", "File Path"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Stretch filename column
        self.history_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)  # Stretch error column
        self.history_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)  # Stretch file path column
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Add history table to main layout
        main_layout.addWidget(self.history_table)
    
    def load_history(self):
        """Load the download history from the database."""
        try:
            # Get the download history
            history = self.download_model.get_download_history(limit=1000)
            
            # Apply filters
            self.apply_filters(history)
        except Exception as e:
            logger.error(f"Error loading download history: {e}")
            QMessageBox.warning(self, "Error", f"Error loading download history: {e}")
    
    def apply_filters(self, history=None):
        """Apply filters to the download history.
        
        Args:
            history: Download history data (optional, will be loaded if not provided)
        """
        try:
            # Get the download history if not provided
            if history is None:
                history = self.download_model.get_download_history(limit=1000)
            
            # Get filter values
            status = self.status_filter.currentData()
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            search_text = self.search_box.text().lower()
            
            # Apply filters
            filtered_history = []
            for item in history:
                # Status filter
                if status and item["status"] != status:
                    continue
                
                # Date filter for started_at
                if item["started_at"]:
                    started_date = item["started_at"].split(" ")[0]  # Extract date part
                    if started_date < date_from or started_date > date_to:
                        continue
                
                # Search filter
                if search_text and search_text not in item.get("file_name", "").lower():
                    continue
                
                filtered_history.append(item)
            
            # Update the table
            self.update_table(filtered_history)
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            QMessageBox.warning(self, "Error", f"Error applying filters: {e}")
    
    def update_table(self, history):
        """Update the history table with the filtered data.
        
        Args:
            history: Filtered download history data
        """
        # Clear the table
        self.history_table.setRowCount(0)
        
        # Add rows to the table
        for item in history:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(item["id"]))
            id_item.setData(Qt.UserRole, item["id"])
            self.history_table.setItem(row, 0, id_item)
            
            # Filename
            filename = item.get("file_name", "")
            filename_item = QTableWidgetItem(filename)
            self.history_table.setItem(row, 1, filename_item)
            
            # Status
            status = item["status"]
            status_item = QTableWidgetItem(status.capitalize())
            if status == "completed":
                status_item.setForeground(QColor(0, 128, 0))  # Green
            elif status == "failed":
                status_item.setForeground(QColor(255, 0, 0))  # Red
            elif status == "in_progress":
                status_item.setForeground(QColor(0, 0, 255))  # Blue
            self.history_table.setItem(row, 2, status_item)
            
            # Started
            started_at = item["started_at"]
            started_item = QTableWidgetItem(started_at if started_at else "")
            self.history_table.setItem(row, 3, started_item)
            
            # Completed
            completed_at = item["completed_at"]
            completed_item = QTableWidgetItem(completed_at if completed_at else "")
            self.history_table.setItem(row, 4, completed_item)
            
            # Error
            error_message = item["error_message"]
            error_item = QTableWidgetItem(error_message if error_message else "")
            self.history_table.setItem(row, 5, error_item)
            
            # File Path
            # Get the local file path if available
            local_file_id = item["local_file_id"]
            file_path = ""
            if local_file_id:
                from src.db.local_file_model import LocalFileModel
                local_file_model = LocalFileModel()
                local_file = local_file_model.get_file_by_id(local_file_id)
                if local_file:
                    file_path = local_file["path"]
            
            path_item = QTableWidgetItem(file_path)
            self.history_table.setItem(row, 6, path_item)
    
    def show_context_menu(self, position):
        """Show context menu for the history table.
        
        Args:
            position: Position where the context menu should be shown
        """
        # Get the selected row
        row = self.history_table.rowAt(position.y())
        if row < 0:
            return
        
        # Get the download ID and status
        download_id = self.history_table.item(row, 0).data(Qt.UserRole)
        status = self.history_table.item(row, 2).text().lower()
        
        # Create menu
        menu = QMenu()
        
        # Add actions based on status
        if status == "failed":
            retry_action = QAction("Retry Download", self)
            menu.addAction(retry_action)
        
        if status in ["completed", "failed"]:
            open_file_action = QAction("Open File Location", self)
            menu.addAction(open_file_action)
        
        delete_action = QAction("Delete Record", self)
        menu.addAction(delete_action)
        
        # Show menu and handle action
        action = menu.exec_(self.history_table.mapToGlobal(position))
        
        if action == delete_action:
            self.delete_record(download_id)
        elif status == "failed" and action == retry_action:
            self.retry_download(download_id)
        elif status in ["completed", "failed"] and action == open_file_action:
            self.open_file_location(row)
    
    def delete_record(self, download_id):
        """Delete a download record.
        
        Args:
            download_id: ID of the download record to delete
        """
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Delete Record",
            "Are you sure you want to delete this download record?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Delete the record
                success = self.download_model.delete_download(download_id)
                
                if success:
                    # Reload the history
                    self.load_history()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete download record")
            except Exception as e:
                logger.error(f"Error deleting download record: {e}")
                QMessageBox.warning(self, "Error", f"Error deleting download record: {e}")
    
    def retry_download(self, download_id):
        """Retry a failed download.
        
        Args:
            download_id: ID of the download record to retry
        """
        try:
            # Get the download record
            download = self.download_model.get_download_by_id(download_id)
            if not download:
                QMessageBox.warning(self, "Error", "Download record not found")
                return
            
            # Get the remote file ID
            remote_file_id = download["remote_file_id"]
            
            # Add the file to the download queue
            from src.core.download_manager import DownloadManager
            download_manager = DownloadManager()
            success = download_manager.queue_download(remote_file_id)
            
            if success:
                QMessageBox.information(self, "Retry Download", "File added to download queue")
                # Reload the history
                self.load_history()
            else:
                QMessageBox.warning(self, "Error", "Failed to add file to download queue")
        except Exception as e:
            logger.error(f"Error retrying download: {e}")
            QMessageBox.warning(self, "Error", f"Error retrying download: {e}")
    
    def open_file_location(self, row):
        """Open the file location in the file explorer.
        
        Args:
            row: Row index in the history table
        """
        try:
            # Get the file path
            file_path = self.history_table.item(row, 6).text()
            
            if not file_path:
                QMessageBox.warning(self, "Error", "File path not available")
                return
            
            # Open the file location
            import os
            import subprocess
            import platform
            
            # Get the directory containing the file
            dir_path = os.path.dirname(file_path)
            
            # Open the directory in the file explorer
            if platform.system() == "Windows":
                os.startfile(dir_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", dir_path])
            else:  # Linux
                subprocess.call(["xdg-open", dir_path])
        except Exception as e:
            logger.error(f"Error opening file location: {e}")
            QMessageBox.warning(self, "Error", f"Error opening file location: {e}")
"""Library tab for the PDF Downloader application.

This module contains the LibraryTab class for browsing and managing downloaded files.
"""

import os
import logging
from typing import Dict, Any, List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFormLayout, QMessageBox, QComboBox, QProgressBar, QFileDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from src.db.remote_file_model import RemoteFileModel
from src.db.category_model import CategoryModel
from src.db.site_model import SiteModel
from src.core.download_manager import DownloadManager


logger = logging.getLogger(__name__)


class LibraryTab(QWidget):
    """Tab for browsing and managing downloaded files.
    
    This tab allows users to browse files by site and category,
    view file details, and download files.
    """
    
    def __init__(self, parent=None):
        """Initialize the library tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.site_model = SiteModel()
        self.category_model = CategoryModel()
        self.remote_file_model = RemoteFileModel()
        self.download_manager = DownloadManager()
        self.current_site_id = None
        self.current_category_id = None
        self.init_ui()
        self.load_sites()
        
        # Start the download manager
        self.download_manager.start()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Site and category selection
        selection_layout = QHBoxLayout()
        
        # Site selection
        site_layout = QFormLayout()
        self.site_combo = QComboBox()
        self.site_combo.currentIndexChanged.connect(self.on_site_changed)
        site_layout.addRow("Site:", self.site_combo)
        selection_layout.addLayout(site_layout)
        
        # Category selection
        category_layout = QFormLayout()
        self.category_combo = QComboBox()
        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        category_layout.addRow("Category:", self.category_combo)
        selection_layout.addLayout(category_layout)
        
        # Add selection layout to main layout
        layout.addLayout(selection_layout)
        
        # Table for displaying files
        self.files_table = QTableWidget(0, 5)  # 0 rows, 5 columns
        self.files_table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Size", "Status"])
        self.files_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.files_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.files_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.files_table.itemClicked.connect(self.select_file)
        layout.addWidget(self.files_table)
        
        # Buttons for table actions
        button_layout = QHBoxLayout()
        
        self.download_button = QPushButton("Download Selected")
        self.download_button.clicked.connect(self.download_file)
        self.download_button.setEnabled(False)
        button_layout.addWidget(self.download_button)
        
        self.view_button = QPushButton("View Selected")
        self.view_button.clicked.connect(self.view_file)
        self.view_button.setEnabled(False)
        button_layout.addWidget(self.view_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_files)
        button_layout.addWidget(self.refresh_button)
        
        layout.addLayout(button_layout)
        
        # Progress bar for downloads
        self.progress_layout = QFormLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_layout.addRow("Download Progress:", self.progress_bar)
        layout.addLayout(self.progress_layout)
    
    def load_sites(self):
        """Load sites from the database and display them in the combo box."""
        try:
            sites = self.site_model.get_all_sites()
            
            self.site_combo.clear()
            self.site_combo.addItem("All Sites", -1)
            
            for site in sites:
                self.site_combo.addItem(site["name"], site["id"])
            
            logger.info(f"Loaded {len(sites)} sites into the library tab")
        except Exception as e:
            logger.error(f"Error loading sites: {e}")
            QMessageBox.critical(self, "Database Error", f"Error loading sites: {str(e)}")
    
    def load_categories(self, site_id: Optional[int] = None):
        """Load categories from the database and display them in the combo box.
        
        Args:
            site_id: ID of the site to load categories for (optional)
        """
        try:
            self.category_combo.clear()
            self.category_combo.addItem("All Categories", -1)
            
            if site_id is not None and site_id != -1:
                categories = self.category_model.get_categories_by_site(site_id)
                
                for category in categories:
                    self.category_combo.addItem(category["name"], category["id"])
                
                logger.info(f"Loaded {len(categories)} categories for site {site_id}")
            
            self.current_category_id = -1
        except Exception as e:
            logger.error(f"Error loading categories: {e}")
            QMessageBox.critical(self, "Database Error", f"Error loading categories: {str(e)}")
    
    def load_files(self, site_id: Optional[int] = None, category_id: Optional[int] = None):
        """Load files from the database and display them in the table.
        
        Args:
            site_id: ID of the site to load files for (optional)
            category_id: ID of the category to load files for (optional)
        """
        try:
            self.files_table.setRowCount(0)
            
            files = []
            
            if site_id is not None and site_id != -1:
                if category_id is not None and category_id != -1:
                    # Load files for the specific site and category
                    files = self.remote_file_model.get_files_by_category(category_id)
                else:
                    # Load files for the specific site
                    files = self.remote_file_model.get_files_by_site(site_id)
            
            for file in files:
                row_position = self.files_table.rowCount()
                self.files_table.insertRow(row_position)
                
                self.files_table.setItem(row_position, 0, QTableWidgetItem(str(file["id"])))
                self.files_table.setItem(row_position, 1, QTableWidgetItem(file["name"]))
                self.files_table.setItem(row_position, 2, QTableWidgetItem(file.get("file_type", "")))
                
                # Format the file size
                size = file.get("size")
                size_text = "Unknown" if size is None else self._format_size(size)
                self.files_table.setItem(row_position, 3, QTableWidgetItem(size_text))
                
                # Check if the file is downloaded
                status = "Not Downloaded"  # TODO: Check if the file is downloaded
                self.files_table.setItem(row_position, 4, QTableWidgetItem(status))
            
            logger.info(f"Loaded {len(files)} files")
        except Exception as e:
            logger.error(f"Error loading files: {e}")
            QMessageBox.critical(self, "Database Error", f"Error loading files: {str(e)}")
    
    def on_site_changed(self, index):
        """Handle site selection change.
        
        Args:
            index: Index of the selected site in the combo box
        """
        site_id = self.site_combo.itemData(index)
        self.current_site_id = site_id
        
        # Load categories for the selected site
        self.load_categories(site_id)
        
        # Load files for the selected site
        self.load_files(site_id, self.current_category_id)
    
    def on_category_changed(self, index):
        """Handle category selection change.
        
        Args:
            index: Index of the selected category in the combo box
        """
        category_id = self.category_combo.itemData(index)
        self.current_category_id = category_id
        
        # Load files for the selected category
        self.load_files(self.current_site_id, category_id)
    
    def select_file(self):
        """Handle file selection in the table."""
        self.download_button.setEnabled(True)
        self.view_button.setEnabled(True)
    
    def download_file(self):
        """Download the selected file."""
        selected_rows = self.files_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        file_id = int(self.files_table.item(row, 0).text())
        file_name = self.files_table.item(row, 1).text()
        
        # Show the progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Queue the download
        success = self.download_manager.queue_download(file_id, self.update_progress)
        
        if success:
            QMessageBox.information(self, "Download Queued", f"File '{file_name}' has been queued for download.")
        else:
            QMessageBox.warning(self, "Download Failed", f"Failed to queue file '{file_name}' for download.")
            self.progress_bar.setVisible(False)
    
    def update_progress(self, file_id: int, progress: float):
        """Update the progress bar for a download.
        
        Args:
            file_id: ID of the file being downloaded
            progress: Progress of the download (0.0 to 1.0)
        """
        self.progress_bar.setValue(int(progress * 100))
        
        # Check if the download is complete
        if progress >= 1.0:
            self.progress_bar.setVisible(False)
            self.refresh_files()
    
    def view_file(self):
        """View the selected file."""
        selected_rows = self.files_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        file_id = int(self.files_table.item(row, 0).text())
        file_name = self.files_table.item(row, 1).text()
        
        # TODO: Implement file viewing
        QMessageBox.information(self, "View File", f"Viewing file '{file_name}' is not yet implemented.")
    
    def refresh_files(self):
        """Refresh the file list."""
        self.load_files(self.current_site_id, self.current_category_id)
    
    def _format_size(self, size: int) -> str:
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
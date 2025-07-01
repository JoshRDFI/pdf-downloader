"""Library tab for the PDF Downloader application.

This module contains the LibraryTab class for managing remote files.
"""

import logging
from typing import Dict, Any, List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QGroupBox, QRadioButton, QButtonGroup, QMessageBox,
    QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from src.db.remote_file_model import RemoteFileModel
from src.db.site_model import SiteModel
from src.core.site_scanner import SiteScannerThread
from src.core.download_manager import DownloadManager


logger = logging.getLogger(__name__)


class LibraryTab(QWidget):
    """Tab for managing remote files.
    
    This tab allows users to view and download remote files.
    """
    
    # Signal for when a file is added to the download queue
    file_queued = pyqtSignal(int)  # file_id
    
    def __init__(self, parent=None):
        """Initialize the library tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.remote_file_model = RemoteFileModel()
        self.site_model = SiteModel()
        self.download_manager = DownloadManager()
        self.init_ui()
        self.load_sites()
        self.load_file_stats()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Site selection
        site_group = QGroupBox("Site Selection")
        site_layout = QHBoxLayout(site_group)
        
        site_layout.addWidget(QLabel("Site:"))
        self.site_combo = QComboBox()
        self.site_combo.currentIndexChanged.connect(self.site_changed)
        site_layout.addWidget(self.site_combo)
        
        self.scan_button = QPushButton("Scan Site")
        self.scan_button.clicked.connect(self.scan_site)
        site_layout.addWidget(self.scan_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_files)
        site_layout.addWidget(self.refresh_button)
        
        layout.addWidget(site_group)
        
        # File filter
        filter_group = QGroupBox("File Filter")
        filter_layout = QHBoxLayout(filter_group)
        
        self.filter_all = QRadioButton("All Files")
        self.filter_all.setChecked(True)
        filter_layout.addWidget(self.filter_all)
        
        self.filter_pdf = QRadioButton("PDF Files")
        filter_layout.addWidget(self.filter_pdf)
        
        self.filter_epub = QRadioButton("EPUB Files")
        filter_layout.addWidget(self.filter_epub)
        
        self.filter_txt = QRadioButton("Text Files")
        filter_layout.addWidget(self.filter_txt)
        
        # Create a button group for the radio buttons
        self.filter_group = QButtonGroup()
        self.filter_group.addButton(self.filter_all, 0)
        self.filter_group.addButton(self.filter_pdf, 1)
        self.filter_group.addButton(self.filter_epub, 2)
        self.filter_group.addButton(self.filter_txt, 3)
        self.filter_group.buttonClicked.connect(self.filter_files)
        
        layout.addWidget(filter_group)
        
        # Search group
        search_group = QGroupBox("Search")
        search_layout = QHBoxLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by filename...")
        self.search_input.textChanged.connect(self.search_files)
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(lambda: self.search_files(self.search_input.text()))
        search_layout.addWidget(self.search_button)
        
        self.clear_search_button = QPushButton("Clear")
        self.clear_search_button.clicked.connect(self.clear_search)
        search_layout.addWidget(self.clear_search_button)
        
        layout.addWidget(search_group)
        
        # Statistics
        self.stats_label = QLabel("No remote files in database")
        layout.addWidget(self.stats_label)
        
        # Files table
        self.files_table = QTableWidget(0, 5)  # 0 rows, 5 columns
        self.files_table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Size", "Site"])
        self.files_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Stretch name column
        self.files_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.files_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.files_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.files_table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.files_table)
    
    def load_sites(self):
        """Load sites from the database."""
        try:
            # Clear the combo box
            self.site_combo.clear()
            
            # Add "All Sites" option
            self.site_combo.addItem("All Sites", None)
            
            # Get sites from the database
            sites = self.site_model.get_sites()
            
            # Add sites to the combo box
            for site in sites:
                self.site_combo.addItem(site["name"], site["id"])
            
            logger.info(f"Loaded {len(sites)} sites")
        except Exception as e:
            logger.error(f"Error loading sites: {e}")
            QMessageBox.critical(self, "Database Error", f"Error loading sites: {str(e)}")
    
    def load_file_stats(self):
        """Load file statistics from the database."""
        try:
            # Get file statistics
            total_files = self.remote_file_model.count_files()
            pdf_files = self.remote_file_model.count_files_by_type("pdf")
            epub_files = self.remote_file_model.count_files_by_type("epub")
            txt_files = self.remote_file_model.count_files_by_type("txt")
            
            # Update the stats label
            self.stats_label.setText(
                f"Total Files: {total_files} | "
                f"PDF: {pdf_files} | "
                f"EPUB: {epub_files} | "
                f"TXT: {txt_files}"
            )
            
            logger.info(f"Loaded file statistics: {total_files} total files")
        except Exception as e:
            logger.error(f"Error loading file statistics: {e}")
            QMessageBox.critical(self, "Database Error", f"Error loading file statistics: {str(e)}")
    
    def site_changed(self):
        """Handle site selection change."""
        self.refresh_files()
    
    def scan_site(self):
        """Scan the selected site for files."""
        # Get the selected site ID
        site_id = self.site_combo.currentData()
        
        if site_id is None:
            QMessageBox.warning(self, "No Site Selected", "Please select a specific site to scan.")
            return
        
        try:
            # Get the site information
            site = self.site_model.get_site_by_id(site_id)
            
            if not site:
                QMessageBox.warning(self, "Site Not Found", "The selected site was not found in the database.")
                return
            
            # Create and start the scanner thread
            self.scanner_thread = SiteScannerThread(site)
            self.scanner_thread.scan_complete.connect(self.scan_complete)
            self.scanner_thread.start()
            
            # Disable the scan button while scanning
            self.scan_button.setEnabled(False)
            self.scan_button.setText("Scanning...")
            
            logger.info(f"Started scanning site: {site['name']}")
        except Exception as e:
            logger.error(f"Error starting site scan: {e}")
            QMessageBox.critical(self, "Scan Error", f"Error starting site scan: {str(e)}")
    
    def scan_complete(self, result):
        """Handle scan completion.
        
        Args:
            result: Scan result dictionary
        """
        # Re-enable the scan button
        self.scan_button.setEnabled(True)
        self.scan_button.setText("Scan Site")
        
        # Check for errors
        if "error" in result:
            QMessageBox.critical(self, "Scan Error", f"Error scanning site: {result['error']}")
            logger.error(f"Scan error: {result['error']}")
            return
        
        # Show scan results
        files_found = result.get("files_found", 0)
        files_added = result.get("files_added", 0)
        
        QMessageBox.information(
            self, "Scan Complete",
            f"Scan completed successfully.\n\n"
            f"Files found: {files_found}\n"
            f"New files added: {files_added}"
        )
        
        # Refresh the file list and statistics
        self.refresh_files()
        self.load_file_stats()
        
        logger.info(f"Scan completed: {files_found} files found, {files_added} new files added")
    
    def refresh_files(self):
        """Refresh the files table."""
        # Get the selected site ID
        site_id = self.site_combo.currentData()
        
        # Get the current filter
        filter_id = self.filter_group.checkedId()
        file_type = None
        
        if filter_id == 1:
            file_type = "pdf"
        elif filter_id == 2:
            file_type = "epub"
        elif filter_id == 3:
            file_type = "txt"
        
        try:
            # Get files from the database
            if site_id is None:
                # All sites
                if file_type:
                    files = self.remote_file_model.get_files_by_type(file_type)
                else:
                    files = self.remote_file_model.get_files()
            else:
                # Specific site
                if file_type:
                    files = self.remote_file_model.get_files_by_site_and_type(site_id, file_type)
                else:
                    files = self.remote_file_model.get_files_by_site(site_id)
            
            # Clear the table
            self.files_table.setRowCount(0)
            
            # Add files to the table
            for file in files:
                row_position = self.files_table.rowCount()
                self.files_table.insertRow(row_position)
                
                # ID
                id_item = QTableWidgetItem(str(file["id"]))
                id_item.setData(Qt.UserRole, file["id"])  # Store the ID as user data
                self.files_table.setItem(row_position, 0, id_item)
                
                # Name
                self.files_table.setItem(row_position, 1, QTableWidgetItem(file["name"]))
                
                # Type
                self.files_table.setItem(row_position, 2, QTableWidgetItem(file["file_type"].upper()))
                
                # Size
                size = file.get("size")
                size_text = "Unknown" if size is None else self._format_size(size)
                self.files_table.setItem(row_position, 3, QTableWidgetItem(size_text))
                
                # Site
                site_name = "Unknown"
                if file["site_id"]:
                    site = self.site_model.get_site_by_id(file["site_id"])
                    if site:
                        site_name = site["name"]
                self.files_table.setItem(row_position, 4, QTableWidgetItem(site_name))
            
            logger.info(f"Loaded {len(files)} files")
        except Exception as e:
            logger.error(f"Error refreshing files: {e}")
            QMessageBox.critical(self, "Database Error", f"Error refreshing files: {str(e)}")
    
    def filter_files(self):
        """Filter files based on the selected filter."""
        self.refresh_files()
    
    def search_files(self, search_text):
        """Search for files by name.
        
        Args:
            search_text: Text to search for
        """
        # Get the selected site ID
        site_id = self.site_combo.currentData()
        
        # Get the current filter
        filter_id = self.filter_group.checkedId()
        file_type = None
        
        if filter_id == 1:
            file_type = "pdf"
        elif filter_id == 2:
            file_type = "epub"
        elif filter_id == 3:
            file_type = "txt"
        
        try:
            # Get files from the database
            if site_id is None:
                # All sites
                if file_type:
                    files = self.remote_file_model.get_files_by_type(file_type)
                else:
                    files = self.remote_file_model.get_files()
            else:
                # Specific site
                if file_type:
                    files = self.remote_file_model.get_files_by_site_and_type(site_id, file_type)
                else:
                    files = self.remote_file_model.get_files_by_site(site_id)
            
            # Apply search filter
            search_text = search_text.lower()
            filtered_files = []
            
            for file in files:
                # Check if the search text is in the file name
                if search_text in file["name"].lower():
                    filtered_files.append(file)
            
            # Clear the table
            self.files_table.setRowCount(0)
            
            # Add filtered files to the table
            for file in filtered_files:
                row_position = self.files_table.rowCount()
                self.files_table.insertRow(row_position)
                
                # ID
                id_item = QTableWidgetItem(str(file["id"]))
                id_item.setData(Qt.UserRole, file["id"])  # Store the ID as user data
                self.files_table.setItem(row_position, 0, id_item)
                
                # Name
                self.files_table.setItem(row_position, 1, QTableWidgetItem(file["name"]))
                
                # Type
                self.files_table.setItem(row_position, 2, QTableWidgetItem(file["file_type"].upper()))
                
                # Size
                size = file.get("size")
                size_text = "Unknown" if size is None else self._format_size(size)
                self.files_table.setItem(row_position, 3, QTableWidgetItem(size_text))
                
                # Site
                site_name = "Unknown"
                if file["site_id"]:
                    site = self.site_model.get_site_by_id(file["site_id"])
                    if site:
                        site_name = site["name"]
                self.files_table.setItem(row_position, 4, QTableWidgetItem(site_name))
            
            logger.info(f"Found {len(filtered_files)} files matching '{search_text}'")
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            QMessageBox.critical(self, "Search Error", f"Error searching files: {str(e)}")
    
    def clear_search(self):
        """Clear the search and show all files."""
        self.search_input.clear()
        self.refresh_files()
    
    def show_context_menu(self, position):
        """Show context menu for the files table.
        
        Args:
            position: Position where the context menu should be shown
        """
        # Get the selected row
        row = self.files_table.rowAt(position.y())
        if row < 0:
            return
        
        # Get the file ID
        file_id = self.files_table.item(row, 0).data(Qt.UserRole)
        
        # Create menu
        menu = QMenu()
        
        # Add actions
        download_action = QAction("Add to Download Queue", self)
        menu.addAction(download_action)
        
        # Show menu and handle action
        action = menu.exec_(self.files_table.mapToGlobal(position))
        
        if action == download_action:
            self.queue_download(file_id)
    
    def queue_download(self, file_id):
        """Add a file to the download queue.
        
        Args:
            file_id: ID of the file to download
        """
        try:
            # Add the file to the download queue
            success = self.download_manager.queue_download(file_id)
            
            if success:
                # Emit the file_queued signal
                self.file_queued.emit(file_id)
                
                # Show a message
                QMessageBox.information(self, "Download Queued", "File added to download queue.")
                logger.info(f"File {file_id} added to download queue")
            else:
                QMessageBox.warning(self, "Queue Error", "Failed to add file to download queue.")
                logger.error(f"Failed to add file {file_id} to download queue")
        except Exception as e:
            logger.error(f"Error queueing download: {e}")
            QMessageBox.critical(self, "Queue Error", f"Error queueing download: {str(e)}")
    
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
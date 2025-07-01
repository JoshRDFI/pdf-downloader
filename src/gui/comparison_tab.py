"""Comparison tab for the PDF Downloader application.

This module provides a tab for comparing local and remote files.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QComboBox, QCheckBox,
                             QMessageBox, QProgressBar, QHeaderView, QSplitter,
                             QTabWidget, QMenu, QAction)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt5.QtGui import QColor

import logging
from typing import Dict, Any, List, Optional

from src.core.file_comparison import FileComparisonService
from src.db.remote_file_model import RemoteFileModel


logger = logging.getLogger(__name__)


class ComparisonThread(QThread):
    """Thread for comparing local and remote files.
    
    This thread runs the file comparison in the background to avoid blocking the UI.
    """
    
    comparison_complete = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, site_id: Optional[int] = None):
        """Initialize the comparison thread.
        
        Args:
            site_id: ID of the site to compare files for (optional)
        """
        super().__init__()
        self.site_id = site_id
        self.comparison_service = FileComparisonService()
    
    def run(self):
        """Run the comparison thread."""
        try:
            # Compare files
            result = self.comparison_service.compare_files(self.site_id)
            self.comparison_complete.emit(result)
        except Exception as e:
            logger.error(f"Error comparing files: {e}")
            self.error.emit(str(e))


class ComparisonTab(QWidget):
    """Tab for comparing local and remote files.
    
    This tab allows users to compare local and remote files, identify new, updated,
    and corrupted files, and build a download queue.
    """
    
    def __init__(self, parent=None):
        """Initialize the comparison tab."""
        super().__init__(parent)
        self.comparison_service = FileComparisonService()
        self.remote_file_model = RemoteFileModel()
        self.download_manager = DownloadManager()
        self.comparison_thread = None
        self.comparison_results = None

        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Site selection
        self.site_label = QLabel("Site:")
        self.site_combo = QComboBox()
        self.site_combo.addItem("All Sites", None)
        
        # Load sites
        self.load_sites()
        
        # Compare button
        self.compare_button = QPushButton("Compare Files")
        self.compare_button.clicked.connect(self.start_comparison)
        
        # Add to controls layout
        controls_layout.addWidget(self.site_label)
        controls_layout.addWidget(self.site_combo)
        controls_layout.addWidget(self.compare_button)
        controls_layout.addStretch()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Status label
        self.status_label = QLabel("Ready")
        
        # Tab widget for different file categories
        self.tab_widget = QTabWidget()
        
        # New files tab
        self.new_files_tab = QWidget()
        new_files_layout = QVBoxLayout(self.new_files_tab)
        self.new_files_table = QTableWidget()
        self.new_files_table.setColumnCount(5)
        self.new_files_table.setHorizontalHeaderLabels(["Name", "Size", "Type", "Category", "URL"])
        self.new_files_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.new_files_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.new_files_table.customContextMenuRequested.connect(self.show_new_files_context_menu)
        new_files_layout.addWidget(self.new_files_table)
        
        # Updated files tab
        self.updated_files_tab = QWidget()
        updated_files_layout = QVBoxLayout(self.updated_files_tab)
        self.updated_files_table = QTableWidget()
        self.updated_files_table.setColumnCount(6)
        self.updated_files_table.setHorizontalHeaderLabels(["Name", "Local Size", "Remote Size", "Type", "Category", "Path"])
        self.updated_files_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.updated_files_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.updated_files_table.customContextMenuRequested.connect(self.show_updated_files_context_menu)
        updated_files_layout.addWidget(self.updated_files_table)
        
        # Corrupted files tab
        self.corrupted_files_tab = QWidget()
        corrupted_files_layout = QVBoxLayout(self.corrupted_files_tab)
        self.corrupted_files_table = QTableWidget()
        self.corrupted_files_table.setColumnCount(6)
        self.corrupted_files_table.setHorizontalHeaderLabels(["Name", "Size", "Type", "Path", "Error", "URL"])
        self.corrupted_files_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.corrupted_files_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.corrupted_files_table.customContextMenuRequested.connect(self.show_corrupted_files_context_menu)
        corrupted_files_layout.addWidget(self.corrupted_files_table)
        
        # OK files tab
        self.ok_files_tab = QWidget()
        ok_files_layout = QVBoxLayout(self.ok_files_tab)
        self.ok_files_table = QTableWidget()
        self.ok_files_table.setColumnCount(5)
        self.ok_files_table.setHorizontalHeaderLabels(["Name", "Size", "Type", "Category", "Path"])
        self.ok_files_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ok_files_layout.addWidget(self.ok_files_table)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.new_files_tab, "New Files (0)")
        self.tab_widget.addTab(self.updated_files_tab, "Updated Files (0)")
        self.tab_widget.addTab(self.corrupted_files_tab, "Corrupted Files (0)")
        self.tab_widget.addTab(self.ok_files_tab, "OK Files (0)")
        
        # Add widgets to main layout
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.status_label)
    
    def load_sites(self):
        """Load sites into the site combo box."""
        try:
            # Clear existing items (except "All Sites")
            while self.site_combo.count() > 1:
                self.site_combo.removeItem(1)
            
            # Get all sites
            sites = self.remote_file_model.get_all_sites()
            
            # Add sites to combo box
            for site in sites:
                self.site_combo.addItem(site["name"], site["id"])
        except Exception as e:
            logger.error(f"Error loading sites: {e}")
            QMessageBox.warning(self, "Error", f"Error loading sites: {e}")
    
    def start_comparison(self):
        """Start the file comparison process."""
        try:
            # Get selected site ID
            site_id = self.site_combo.currentData()
            
            # Show progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Update status
            self.status_label.setText("Comparing files...")
            
            # Disable compare button
            self.compare_button.setEnabled(False)
            
            # Create and start comparison thread
            self.comparison_thread = ComparisonThread(site_id)
            self.comparison_thread.comparison_complete.connect(self.handle_comparison_complete)
            self.comparison_thread.error.connect(self.handle_comparison_error)
            self.comparison_thread.start()
        except Exception as e:
            logger.error(f"Error starting comparison: {e}")
            QMessageBox.warning(self, "Error", f"Error starting comparison: {e}")
            self.progress_bar.setVisible(False)
            self.compare_button.setEnabled(True)
            self.status_label.setText("Ready")
    
    def handle_comparison_complete(self, results):
        """Handle the completion of the file comparison.
        
        Args:
            results: Dictionary containing comparison results
        """
        try:
            # Store results
            self.comparison_results = results
            
            # Update tables
            self.update_new_files_table(results["new_files"])
            self.update_updated_files_table(results["updated_files"])
            self.update_corrupted_files_table(results["corrupted_files"])
            self.update_ok_files_table(results["ok_files"])
            
            # Update tab titles
            self.tab_widget.setTabText(0, f"New Files ({len(results['new_files'])})")
            self.tab_widget.setTabText(1, f"Updated Files ({len(results['updated_files'])})")
            self.tab_widget.setTabText(2, f"Corrupted Files ({len(results['corrupted_files'])})")
            self.tab_widget.setTabText(3, f"OK Files ({len(results['ok_files'])})")
            
            # Hide progress bar
            self.progress_bar.setVisible(False)
            
            # Enable compare button
            self.compare_button.setEnabled(True)
            
            # Update status
            self.status_label.setText(
                f"Comparison complete: {len(results['new_files'])} new, "
                f"{len(results['updated_files'])} updated, "
                f"{len(results['corrupted_files'])} corrupted, "
                f"{len(results['ok_files'])} OK"
            )
        except Exception as e:
            logger.error(f"Error handling comparison results: {e}")
            QMessageBox.warning(self, "Error", f"Error handling comparison results: {e}")
            self.progress_bar.setVisible(False)
            self.compare_button.setEnabled(True)
            self.status_label.setText("Ready")
    
    def handle_comparison_error(self, error_message):
        """Handle an error during file comparison.
        
        Args:
            error_message: Error message
        """
        logger.error(f"Comparison error: {error_message}")
        QMessageBox.warning(self, "Error", f"Error comparing files: {error_message}")
        self.progress_bar.setVisible(False)
        self.compare_button.setEnabled(True)
        self.status_label.setText("Ready")
    
    def update_new_files_table(self, new_files):
        """Update the new files table.
        
        Args:
            new_files: List of new files
        """
        # Clear table
        self.new_files_table.setRowCount(0)
        
        # Add rows
        for i, file in enumerate(new_files):
            self.new_files_table.insertRow(i)
            
            # Set data
            self.new_files_table.setItem(i, 0, QTableWidgetItem(file["name"]))
            self.new_files_table.setItem(i, 1, QTableWidgetItem(str(file["size"])))
            self.new_files_table.setItem(i, 2, QTableWidgetItem(file["file_type"]))
            self.new_files_table.setItem(i, 3, QTableWidgetItem(file.get("category", "")))
            self.new_files_table.setItem(i, 4, QTableWidgetItem(file["url"]))
            
            # Store file ID in the first column
            self.new_files_table.item(i, 0).setData(Qt.UserRole, file["id"])
    
    def update_updated_files_table(self, updated_files):
        """Update the updated files table.
        
        Args:
            updated_files: List of updated files
        """
        # Clear table
        self.updated_files_table.setRowCount(0)
        
        # Add rows
        for i, item in enumerate(updated_files):
            self.updated_files_table.insertRow(i)
            
            remote_file = item["remote"]
            local_file = item["local"]
            
            # Set data
            self.updated_files_table.setItem(i, 0, QTableWidgetItem(remote_file["name"]))
            self.updated_files_table.setItem(i, 1, QTableWidgetItem(str(local_file["size"])))
            self.updated_files_table.setItem(i, 2, QTableWidgetItem(str(remote_file["size"])))
            self.updated_files_table.setItem(i, 3, QTableWidgetItem(remote_file["file_type"]))
            self.updated_files_table.setItem(i, 4, QTableWidgetItem(remote_file.get("category", "")))
            self.updated_files_table.setItem(i, 5, QTableWidgetItem(local_file["path"]))
            
            # Store file IDs in the first column
            self.updated_files_table.item(i, 0).setData(Qt.UserRole, {
                "remote_id": remote_file["id"],
                "local_id": local_file["id"]
            })
            
            # Highlight size difference
            if local_file["size"] != remote_file["size"]:
                self.updated_files_table.item(i, 1).setBackground(QColor(255, 200, 200))
                self.updated_files_table.item(i, 2).setBackground(QColor(200, 255, 200))
    
    def update_corrupted_files_table(self, corrupted_files):
        """Update the corrupted files table.
        
        Args:
            corrupted_files: List of corrupted files
        """
        # Clear table
        self.corrupted_files_table.setRowCount(0)
        
        # Add rows
        for i, item in enumerate(corrupted_files):
            self.corrupted_files_table.insertRow(i)
            
            remote_file = item["remote"]
            local_file = item["local"]
            error = item["error"]
            
            # Set data
            self.corrupted_files_table.setItem(i, 0, QTableWidgetItem(remote_file["name"]))
            self.corrupted_files_table.setItem(i, 1, QTableWidgetItem(str(local_file["size"])))
            self.corrupted_files_table.setItem(i, 2, QTableWidgetItem(remote_file["file_type"]))
            self.corrupted_files_table.setItem(i, 3, QTableWidgetItem(local_file["path"]))
            self.corrupted_files_table.setItem(i, 4, QTableWidgetItem(error))
            self.corrupted_files_table.setItem(i, 5, QTableWidgetItem(remote_file["url"]))
            
            # Store file IDs in the first column
            self.corrupted_files_table.item(i, 0).setData(Qt.UserRole, {
                "remote_id": remote_file["id"],
                "local_id": local_file["id"]
            })
            
            # Highlight error
            self.corrupted_files_table.item(i, 4).setBackground(QColor(255, 200, 200))
    
    def update_ok_files_table(self, ok_files):
        """Update the OK files table.
        
        Args:
            ok_files: List of OK files
        """
        # Clear table
        self.ok_files_table.setRowCount(0)
        
        # Add rows
        for i, item in enumerate(ok_files):
            self.ok_files_table.insertRow(i)
            
            remote_file = item["remote"]
            local_file = item["local"]
            
            # Set data
            self.ok_files_table.setItem(i, 0, QTableWidgetItem(remote_file["name"]))
            self.ok_files_table.setItem(i, 1, QTableWidgetItem(str(local_file["size"])))
            self.ok_files_table.setItem(i, 2, QTableWidgetItem(remote_file["file_type"]))
            self.ok_files_table.setItem(i, 3, QTableWidgetItem(remote_file.get("category", "")))
            self.ok_files_table.setItem(i, 4, QTableWidgetItem(local_file["path"]))
            
            # Store file IDs in the first column
            self.ok_files_table.item(i, 0).setData(Qt.UserRole, {
                "remote_id": remote_file["id"],
                "local_id": local_file["id"]
            })
    
    def show_new_files_context_menu(self, position):
        """Show context menu for new files table.
        
        Args:
            position: Position where the context menu should be shown
        """
        # Get selected row
        row = self.new_files_table.indexAt(position).row()
        if row < 0:
            return
        
        # Create menu
        menu = QMenu()
        add_to_queue_action = QAction("Add to Download Queue", self)
        menu.addAction(add_to_queue_action)
        
        # Show menu and handle action
        action = menu.exec_(self.new_files_table.mapToGlobal(position))
        
        if action == add_to_queue_action:
            # Get file ID
            file_id = self.new_files_table.item(row, 0).data(Qt.UserRole)
            # Add file to download queue
            success = self.download_manager.queue_download(file_id)

            if success:
                QMessageBox.information(self, "Add to Queue", f"File {file_id} added to download queue")
            else:
                QMessageBox.warning(self, "Add to Queue", f"Failed to add file {file_id} to download queue")
            QMessageBox.information(self, "Add to Queue", f"File {file_id} added to download queue")
    
    def show_updated_files_context_menu(self, position):
        """Show context menu for updated files table.
        
        Args:
            position: Position where the context menu should be shown
        """
        # Get selected row
        row = self.updated_files_table.indexAt(position).row()
        if row < 0:
            return
        
        # Create menu
        menu = QMenu()
        add_to_queue_action = QAction("Add to Download Queue", self)
        menu.addAction(add_to_queue_action)
        
        # Show menu and handle action
        action = menu.exec_(self.updated_files_table.mapToGlobal(position))
        
        if action == add_to_queue_action:
            # Get file IDs
            file_ids = self.updated_files_table.item(row, 0).data(Qt.UserRole)
            
            # Add file to download queue
            success = self.download_manager.queue_download(file_ids['remote_id'])

            if success:
                QMessageBox.information(self, "Add to Queue", 
                                   f"File {file_ids['remote_id']} added to download queue")
    
    def show_corrupted_files_context_menu(self, position):
        """Show context menu for corrupted files table.
        
        Args:
            position: Position where the context menu should be shown
        """
        # Get selected row
        row = self.corrupted_files_table.indexAt(position).row()
        if row < 0:
            return
        
        # Create menu
        menu = QMenu()
        add_to_queue_action = QAction("Add to Download Queue", self)
        menu.addAction(add_to_queue_action)
        
        # Show menu and handle action
        action = menu.exec_(self.corrupted_files_table.mapToGlobal(position))
        
        if action == add_to_queue_action:
            # Get file IDs
            file_ids = self.corrupted_files_table.item(row, 0).data(Qt.UserRole)
            
            # Add file to download queue
            success = self.download_manager.queue_download(file_ids['remote_id'])

            if success:
                QMessageBox.information(self, "Add to Queue",
                                   f"File {file_ids['remote_id']} added to download queue")
            else:
                QMessageBox.warning(self, "Add to Queue",
                                f"Failed to add file {file_ids['remote_id']} to download queue")
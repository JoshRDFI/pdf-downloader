"""Local library tab for the PDF Downloader application.

This module contains the LocalLibraryTab class for managing local files.
"""

import os
import logging
from typing import Dict, Any, List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFormLayout, QMessageBox, QComboBox, QProgressBar, QFileDialog,
    QGroupBox, QRadioButton, QButtonGroup, QListWidget, QListWidgetItem,
    QMenu, QAction
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from src.db.local_file_model import LocalFileModel
from src.core.directory_scanner import DirectoryScanner
from config import config


logger = logging.getLogger(__name__)


class ScanThread(QThread):
    """Thread for scanning a directory in the background.
    
    This thread runs the directory scanning process in the background to keep
    the UI responsive during long-running scans.
    """
    
    scan_progress = pyqtSignal(int, int, str)
    scan_complete = pyqtSignal(dict)
    
    def __init__(self, root_dir):
        """Initialize the scan thread.
        
        Args:
            root_dir: Root directory to scan
        """
        super().__init__()
        self.root_dir = root_dir
        self.scanner = DirectoryScanner()
    
    def run(self):
        """Run the scan thread."""
        result = self.scanner.scan_directory(self.root_dir, self.update_progress)
        self.scan_complete.emit(result)
    
    def update_progress(self, files_processed, total_files, current_file):
        """Update the scan progress.
        
        Args:
            files_processed: Number of files processed so far
            total_files: Total number of files to process
            current_file: Path of the current file being processed
        """
        self.scan_progress.emit(files_processed, total_files, current_file)
    
    def cancel(self):
        """Cancel the scan operation."""
        self.scanner.cancel_scan()


class LocalLibraryTab(QWidget):
    """Tab for managing local files.
    
    This tab allows users to scan local directories, view file information,
    and manage local files.
    """
    
    def __init__(self, parent=None):
        """Initialize the local library tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.local_file_model = LocalFileModel()
        self.directory_scanner = DirectoryScanner()
        self.scan_thread = None
        self.init_ui()
        self.load_file_stats()
        self.load_directories()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Directory management group
        dir_group = QGroupBox("Directory Management")
        dir_layout = QVBoxLayout(dir_group)
        
        # Directory list
        self.dir_list = QListWidget()
        self.dir_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dir_list.customContextMenuRequested.connect(self.show_dir_context_menu)
        dir_layout.addWidget(self.dir_list)
        
        # Directory buttons
        dir_button_layout = QHBoxLayout()
        
        self.add_dir_button = QPushButton("Add Directory")
        self.add_dir_button.clicked.connect(self.add_directory)
        dir_button_layout.addWidget(self.add_dir_button)
        
        self.remove_dir_button = QPushButton("Remove Directory")
        self.remove_dir_button.clicked.connect(self.remove_directory)
        self.remove_dir_button.setEnabled(False)
        dir_button_layout.addWidget(self.remove_dir_button)
        
        self.scan_all_button = QPushButton("Scan All Directories")
        self.scan_all_button.clicked.connect(self.scan_all_directories)
        dir_button_layout.addWidget(self.scan_all_button)
        
        dir_layout.addLayout(dir_button_layout)
        
        # Add directory group to main layout
        layout.addWidget(dir_group)
        
        # Progress group
        progress_group = QGroupBox("Scan Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_label)
        
        self.cancel_button = QPushButton("Cancel Scan")
        self.cancel_button.clicked.connect(self.cancel_scan)
        self.cancel_button.setEnabled(False)
        progress_layout.addWidget(self.cancel_button)
        
        # Add progress group to main layout
        layout.addWidget(progress_group)
        
        # File statistics group
        stats_group = QGroupBox("File Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("No files in database")
        stats_layout.addWidget(self.stats_label)
        
        # Add stats group to main layout
        layout.addWidget(stats_group)
        
        # File filter group
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
        
        # Add filter group to main layout
        layout.addWidget(filter_group)
        
        # Table for displaying files
        self.files_table = QTableWidget(0, 4)  # 0 rows, 4 columns
        self.files_table.setHorizontalHeaderLabels(["ID", "Path", "Type", "Size"])
        self.files_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.files_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.files_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.files_table)
        
        # Buttons for table actions
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_files)
        button_layout.addWidget(self.refresh_button)
        
        self.clear_button = QPushButton("Clear Database")
        self.clear_button.clicked.connect(self.clear_database)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # Connect directory list selection
        self.dir_list.itemSelectionChanged.connect(self.on_dir_selection_changed)
    
    def load_directories(self):
        """Load the list of directories from the configuration."""
        # Clear the list
        self.dir_list.clear()
        
        # Get the directories from the configuration
        directories = config.get_local_directories()
        
        # Add the directories to the list
        for directory in directories:
            item = QListWidgetItem(directory)
            self.dir_list.addItem(item)
    
    def add_directory(self):
        """Add a directory to the list."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if directory:
            # Add the directory to the configuration
            if config.add_local_directory(directory):
                # Reload the directory list
                self.load_directories()
                
                # Ask if the user wants to scan the directory now
                reply = QMessageBox.question(
                    self, "Scan Directory",
                    f"Do you want to scan the directory '{directory}' now?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    self.scan_directory(directory)
            else:
                QMessageBox.critical(self, "Error", f"Failed to add directory '{directory}' to the configuration.")
    
    def remove_directory(self):
        """Remove the selected directory from the list."""
        selected_items = self.dir_list.selectedItems()
        
        if not selected_items:
            return
        
        directory = selected_items[0].text()
        
        # Confirm the removal
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove the directory '{directory}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove the directory from the configuration
            if config.remove_local_directory(directory):
                # Reload the directory list
                self.load_directories()
            else:
                QMessageBox.critical(self, "Error", f"Failed to remove directory '{directory}' from the configuration.")
    
    def on_dir_selection_changed(self):
        """Handle the directory selection change."""
        selected_items = self.dir_list.selectedItems()
        self.remove_dir_button.setEnabled(len(selected_items) > 0)
    
    def show_dir_context_menu(self, position):
        """Show the context menu for the directory list.
        
        Args:
            position: Position where the context menu should be shown
        """
        # Get the item at the position
        item = self.dir_list.itemAt(position)
        
        if item is None:
            return
        
        # Create the context menu
        menu = QMenu()
        
        # Add actions
        scan_action = QAction("Scan Directory", self)
        scan_action.triggered.connect(lambda: self.scan_directory(item.text()))
        menu.addAction(scan_action)
        
        remove_action = QAction("Remove Directory", self)
        remove_action.triggered.connect(self.remove_directory)
        menu.addAction(remove_action)
        
        # Show the menu
        menu.exec_(self.dir_list.mapToGlobal(position))
    
    def scan_directory(self, directory=None):
        """Scan a directory for files.
        
        Args:
            directory: Directory to scan (optional, will use the selected directory if not provided)
        """
        if directory is None:
            # Get the selected directory
            selected_items = self.dir_list.selectedItems()
            
            if not selected_items:
                QMessageBox.warning(self, "No Directory", "Please select a directory to scan.")
                return
            
            directory = selected_items[0].text()
        
        if not os.path.isdir(directory):
            QMessageBox.warning(self, "Invalid Directory", f"The directory '{directory}' does not exist.")
            return
        
        # Disable the scan buttons and enable the cancel button
        self.scan_all_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        
        # Reset the progress bar
        self.progress_bar.setValue(0)
        self.progress_label.setText("Scanning...")
        
        # Create and start the scan thread
        self.scan_thread = ScanThread(directory)
        self.scan_thread.scan_progress.connect(self.update_scan_progress)
        self.scan_thread.scan_complete.connect(self.on_scan_complete)
        self.scan_thread.start()
        
        logger.info(f"Started scanning directory: {directory}")
    
    def scan_all_directories(self):
        """Scan all directories in the list."""
        # Get the directories from the configuration
        directories = config.get_local_directories()
        
        if not directories:
            QMessageBox.warning(self, "No Directories", "There are no directories to scan.")
            return
        
        # Scan the first directory
        self.current_scan_index = 0
        self.scan_directory(directories[self.current_scan_index])
    
    def update_scan_progress(self, files_processed, total_files, current_file):
        """Update the scan progress.
        
        Args:
            files_processed: Number of files processed so far
            total_files: Total number of files to process
            current_file: Path of the current file being processed
        """
        if total_files > 0:
            progress = int((files_processed / total_files) * 100)
            self.progress_bar.setValue(progress)
        
        if current_file:
            # Truncate the path if it's too long
            if len(current_file) > 50:
                current_file = "..." + current_file[-47:]
            
            self.progress_label.setText(f"Scanning: {current_file}")
        else:
            self.progress_label.setText(f"Processed {files_processed} of {total_files} files")
    
    def on_scan_complete(self, result):
        """Handle the completion of a directory scan.
        
        Args:
            result: Dictionary containing scan results
        """
        # Re-enable the scan button and disable the cancel button
        self.scan_all_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        if result["cancelled"]:
            self.progress_label.setText("Scan cancelled")
            QMessageBox.information(self, "Scan Cancelled", "The directory scan was cancelled.")
        elif result["success"]:
            self.progress_label.setText("Scan completed successfully")
            
            # Update the file statistics
            self.load_file_stats()
            
            # Refresh the file list
            self.refresh_files()
            
            # Check if we're scanning all directories
            if hasattr(self, "current_scan_index"):
                # Get the directories from the configuration
                directories = config.get_local_directories()
                
                # Increment the index
                self.current_scan_index += 1
                
                # Check if there are more directories to scan
                if self.current_scan_index < len(directories):
                    # Scan the next directory
                    self.scan_directory(directories[self.current_scan_index])
                    return
                else:
                    # All directories have been scanned
                    del self.current_scan_index
                    QMessageBox.information(self, "Scan Complete", "All directories have been scanned.")
            else:
                # Show a success message for a single directory scan
                QMessageBox.information(
                    self, "Scan Complete",
                    f"Scan completed successfully.\n\n"
                    f"Files found: {result['files_found']}\n"
                    f"Files added: {result['files_added']}\n"
                    f"Files updated: {result['files_updated']}"
                )
        else:
            self.progress_label.setText(f"Scan failed: {result['error']}")
            QMessageBox.warning(self, "Scan Failed", f"Scan failed: {result['error']}")
        
        # Clear the scan thread
        self.scan_thread = None
    
    def cancel_scan(self):
        """Cancel the current scan operation."""
        if self.scan_thread is not None:
            self.scan_thread.cancel()
            self.progress_label.setText("Cancelling scan...")
            
            # Clear the current scan index if we're scanning all directories
            if hasattr(self, "current_scan_index"):
                del self.current_scan_index
    
    def load_file_stats(self):
        """Load and display file statistics."""
        try:
            # Get the total file count
            total_count = self.directory_scanner.get_total_file_count()
            
            if total_count == 0:
                self.stats_label.setText("No files in database")
                return
            
            # Get the file counts by type
            type_counts = self.directory_scanner.get_file_count_by_type()
            
            # Build the statistics text
            stats_text = f"Total files: {total_count}\n"
            
            for file_type, count in type_counts.items():
                stats_text += f"{file_type.upper()} files: {count}\n"
            
            self.stats_label.setText(stats_text)
        except Exception as e:
            logger.error(f"Error loading file statistics: {e}")
            self.stats_label.setText(f"Error loading statistics: {str(e)}")
    
    def filter_files(self):
        """Filter the file list based on the selected filter."""
        self.refresh_files()
    
    def refresh_files(self):
        """Refresh the file list."""
        try:
            # Clear the table
            self.files_table.setRowCount(0)
            
            # Get the selected filter
            filter_id = self.filter_group.checkedId()
            
            # Get the files based on the filter
            files = []
            
            if filter_id == 0:  # All Files
                files = self.local_file_model.get_all_files()
            elif filter_id == 1:  # PDF Files
                files = self.local_file_model.get_files_by_type("pdf")
            elif filter_id == 2:  # EPUB Files
                files = self.local_file_model.get_files_by_type("epub")
            elif filter_id == 3:  # Text Files
                files = self.local_file_model.get_files_by_type("txt")
            
            # Add the files to the table
            for file in files:
                row_position = self.files_table.rowCount()
                self.files_table.insertRow(row_position)
                
                self.files_table.setItem(row_position, 0, QTableWidgetItem(str(file["id"])))
                self.files_table.setItem(row_position, 1, QTableWidgetItem(file["path"]))
                self.files_table.setItem(row_position, 2, QTableWidgetItem(file["file_type"].upper()))
                
                # Format the file size
                size = file.get("size")
                size_text = "Unknown" if size is None else self._format_size(size)
                self.files_table.setItem(row_position, 3, QTableWidgetItem(size_text))
            
            logger.info(f"Loaded {len(files)} files")
        except Exception as e:
            logger.error(f"Error refreshing files: {e}")
            QMessageBox.critical(self, "Database Error", f"Error refreshing files: {str(e)}")
    
    def clear_database(self):
        """Clear all local files from the database."""
        reply = QMessageBox.question(
            self, "Confirm Clear",
            "Are you sure you want to clear all local files from the database?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Delete all files from the database
                count = self.local_file_model.delete_all_files()
                
                # Update the file statistics
                self.load_file_stats()
                
                # Refresh the file list
                self.refresh_files()
                
                QMessageBox.information(self, "Database Cleared", f"Removed {count} files from the database.")
                logger.info(f"Cleared {count} files from the database")
            except Exception as e:
                logger.error(f"Error clearing database: {e}")
                QMessageBox.critical(self, "Database Error", f"Error clearing database: {str(e)}")
    
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
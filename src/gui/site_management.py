"""Site management tab for the PDF Downloader application.

This module contains the SiteManagementTab class for managing library/archive sites.
"""

import logging
import sqlite3
from urllib.parse import urlparse

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFormLayout, QMessageBox, QComboBox, QProgressDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from src.db.site_model import SiteModel
from src.core.site_scanner import SiteScanner
from src.scrapers.registry import ScraperRegistry


logger = logging.getLogger(__name__)


class ScanThread(QThread):
    """Thread for scanning a site in the background.
    
    This thread runs the site scanning process in the background to keep
    the UI responsive during long-running scans.
    """
    
    scan_complete = pyqtSignal(dict)
    
    def __init__(self, site_id):
        """Initialize the scan thread.
        
        Args:
            site_id: ID of the site to scan
        """
        super().__init__()
        self.site_id = site_id
        self.scanner = SiteScanner()
    
    def run(self):
        """Run the scan thread."""
        result = self.scanner.scan_site(self.site_id)
        self.scan_complete.emit(result)


class SiteManagementTab(QWidget):
    """Tab for managing library/archive sites.
    
    This tab allows users to add, edit, and remove sites from the application.
    """
    
    def __init__(self, parent=None):
        """Initialize the site management tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.site_model = SiteModel()
        self.scraper_registry = ScraperRegistry()
        self.current_site_id = None
        self.scan_thread = None
        self.init_ui()
        self.load_sites()
        self.load_scraper_types()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Form for adding/editing sites
        form_layout = QFormLayout()
        
        # Site name input
        self.name_input = QLineEdit()
        form_layout.addRow("Site Name:", self.name_input)
        
        # Site URL input
        self.url_input = QLineEdit()
        form_layout.addRow("Site URL:", self.url_input)
        
        # Scraper type selection
        self.scraper_type_combo = QComboBox()
        form_layout.addRow("Scraper Type:", self.scraper_type_combo)
        
        # Buttons for form actions
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Site")
        self.add_button.clicked.connect(self.add_site)
        button_layout.addWidget(self.add_button)
        
        self.update_button = QPushButton("Update Site")
        self.update_button.clicked.connect(self.update_site)
        self.update_button.setEnabled(False)
        button_layout.addWidget(self.update_button)
        
        self.clear_button = QPushButton("Clear Form")
        self.clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_button)
        
        # Add form and buttons to main layout
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        
        # Table for displaying sites
        self.sites_table = QTableWidget(0, 5)  # 0 rows, 5 columns
        self.sites_table.setHorizontalHeaderLabels(["ID", "Name", "URL", "Scraper Type", "Last Scan"])
        self.sites_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sites_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sites_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sites_table.itemClicked.connect(self.select_site)
        layout.addWidget(self.sites_table)
        
        # Buttons for table actions
        table_button_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.clicked.connect(self.edit_site)
        self.edit_button.setEnabled(False)
        table_button_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_site)
        self.remove_button.setEnabled(False)
        table_button_layout.addWidget(self.remove_button)
        
        self.scan_button = QPushButton("Scan Selected")
        self.scan_button.clicked.connect(self.scan_site)
        self.scan_button.setEnabled(False)
        table_button_layout.addWidget(self.scan_button)
        
        layout.addLayout(table_button_layout)
    
    def load_scraper_types(self):
        """Load available scraper types into the combo box."""
        self.scraper_type_combo.clear()
        
        # Get available scrapers from the registry
        scrapers = self.scraper_registry.get_available_scrapers()
        
        # Add scraper types to the combo box
        for scraper_type in scrapers.keys():
            self.scraper_type_combo.addItem(scraper_type)
    
    def load_sites(self):
        """Load sites from the database and display them in the table."""
        try:
            sites = self.site_model.get_all_sites()
            
            self.sites_table.setRowCount(0)
            
            for site in sites:
                row_position = self.sites_table.rowCount()
                self.sites_table.insertRow(row_position)
                
                self.sites_table.setItem(row_position, 0, QTableWidgetItem(str(site["id"])))
                self.sites_table.setItem(row_position, 1, QTableWidgetItem(site["name"]))
                self.sites_table.setItem(row_position, 2, QTableWidgetItem(site["url"]))
                self.sites_table.setItem(row_position, 3, QTableWidgetItem(site["scraper_type"]))
                
                # Format the last scan date
                last_scan = site.get("last_scan_date")
                last_scan_text = "Never" if last_scan is None else last_scan
                self.sites_table.setItem(row_position, 4, QTableWidgetItem(last_scan_text))
            
            logger.info(f"Loaded {len(sites)} sites from the database")
        except Exception as e:
            logger.error(f"Error loading sites: {e}")
            QMessageBox.critical(self, "Database Error", f"Error loading sites: {str(e)}")
    
    def validate_inputs(self):
        """Validate the form inputs.
        
        Returns:
            Tuple of (is_valid, name, url, scraper_type) if valid,
            or (False, error_message, None, None) if invalid
        """
        name = self.name_input.text().strip()
        url = self.url_input.text().strip()
        scraper_type = self.scraper_type_combo.currentText()
        
        if not name:
            return (False, "Site name is required", None, None, None)
        
        if not url:
            return (False, "Site URL is required", None, None, None)
        
        # Validate URL format
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return (False, "Invalid URL format. Please include http:// or https://", None, None, None)
        except Exception:
            return (False, "Invalid URL format", None, None, None)
        
        return (True, name, url, scraper_type)
    
    def clear_form(self):
        """Clear the form inputs."""
        self.name_input.clear()
        self.url_input.clear()
        if self.scraper_type_combo.count() > 0:
            self.scraper_type_combo.setCurrentIndex(0)
        self.add_button.setEnabled(True)
        self.update_button.setEnabled(False)
        self.current_site_id = None
    
    def select_site(self):
        """Handle site selection in the table."""
        self.edit_button.setEnabled(True)
        self.remove_button.setEnabled(True)
        self.scan_button.setEnabled(True)
    
    def add_site(self):
        """Add a new site to the database."""
        valid, *result = self.validate_inputs()
        
        if not valid:
            error_message = result[0]
            QMessageBox.warning(self, "Input Error", error_message)
            return
        
        name, url, scraper_type = result
        
        try:
            site_id = self.site_model.add_site(name, url, scraper_type)
            logger.info(f"Added site '{name}' with ID {site_id}")
            QMessageBox.information(self, "Success", f"Site '{name}' added successfully.")
            self.clear_form()
            self.load_sites()
        except sqlite3.IntegrityError:
            logger.warning(f"Attempted to add duplicate site URL: {url}")
            QMessageBox.warning(self, "Duplicate URL", f"A site with the URL '{url}' already exists.")
        except Exception as e:
            logger.error(f"Error adding site: {e}")
            QMessageBox.critical(self, "Database Error", f"Error adding site: {str(e)}")
    
    def edit_site(self):
        """Load the selected site into the form for editing."""
        selected_rows = self.sites_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        site_id = int(self.sites_table.item(row, 0).text())
        name = self.sites_table.item(row, 1).text()
        url = self.sites_table.item(row, 2).text()
        scraper_type = self.sites_table.item(row, 3).text()
        
        self.name_input.setText(name)
        self.url_input.setText(url)
        self.scraper_type_combo.setCurrentText(scraper_type)
        
        self.current_site_id = site_id
        self.add_button.setEnabled(False)
        self.update_button.setEnabled(True)
        
        logger.info(f"Loaded site ID {site_id} for editing")
    
    def update_site(self):
        """Update the selected site in the database."""
        if self.current_site_id is None:
            return
        
        valid, *result = self.validate_inputs()
        
        if not valid:
            error_message = result[0]
            QMessageBox.warning(self, "Input Error", error_message)
            return
        
        name, url, scraper_type = result
        
        try:
            success = self.site_model.update_site(self.current_site_id, name, url, scraper_type)
            
            if success:
                logger.info(f"Updated site ID {self.current_site_id}")
                QMessageBox.information(self, "Success", f"Site '{name}' updated successfully.")
                self.clear_form()
                self.load_sites()
            else:
                logger.warning(f"Site ID {self.current_site_id} not found for update")
                QMessageBox.warning(self, "Not Found", f"Site with ID {self.current_site_id} not found.")
        except sqlite3.IntegrityError:
            logger.warning(f"Attempted to update to duplicate site URL: {url}")
            QMessageBox.warning(self, "Duplicate URL", f"Another site with the URL '{url}' already exists.")
        except Exception as e:
            logger.error(f"Error updating site: {e}")
            QMessageBox.critical(self, "Database Error", f"Error updating site: {str(e)}")
    
    def remove_site(self):
        """Remove the selected site from the database."""
        selected_rows = self.sites_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        site_id = int(self.sites_table.item(row, 0).text())
        name = self.sites_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove the site '{name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.site_model.delete_site(site_id)
                
                if success:
                    logger.info(f"Removed site ID {site_id}")
                    QMessageBox.information(self, "Success", f"Site '{name}' removed successfully.")
                    self.load_sites()
                else:
                    logger.warning(f"Site ID {site_id} not found for removal")
                    QMessageBox.warning(self, "Not Found", f"Site with ID {site_id} not found.")
            except Exception as e:
                logger.error(f"Error removing site: {e}")
                QMessageBox.critical(self, "Database Error", f"Error removing site: {str(e)}")
    
    def scan_site(self):
        """Scan the selected site for available files."""
        selected_rows = self.sites_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        site_id = int(self.sites_table.item(row, 0).text())
        name = self.sites_table.item(row, 1).text()
        
        # Create a progress dialog
        progress = QProgressDialog(f"Scanning site '{name}'...", "Cancel", 0, 0, self)
        progress.setWindowTitle("Scanning Site")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()
        
        # Create and start the scan thread
        self.scan_thread = ScanThread(site_id)
        self.scan_thread.scan_complete.connect(self.on_scan_complete)
        self.scan_thread.finished.connect(progress.close)
        
        # Connect the cancel button
        progress.canceled.connect(self.scan_thread.terminate)
        
        self.scan_thread.start()
    
    def on_scan_complete(self, result):
        """Handle the completion of a site scan.
        
        Args:
            result: Dictionary containing scan results
        """
        if result["success"]:
            QMessageBox.information(
                self, "Scan Complete",
                f"Scan completed successfully.\n\n"
                f"Categories: {len(result['categories'])}\n"
                f"Files: {len(result['files'])}"
            )
            self.load_sites()  # Refresh the site list to show updated last scan date
        else:
            QMessageBox.warning(
                self, "Scan Failed",
                f"Scan failed: {result['error']}"
            )
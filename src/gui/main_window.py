"""Main window for the PDF Downloader application.

This module contains the MainWindow class for the application's main window.
"""

import logging
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QStatusBar
from PyQt5.QtCore import Qt

from src.gui.site_management import SiteManagementTab
from src.gui.library_tab import LibraryTab


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window for the PDF Downloader application.
    
    This class represents the main window of the application, containing
    tabs for different functionality.
    """
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.init_ui()
        logger.info("Main window initialized")
    
    def init_ui(self):
        """Initialize the UI components."""
        # Set window properties
        self.setWindowTitle("PDF Downloader")
        self.setMinimumSize(800, 600)
        
        # Create the central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create the main layout
        layout = QVBoxLayout(central_widget)
        
        # Create the tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create and add tabs
        self.site_management_tab = SiteManagementTab()
        self.tab_widget.addTab(self.site_management_tab, "Site Management")
        
        self.library_tab = LibraryTab()
        self.tab_widget.addTab(self.library_tab, "Library")
        
        # Create the status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def closeEvent(self, event):
        """Handle the window close event.
        
        Args:
            event: Close event
        """
        # Clean up resources
        if hasattr(self, "library_tab") and hasattr(self.library_tab, "download_manager"):
            self.library_tab.download_manager.stop()
        
        logger.info("Main window closed")
        event.accept()
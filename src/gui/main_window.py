"""Main window for the PDF Downloader application.

This module contains the MainWindow class for the application's main window.
"""

import logging
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QStatusBar, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from src.gui.site_management import SiteManagementTab
from src.gui.library_tab import LibraryTab
from src.gui.local_library_tab import LocalLibraryTab
from src.gui.comparison_tab import ComparisonTab
from src.gui.download_queue_tab import DownloadQueueTab
from src.gui.download_history_tab import DownloadHistoryTab


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
        
        self.local_library_tab = LocalLibraryTab()
        self.tab_widget.addTab(self.local_library_tab, "Local Library")

        self.library_tab = LibraryTab()
        self.tab_widget.addTab(self.library_tab, "Remote Library")

        self.comparison_tab = ComparisonTab()
        self.tab_widget.addTab(self.comparison_tab, "File Comparison")

        self.download_queue_tab = DownloadQueueTab()
        self.tab_widget.addTab(self.download_queue_tab, "Download Queue")
        
        self.download_history_tab = DownloadHistoryTab()
        self.tab_widget.addTab(self.download_history_tab, "Download History")
        
        # Create the status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Set up system tray icon
        self.setup_tray_icon()
    
    def closeEvent(self, event):
        """Handle the window close event.
        
        Args:
            event: Close event
        """
        # Clean up resources
        if hasattr(self, "library_tab") and hasattr(self.library_tab, "download_manager"):
            self.library_tab.download_manager.stop()

        if hasattr(self, "download_queue_tab") and hasattr(self.download_queue_tab, "download_manager"):
            self.download_queue_tab.download_manager.stop()

        logger.info("Main window closed")
        event.accept()
    
    def setup_tray_icon(self):
        """Set up the system tray icon."""
        # Create the tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Set the icon (use a default icon if available)
        try:
            import os
            icon_path = os.path.join(os.path.dirname(__file__), "../../assets/icon.png")
            if os.path.exists(icon_path):
                self.tray_icon.setIcon(QIcon(icon_path))
            else:
                # Use a default icon from Qt
                self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        except Exception as e:
            logger.error(f"Error setting tray icon: {e}")
            # Use a default icon from Qt
            self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        
        # Create the tray menu
        tray_menu = QMenu()
        
        # Add actions to the menu
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        # Set the tray menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Connect signals
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Connect download signals
        if hasattr(self, "download_queue_tab") and hasattr(self.download_queue_tab, "download_manager"):
            self.download_queue_tab.download_manager.download_completed.connect(self.show_download_notification)
            self.download_queue_tab.download_manager.download_failed.connect(self.show_error_notification)
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation.
        
        Args:
            reason: Activation reason
        """
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()
    
    def show_download_notification(self, file_id):
        """Show a notification for a completed download.
        
        Args:
            file_id: ID of the downloaded file
        """
        try:
            # Get the file information
            from src.db.remote_file_model import RemoteFileModel
            remote_file_model = RemoteFileModel()
            file_info = remote_file_model.get_file_by_id(file_id)
            
            if file_info:
                self.tray_icon.showMessage(
                    "Download Completed",
                    f"File '{file_info['name']}' has been downloaded successfully.",
                    QSystemTrayIcon.Information,
                    5000  # Show for 5 seconds
                )
        except Exception as e:
            logger.error(f"Error showing download notification: {e}")
    
    def show_error_notification(self, file_id, error):
        """Show a notification for a failed download.
        
        Args:
            file_id: ID of the file that failed to download
            error: Error message
        """
        try:
            # Get the file information
            from src.db.remote_file_model import RemoteFileModel
            remote_file_model = RemoteFileModel()
            file_info = remote_file_model.get_file_by_id(file_id)
            
            if file_info:
                self.tray_icon.showMessage(
                    "Download Failed",
                    f"Failed to download file '{file_info['name']}': {error}",
                    QSystemTrayIcon.Critical,
                    5000  # Show for 5 seconds
                )
        except Exception as e:
            logger.error(f"Error showing error notification: {e}")
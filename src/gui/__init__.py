"""PyQt UI components for the PDF Downloader application.

This module contains all the UI components for the application, including:
- Main window and application layout
- Site management interface
- Local and remote library views
- Download queue management
- Download history tracking
- Settings and configuration panels
- Log and notification displays
"""

from src.gui.main_window import MainWindow
from src.gui.site_management import SiteManagementTab
from src.gui.library_tab import LibraryTab
from src.gui.local_library_tab import LocalLibraryTab
from src.gui.comparison_tab import ComparisonTab
from src.gui.settings_dialog import SettingsDialog
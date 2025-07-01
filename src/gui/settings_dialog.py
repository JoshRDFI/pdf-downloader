"""Settings dialog for the PDF Downloader application.

This module contains the SettingsDialog class for managing application settings.
"""

import logging
from typing import Dict, Any, List, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QLineEdit, QCheckBox, QSpinBox, QComboBox, QPushButton, QFormLayout,
    QGroupBox, QMessageBox, QFileDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QSettings

from config import config


logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Dialog for managing application settings.
    
    This dialog allows users to configure various aspects of the application,
    including network settings, download settings, file type preferences,
    notification settings, and appearance settings.
    """
    
    def __init__(self, parent=None):
        """Initialize the settings dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_network_tab()
        self.create_download_tab()
        self.create_file_types_tab()
        self.create_notification_tab()
        self.create_appearance_tab()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply | QDialogButtonBox.Reset)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        button_box.button(QDialogButtonBox.Reset).clicked.connect(self.reset_settings)
        layout.addWidget(button_box)
    
    def create_network_tab(self):
        """Create the network settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Proxy settings
        proxy_group = QGroupBox("Proxy Settings")
        proxy_layout = QFormLayout(proxy_group)
        
        self.proxy_enabled = QCheckBox("Use Proxy")
        proxy_layout.addRow(self.proxy_enabled)
        
        self.proxy_url = QLineEdit()
        self.proxy_url.setPlaceholderText("http://proxy.example.com:8080")
        proxy_layout.addRow("Proxy URL:", self.proxy_url)
        
        self.proxy_username = QLineEdit()
        proxy_layout.addRow("Username:", self.proxy_username)
        
        self.proxy_password = QLineEdit()
        self.proxy_password.setEchoMode(QLineEdit.Password)
        proxy_layout.addRow("Password:", self.proxy_password)
        
        layout.addWidget(proxy_group)
        
        # User agent settings
        user_agent_group = QGroupBox("User Agent")
        user_agent_layout = QFormLayout(user_agent_group)
        
        self.user_agent = QLineEdit()
        user_agent_layout.addRow("User Agent:", self.user_agent)
        
        layout.addWidget(user_agent_group)
        
        # Timeout settings
        timeout_group = QGroupBox("Timeout")
        timeout_layout = QFormLayout(timeout_group)
        
        self.timeout = QSpinBox()
        self.timeout.setRange(1, 300)
        self.timeout.setSuffix(" seconds")
        timeout_layout.addRow("Request Timeout:", self.timeout)
        
        layout.addWidget(timeout_group)
        
        # Add the tab
        self.tab_widget.addTab(tab, "Network")
    
    def create_download_tab(self):
        """Create the download settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Concurrent downloads
        concurrent_group = QGroupBox("Concurrent Downloads")
        concurrent_layout = QFormLayout(concurrent_group)
        
        self.concurrent_downloads = QSpinBox()
        self.concurrent_downloads.setRange(1, 10)
        concurrent_layout.addRow("Number of concurrent downloads:", self.concurrent_downloads)
        
        layout.addWidget(concurrent_group)
        
        # Rate limiting
        rate_limit_group = QGroupBox("Rate Limiting")
        rate_limit_layout = QFormLayout(rate_limit_group)
        
        self.rate_limit = QSpinBox()
        self.rate_limit.setRange(0, 10000)
        self.rate_limit.setSuffix(" KB/s")
        self.rate_limit.setSpecialValueText("Unlimited")
        rate_limit_layout.addRow("Download rate limit:", self.rate_limit)
        
        layout.addWidget(rate_limit_group)
        
        # Retry settings
        retry_group = QGroupBox("Retry Settings")
        retry_layout = QFormLayout(retry_group)
        
        self.retry_count = QSpinBox()
        self.retry_count.setRange(0, 10)
        retry_layout.addRow("Number of retry attempts:", self.retry_count)
        
        self.retry_delay = QSpinBox()
        self.retry_delay.setRange(1, 60)
        self.retry_delay.setSuffix(" seconds")
        retry_layout.addRow("Delay between retries:", self.retry_delay)
        
        layout.addWidget(retry_group)
        
        # Add the tab
        self.tab_widget.addTab(tab, "Download")
    
    def create_file_types_tab(self):
        """Create the file types tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File types
        file_types_group = QGroupBox("File Types")
        file_types_layout = QVBoxLayout(file_types_group)
        
        self.pdf_enabled = QCheckBox("PDF Files (.pdf)")
        file_types_layout.addWidget(self.pdf_enabled)
        
        self.epub_enabled = QCheckBox("EPUB Files (.epub)")
        file_types_layout.addWidget(self.epub_enabled)
        
        self.txt_enabled = QCheckBox("Text Files (.txt)")
        file_types_layout.addWidget(self.txt_enabled)
        
        layout.addWidget(file_types_group)
        
        # Add the tab
        self.tab_widget.addTab(tab, "File Types")
    
    def create_notification_tab(self):
        """Create the notification settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Notification settings
        notification_group = QGroupBox("Notifications")
        notification_layout = QVBoxLayout(notification_group)
        
        self.notification_enabled = QCheckBox("Enable Notifications")
        notification_layout.addWidget(self.notification_enabled)
        
        self.download_completed = QCheckBox("Show notification when download completes")
        notification_layout.addWidget(self.download_completed)
        
        self.download_failed = QCheckBox("Show notification when download fails")
        notification_layout.addWidget(self.download_failed)
        
        self.scan_completed = QCheckBox("Show notification when scan completes")
        notification_layout.addWidget(self.scan_completed)
        
        layout.addWidget(notification_group)
        
        # Add the tab
        self.tab_widget.addTab(tab, "Notifications")
    
    def create_appearance_tab(self):
        """Create the appearance settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)
        
        self.theme = QComboBox()
        self.theme.addItem("System", "system")
        self.theme.addItem("Light", "light")
        self.theme.addItem("Dark", "dark")
        theme_layout.addRow("Application Theme:", self.theme)
        
        layout.addWidget(theme_group)
        
        # Font settings
        font_group = QGroupBox("Font")
        font_layout = QFormLayout(font_group)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setSuffix(" pt")
        font_layout.addRow("Font Size:", self.font_size)
        
        layout.addWidget(font_group)
        
        # Add the tab
        self.tab_widget.addTab(tab, "Appearance")
    
    def load_settings(self):
        """Load settings from the configuration."""
        # Network settings
        self.proxy_enabled.setChecked(config.get("network", "proxy_enabled", False))
        self.proxy_url.setText(config.get("network", "proxy_url", ""))
        self.proxy_username.setText(config.get("network", "proxy_username", ""))
        self.proxy_password.setText(config.get("network", "proxy_password", ""))
        self.user_agent.setText(config.get("network", "user_agent", ""))
        self.timeout.setValue(config.get("network", "timeout", 30))
        
        # Download settings
        self.concurrent_downloads.setValue(config.get("download", "concurrent_downloads", 3))
        self.rate_limit.setValue(config.get("download", "rate_limit_kbps", 500))
        self.retry_count.setValue(config.get("download", "retry_count", 3))
        self.retry_delay.setValue(config.get("download", "retry_delay", 5))
        
        # File type settings
        self.pdf_enabled.setChecked(config.get("file_types", "pdf_enabled", True))
        self.epub_enabled.setChecked(config.get("file_types", "epub_enabled", True))
        self.txt_enabled.setChecked(config.get("file_types", "txt_enabled", True))
        
        # Notification settings
        self.notification_enabled.setChecked(config.get("notification", "enabled", True))
        self.download_completed.setChecked(config.get("notification", "download_completed", True))
        self.download_failed.setChecked(config.get("notification", "download_failed", True))
        self.scan_completed.setChecked(config.get("notification", "scan_completed", True))
        
        # Appearance settings
        theme = config.get("appearance", "theme", "system")
        index = self.theme.findData(theme)
        if index >= 0:
            self.theme.setCurrentIndex(index)
        self.font_size.setValue(config.get("appearance", "font_size", 12))
    
    def save_settings(self):
        """Save settings to the configuration."""
        # Network settings
        config.set("network", "proxy_enabled", self.proxy_enabled.isChecked())
        config.set("network", "proxy_url", self.proxy_url.text())
        config.set("network", "proxy_username", self.proxy_username.text())
        config.set("network", "proxy_password", self.proxy_password.text())
        config.set("network", "user_agent", self.user_agent.text())
        config.set("network", "timeout", self.timeout.value())
        
        # Download settings
        config.set("download", "concurrent_downloads", self.concurrent_downloads.value())
        config.set("download", "rate_limit_kbps", self.rate_limit.value())
        config.set("download", "retry_count", self.retry_count.value())
        config.set("download", "retry_delay", self.retry_delay.value())
        
        # File type settings
        config.set("file_types", "pdf_enabled", self.pdf_enabled.isChecked())
        config.set("file_types", "epub_enabled", self.epub_enabled.isChecked())
        config.set("file_types", "txt_enabled", self.txt_enabled.isChecked())
        
        # Notification settings
        config.set("notification", "enabled", self.notification_enabled.isChecked())
        config.set("notification", "download_completed", self.download_completed.isChecked())
        config.set("notification", "download_failed", self.download_failed.isChecked())
        config.set("notification", "scan_completed", self.scan_completed.isChecked())
        
        # Appearance settings
        config.set("appearance", "theme", self.theme.currentData())
        config.set("appearance", "font_size", self.font_size.value())
    
    def apply_settings(self):
        """Apply the current settings."""
        self.save_settings()

        # Reload settings in active components
        self.reload_active_components()

        QMessageBox.information(self, "Settings", "Settings have been applied.")

    def reload_active_components(self):
        """Reload settings in active components."""
        try:
            # Get the main window
            main_window = self.parent()
            if not main_window:
                return

            # Reload download manager settings
            if hasattr(main_window, "download_queue_tab") and hasattr(main_window.download_queue_tab, "download_manager"):
                main_window.download_queue_tab.download_manager.reload_settings()

            if hasattr(main_window, "library_tab") and hasattr(main_window.library_tab, "download_manager"):
                main_window.library_tab.download_manager.reload_settings()

            # Apply theme settings
            theme = config.get("appearance", "theme", "system")
            # Theme application would go here

            # Apply font settings
            font_size = config.get("appearance", "font_size", 12)
            # Font application would go here

            logger.info("Reloaded settings in active components")
        except Exception as e:
            logger.error(f"Error reloading settings in active components: {e}")

    def accept(self):
        """Handle the OK button click."""
        self.save_settings()
        self.reload_active_components()
        super().accept()
    
    def reset_settings(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset settings in the database
            from src.db.settings_model import SettingsModel
            settings_model = SettingsModel()
            settings_model.reset_to_defaults()
            
            # Reload settings
            self.load_settings()
            
            QMessageBox.information(self, "Settings", "Settings have been reset to defaults.")
    
    def accept(self):
        """Handle the OK button click."""
        self.save_settings()
        super().accept()
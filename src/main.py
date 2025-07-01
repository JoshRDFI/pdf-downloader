"""Main entry point for the PDF Downloader application.

This module initializes the application, sets up logging, and starts the GUI.
"""

import sys
import os
import logging
from datetime import datetime

from PyQt5.QtWidgets import QApplication

from src.gui.main_window import MainWindow
from src.db.database import DatabaseManager
from src.scrapers import register_builtin_scrapers, load_scrapers
from src.plugins.scrapers import scraper_plugin_manager
from src.plugins.file_types import file_type_plugin_manager
from src.core.file_validator import FileValidator


def setup_logging():
    """Set up logging for the application.
    
    This function configures logging to write to both a file and the console.
    """
    # Create the log directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a log file with the current date and time
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Log the start of the application
    logging.info("PDF Downloader application starting")


def initialize_database():
    """Initialize the database for the application.
    
    This function creates the database tables if they don't exist.
    """
    db_manager = DatabaseManager()
    db_manager.initialize_database()
    logging.info("Database initialized")


def initialize_scrapers():
    """Initialize the scraper registry.
    
    This function registers the built-in scrapers and loads any custom scrapers.
    """
    register_builtin_scrapers()
    load_scrapers()
    logging.info("Scrapers initialized")


def initialize_plugins():
    """Initialize the plugin system.
    
    This function discovers and loads plugins for scrapers and file types.
    """
    # Discover scraper plugins
    scraper_plugin_manager.discover_plugins()
    logging.info(f"Discovered {len(scraper_plugin_manager.get_all_plugins())} scraper plugins")
    
    # Discover file type plugins
    file_type_plugin_manager.discover_plugins()
    logging.info(f"Discovered {len(file_type_plugin_manager.get_all_plugins())} file type plugins")
    
    # Initialize the file validator to register built-in validators
    FileValidator()
    logging.info(f"Supported file types: {', '.join(file_type_plugin_manager.get_supported_types())}")
    logging.info(f"Supported file extensions: {', '.join(file_type_plugin_manager.get_supported_extensions())}")


def main():
    """Main entry point for the application.
    
    This function sets up logging, initializes the database,
    initializes the scraper registry, and starts the GUI.
    """
    # Set up logging
    setup_logging()
    
    # Initialize the database
    initialize_database()
    
    # Initialize the scraper registry
    initialize_scrapers()
    
    # Initialize the plugin system
    initialize_plugins()
    
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Downloader")
    
    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
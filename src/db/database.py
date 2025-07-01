"""Database connection and management for the PDF Downloader application.

This module provides database connection management and basic query functionality.
"""

import sqlite3
from pathlib import Path
from typing import Optional


class DatabaseManager:
    """Manages database connections and provides query methods.
    
    This class handles SQLite database connections, schema initialization,
    and provides methods for common database operations.
    """
    
    def __init__(self, db_path: str = "database/pdf_downloader.db"):
        """Initialize the database manager with the given database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None
        
    def connect(self) -> sqlite3.Connection:
        """Connect to the SQLite database.
        
        Returns:
            An active SQLite connection
        """
        if self.connection is None:
            # Ensure the directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to the database
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            
        return self.connection
    
    def close(self) -> None:
        """Close the database connection if open."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None
    
    def initialize_schema(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Read schema from file
        schema_path = Path("database/schema.sql")
        if schema_path.exists():
            with open(schema_path, "r") as f:
                schema_sql = f.read()
                cursor.executescript(schema_sql)
        else:
            # TODO: Create schema if file doesn't exist
            pass
        
        conn.commit()
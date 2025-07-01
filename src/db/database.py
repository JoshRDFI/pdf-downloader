"""Database connection and management for the PDF Downloader application.

This module provides database connection management and basic query functionality.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional
import logging


logger = logging.getLogger(__name__)


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
            logger.error(f"Schema file not found: {schema_path}")
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        conn.commit()
        logger.info("Database schema initialized")
    
    def initialize_database(self) -> None:
        """Initialize the database for the application.
        
        This method creates the database tables if they don't exist.
        """
        try:
            self.initialize_schema()
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def execute_query(self, query: str, parameters: tuple = ()) -> sqlite3.Cursor:
        """Execute a SQL query with parameters.
        
        Args:
            query: SQL query to execute
            parameters: Query parameters (optional)
            
        Returns:
            SQLite cursor with the query results
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        return cursor
    
    def execute_script(self, script: str) -> None:
        """Execute a SQL script.
        
        Args:
            script: SQL script to execute
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.executescript(script)
        conn.commit()
    
    def commit(self) -> None:
        """Commit the current transaction."""
        if self.connection is not None:
            self.connection.commit()
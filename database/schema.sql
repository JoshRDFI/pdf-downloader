-- Database schema for the PDF Downloader application

-- Sites table for storing information about library/archive sites
CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    scraper_type TEXT NOT NULL,
    last_scan_date TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Categories table for storing category information from sites
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    url TEXT,
    parent_id INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (site_id) REFERENCES sites (id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES categories (id) ON DELETE SET NULL,
    UNIQUE (site_id, url) ON CONFLICT REPLACE
);

-- Remote files table for storing information about files on remote sites
CREATE TABLE IF NOT EXISTS remote_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER NOT NULL,
    category_id INTEGER,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    size INTEGER,
    file_type TEXT,
    last_checked TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (site_id) REFERENCES sites (id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL,
    UNIQUE (site_id, url) ON CONFLICT REPLACE
);

-- Local files table for storing information about downloaded files
CREATE TABLE IF NOT EXISTS local_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    remote_file_id INTEGER,
    path TEXT NOT NULL,
    size INTEGER,
    file_type TEXT,
    last_checked TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (remote_file_id) REFERENCES remote_files (id) ON DELETE SET NULL,
    UNIQUE (path) ON CONFLICT REPLACE
);

-- Downloads table for storing download history
CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    remote_file_id INTEGER NOT NULL,
    local_file_id INTEGER,
    status TEXT NOT NULL,  -- 'pending', 'in_progress', 'completed', 'failed'
    started_at TEXT,
    completed_at TEXT,
    error_message TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (remote_file_id) REFERENCES remote_files (id) ON DELETE CASCADE,
    FOREIGN KEY (local_file_id) REFERENCES local_files (id) ON DELETE SET NULL
);

-- Settings table for storing application settings
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    category TEXT NOT NULL,  -- 'network', 'download', 'notification', 'appearance', etc.
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Triggers to update the updated_at timestamp
CREATE TRIGGER IF NOT EXISTS sites_update_timestamp
AFTER UPDATE ON sites
BEGIN
    UPDATE sites SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS categories_update_timestamp
AFTER UPDATE ON categories
BEGIN
    UPDATE categories SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS remote_files_update_timestamp
AFTER UPDATE ON remote_files
BEGIN
    UPDATE remote_files SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS local_files_update_timestamp
AFTER UPDATE ON local_files
BEGIN
    UPDATE local_files SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS downloads_update_timestamp
AFTER UPDATE ON downloads
BEGIN
    UPDATE downloads SET updated_at = datetime('now') WHERE id = NEW.id;
END;
CREATE TRIGGER IF NOT EXISTS settings_update_timestamp
AFTER UPDATE ON settings
BEGIN
    UPDATE settings SET updated_at = datetime('now') WHERE key = NEW.key;
END;

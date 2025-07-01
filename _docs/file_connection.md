# Connecting Local Files to Remote Sources

## Overview
This document explains how the PDF Downloader application connects local files to their remote sources to avoid duplicate downloads and only fetch new or corrupted files.

## Database Relationship
The connection between local and remote files is maintained through the database schema:

```sql
CREATE TABLE IF NOT EXISTS local_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    remote_file_id INTEGER,
    path TEXT NOT NULL,
    ...
    FOREIGN KEY (remote_file_id) REFERENCES remote_files (id) ON DELETE SET NULL
);
```

This foreign key relationship allows us to track which local files correspond to which remote files.

## Implementation Strategy

### During Remote Scanning (Phase 3)
- When the application scans a remote site, it identifies files and stores their metadata in the `remote_files` table
- Each remote file gets a unique ID and includes information like URL, size, and file type

### During Download
- When a file is downloaded, the application creates a record in the `local_files` table
- The `remote_file_id` field is set to the ID of the corresponding remote file
- This establishes the connection between the local and remote files

### During Comparison
- The application compares local and remote files to identify:
  - New files (exist remotely but not locally)
  - Updated files (exist in both places but with different sizes/checksums)
  - Corrupted files (local files that fail validation)
- Only files that don't exist locally or need updating are queued for download

## Key Components

### FileComparisonService
The `FileComparisonService` class is responsible for comparing local and remote files:

```python
def compare_files(self, site_id: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Compare local and remote files.
    
    Args:
        site_id: ID of the site to compare files for (optional)
                If not provided, all sites will be compared
        
    Returns:
        Dictionary with lists of new, updated, and corrupted files
    """
    result = {
        "new_files": [],
        "updated_files": [],
        "corrupted_files": [],
        "ok_files": []
    }
    
    # Get all remote files, optionally filtered by site
    if site_id is not None:
        remote_files = self.remote_file_model.get_files_by_site(site_id)
    else:
        remote_files = self.remote_file_model.get_all_files()
    
    for remote_file in remote_files:
        # Check if the file exists locally by remote ID
        local_file = self.local_file_model.get_file_by_remote_id(remote_file["id"])
        
        if local_file is None:
            # File doesn't exist locally, add to new files
            result["new_files"].append(remote_file)
        else:
            # File exists locally, check if it needs updating
            if local_file["size"] != remote_file["size"]:
                # File sizes don't match, add to updated files
                result["updated_files"].append({
                    "remote": remote_file,
                    "local": local_file
                })
            else:
                # File sizes match, check if the file is valid
                validation_result = self.file_validator.validate_file(
                    local_file["path"], local_file["file_type"]
                )
                
                if not validation_result["valid"]:
                    # File is corrupted, add to corrupted files
                    result["corrupted_files"].append({
                        "remote": remote_file,
                        "local": local_file,
                        "error": validation_result["error"]
                    })
                else:
                    # File is OK, add to OK files
                    result["ok_files"].append({
                        "remote": remote_file,
                        "local": local_file
                    })
    
    return result
```

### LocalFileModel
The `LocalFileModel` class provides methods for finding files by remote ID:

```python
def get_file_by_remote_id(self, remote_file_id: int) -> Optional[Dict[str, Any]]:
    """Get a local file by its remote file ID.
    
    Args:
        remote_file_id: ID of the remote file
        
    Returns:
        Dictionary containing file information, or None if not found
    """
    conn = self.db_manager.connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, remote_file_id, path, size, file_type, last_checked, created_at, updated_at
        FROM local_files
        WHERE remote_file_id = ?
    """, (remote_file_id,))
    
    row = cursor.fetchone()
    if row is None:
        return None
    
    return dict(row)
```

### ComparisonTab
The `ComparisonTab` class provides a user interface for comparing local and remote files:

- Shows new files (exist remotely but not locally)
- Shows updated files (exist in both places but with different sizes)
- Shows corrupted files (local files that fail validation)
- Shows OK files (local files that match remote files)
- Provides context menus for adding files to the download queue

## User Interface
The user interface shows the connection status between local and remote files:

- New files are shown in the "New Files" tab
- Updated files are shown in the "Updated Files" tab, with size differences highlighted
- Corrupted files are shown in the "Corrupted Files" tab, with errors highlighted
- OK files are shown in the "OK Files" tab

## Conclusion
By maintaining a connection between local and remote files, the application can:

- Avoid downloading files that already exist locally
- Only download files that are new or need updating
- Identify and re-download corrupted files
- Save bandwidth and storage space
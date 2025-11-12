# File Metadata Database Integration

This document describes the integration of the SQLite-based file metadata database into the WebBasedOS backend.

## Overview

The file metadata database provides a centralized way to track and query file and directory information, enabling faster file operations and better user experience. It stores metadata such as file names, paths, sizes, modification times, and content previews.

## Components

1. **FileMetadataDB Class** (`backend/services/file_metadata_db.py`)
   - Manages the SQLite database connection and schema
   - Provides methods for CRUD operations on file metadata
   - Handles content preview generation and storage

2. **Updated File Router** (`backend/routers/file_router.py`)
   - Modified to use the metadata database for file operations
   - Provides fallback to direct filesystem operations when needed
   - Maintains consistency between the database and actual filesystem

3. **Initialization Script** (`scripts/init_metadata_db.py`)
   - Scans the VFS and populates the metadata database
   - Can be run manually or as part of the setup process

## Database Schema

The SQLite database (`scripts/file_metadata.db`) contains a single table:

```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    size INTEGER DEFAULT 0,
    parent_path TEXT,
    created_at REAL,
    modified_at REAL,
    content_preview TEXT,
    is_encrypted BOOLEAN DEFAULT 1,
    encryption_status TEXT,
    last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Setup and Usage

### Initial Setup

1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize the metadata database:
   ```bash
   python scripts/init_metadata_db.py
   ```

### API Endpoints

The following endpoints have been updated to use the metadata database:

- `GET /files/list` - List directory contents with metadata
- `POST /files/read` - Read file content with metadata
- `POST /files/write` - Write to file and update metadata
- `DELETE /files/delete` - Delete file and its metadata
- `POST /files/mkdir` - Create directory and update metadata

### Manual Database Management

To inspect or modify the database directly, you can use the SQLite command-line tool:

```bash
sqlite3 scripts/file_metadata.db
```

## Maintenance

### Rebuilding the Database

If the database becomes corrupted or out of sync with the filesystem, you can rebuild it:

1. Delete the existing database:
   ```bash
   rm scripts/file_metadata.db
   ```

2. Reinitialize the database:
   ```bash
   python scripts/init_metadata_db.py
   ```

### Performance Considerations

- The database is optimized for read-heavy workloads
- Content previews are limited to the first 500 characters of text files
- Binary files are not indexed for content
- The database is automatically updated on file operations

## Troubleshooting

### Common Issues

1. **Database Locking**
   - Ensure only one process accesses the database at a time
   - Use the provided API endpoints instead of direct database access

2. **Out of Sync**
   - If files are modified outside the API, run `init_metadata_db.py` to rescan
   - The system will automatically detect and correct most inconsistencies

3. **Performance**
   - For large directories, consider implementing pagination in the API
   - The `content_preview` field can be excluded from list operations if not needed

## Future Enhancements

1. Implement file watching to automatically update the database on changes
2. Add support for file search with full-text indexing
3. Implement file versioning and history
4. Add support for file tags and custom metadata
5. Implement database backup and recovery

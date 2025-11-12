#!/usr/bin/env python3
"""
Initialize File Metadata Database

This script scans the VFS and populates the file metadata database.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add the backend directory to the path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.append(backend_dir)

from services.file_metadata_db import FileMetadataDB

# Configuration
VFS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vfs_storage', 'MainDisk')
DATA_DIR = os.path.join(VFS_ROOT, 'data')

def scan_directory(directory: str, db: FileMetadataDB, base_path: str = '') -> int:
    """Recursively scan a directory and save metadata to the database.
    
    Args:
        directory: Directory to scan
        db: FileMetadataDB instance
        base_path: Base path for relative paths
        
    Returns:
        Number of files processed
    """
    count = 0
    
    try:
        # List all entries in the directory
        with os.scandir(directory) as entries:
            for entry in entries:
                try:
                    # Skip hidden files and directories
                    if entry.name.startswith('.'):
                        continue
                        
                    # Get file stats
                    stat = entry.stat()
                    rel_path = os.path.relpath(entry.path, VFS_ROOT).replace('\\', '/')
                    parent_path = os.path.dirname(rel_path).replace('\\', '/') or '/'
                    
                    # Prepare file info
                    file_info = {
                        'path': f"/{rel_path}",
                        'name': entry.name,
                        'type': 'directory' if entry.is_dir() else 'file',
                        'size': stat.st_size,
                        'parent_path': f"/{parent_path}" if parent_path != '.' else '/',
                        'created_at': stat.st_ctime,
                        'modified_at': stat.st_mtime,
                        'is_encrypted': False,
                        'encryption_status': 'not_encrypted'
                    }
                    
                    # For files, read a preview of the content
                    if entry.is_file() and not entry.is_symlink() and stat.st_size > 0:
                        try:
                            with open(entry.path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(500)  # Read first 500 chars
                                file_info['content_preview'] = content
                        except (IOError, UnicodeDecodeError):
                            # Skip binary files or files that can't be read
                            file_info['content_preview'] = ''
                    
                    # Save to database
                    if db.save_file_metadata(file_info):
                        count += 1
                    
                    # Recurse into subdirectories
                    if entry.is_dir() and not entry.is_symlink():
                        count += scan_directory(entry.path, db, base_path)
                        
                except (OSError, PermissionError) as e:
                    print(f"Error processing {entry.path}: {e}")
                    continue
                    
    except (OSError, PermissionError) as e:
        print(f"Error scanning directory {directory}: {e}")
    
    return count

def main():
    """Main function to initialize the metadata database."""
    print("Initializing file metadata database...")
    
    # Initialize the database
    db = FileMetadataDB()
    
    # Check if the VFS directory exists
    if not os.path.exists(DATA_DIR):
        print(f"Error: VFS data directory not found at {DATA_DIR}")
        return 1
    
    # Scan the VFS and populate the database
    print(f"Scanning VFS at {DATA_DIR}...")
    start_time = datetime.now()
    file_count = scan_directory(DATA_DIR, db)
    duration = (datetime.now() - start_time).total_seconds()
    
    print(f"\nScan completed in {duration:.2f} seconds")
    print(f"Processed {file_count} files and directories")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

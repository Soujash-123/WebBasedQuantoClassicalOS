"""
File Metadata Database Service
Manages file metadata in SQLite database.
"""

import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class FileMetadataDB:
    """Manages file metadata in SQLite database."""
    
    def __init__(self, db_path: str = None):
        """Initialize the database.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Default to scripts/file_metadata.db relative to project root
            base_dir = Path(__file__).parent.parent
            self.db_path = str(base_dir / "scripts" / "file_metadata.db")
        else:
            self.db_path = db_path
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
    
    def _get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        """Initialize the database schema if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create files table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
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
            )
            ''')
            
            # Create indexes for faster lookups
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_parent ON files(parent_path)')
            
            conn.commit()
    
    def save_file_metadata(self, file_info: Dict[str, Any]) -> bool:
        """Save file metadata to the database.
        
        Args:
            file_info: Dictionary containing file metadata
            
        Returns:
            True if successful, False otherwise
        """
        required_fields = {'path', 'name', 'type', 'size', 'parent_path', 
                          'modified_at', 'is_encrypted', 'encryption_status'}
        
        # Ensure all required fields are present
        if not all(field in file_info for field in required_fields):
            missing = required_fields - file_info.keys()
            raise ValueError(f"Missing required fields: {missing}")
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if file exists
                cursor.execute('SELECT id FROM files WHERE path = ?', (file_info['path'],))
                exists = cursor.fetchone()
                
                if exists:
                    # Update existing record
                    cursor.execute('''
                    UPDATE files 
                    SET name = ?, type = ?, size = ?, parent_path = ?, 
                        modified_at = ?, content_preview = ?, 
                        is_encrypted = ?, encryption_status = ?, 
                        last_scanned = CURRENT_TIMESTAMP
                    WHERE path = ?
                    ''', (
                        file_info['name'], 
                        file_info['type'], 
                        file_info['size'],
                        file_info['parent_path'],
                        file_info['modified_at'],
                        file_info.get('content_preview', ''),
                        file_info['is_encrypted'],
                        file_info['encryption_status'],
                        file_info['path']
                    ))
                else:
                    # Insert new record
                    cursor.execute('''
                    INSERT INTO files 
                    (path, name, type, size, parent_path, created_at, 
                     modified_at, content_preview, is_encrypted, encryption_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        file_info['path'],
                        file_info['name'],
                        file_info['type'],
                        file_info['size'],
                        file_info['parent_path'],
                        file_info.get('created_at', datetime.now().timestamp()),
                        file_info['modified_at'],
                        file_info.get('content_preview', ''),
                        file_info['is_encrypted'],
                        file_info['encryption_status']
                    ))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_file_metadata(self, path: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a file.
        
        Args:
            path: File path
            
        Returns:
            Dictionary with file metadata or None if not found
        """
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM files WHERE path = ?', (path,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def list_directory(self, path: str) -> List[Dict[str, Any]]:
        """List contents of a directory.
        
        Args:
            path: Directory path
            
        Returns:
            List of file metadata dictionaries
        """
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT * FROM files 
                WHERE parent_path = ?
                ORDER BY type DESC, name ASC
                ''', (path.rstrip('/') + '/',))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def delete_file_metadata(self, path: str) -> bool:
        """Delete file metadata.
        
        Args:
            path: File path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM files WHERE path = ?', (path,))
                conn.commit()
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def search_files(self, query: str) -> List[Dict[str, Any]]:
        """Search for files by name or content.
        
        Args:
            query: Search query
            
        Returns:
            List of matching file metadata
        """
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                search = f"%{query}%"
                cursor.execute('''
                SELECT * FROM files 
                WHERE name LIKE ? OR content_preview LIKE ?
                ORDER BY modified_at DESC
                ''', (search, search))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []


# Singleton instance
file_metadata_db = FileMetadataDB()

"""
Storage Adapter
Handles physical storage with AES-256 encryption and SQLite metadata.
"""

import os
import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class StorageAdapter:
    """Manages encrypted file storage and SQLite metadata."""
    
    def __init__(self, disk_name: str, base_path: str = "./vfs_storage"):
        """
        Initialize storage adapter.
        
        Args:
            disk_name: Name of the virtual disk
            base_path: Base directory for VFS storage
        """
        self.disk_name = disk_name
        self.base_path = base_path
        self.disk_path = os.path.join(base_path, disk_name)
        self.data_path = os.path.join(self.disk_path, "data")
        self.db_path = os.path.join(self.disk_path, "metadata.db")
        
        # Encryption key (in production, this should be securely managed)
        self.encryption_key = self._generate_key(disk_name)
        self.cipher = Fernet(self.encryption_key)
        
        # Initialize storage
        self._initialize_storage()
    
    def _generate_key(self, password: str) -> bytes:
        """
        Generate encryption key from password.
        
        Args:
            password: Password/disk name to derive key from
            
        Returns:
            Base64-encoded encryption key
        """
        # Use PBKDF2HMAC to derive a key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'ai_os_vfs_salt_2024',  # In production, use random salt per disk
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _initialize_storage(self) -> None:
        """Initialize storage directories and database."""
        # Create directories
        Path(self.data_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                path TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                size INTEGER DEFAULT 0,
                parent_path TEXT,
                created_at REAL,
                modified_at REAL,
                accessed_at REAL,
                permissions INTEGER,
                encrypted INTEGER DEFAULT 1,
                metadata TEXT
            )
        ''')
        
        # Create root folder if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO files (path, name, type, parent_path, created_at, modified_at, accessed_at, permissions, encrypted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('/', 'root', 'folder', None, 0, 0, 0, 0o755, 0))
        
        conn.commit()
        conn.close()
        
        print(f"[StorageAdapter] Initialized storage for disk '{self.disk_name}'")
    
    def encrypt(self, content: str) -> bytes:
        """
        Encrypt content using AES-256.
        
        Args:
            content: Plain text content
            
        Returns:
            Encrypted bytes
        """
        return self.cipher.encrypt(content.encode('utf-8'))
    
    def decrypt(self, encrypted_content: bytes) -> str:
        """
        Decrypt content.
        
        Args:
            encrypted_content: Encrypted bytes
            
        Returns:
            Decrypted plain text
        """
        return self.cipher.decrypt(encrypted_content).decode('utf-8')
    
    def _get_file_storage_path(self, vfs_path: str) -> str:
        """Get physical storage path for a VFS path."""
        # Convert VFS path to safe filename
        safe_path = vfs_path.replace('/', '_').replace('\\', '_')
        if safe_path.startswith('_'):
            safe_path = safe_path[1:]
        return os.path.join(self.data_path, safe_path + '.enc')
    
    def save_file(self, vfs_path: str, content: str, file_node: Any) -> bool:
        """
        Save file with encryption.
        
        Args:
            vfs_path: Virtual file system path
            content: File content
            file_node: FileNode object with metadata
            
        Returns:
            True if successful
        """
        try:
            # Encrypt and save content
            encrypted_content = self.encrypt(content)
            storage_path = self._get_file_storage_path(vfs_path)
            
            with open(storage_path, 'wb') as f:
                f.write(encrypted_content)
            
            # Update file size
            file_node.set_size(len(content))
            file_node.set_encrypted(True)
            
            # Save metadata to database
            self._save_metadata(file_node)
            
            print(f"[StorageAdapter] Saved encrypted file: {vfs_path}")
            return True
            
        except Exception as e:
            print(f"[StorageAdapter] Error saving file {vfs_path}: {e}")
            return False
    
    def read_file(self, vfs_path: str) -> Optional[str]:
        """
        Read and decrypt file.
        
        Args:
            vfs_path: Virtual file system path
            
        Returns:
            Decrypted content or None if error
        """
        try:
            storage_path = self._get_file_storage_path(vfs_path)
            
            if not os.path.exists(storage_path):
                print(f"[StorageAdapter] File not found: {vfs_path}")
                return None
            
            with open(storage_path, 'rb') as f:
                encrypted_content = f.read()
            
            content = self.decrypt(encrypted_content)
            
            # Update access time in metadata
            self._update_access_time(vfs_path)
            
            return content
            
        except Exception as e:
            print(f"[StorageAdapter] Error reading file {vfs_path}: {e}")
            return None
    
    def delete_file(self, vfs_path: str) -> bool:
        """
        Delete file and its metadata.
        
        Args:
            vfs_path: Virtual file system path
            
        Returns:
            True if successful
        """
        try:
            # Delete physical file
            storage_path = self._get_file_storage_path(vfs_path)
            if os.path.exists(storage_path):
                os.remove(storage_path)
            
            # Delete metadata
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM files WHERE path = ?', (vfs_path,))
            conn.commit()
            conn.close()
            
            print(f"[StorageAdapter] Deleted file: {vfs_path}")
            return True
            
        except Exception as e:
            print(f"[StorageAdapter] Error deleting file {vfs_path}: {e}")
            return False
    
    def list_files(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        List files in a directory.
        
        Args:
            directory_path: Directory path
            
        Returns:
            List of file metadata dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT path, name, type, size, created_at, modified_at, permissions, encrypted
                FROM files
                WHERE parent_path = ?
                ORDER BY type DESC, name ASC
            ''', (directory_path,))
            
            files = []
            for row in cursor.fetchall():
                files.append({
                    'path': row[0],
                    'name': row[1],
                    'type': row[2],
                    'size': row[3],
                    'created_at': row[4],
                    'modified_at': row[5],
                    'permissions': row[6],
                    'encrypted': bool(row[7])
                })
            
            conn.close()
            return files
            
        except Exception as e:
            print(f"[StorageAdapter] Error listing files in {directory_path}: {e}")
            return []
    
    def get_metadata(self, vfs_path: str) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from database.
        
        Args:
            vfs_path: Virtual file system path
            
        Returns:
            Metadata dictionary or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM files WHERE path = ?', (vfs_path,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'path': row[0],
                    'name': row[1],
                    'type': row[2],
                    'size': row[3],
                    'parent_path': row[4],
                    'created_at': row[5],
                    'modified_at': row[6],
                    'accessed_at': row[7],
                    'permissions': row[8],
                    'encrypted': bool(row[9]),
                    'metadata': json.loads(row[10]) if row[10] else {}
                }
            return None
            
        except Exception as e:
            print(f"[StorageAdapter] Error getting metadata for {vfs_path}: {e}")
            return None
    
    def _save_metadata(self, file_node: Any) -> None:
        """Save file node metadata to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(file_node.metadata)
        
        cursor.execute('''
            INSERT OR REPLACE INTO files 
            (path, name, type, size, parent_path, created_at, modified_at, accessed_at, permissions, encrypted, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_node.path,
            file_node.name,
            file_node.type,
            file_node.size,
            file_node.parent_path,
            file_node.created_at,
            file_node.modified_at,
            file_node.accessed_at,
            file_node.permissions,
            1 if file_node.encrypted else 0,
            metadata_json
        ))
        
        conn.commit()
        conn.close()
    
    def _update_access_time(self, vfs_path: str) -> None:
        """Update file access time."""
        import time
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE files SET accessed_at = ? WHERE path = ?', (time.time(), vfs_path))
        conn.commit()
        conn.close()
    
    def path_exists(self, vfs_path: str) -> bool:
        """Check if path exists in VFS."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM files WHERE path = ?', (vfs_path,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def get_disk_stats(self) -> Dict[str, Any]:
        """Get disk usage statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total size
            cursor.execute('SELECT SUM(size) FROM files WHERE type = "file"')
            used_space = cursor.fetchone()[0] or 0
            
            # Get file count
            cursor.execute('SELECT COUNT(*) FROM files WHERE type = "file"')
            file_count = cursor.fetchone()[0] or 0
            
            # Get folder count
            cursor.execute('SELECT COUNT(*) FROM files WHERE type = "folder"')
            folder_count = cursor.fetchone()[0] or 0
            
            conn.close()
            
            # Virtual capacity (100 MB)
            total_capacity = 100 * 1024 * 1024
            
            return {
                'disk_name': self.disk_name,
                'total_capacity': total_capacity,
                'used_space': used_space,
                'free_space': total_capacity - used_space,
                'file_count': file_count,
                'folder_count': folder_count,
                'usage_percent': round((used_space / total_capacity) * 100, 2) if total_capacity > 0 else 0,
                'encrypted': True
            }
            
        except Exception as e:
            print(f"[StorageAdapter] Error getting disk stats: {e}")
            return {}

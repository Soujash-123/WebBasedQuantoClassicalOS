"""
Storage Device
Virtual disk device for file storage operations.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from .base_device import BaseDevice


class StorageDevice(BaseDevice):
    """Virtual storage device for file operations."""
    
    def __init__(self, name: str = "StorageDisk", storage_path: Optional[str] = None):
        """
        Initialize the storage device.
        
        Args:
            name: Device name
            storage_path: Path to storage directory (default: ./virtual_storage)
        """
        super().__init__(name, "storage")
        self.storage_path = storage_path or "./virtual_storage"
        self.files: Dict[str, Any] = {}
        self.total_capacity = 1024 * 1024 * 100  # 100 MB virtual capacity
        self.used_space = 0
    
    def initialize(self) -> bool:
        """Initialize the storage device."""
        try:
            # Create storage directory
            Path(self.storage_path).mkdir(parents=True, exist_ok=True)
            
            # Load existing files index
            index_file = os.path.join(self.storage_path, ".index.json")
            if os.path.exists(index_file):
                with open(index_file, 'r') as f:
                    self.files = json.load(f)
            
            # Calculate used space
            self._calculate_used_space()
            
            result = super().initialize()
            self.set_metadata("capacity", self.total_capacity)
            self.set_metadata("used", self.used_space)
            self.set_metadata("available", self.total_capacity - self.used_space)
            
            return result
        except Exception as e:
            print(f"[StorageDevice] Error initializing: {e}")
            return False
    
    def write_file(self, filename: str, content: str) -> bool:
        """
        Write content to a file.
        
        Args:
            filename: Name of the file
            content: Content to write
            
        Returns:
            True if write successful
        """
        try:
            file_path = os.path.join(self.storage_path, filename)
            file_size = len(content.encode('utf-8'))
            
            # Check capacity
            if self.used_space + file_size > self.total_capacity:
                print(f"[StorageDevice] Insufficient space for {filename}")
                return False
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update index
            self.files[filename] = {
                "size": file_size,
                "path": file_path,
                "created": os.path.getctime(file_path),
                "modified": os.path.getmtime(file_path)
            }
            
            self.used_space += file_size
            self._save_index()
            
            print(f"[StorageDevice] File '{filename}' written ({file_size} bytes)")
            return True
            
        except Exception as e:
            print(f"[StorageDevice] Error writing file '{filename}': {e}")
            return False
    
    def read_file(self, filename: str) -> Optional[str]:
        """
        Read content from a file.
        
        Args:
            filename: Name of the file
            
        Returns:
            File content or None if error
        """
        try:
            if filename not in self.files:
                print(f"[StorageDevice] File '{filename}' not found")
                return None
            
            file_path = os.path.join(self.storage_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"[StorageDevice] File '{filename}' read")
            return content
            
        except Exception as e:
            print(f"[StorageDevice] Error reading file '{filename}': {e}")
            return None
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if deletion successful
        """
        try:
            if filename not in self.files:
                print(f"[StorageDevice] File '{filename}' not found")
                return False
            
            file_path = os.path.join(self.storage_path, filename)
            file_size = self.files[filename]["size"]
            
            os.remove(file_path)
            del self.files[filename]
            self.used_space -= file_size
            self._save_index()
            
            print(f"[StorageDevice] File '{filename}' deleted")
            return True
            
        except Exception as e:
            print(f"[StorageDevice] Error deleting file '{filename}': {e}")
            return False
    
    def list_files(self) -> List[str]:
        """Get list of all files."""
        return list(self.files.keys())
    
    def file_exists(self, filename: str) -> bool:
        """Check if a file exists."""
        return filename in self.files
    
    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get information about a file."""
        return self.files.get(filename)
    
    def _calculate_used_space(self) -> None:
        """Calculate total used space."""
        self.used_space = sum(info["size"] for info in self.files.values())
    
    def _save_index(self) -> None:
        """Save file index to disk."""
        try:
            index_file = os.path.join(self.storage_path, ".index.json")
            with open(index_file, 'w') as f:
                json.dump(self.files, f, indent=2)
        except Exception as e:
            print(f"[StorageDevice] Error saving index: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get detailed storage information."""
        return {
            "name": self.name,
            "type": self.device_type,
            "status": self.status_flag,
            "path": self.storage_path,
            "capacity": self.total_capacity,
            "used": self.used_space,
            "available": self.total_capacity - self.used_space,
            "file_count": len(self.files),
            "usage_percent": round((self.used_space / self.total_capacity) * 100, 2)
        }
    
    def shutdown(self) -> bool:
        """Shutdown the storage device."""
        self._save_index()
        return super().shutdown()

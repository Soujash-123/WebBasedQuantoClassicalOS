"""
File Node
Represents a file or folder in the virtual file system.
"""

import time
from typing import Dict, Any, Optional


class FileNode:
    """Represents a file or directory node in the VFS."""
    
    def __init__(
        self,
        name: str,
        path: str,
        node_type: str = "file",
        size: int = 0,
        parent_path: Optional[str] = None
    ):
        """
        Initialize a file node.
        
        Args:
            name: Name of the file/folder
            path: Full path in VFS
            node_type: 'file' or 'folder'
            size: Size in bytes (for files)
            parent_path: Path to parent directory
        """
        self.name = name
        self.path = path
        self.type = node_type
        self.size = size
        self.parent_path = parent_path or "/"
        
        # Timestamps
        current_time = time.time()
        self.created_at = current_time
        self.modified_at = current_time
        self.accessed_at = current_time
        
        # Permissions (Unix-style)
        self.permissions = 0o755 if node_type == "folder" else 0o644
        
        # Encryption status
        self.encrypted = False
        
        # Additional metadata
        self.metadata: Dict[str, Any] = {}
    
    def update_timestamps(self, access: bool = True, modify: bool = False) -> None:
        """
        Update file timestamps.
        
        Args:
            access: Update access time
            modify: Update modification time
        """
        current_time = time.time()
        
        if access:
            self.accessed_at = current_time
        
        if modify:
            self.modified_at = current_time
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get complete metadata for the node.
        
        Returns:
            Dictionary with all node metadata
        """
        return {
            "name": self.name,
            "path": self.path,
            "type": self.type,
            "size": self.size,
            "parent_path": self.parent_path,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "accessed_at": self.accessed_at,
            "permissions": oct(self.permissions),
            "encrypted": self.encrypted,
            "metadata": self.metadata
        }
    
    def set_permissions(self, permissions: int) -> None:
        """Set Unix-style permissions."""
        self.permissions = permissions
    
    def set_size(self, size: int) -> None:
        """Update file size."""
        self.size = size
        self.update_timestamps(modify=True)
    
    def set_encrypted(self, encrypted: bool) -> None:
        """Set encryption status."""
        self.encrypted = encrypted
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add custom metadata."""
        self.metadata[key] = value
    
    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """Get custom metadata value."""
        return self.metadata.get(key, default)
    
    def is_file(self) -> bool:
        """Check if node is a file."""
        return self.type == "file"
    
    def is_folder(self) -> bool:
        """Check if node is a folder."""
        return self.type == "folder"
    
    def __repr__(self) -> str:
        """String representation."""
        return f"FileNode(name='{self.name}', type='{self.type}', path='{self.path}')"

"""
VFS Manager
High-level virtual file system operations.
"""

import os
import shutil
from typing import Optional, List, Dict, Any
from .file_node import FileNode
from .storage_adapter import StorageAdapter


class VFSManager:
    """Manages virtual file system operations."""
    
    def __init__(self, storage_adapter: StorageAdapter):
        """
        Initialize VFS Manager.
        
        Args:
            storage_adapter: Storage adapter instance
        """
        self.storage = storage_adapter
        self.current_directory = "/"
        print(f"[VFSManager] VFS Manager initialized")
    
    def _normalize_path(self, path: str) -> str:
        """Normalize a VFS path."""
        if not path.startswith('/'):
            # Relative path - combine with current directory
            path = os.path.join(self.current_directory, path)
        
        # Normalize the path
        path = os.path.normpath(path).replace('\\', '/')
        
        # Ensure it starts with /
        if not path.startswith('/'):
            path = '/' + path
        
        return path
    
    def _get_parent_path(self, path: str) -> str:
        """Get parent directory path."""
        if path == '/':
            return '/'
        return os.path.dirname(path).replace('\\', '/') or '/'
    
    def mkdir(self, path: str) -> bool:
        """
        Create a directory.
        
        Args:
            path: Directory path
            
        Returns:
            True if successful
        """
        path = self._normalize_path(path)
        
        if self.storage.path_exists(path):
            print(f"[VFSManager] Directory already exists: {path}")
            return False
        
        # Check if parent exists
        parent_path = self._get_parent_path(path)
        if not self.storage.path_exists(parent_path):
            print(f"[VFSManager] Parent directory does not exist: {parent_path}")
            return False
        
        # Create folder node
        folder_name = os.path.basename(path)
        folder_node = FileNode(
            name=folder_name,
            path=path,
            node_type="folder",
            parent_path=parent_path
        )
        
        self.storage._save_metadata(folder_node)
        print(f"[VFSManager] Created directory: {path}")
        return True
    
    def ls(self, path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List files in a directory.
        
        Args:
            path: Directory path (default: current directory)
            
        Returns:
            List of file metadata
        """
        if path is None:
            path = self.current_directory
        else:
            path = self._normalize_path(path)
        
        if not self.storage.path_exists(path):
            print(f"[VFSManager] Directory not found: {path}")
            return []
        
        return self.storage.list_files(path)
    
    def cd(self, path: str) -> bool:
        """
        Change current directory.
        
        Args:
            path: Directory path
            
        Returns:
            True if successful
        """
        path = self._normalize_path(path)
        
        if not self.storage.path_exists(path):
            print(f"[VFSManager] Directory not found: {path}")
            return False
        
        metadata = self.storage.get_metadata(path)
        if metadata and metadata['type'] != 'folder':
            print(f"[VFSManager] Not a directory: {path}")
            return False
        
        self.current_directory = path
        print(f"[VFSManager] Changed directory to: {path}")
        return True
    
    def pwd(self) -> str:
        """
        Get current working directory.
        
        Returns:
            Current directory path
        """
        return self.current_directory
    
    def write(self, path: str, content: str) -> bool:
        """
        Write content to a file.
        
        Args:
            path: File path
            content: File content
            
        Returns:
            True if successful
        """
        path = self._normalize_path(path)
        parent_path = self._get_parent_path(path)
        
        # Check if parent directory exists
        if not self.storage.path_exists(parent_path):
            print(f"[VFSManager] Parent directory does not exist: {parent_path}")
            return False
        
        # Create or update file node
        file_name = os.path.basename(path)
        file_node = FileNode(
            name=file_name,
            path=path,
            node_type="file",
            parent_path=parent_path
        )
        
        return self.storage.save_file(path, content, file_node)
    
    def append(self, path: str, content: str) -> bool:
        """
        Append content to a file.
        
        Args:
            path: File path
            content: Content to append
            
        Returns:
            True if successful
        """
        path = self._normalize_path(path)
        
        # Read existing content
        existing_content = self.read(path)
        if existing_content is None:
            existing_content = ""
        
        # Append new content
        new_content = existing_content + content
        return self.write(path, new_content)
    
    def read(self, path: str) -> Optional[str]:
        """
        Read file content.
        
        Args:
            path: File path
            
        Returns:
            File content or None
        """
        path = self._normalize_path(path)
        return self.storage.read_file(path)
    
    def cat(self, path: str) -> Optional[str]:
        """Alias for read()."""
        return self.read(path)
    
    def rm(self, path: str) -> bool:
        """
        Delete a file.
        
        Args:
            path: File path
            
        Returns:
            True if successful
        """
        path = self._normalize_path(path)
        
        metadata = self.storage.get_metadata(path)
        if not metadata:
            print(f"[VFSManager] File not found: {path}")
            return False
        
        if metadata['type'] == 'folder':
            print(f"[VFSManager] Use rmdir to remove directories: {path}")
            return False
        
        return self.storage.delete_file(path)
    
    def rmdir(self, path: str) -> bool:
        """
        Remove an empty directory.
        
        Args:
            path: Directory path
            
        Returns:
            True if successful
        """
        path = self._normalize_path(path)
        
        if path == '/':
            print(f"[VFSManager] Cannot remove root directory")
            return False
        
        metadata = self.storage.get_metadata(path)
        if not metadata:
            print(f"[VFSManager] Directory not found: {path}")
            return False
        
        if metadata['type'] != 'folder':
            print(f"[VFSManager] Not a directory: {path}")
            return False
        
        # Check if directory is empty
        files = self.ls(path)
        if files:
            print(f"[VFSManager] Directory not empty: {path}")
            return False
        
        return self.storage.delete_file(path)
    
    def mv(self, src: str, dest: str) -> bool:
        """
        Move a file or folder.
        
        Args:
            src: Source path
            dest: Destination path
            
        Returns:
            True if successful
        """
        src = self._normalize_path(src)
        dest = self._normalize_path(dest)
        
        # For simplicity, implement as copy + delete
        if self.cp(src, dest):
            return self.rm(src) if self.storage.get_metadata(src)['type'] == 'file' else self.rmdir(src)
        return False
    
    def cp(self, src: str, dest: str) -> bool:
        """
        Copy a file.
        
        Args:
            src: Source path
            dest: Destination path
            
        Returns:
            True if successful
        """
        src = self._normalize_path(src)
        dest = self._normalize_path(dest)
        
        metadata = self.storage.get_metadata(src)
        if not metadata:
            print(f"[VFSManager] Source not found: {src}")
            return False
        
        if metadata['type'] == 'folder':
            print(f"[VFSManager] Cannot copy directories yet: {src}")
            return False
        
        # Read source content
        content = self.read(src)
        if content is None:
            return False
        
        # Write to destination
        return self.write(dest, content)
    
    def rename(self, src: str, new_name: str) -> bool:
        """
        Rename a file or folder.
        
        Args:
            src: Source path
            new_name: New name (not full path)
            
        Returns:
            True if successful
        """
        src = self._normalize_path(src)
        parent_path = self._get_parent_path(src)
        dest = os.path.join(parent_path, new_name).replace('\\', '/')
        
        return self.mv(src, dest)
    
    def file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Get file information.
        
        Args:
            path: File path
            
        Returns:
            File metadata dictionary
        """
        path = self._normalize_path(path)
        return self.storage.get_metadata(path)
    
    def search(self, pattern: str, search_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for files by name pattern.
        
        Args:
            pattern: Search pattern (substring match)
            search_path: Path to search in (default: root)
            
        Returns:
            List of matching files
        """
        if search_path is None:
            search_path = "/"
        else:
            search_path = self._normalize_path(search_path)
        
        results = []
        
        def search_recursive(path: str):
            files = self.ls(path)
            for file in files:
                if pattern.lower() in file['name'].lower():
                    results.append(file)
                if file['type'] == 'folder':
                    search_recursive(file['path'])
        
        search_recursive(search_path)
        return results
    
    def tree(self, path: Optional[str] = None, prefix: str = "", is_last: bool = True) -> None:
        """
        Display directory tree.
        
        Args:
            path: Root path for tree (default: current directory)
            prefix: Prefix for tree display (internal use)
            is_last: Whether this is the last item (internal use)
        """
        if path is None:
            path = self.current_directory
        else:
            path = self._normalize_path(path)
        
        if prefix == "":
            # First call - print root
            print(path)
        
        files = self.ls(path)
        for i, file in enumerate(files):
            is_last_item = (i == len(files) - 1)
            connector = "└── " if is_last_item else "├── "
            print(f"{prefix}{connector}{file['name']}" + (" /" if file['type'] == 'folder' else ""))
            
            if file['type'] == 'folder':
                extension = "    " if is_last_item else "│   "
                self.tree(file['path'], prefix + extension, is_last_item)
    
    def clear_file(self, path: str) -> bool:
        """
        Clear file content (make it empty).
        
        Args:
            path: File path
            
        Returns:
            True if successful
        """
        return self.write(path, "")

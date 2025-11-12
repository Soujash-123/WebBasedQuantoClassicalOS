"""
VFS Master
Integrates all VFS components into unified interface.
"""

from typing import Optional, List, Dict, Any
from .vfs_manager import VFSManager
from .mount_manager import MountManager
from .storage_adapter import StorageAdapter
from .nano_editor import nano_command


class VirtualFileSystem:
    """
    Main interface for the Virtual File System Layer.
    Integrates VFSManager, MountManager, and StorageAdapter.
    """
    
    def __init__(self, core_system=None, device_layer=None, default_disk: str = "MainDisk"):
        """
        Initialize the Virtual File System.
        
        Args:
            core_system: Reference to AIOSCore instance
            device_layer: Reference to DeviceLayer instance
            default_disk: Name of default disk to mount
        """
        print("=" * 60)
        print("Initializing Virtual File System Layer")
        print("=" * 60)
        
        self.core = core_system
        self.device_layer = device_layer
        
        # Initialize mount manager
        self.mount_manager = MountManager()
        
        # Mount default disk
        self.default_disk = default_disk
        self.mount_manager.mount_disk(default_disk)
        
        # Initialize VFS manager with default disk
        storage = self.mount_manager.get_disk(default_disk)
        self.vfs_manager = VFSManager(storage)
        
        # Current active disk
        self.current_disk = default_disk
        
        # Register with core if available
        if self.core:
            self.core.system_registry.register_module("vfs_layer", self)
            self.event_bus = self.core.event_bus
            self._setup_event_handlers()
        else:
            self.event_bus = None
        
        print("=" * 60)
        print("Virtual File System Layer initialized successfully")
        print("=" * 60)
    
    def _setup_event_handlers(self) -> None:
        """Setup event handlers for VFS events."""
        if not self.event_bus:
            return
        
        # Subscribe to system events
        self.event_bus.subscribe("system.shutdown", self._on_system_shutdown)
    
    def _on_system_shutdown(self, data: Any) -> None:
        """Handle system shutdown event."""
        print("[VirtualFileSystem] Received shutdown signal, unmounting disks...")
        self.shutdown()
    
    def switch_disk(self, disk_name: str) -> bool:
        """
        Switch to a different mounted disk.
        
        Args:
            disk_name: Name of disk to switch to
            
        Returns:
            True if successful
        """
        if not self.mount_manager.is_mounted(disk_name):
            print(f"[VirtualFileSystem] Disk not mounted: {disk_name}")
            return False
        
        storage = self.mount_manager.get_disk(disk_name)
        self.vfs_manager = VFSManager(storage)
        self.current_disk = disk_name
        print(f"[VirtualFileSystem] Switched to disk: {disk_name}")
        return True
    
    def get_current_disk(self) -> str:
        """Get name of currently active disk."""
        return self.current_disk
    
    # Convenience methods that delegate to vfs_manager
    
    def mkdir(self, path: str) -> bool:
        """Create a directory."""
        return self.vfs_manager.mkdir(path)
    
    def ls(self, path: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in directory."""
        return self.vfs_manager.ls(path)
    
    def cd(self, path: str) -> bool:
        """Change directory."""
        return self.vfs_manager.cd(path)
        
    def cmd_cd(self, args=None) -> str:
        """Handle cd command with argument processing"""
        if not args:
            # Default to home directory if no arguments provided
            path = "~"
        elif isinstance(args, list):
            # Join the list of arguments with spaces and strip any extra quotes
            path = ' '.join(args).strip('"\'')
        else:
            path = str(args).strip('"\'')
            
        if not path or path == '~':
            # If no path or ~, go to home directory
            path = "/home"
            
        try:
            success = self.cd(path)
            if success:
                return f"Changed directory to {self.pwd()}"
            return f"cd: No such file or directory: {path}"
        except Exception as e:
            return f"cd: {str(e)}"
    
    def pwd(self) -> str:
        """Print working directory."""
        return self.vfs_manager.pwd()
    
    def write(self, path: str, content: str) -> bool:
        """Write file."""
        return self.vfs_manager.write(path, content)
    
    def append(self, path: str, content: str) -> bool:
        """Append to file."""
        return self.vfs_manager.append(path, content)
    
    def read(self, path: str) -> Optional[str]:
        """Read file."""
        return self.vfs_manager.read(path)
    
    def cat(self, path: str) -> Optional[str]:
        """Display file contents."""
        return self.vfs_manager.cat(path)
    
    def rm(self, path: str) -> bool:
        """Remove file."""
        return self.vfs_manager.rm(path)
    
    def rmdir(self, path: str) -> bool:
        """Remove directory."""
        return self.vfs_manager.rmdir(path)
    
    def mv(self, src: str, dest: str) -> bool:
        """Move file/folder."""
        return self.vfs_manager.mv(src, dest)
    
    def cp(self, src: str, dest: str) -> bool:
        """Copy file."""
        return self.vfs_manager.cp(src, dest)
    
    def rename(self, src: str, new_name: str) -> bool:
        """Rename file/folder."""
        return self.vfs_manager.rename(src, new_name)
    
    def file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Get file information."""
        return self.vfs_manager.file_info(path)
    
    def search(self, pattern: str, search_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for files."""
        return self.vfs_manager.search(pattern, search_path)
    
    def tree(self, path: Optional[str] = None) -> None:
        """Display directory tree."""
        return self.vfs_manager.tree(path)
    
    def clear_file(self, path: str) -> bool:
        """Clear file content."""
        return self.vfs_manager.clear_file(path)
    
    # Mount manager convenience methods
    
    def mount(self, disk_name: str) -> bool:
        """Mount a disk."""
        return self.mount_manager.mount_disk(disk_name)
    
    def unmount(self, disk_name: str) -> bool:
        """Unmount a disk."""
        return self.mount_manager.unmount_disk(disk_name)
    
    def disks(self) -> List[str]:
        """List mounted disks."""
        return self.mount_manager.list_mounted_disks()
    
    def disk_info(self, disk_name: str) -> Optional[Dict[str, Any]]:
        """Get disk information."""
        return self.mount_manager.disk_info(disk_name)
    
    def help(self) -> None:
        """Display available VFS commands."""
        commands = {
            "File Operations": [
                "ls [path] - List files/folders",
                "cd <path> - Change directory",
                "pwd - Print working directory",
                "mkdir <folder> - Create directory",
                "rmdir <folder> - Remove empty directory",
                "write <file> <content> - Write to file",
                "append <file> <content> - Append to file",
                "cat <file> - Display file contents",
                "read <file> - Read file (alias to cat)",
                "rm <file> - Delete file",
                "mv <src> <dest> - Move file/folder",
                "cp <src> <dest> - Copy file",
                "rename <src> <new_name> - Rename file/folder",
                "file_info <file> - Show file metadata",
                "clear_file <file> - Clear file content"
            ],
            "Search & Navigation": [
                "search <pattern> - Search files by name",
                "tree [path] - Show directory tree"
            ],
            "Disk Management": [
                "mount <disk_name> - Mount a virtual disk",
                "unmount <disk_name> - Unmount a disk",
                "disks - List mounted disks",
                "disk_info <disk_name> - Show disk statistics",
                "switch_disk <disk_name> - Switch active disk"
            ],
            "Help": [
                "help - Show this help message"
            ]
        }
        
        print("\n" + "=" * 60)
        print("Virtual File System - Available Commands")
        print("=" * 60)
        
        for category, cmds in commands.items():
            print(f"\n{category}:")
            for cmd in cmds:
                print(f"  {cmd}")
        
        print("\n" + "=" * 60)
    
    def initialize(self) -> bool:
        """Initialize the VFS layer"""
        # Already initialized in __init__
        return True
    
    def get_commands(self) -> Dict:
        """Get available VFS commands"""
        return {
            'cd': {
                'function': self.cmd_cd,
                'description': 'Change current working directory',
                'usage': 'cd <directory>',
                'layer': 'filesystem'
            },
            'ls': {
                'function': self.cmd_ls,
                'description': 'List directory contents',
                'usage': 'ls [path]',
                'layer': 'filesystem'
            },
            'cat': {
                'function': self.cmd_cat,
                'description': 'Display file contents',
                'usage': 'cat <file>',
                'layer': 'filesystem'
            },
            'mkdir': {
                'function': self.cmd_mkdir,
                'description': 'Create directory',
                'usage': 'mkdir <directory>',
                'layer': 'filesystem'
            },
            'rm': {
                'function': self.cmd_rm,
                'description': 'Remove file',
                'usage': 'rm <file>',
                'layer': 'filesystem'
            },
            'touch': {
                'function': self.cmd_touch,
                'description': 'Create empty file',
                'usage': 'touch <file>',
                'layer': 'filesystem'
            },
            'pwd': {
                'function': self.cmd_pwd,
                'description': 'Print working directory',
                'usage': 'pwd',
                'layer': 'filesystem'
            },
            'cp': {
                'function': self.cmd_cp,
                'description': 'Copy file',
                'usage': 'cp <src> <dest>',
                'layer': 'filesystem'
            },
            'mv': {
                'function': self.cmd_mv,
                'description': 'Move/rename file',
                'usage': 'mv <src> <dest>',
                'layer': 'filesystem'
            },
            'nano': {
                'function': self.cmd_nano,
                'description': 'Edit file with nano-like editor',
                'usage': 'nano <filename>',
                'layer': 'filesystem'
            },
            'vi': {
                'function': self.cmd_nano,
                'description': 'Edit file (alias for nano)',
                'usage': 'vi <filename>',
                'layer': 'filesystem'
            },
            'edit': {
                'function': self.cmd_nano,
                'description': 'Edit file (alias for nano)',
                'usage': 'edit <filename>',
                'layer': 'filesystem'
            }
        }
    
    def cmd_ls(self, args=None):
        """List directory contents"""
        path = args[0] if args else None
        files = self.vfs_manager.ls(path)
        
        if not files:
            return "Directory is empty"
        
        result = []
        for file in files:
            file_type = "d" if file['type'] == 'folder' else "-"
            size = file.get('size', 0)
            name = file['name']
            result.append(f"{file_type}  {size:>8}  {name}")
        
        return "\n".join(result)
    
    def cmd_cat(self, args=None):
        """Display file contents"""
        if not args:
            return "Usage: cat <file>"
        
        content = self.vfs_manager.cat(args[0])
        if content is None:
            return f"Error: File not found or cannot be read: {args[0]}"
        
        return content
    
    def cmd_mkdir(self, args=None):
        """Create directory"""
        if not args:
            return "Usage: mkdir <directory>"
        
        if self.vfs_manager.mkdir(args[0]):
            return f"Directory created: {args[0]}"
        else:
            return f"Error: Could not create directory: {args[0]}"
    
    def cmd_rm(self, args=None):
        """Remove file"""
        if not args:
            return "Usage: rm <file>"
        
        if self.vfs_manager.rm(args[0]):
            return f"File removed: {args[0]}"
        else:
            return f"Error: Could not remove file: {args[0]}"
    
    def cmd_touch(self, args=None):
        """Create empty file"""
        if not args:
            return "Usage: touch <file>"
        
        if self.vfs_manager.write(args[0], ""):
            return f"File created: {args[0]}"
        else:
            return f"Error: Could not create file: {args[0]}"
    
    def cmd_pwd(self, args=None):
        """Print working directory"""
        return self.vfs_manager.pwd()
    
    def cmd_cp(self, args=None):
        """Copy file"""
        if not args or len(args) < 2:
            return "Usage: cp <src> <dest>"
        
        if self.vfs_manager.cp(args[0], args[1]):
            return f"Copied {args[0]} to {args[1]}"
        else:
            return f"Error: Could not copy file"
    
    def cmd_mv(self, args=None):
        """Move/rename file"""
        if not args or len(args) < 2:
            return "Usage: mv <src> <dest>"
        
        if self.vfs_manager.mv(args[0], args[1]):
            return f"Moved {args[0]} to {args[1]}"
        else:
            return f"Error: Could not move file"
    
    def cmd_nano(self, args=None):
        """Edit file with nano-like editor
        
        Args:
            args: Command arguments (filename [--gui])
            
        Returns:
            File content if --gui flag is used, otherwise editor output
        """
        gui_mode = False
        if isinstance(args, list) and '--gui' in args:
            gui_mode = True
        return nano_command(self.vfs_manager, args, gui_mode)
    
    def shutdown(self) -> None:
        """Shutdown the VFS layer."""
        print("\n" + "=" * 60)
        print("Shutting down Virtual File System Layer")
        print("=" * 60)
        
        # Unmount all disks
        self.mount_manager.unmount_all()
        
        print("=" * 60)
        print("Virtual File System Layer shut down successfully")
        print("=" * 60 + "\n")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
        return False


# Alias for compatibility with OS Master
VFSLayer = VirtualFileSystem

"""
Mount Manager
Manages virtual disk mounting and unmounting.
"""

from typing import Dict, List, Optional, Any
from .storage_adapter import StorageAdapter


class MountManager:
    """Manages virtual disk mounts."""
    
    def __init__(self, base_path: str = "./vfs_storage"):
        """
        Initialize mount manager.
        
        Args:
            base_path: Base path for VFS storage
        """
        self.base_path = base_path
        self.mounted_disks: Dict[str, StorageAdapter] = {}
        print(f"[MountManager] Mount Manager initialized")
    
    def mount_disk(self, disk_name: str) -> bool:
        """
        Mount a virtual disk.
        
        Args:
            disk_name: Name of the disk to mount
            
        Returns:
            True if successful
        """
        if disk_name in self.mounted_disks:
            print(f"[MountManager] Disk already mounted: {disk_name}")
            return False
        
        try:
            storage_adapter = StorageAdapter(disk_name, self.base_path)
            self.mounted_disks[disk_name] = storage_adapter
            print(f"[MountManager] Mounted disk: {disk_name}")
            return True
        except Exception as e:
            print(f"[MountManager] Error mounting disk {disk_name}: {e}")
            return False
    
    def unmount_disk(self, disk_name: str) -> bool:
        """
        Unmount a virtual disk.
        
        Args:
            disk_name: Name of the disk to unmount
            
        Returns:
            True if successful
        """
        if disk_name not in self.mounted_disks:
            print(f"[MountManager] Disk not mounted: {disk_name}")
            return False
        
        del self.mounted_disks[disk_name]
        print(f"[MountManager] Unmounted disk: {disk_name}")
        return True
    
    def list_mounted_disks(self) -> List[str]:
        """
        Get list of mounted disk names.
        
        Returns:
            List of disk names
        """
        return list(self.mounted_disks.keys())
    
    def get_disk(self, disk_name: str) -> Optional[StorageAdapter]:
        """
        Get storage adapter for a mounted disk.
        
        Args:
            disk_name: Disk name
            
        Returns:
            StorageAdapter instance or None
        """
        return self.mounted_disks.get(disk_name)
    
    def is_mounted(self, disk_name: str) -> bool:
        """
        Check if a disk is mounted.
        
        Args:
            disk_name: Disk name
            
        Returns:
            True if mounted
        """
        return disk_name in self.mounted_disks
    
    def disk_info(self, disk_name: str) -> Optional[Dict[str, Any]]:
        """
        Get disk information.
        
        Args:
            disk_name: Disk name
            
        Returns:
            Disk statistics dictionary or None
        """
        if disk_name not in self.mounted_disks:
            print(f"[MountManager] Disk not mounted: {disk_name}")
            return None
        
        storage = self.mounted_disks[disk_name]
        return storage.get_disk_stats()
    
    def get_all_disk_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information for all mounted disks.
        
        Returns:
            Dictionary mapping disk names to their info
        """
        info = {}
        for disk_name in self.mounted_disks:
            info[disk_name] = self.disk_info(disk_name)
        return info
    
    def unmount_all(self) -> int:
        """
        Unmount all disks.
        
        Returns:
            Number of disks unmounted
        """
        count = len(self.mounted_disks)
        self.mounted_disks.clear()
        print(f"[MountManager] Unmounted {count} disk(s)")
        return count

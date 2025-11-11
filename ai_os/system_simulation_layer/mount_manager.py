"""
Mount Manager
Handles mounting and unmounting of drives and devices.
"""

import os
from typing import List, Dict, Optional
from .system_logger import SystemLogger
from .system_environment import SystemEnvironment


class MountManager:
    """Manages device mounting and unmounting."""
    
    def __init__(
        self,
        mount_base: str = "/mnt",
        logger: Optional[SystemLogger] = None,
        environment: Optional[SystemEnvironment] = None,
        device_layer=None,
        vfs_layer=None
    ):
        """
        Initialize mount manager.
        
        Args:
            mount_base: Base directory for mounts
            logger: System logger
            environment: System environment
            device_layer: Device layer for device info
            vfs_layer: VFS layer for filesystem operations
        """
        self.mount_base = mount_base
        self.logger = logger or SystemLogger()
        self.environment = environment or SystemEnvironment()
        self.device_layer = device_layer
        self.vfs_layer = vfs_layer
        
        # Mount table: path -> device info
        self.mount_table: Dict[str, dict] = {}
        
        # Load existing mounts from environment
        self._load_mounts()
    
    def _load_mounts(self) -> None:
        """Load mounts from environment."""
        mounts = self.environment.list_mounts()
        for path, device in mounts.items():
            self.mount_table[path] = {
                'device': device,
                'type': 'simulated',
                'options': 'rw'
            }
    
    def mount(self, device: str, path: str, fs_type: str = 'ext4', 
              options: str = 'rw') -> bool:
        """
        Mount a device.
        
        Args:
            device: Device name (e.g., 'usb0', '/dev/sda1')
            path: Mount point
            fs_type: Filesystem type
            options: Mount options
            
        Returns:
            True if successful
        """
        # Normalize path
        if not path.startswith('/'):
            path = os.path.join(self.mount_base, path)
        
        # Check if already mounted
        if path in self.mount_table:
            print(f"mount: {path} is already mounted")
            return False
        
        # Check if device exists (if device layer available)
        if self.device_layer:
            # Try to find device
            devices = self.device_layer.manager.list_devices()
            device_found = any(d.name == device for d in devices)
            
            if not device_found:
                print(f"mount: {device}: device not found")
                # Allow mounting anyway for simulation
        
        # Create mount point in VFS if available
        if self.vfs_layer:
            try:
                self.vfs_layer.mkdir(path)
            except:
                pass  # Directory may already exist
        
        # Add to mount table
        self.mount_table[path] = {
            'device': device,
            'type': fs_type,
            'options': options,
            'mounted_at': self._get_timestamp()
        }
        
        # Register in environment
        self.environment.register_mount(device, path)
        
        # Log mount
        self.logger.log_mount(device, path, success=True)
        
        print(f"✓ Mounted {device} on {path}")
        return True
    
    def unmount(self, path: str) -> bool:
        """
        Unmount a device.
        
        Args:
            path: Mount point
            
        Returns:
            True if successful
        """
        # Normalize path
        if not path.startswith('/'):
            path = os.path.join(self.mount_base, path)
        
        # Check if mounted
        if path not in self.mount_table:
            print(f"umount: {path}: not mounted")
            return False
        
        device = self.mount_table[path]['device']
        
        # Remove from mount table
        del self.mount_table[path]
        
        # Unregister from environment
        self.environment.unregister_mount(path)
        
        # Log unmount
        self.logger.log_unmount(path, success=True)
        
        print(f"✓ Unmounted {path}")
        return True
    
    def list_mounts(self) -> List[dict]:
        """List all mounted devices."""
        mounts = []
        for path, info in self.mount_table.items():
            mounts.append({
                'device': info['device'],
                'path': path,
                'type': info.get('type', 'unknown'),
                'options': info.get('options', 'rw')
            })
        return mounts
    
    def disk_usage(self) -> None:
        """Show disk usage (df command)."""
        print(f"{'Filesystem':<20} {'Size':>10} {'Used':>10} {'Avail':>10} {'Use%':>6} {'Mounted on'}")
        print("-" * 80)
        
        # Root filesystem
        print(f"{'rootfs':<20} {'10G':>10} {'2.5G':>10} {'7.5G':>10} {'25%':>6} {'/':20}")
        
        # Mounted devices
        for path, info in self.mount_table.items():
            device = info['device']
            # Simulated sizes
            print(f"{device:<20} {'5G':>10} {'1.2G':>10} {'3.8G':>10} {'24%':>6} {path:20}")
    
    def list_devices(self) -> None:
        """List block devices (lsblk command)."""
        print(f"{'NAME':<15} {'SIZE':>10} {'TYPE':<10} {'MOUNTPOINT'}")
        print("-" * 60)
        
        # Root device
        print(f"{'sda':<15} {'100G':>10} {'disk':<10}")
        print(f"{'└─sda1':<15} {'100G':>10} {'part':<10} {'/':20}")
        
        # Get devices from device layer
        if self.device_layer:
            devices = self.device_layer.manager.list_devices()
            for device in devices:
                status = device.status()
                device_name = status.get('name', 'unknown')
                device_type = status.get('type', 'unknown')
                
                # Check if mounted
                mount_point = ""
                for path, info in self.mount_table.items():
                    if info['device'] == device_name:
                        mount_point = path
                        break
                
                # Simulated size
                size = "8G" if 'usb' in device_name.lower() else "1G"
                print(f"{device_name:<15} {size:>10} {device_type:<10} {mount_point:20}")
    
    def is_mounted(self, path: str) -> bool:
        """Check if path is mounted."""
        return path in self.mount_table
    
    def get_mount_info(self, path: str) -> Optional[dict]:
        """Get mount information."""
        return self.mount_table.get(path)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def run_mount_command(self, args: List[str], context) -> bool:
        """
        Run mount command.
        
        Args:
            args: Command arguments
            context: Execution context
            
        Returns:
            True if successful
        """
        if len(args) < 2:
            # List mounts
            mounts = self.list_mounts()
            if not mounts:
                print("No devices mounted")
            else:
                for mount in mounts:
                    print(f"{mount['device']} on {mount['path']} type {mount['type']} ({mount['options']})")
            return True
        
        device = args[0]
        path = args[1]
        fs_type = args[2] if len(args) > 2 else 'ext4'
        
        return self.mount(device, path, fs_type)
    
    def run_unmount_command(self, args: List[str], context) -> bool:
        """
        Run unmount command.
        
        Args:
            args: Command arguments
            context: Execution context
            
        Returns:
            True if successful
        """
        if not args:
            print("umount: missing operand")
            print("Usage: umount <path>")
            return False
        
        return self.unmount(args[0])
    
    def run_df_command(self, args: List[str], context) -> bool:
        """Run df command."""
        self.disk_usage()
        return True
    
    def run_lsblk_command(self, args: List[str], context) -> bool:
        """Run lsblk command."""
        self.list_devices()
        return True

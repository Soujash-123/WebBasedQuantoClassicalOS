"""
Update Manager
Handles system updates and upgrades.
"""

from typing import List, Dict, Optional
from .system_logger import SystemLogger


class UpdateManager:
    """Manages system updates."""
    
    def __init__(
        self,
        logger: Optional[SystemLogger] = None,
        package_manager=None
    ):
        """
        Initialize update manager.
        
        Args:
            logger: System logger
            package_manager: Package manager instance
        """
        self.logger = logger or SystemLogger()
        self.package_manager = package_manager
        self.last_update = None
        self.update_available = []
    
    def check_updates(self) -> List[dict]:
        """
        Check for available updates.
        
        Returns:
            List of packages with updates
        """
        if not self.package_manager:
            return []
        
        print("Checking for updates...")
        
        # Get installed packages
        installed = self.package_manager.environment.list_modules()
        available = self.package_manager.available_packages
        
        updates = []
        for name, info in installed.items():
            if name in available:
                available_version = available[name]['version']
                installed_version = info['version']
                
                if available_version != installed_version:
                    updates.append({
                        'name': name,
                        'installed': installed_version,
                        'available': available_version
                    })
        
        self.update_available = updates
        
        if updates:
            print(f"{len(updates)} packages can be upgraded")
            for update in updates:
                print(f"  {update['name']}: {update['installed']} -> {update['available']}")
        else:
            print("All packages are up to date")
        
        return updates
    
    def apply_updates(self) -> bool:
        """
        Apply all available updates.
        
        Returns:
            True if successful
        """
        if not self.update_available:
            print("No updates available")
            return True
        
        if not self.package_manager:
            print("Package manager not available")
            return False
        
        print(f"Applying {len(self.update_available)} updates...")
        
        success_count = 0
        for update in self.update_available:
            print(f"\nUpdating {update['name']}...")
            if self.package_manager.install(update['name']):
                success_count += 1
        
        print(f"\n✓ {success_count}/{len(self.update_available)} packages updated")
        
        self.update_available = []
        return success_count > 0

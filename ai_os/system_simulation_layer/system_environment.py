"""
System Environment
Manages system environment, PATH, installed modules, and OS info.
"""

import os
import json
from typing import Dict, List, Optional


class SystemEnvironment:
    """Manages system environment and state."""
    
    def __init__(self, env_file: str = "./system_env.json"):
        """
        Initialize system environment.
        
        Args:
            env_file: File to persist environment
        """
        self.env_file = env_file
        self.path_dirs: List[str] = []
        self.installed_modules: Dict[str, dict] = {}
        self.mounted_drives: Dict[str, str] = {}
        self.os_info: Dict[str, str] = {}
        self.user_profiles: Dict[str, dict] = {}
        
        # Initialize defaults
        self._init_defaults()
        
        # Load existing environment
        self.load()
    
    def _init_defaults(self) -> None:
        """Initialize default environment."""
        self.path_dirs = [
            '/bin',
            '/usr/bin',
            '/usr/local/bin',
            '/sbin',
            '/usr/sbin',
            '/opt/bin'
        ]
        
        self.os_info = {
            'name': 'AI OS',
            'version': '1.0.0',
            'codename': 'Genesis',
            'kernel': '5.15.0-aios',
            'architecture': 'x86_64',
            'distro': 'AI OS Linux'
        }
    
    def add_to_path(self, directory: str) -> bool:
        """Add directory to PATH."""
        if directory not in self.path_dirs:
            self.path_dirs.append(directory)
            self.save()
            return True
        return False
    
    def remove_from_path(self, directory: str) -> bool:
        """Remove directory from PATH."""
        if directory in self.path_dirs:
            self.path_dirs.remove(directory)
            self.save()
            return True
        return False
    
    def get_path(self) -> str:
        """Get PATH as string."""
        return ':'.join(self.path_dirs)
    
    def register_module(self, name: str, version: str, path: str, 
                       commands: Optional[List[str]] = None) -> None:
        """
        Register an installed module.
        
        Args:
            name: Module name
            version: Module version
            path: Installation path
            commands: List of commands provided by module
        """
        self.installed_modules[name] = {
            'version': version,
            'path': path,
            'commands': commands or [],
            'installed_at': self._get_timestamp()
        }
        self.save()
    
    def unregister_module(self, name: str) -> bool:
        """Unregister a module."""
        if name in self.installed_modules:
            del self.installed_modules[name]
            self.save()
            return True
        return False
    
    def get_module(self, name: str) -> Optional[dict]:
        """Get module info."""
        return self.installed_modules.get(name)
    
    def list_modules(self) -> Dict[str, dict]:
        """List all installed modules."""
        return self.installed_modules.copy()
    
    def register_mount(self, device: str, path: str) -> None:
        """Register a mounted device."""
        self.mounted_drives[path] = device
        self.save()
    
    def unregister_mount(self, path: str) -> bool:
        """Unregister a mounted device."""
        if path in self.mounted_drives:
            del self.mounted_drives[path]
            self.save()
            return True
        return False
    
    def get_mount(self, path: str) -> Optional[str]:
        """Get device mounted at path."""
        return self.mounted_drives.get(path)
    
    def list_mounts(self) -> Dict[str, str]:
        """List all mounts."""
        return self.mounted_drives.copy()
    
    def set_os_info(self, key: str, value: str) -> None:
        """Set OS info field."""
        self.os_info[key] = value
        self.save()
    
    def get_os_info(self) -> Dict[str, str]:
        """Get OS information."""
        return self.os_info.copy()
    
    def add_user_profile(self, username: str, profile: dict) -> None:
        """Add user profile."""
        self.user_profiles[username] = profile
        self.save()
    
    def get_user_profile(self, username: str) -> Optional[dict]:
        """Get user profile."""
        return self.user_profiles.get(username)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def save(self) -> bool:
        """Save environment to file."""
        try:
            data = {
                'path_dirs': self.path_dirs,
                'installed_modules': self.installed_modules,
                'mounted_drives': self.mounted_drives,
                'os_info': self.os_info,
                'user_profiles': self.user_profiles
            }
            
            with open(self.env_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving environment: {e}")
            return False
    
    def load(self) -> bool:
        """Load environment from file."""
        if not os.path.exists(self.env_file):
            return False
        
        try:
            with open(self.env_file, 'r') as f:
                data = json.load(f)
            
            self.path_dirs = data.get('path_dirs', self.path_dirs)
            self.installed_modules = data.get('installed_modules', {})
            self.mounted_drives = data.get('mounted_drives', {})
            self.os_info.update(data.get('os_info', {}))
            self.user_profiles = data.get('user_profiles', {})
            
            return True
        except Exception as e:
            print(f"Error loading environment: {e}")
            return False
    
    def get_summary(self) -> dict:
        """Get environment summary."""
        return {
            'os': self.os_info,
            'path_dirs': len(self.path_dirs),
            'installed_modules': len(self.installed_modules),
            'mounted_drives': len(self.mounted_drives),
            'user_profiles': len(self.user_profiles)
        }

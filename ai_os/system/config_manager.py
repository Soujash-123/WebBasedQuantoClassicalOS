"""
Config Manager
Handles global and per-user configurations with encrypted storage.
"""

import json
import os
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet


class ConfigManager:
    """Manages system and user configurations."""
    
    def __init__(self, config_file: str = "./system_config.json", encrypt: bool = False):
        """
        Initialize config manager.
        
        Args:
            config_file: Path to configuration file
            encrypt: Whether to encrypt configuration
        """
        self.config_file = config_file
        self.encrypt = encrypt
        self.config: Dict[str, Any] = {}
        
        # Encryption key (in production, manage securely)
        if encrypt:
            self.cipher = Fernet(Fernet.generate_key())
        else:
            self.cipher = None
        
        # Load existing config
        self.load()
        
        # Set defaults if empty
        if not self.config:
            self._set_defaults()
        
        print("[ConfigManager] Config Manager initialized")
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self.config = {
            "system": {
                "name": "AI OS",
                "version": "1.0.0",
                "prompt_style": "[{user}@AIOS:{path}]$ ",
                "default_editor": "nano",
                "theme": "default",
                "log_level": "INFO"
            },
            "filesystem": {
                "default_disk": "MainDisk",
                "mount_points": {},
                "max_file_size": 104857600  # 100MB
            },
            "shell": {
                "history_size": 1000,
                "aliases": {},
                "macros": {}
            },
            "users": {
                "session_timeout": 3600,
                "password_min_length": 4,
                "default_home": "/home/{username}"
            },
            "processes": {
                "scheduler_algorithm": "fifo",
                "max_concurrent": 10,
                "time_quantum": 0.1
            }
        }
        self.save()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def delete(self, key: str) -> bool:
        """
        Delete configuration key.
        
        Args:
            key: Configuration key
            
        Returns:
            True if deleted
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                return False
            config = config[k]
        
        # Delete key
        if keys[-1] in config:
            del config[keys[-1]]
            return True
        
        return False
    
    def list_all(self, prefix: Optional[str] = None) -> Dict[str, Any]:
        """
        List all configuration values.
        
        Args:
            prefix: Optional prefix filter
            
        Returns:
            Dictionary of configuration values
        """
        if prefix:
            return self.get(prefix, {})
        return self.config.copy()
    
    def save(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            True if successful
        """
        try:
            data = json.dumps(self.config, indent=2)
            
            if self.encrypt and self.cipher:
                data = self.cipher.encrypt(data.encode())
                mode = 'wb'
            else:
                mode = 'w'
            
            with open(self.config_file, mode) as f:
                if isinstance(data, bytes):
                    f.write(data)
                else:
                    f.write(data)
            
            return True
            
        except Exception as e:
            print(f"[ConfigManager] Error saving config: {e}")
            return False
    
    def load(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            True if successful
        """
        if not os.path.exists(self.config_file):
            return False
        
        try:
            if self.encrypt and self.cipher:
                mode = 'rb'
            else:
                mode = 'r'
            
            with open(self.config_file, mode) as f:
                data = f.read()
            
            if self.encrypt and self.cipher and isinstance(data, bytes):
                data = self.cipher.decrypt(data).decode()
            
            self.config = json.loads(data)
            return True
            
        except Exception as e:
            print(f"[ConfigManager] Error loading config: {e}")
            return False
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._set_defaults()
        print("[ConfigManager] Configuration reset to defaults")
    
    def export_config(self, filepath: str) -> bool:
        """Export configuration to a file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"[ConfigManager] Error exporting config: {e}")
            return False
    
    def import_config(self, filepath: str) -> bool:
        """Import configuration from a file."""
        try:
            with open(filepath, 'r') as f:
                self.config = json.load(f)
            self.save()
            return True
        except Exception as e:
            print(f"[ConfigManager] Error importing config: {e}")
            return False

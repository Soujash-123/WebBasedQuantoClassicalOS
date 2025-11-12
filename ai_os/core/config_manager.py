"""
Configuration Manager
Manages global configurations for the AI OS.
"""

import json
import os
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """Manages system-wide configuration settings."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the Configuration Manager.
        
        Args:
            config_file: Path to the configuration JSON file. 
                        If None, uses default 'config.json' in current directory.
        """
        self.config_file = config_file or "config.json"
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file if it exists."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                print(f"[ConfigManager] Configuration loaded from {self.config_file}")
            except json.JSONDecodeError as e:
                print(f"[ConfigManager] Error loading config: {e}. Starting with empty config.")
                self.config = {}
        else:
            print(f"[ConfigManager] No config file found. Starting with empty config.")
            self.config = {}
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation for nested keys, e.g., 'system.mode')
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_config(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation for nested keys)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the nested location
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        print(f"[ConfigManager] Set config: {key} = {value}")
    
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"[ConfigManager] Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"[ConfigManager] Error saving config: {e}")
            return False
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        Get all configuration settings.
        
        Returns:
            Dictionary of all configuration settings
        """
        return self.config.copy()
    
    def clear_config(self) -> None:
        """Clear all configuration settings."""
        self.config = {}
        print("[ConfigManager] Configuration cleared")

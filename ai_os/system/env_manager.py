"""
Environment Manager
Manages environment variables for processes and users.
"""

import os
from typing import Dict, Optional, Any


class EnvManager:
    """Manages environment variables."""
    
    def __init__(self, config_manager=None):
        """
        Initialize environment manager.
        
        Args:
            config_manager: Optional ConfigManager for persistence
        """
        self.config_manager = config_manager
        self.env_vars: Dict[str, str] = {}
        
        # Load system environment variables
        self._load_system_env()
        
        # Load persisted env vars
        if config_manager:
            self._load_persisted_env()
        
        print("[EnvManager] Environment Manager initialized")
    
    def _load_system_env(self) -> None:
        """Load system environment variables."""
        # Copy important system env vars
        important_vars = ['PATH', 'HOME', 'USER', 'SHELL', 'TERM']
        for var in important_vars:
            if var in os.environ:
                self.env_vars[var] = os.environ[var]
        
        # Set AI OS specific vars
        self.env_vars['AIOS_VERSION'] = '1.0.0'
        self.env_vars['AIOS_HOME'] = os.getcwd()
    
    def _load_persisted_env(self) -> None:
        """Load persisted environment variables from config."""
        if self.config_manager:
            env_config = self.config_manager.get('environment', {})
            self.env_vars.update(env_config)
    
    def _save_persisted_env(self) -> None:
        """Save environment variables to config."""
        if self.config_manager:
            # Filter out system vars
            system_vars = ['PATH', 'HOME', 'USER', 'SHELL', 'TERM']
            persisted = {k: v for k, v in self.env_vars.items() if k not in system_vars}
            self.config_manager.set('environment', persisted)
            self.config_manager.save()
    
    def set(self, name: str, value: str, persist: bool = True) -> None:
        """
        Set an environment variable.
        
        Args:
            name: Variable name
            value: Variable value
            persist: Whether to persist to config
        """
        self.env_vars[name] = str(value)
        
        if persist:
            self._save_persisted_env()
        
        print(f"[EnvManager] Set {name}={value}")
    
    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get an environment variable.
        
        Args:
            name: Variable name
            default: Default value if not found
            
        Returns:
            Variable value or default
        """
        return self.env_vars.get(name, default)
    
    def unset(self, name: str) -> bool:
        """
        Unset an environment variable.
        
        Args:
            name: Variable name
            
        Returns:
            True if variable was removed
        """
        if name in self.env_vars:
            del self.env_vars[name]
            self._save_persisted_env()
            print(f"[EnvManager] Unset {name}")
            return True
        return False
    
    def list_all(self) -> Dict[str, str]:
        """
        Get all environment variables.
        
        Returns:
            Dictionary of all environment variables
        """
        return self.env_vars.copy()
    
    def exists(self, name: str) -> bool:
        """Check if an environment variable exists."""
        return name in self.env_vars
    
    def clear_all(self, keep_system: bool = True) -> None:
        """
        Clear all environment variables.
        
        Args:
            keep_system: Whether to keep system variables
        """
        if keep_system:
            system_vars = ['PATH', 'HOME', 'USER', 'SHELL', 'TERM', 'AIOS_VERSION', 'AIOS_HOME']
            self.env_vars = {k: v for k, v in self.env_vars.items() if k in system_vars}
        else:
            self.env_vars.clear()
        
        self._save_persisted_env()
        print("[EnvManager] Environment variables cleared")
    
    def export_to_process(self, process_env: Dict[str, str]) -> Dict[str, str]:
        """
        Export environment variables for a process.
        
        Args:
            process_env: Process-specific environment
            
        Returns:
            Merged environment dictionary
        """
        merged = self.env_vars.copy()
        merged.update(process_env)
        return merged
    
    def expand_variables(self, text: str) -> str:
        """
        Expand environment variables in text.
        
        Args:
            text: Text with variables like $VAR or ${VAR}
            
        Returns:
            Expanded text
        """
        import re
        
        # Expand ${VAR} format
        def replace_braced(match):
            var_name = match.group(1)
            return self.get(var_name, match.group(0))
        
        text = re.sub(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}', replace_braced, text)
        
        # Expand $VAR format
        def replace_simple(match):
            var_name = match.group(1)
            return self.get(var_name, match.group(0))
        
        text = re.sub(r'\$([A-Za-z_][A-Za-z0-9_]*)', replace_simple, text)
        
        return text

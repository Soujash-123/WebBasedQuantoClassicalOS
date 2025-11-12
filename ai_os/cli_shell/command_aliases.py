"""
Command Aliases
User-defined command shortcuts.
"""

import os
import json
from typing import Dict, Optional


class AliasManager:
    """Manages command aliases."""
    
    def __init__(self, alias_file: str = ".cli_aliases.json"):
        """
        Initialize alias manager.
        
        Args:
            alias_file: File to persist aliases
        """
        self.alias_file = alias_file
        self.aliases: Dict[str, str] = {}
        
        # Load existing aliases
        self.load()
        
        # Set default aliases if empty
        if not self.aliases:
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default aliases."""
        self.aliases = {
            'll': 'ls -la',
            'la': 'ls -a',
            'cls': 'clear',
            'md': 'mkdir',
            'rd': 'rmdir',
            'copy': 'cp',
            'move': 'mv',
            'del': 'rm',
            'dir': 'ls',
            'type': 'cat',
            'mem': 'memstat',
            'proc': 'ps',
            'net': 'netstat'
        }
        self.save()
    
    def add(self, name: str, command: str) -> bool:
        """
        Add an alias.
        
        Args:
            name: Alias name
            command: Command to alias
            
        Returns:
            True if added
        """
        if not name or not command:
            return False
        
        self.aliases[name] = command
        self.save()
        return True
    
    def remove(self, name: str) -> bool:
        """
        Remove an alias.
        
        Args:
            name: Alias name
            
        Returns:
            True if removed
        """
        if name in self.aliases:
            del self.aliases[name]
            self.save()
            return True
        return False
    
    def get(self, name: str) -> Optional[str]:
        """
        Get alias command.
        
        Args:
            name: Alias name
            
        Returns:
            Aliased command or None
        """
        return self.aliases.get(name)
    
    def expand(self, command: str) -> str:
        """
        Expand aliases in command.
        
        Args:
            command: Command string
            
        Returns:
            Expanded command
        """
        parts = command.split()
        if parts and parts[0] in self.aliases:
            # Replace first part with alias
            alias_parts = self.aliases[parts[0]].split()
            return ' '.join(alias_parts + parts[1:])
        return command
    
    def list_all(self) -> Dict[str, str]:
        """Get all aliases."""
        return self.aliases.copy()
    
    def exists(self, name: str) -> bool:
        """Check if alias exists."""
        return name in self.aliases
    
    def clear(self) -> None:
        """Clear all aliases."""
        self.aliases.clear()
        self.save()
    
    def save(self) -> bool:
        """
        Save aliases to file.
        
        Returns:
            True if successful
        """
        try:
            with open(self.alias_file, 'w') as f:
                json.dump(self.aliases, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving aliases: {e}")
            return False
    
    def load(self) -> bool:
        """
        Load aliases from file.
        
        Returns:
            True if successful
        """
        if not os.path.exists(self.alias_file):
            return False
        
        try:
            with open(self.alias_file, 'r') as f:
                self.aliases = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading aliases: {e}")
            return False

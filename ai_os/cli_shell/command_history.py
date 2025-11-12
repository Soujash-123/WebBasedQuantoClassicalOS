"""
Command History
Stores and manages command history with persistence.
"""

import os
import json
from typing import List, Optional
from datetime import datetime


class CommandHistory:
    """Manages command history with persistence."""
    
    def __init__(self, max_size: int = 1000, history_file: str = ".cli_history.json"):
        """
        Initialize command history.
        
        Args:
            max_size: Maximum number of commands to store
            history_file: File to persist history
        """
        self.max_size = max_size
        self.history_file = history_file
        self.commands: List[dict] = []
        self.current_index = -1
        
        # Load existing history
        self.load()
    
    def add(self, command: str, success: bool = True) -> None:
        """
        Add a command to history.
        
        Args:
            command: Command string
            success: Whether command executed successfully
        """
        if not command or not command.strip():
            return
        
        entry = {
            'command': command.strip(),
            'timestamp': datetime.now().isoformat(),
            'success': success
        }
        
        self.commands.append(entry)
        
        # Trim if exceeds max size
        if len(self.commands) > self.max_size:
            self.commands.pop(0)
        
        self.current_index = len(self.commands)
    
    def get_all(self, limit: Optional[int] = None) -> List[dict]:
        """
        Get all commands.
        
        Args:
            limit: Maximum number to return (most recent)
            
        Returns:
            List of command entries
        """
        if limit:
            return self.commands[-limit:]
        return self.commands.copy()
    
    def get_recent(self, count: int = 10) -> List[str]:
        """Get recent commands as strings."""
        recent = self.commands[-count:] if count < len(self.commands) else self.commands
        return [entry['command'] for entry in recent]
    
    def search(self, pattern: str) -> List[dict]:
        """
        Search history for pattern.
        
        Args:
            pattern: Search pattern
            
        Returns:
            Matching command entries
        """
        return [
            entry for entry in self.commands
            if pattern.lower() in entry['command'].lower()
        ]
    
    def get_previous(self) -> Optional[str]:
        """Get previous command (for up arrow)."""
        if self.current_index > 0:
            self.current_index -= 1
            return self.commands[self.current_index]['command']
        return None
    
    def get_next(self) -> Optional[str]:
        """Get next command (for down arrow)."""
        if self.current_index < len(self.commands) - 1:
            self.current_index += 1
            return self.commands[self.current_index]['command']
        elif self.current_index == len(self.commands) - 1:
            self.current_index = len(self.commands)
            return ""
        return None
    
    def reset_index(self) -> None:
        """Reset navigation index."""
        self.current_index = len(self.commands)
    
    def clear(self) -> None:
        """Clear all history."""
        self.commands.clear()
        self.current_index = -1
    
    def save(self) -> bool:
        """
        Save history to file.
        
        Returns:
            True if successful
        """
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.commands, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False
    
    def load(self) -> bool:
        """
        Load history from file.
        
        Returns:
            True if successful
        """
        if not os.path.exists(self.history_file):
            return False
        
        try:
            with open(self.history_file, 'r') as f:
                self.commands = json.load(f)
            self.current_index = len(self.commands)
            return True
        except Exception as e:
            print(f"Error loading history: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get history statistics."""
        total = len(self.commands)
        successful = sum(1 for cmd in self.commands if cmd.get('success', True))
        
        return {
            'total_commands': total,
            'successful': successful,
            'failed': total - successful,
            'unique_commands': len(set(cmd['command'] for cmd in self.commands))
        }

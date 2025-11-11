"""
OS Session Manager
Manages session state, user profile, and environment.
"""

import os
import time
from typing import Dict, Any, Optional
from datetime import datetime


class SessionManager:
    """Manages CLI session state."""
    
    def __init__(self, user: str = "root"):
        """
        Initialize session manager.
        
        Args:
            user: Current user
        """
        self.user = user
        self.session_id = f"session_{int(time.time())}"
        self.start_time = time.time()
        self.current_directory = "/"
        self.environment: Dict[str, str] = {}
        self.session_data: Dict[str, Any] = {}
        
        # Initialize environment
        self._init_environment()
        
        print(f"[Session] Started session {self.session_id} for user '{user}'")
    
    def _init_environment(self) -> None:
        """Initialize environment variables."""
        self.environment = {
            'USER': self.user,
            'HOME': f'/home/{self.user}',
            'PWD': self.current_directory,
            'SHELL': 'AI_OS_CLI',
            'PATH': '/bin:/usr/bin:/usr/local/bin',
            'EDITOR': 'nano',
            'LANG': 'en_US.UTF-8',
            'TERM': 'xterm-256color'
        }
    
    def get_user(self) -> str:
        """Get current user."""
        return self.user
    
    def set_user(self, user: str) -> None:
        """Set current user."""
        self.user = user
        self.environment['USER'] = user
        self.environment['HOME'] = f'/home/{user}'
    
    def get_current_directory(self) -> str:
        """Get current working directory."""
        return self.current_directory
    
    def set_current_directory(self, directory: str) -> bool:
        """
        Set current working directory.
        
        Args:
            directory: Directory path
            
        Returns:
            True if successful
        """
        # Normalize path
        if not directory.startswith('/'):
            # Relative path
            if self.current_directory == '/':
                directory = '/' + directory
            else:
                directory = self.current_directory + '/' + directory
        
        # Handle .. and .
        parts = []
        for part in directory.split('/'):
            if part == '..':
                if parts:
                    parts.pop()
            elif part and part != '.':
                parts.append(part)
        
        self.current_directory = '/' + '/'.join(parts) if parts else '/'
        self.environment['PWD'] = self.current_directory
        return True
    
    def get_env(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable."""
        return self.environment.get(name, default)
    
    def set_env(self, name: str, value: str) -> None:
        """Set environment variable."""
        self.environment[name] = value
    
    def unset_env(self, name: str) -> bool:
        """Unset environment variable."""
        if name in self.environment:
            del self.environment[name]
            return True
        return False
    
    def list_env(self) -> Dict[str, str]:
        """List all environment variables."""
        return self.environment.copy()
    
    def get_uptime(self) -> float:
        """Get session uptime in seconds."""
        return time.time() - self.start_time
    
    def get_uptime_formatted(self) -> str:
        """Get formatted uptime string."""
        uptime = self.get_uptime()
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def set_data(self, key: str, value: Any) -> None:
        """Set session data."""
        self.session_data[key] = value
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get session data."""
        return self.session_data.get(key, default)
    
    def get_prompt(self) -> str:
        """
        Generate command prompt.
        
        Returns:
            Prompt string
        """
        # Format: [user@AIOS:path]$
        path = self.current_directory
        
        # Shorten path if in home directory
        home = self.environment.get('HOME', '')
        if home and path.startswith(home):
            path = '~' + path[len(home):]
        
        return f"[{self.user}@AIOS:{path}]$ "
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information."""
        return {
            'session_id': self.session_id,
            'user': self.user,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'uptime': self.get_uptime_formatted(),
            'current_directory': self.current_directory,
            'environment_vars': len(self.environment)
        }
    
    def save_state(self, filepath: str = ".cli_session.json") -> bool:
        """Save session state to file."""
        import json
        try:
            state = {
                'user': self.user,
                'current_directory': self.current_directory,
                'environment': self.environment,
                'session_data': self.session_data
            }
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving session state: {e}")
            return False
    
    def load_state(self, filepath: str = ".cli_session.json") -> bool:
        """Load session state from file."""
        import json
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.user = state.get('user', self.user)
            self.current_directory = state.get('current_directory', '/')
            self.environment.update(state.get('environment', {}))
            self.session_data = state.get('session_data', {})
            return True
        except Exception as e:
            print(f"Error loading session state: {e}")
            return False

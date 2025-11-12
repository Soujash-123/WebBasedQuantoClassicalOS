"""
CLI Logger
Logging utility for CLI operations and debugging.
"""

import os
from datetime import datetime
from typing import Optional


class CLILogger:
    """Logger for CLI operations."""
    
    def __init__(self, log_file: str = ".cli_debug.log", enabled: bool = False):
        """
        Initialize CLI logger.
        
        Args:
            log_file: Log file path
            enabled: Whether logging is enabled
        """
        self.log_file = log_file
        self.enabled = enabled
        self.session_start = datetime.now()
    
    def log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message.
        
        Args:
            message: Log message
            level: Log level (INFO, WARN, ERROR, DEBUG)
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level:5}] {message}\n"
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Logging error: {e}")
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.log(message, "INFO")
    
    def warn(self, message: str) -> None:
        """Log warning message."""
        self.log(message, "WARN")
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.log(message, "ERROR")
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.log(message, "DEBUG")
    
    def log_command(self, command: str, success: bool = True) -> None:
        """Log a command execution."""
        status = "SUCCESS" if success else "FAILED"
        self.log(f"Command: {command} [{status}]", "INFO")
    
    def enable(self) -> None:
        """Enable logging."""
        self.enabled = True
        self.info("CLI logging enabled")
    
    def disable(self) -> None:
        """Disable logging."""
        self.info("CLI logging disabled")
        self.enabled = False
    
    def clear_log(self) -> bool:
        """Clear the log file."""
        try:
            with open(self.log_file, 'w') as f:
                f.write("")
            return True
        except Exception as e:
            print(f"Error clearing log: {e}")
            return False
    
    def read_log(self, lines: Optional[int] = None) -> str:
        """
        Read log file.
        
        Args:
            lines: Number of lines to read (None = all)
            
        Returns:
            Log content
        """
        if not os.path.exists(self.log_file):
            return "Log file not found"
        
        try:
            with open(self.log_file, 'r') as f:
                if lines:
                    all_lines = f.readlines()
                    return ''.join(all_lines[-lines:])
                return f.read()
        except Exception as e:
            return f"Error reading log: {e}"
    
    def get_session_duration(self) -> float:
        """Get session duration in seconds."""
        return (datetime.now() - self.session_start).total_seconds()

"""
Logger
Centralized logging utility for all OS layers.
"""

import os
import time
from enum import Enum
from typing import Optional
from datetime import datetime


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    CRITICAL = 4


class Logger:
    """Centralized logging system."""
    
    def __init__(
        self,
        log_dir: str = "./system/logs",
        min_level: LogLevel = LogLevel.INFO,
        console_output: bool = True
    ):
        """
        Initialize logger.
        
        Args:
            log_dir: Directory for log files
            min_level: Minimum log level to record
            console_output: Whether to also print to console
        """
        self.log_dir = log_dir
        self.min_level = min_level
        self.console_output = console_output
        
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Log files
        self.system_log = os.path.join(log_dir, "system.log")
        self.error_log = os.path.join(log_dir, "error.log")
        self.security_log = os.path.join(log_dir, "security.log")
        
        print("[Logger] Logger initialized")
    
    def _format_message(self, level: LogLevel, message: str, category: str = "SYSTEM") -> str:
        """
        Format log message.
        
        Args:
            level: Log level
            message: Log message
            category: Log category
            
        Returns:
            Formatted log message
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{level.name:8}] [{category:10}] {message}"
    
    def _write_to_file(self, filepath: str, message: str) -> None:
        """Write message to log file."""
        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(message + '\n')
        except Exception as e:
            print(f"[Logger] Error writing to log: {e}")
    
    def log(
        self,
        level: LogLevel,
        message: str,
        category: str = "SYSTEM",
        log_type: str = "system"
    ) -> None:
        """
        Log a message.
        
        Args:
            level: Log level
            message: Log message
            category: Log category
            log_type: Log type ('system', 'error', 'security')
        """
        # Check minimum level
        if level.value < self.min_level.value:
            return
        
        # Format message
        formatted = self._format_message(level, message, category)
        
        # Console output
        if self.console_output:
            if level.value >= LogLevel.ERROR.value:
                print(f"[LOG] {formatted}")
        
        # Write to appropriate log file
        if log_type == "security":
            self._write_to_file(self.security_log, formatted)
        elif level.value >= LogLevel.ERROR.value:
            self._write_to_file(self.error_log, formatted)
        
        # Always write to system log
        self._write_to_file(self.system_log, formatted)
    
    def debug(self, message: str, category: str = "SYSTEM") -> None:
        """Log debug message."""
        self.log(LogLevel.DEBUG, message, category)
    
    def info(self, message: str, category: str = "SYSTEM") -> None:
        """Log info message."""
        self.log(LogLevel.INFO, message, category)
    
    def warn(self, message: str, category: str = "SYSTEM") -> None:
        """Log warning message."""
        self.log(LogLevel.WARN, message, category)
    
    def error(self, message: str, category: str = "SYSTEM") -> None:
        """Log error message."""
        self.log(LogLevel.ERROR, message, category, "error")
    
    def critical(self, message: str, category: str = "SYSTEM") -> None:
        """Log critical message."""
        self.log(LogLevel.CRITICAL, message, category, "error")
    
    def security(self, message: str, category: str = "SECURITY") -> None:
        """Log security event."""
        self.log(LogLevel.INFO, message, category, "security")
    
    def read_log(
        self,
        log_type: str = "system",
        lines: Optional[int] = None,
        level_filter: Optional[LogLevel] = None
    ) -> str:
        """
        Read log file.
        
        Args:
            log_type: Log type to read
            lines: Number of lines to read (None = all)
            level_filter: Filter by log level
            
        Returns:
            Log content
        """
        # Select log file
        if log_type == "error":
            filepath = self.error_log
        elif log_type == "security":
            filepath = self.security_log
        else:
            filepath = self.system_log
        
        if not os.path.exists(filepath):
            return f"Log file not found: {filepath}"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
            
            # Filter by level
            if level_filter:
                log_lines = [
                    line for line in log_lines
                    if f"[{level_filter.name:8}]" in line
                ]
            
            # Limit lines
            if lines:
                log_lines = log_lines[-lines:]
            
            return ''.join(log_lines)
            
        except Exception as e:
            return f"Error reading log: {e}"
    
    def clear_log(self, log_type: str = "system") -> bool:
        """
        Clear a log file.
        
        Args:
            log_type: Log type to clear
            
        Returns:
            True if successful
        """
        # Select log file
        if log_type == "error":
            filepath = self.error_log
        elif log_type == "security":
            filepath = self.security_log
        else:
            filepath = self.system_log
        
        try:
            with open(filepath, 'w') as f:
                f.write("")
            print(f"[Logger] Cleared {log_type} log")
            return True
        except Exception as e:
            print(f"[Logger] Error clearing log: {e}")
            return False
    
    def set_level(self, level: LogLevel) -> None:
        """Set minimum log level."""
        self.min_level = level
        print(f"[Logger] Log level set to {level.name}")
    
    def get_log_stats(self) -> dict:
        """Get log file statistics."""
        stats = {}
        
        for log_type, filepath in [
            ("system", self.system_log),
            ("error", self.error_log),
            ("security", self.security_log)
        ]:
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                with open(filepath, 'r') as f:
                    lines = sum(1 for _ in f)
                stats[log_type] = {
                    "size": size,
                    "lines": lines,
                    "path": filepath
                }
            else:
                stats[log_type] = {
                    "size": 0,
                    "lines": 0,
                    "path": filepath
                }
        
        return stats

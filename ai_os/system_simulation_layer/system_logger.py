"""
System Logger
Logs system operations (installs, mounts, updates).
"""

import os
import json
from datetime import datetime
from typing import Optional


class SystemLogger:
    """Logs system simulation operations."""
    
    def __init__(self, log_dir: str = "./system_logs"):
        """
        Initialize system logger.
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = log_dir
        self.install_log = os.path.join(log_dir, "install.log")
        self.mount_log = os.path.join(log_dir, "mount.log")
        self.git_log = os.path.join(log_dir, "git.log")
        self.system_log = os.path.join(log_dir, "system.log")
        
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)
    
    def _write_log(self, log_file: str, message: str, level: str = "INFO") -> None:
        """Write to log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        try:
            with open(log_file, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to log: {e}")
    
    def log_install(self, package: str, version: str, success: bool = True) -> None:
        """Log package installation."""
        status = "SUCCESS" if success else "FAILED"
        message = f"Package install: {package} v{version} [{status}]"
        self._write_log(self.install_log, message)
        self._write_log(self.system_log, message)
    
    def log_remove(self, package: str, success: bool = True) -> None:
        """Log package removal."""
        status = "SUCCESS" if success else "FAILED"
        message = f"Package remove: {package} [{status}]"
        self._write_log(self.install_log, message)
        self._write_log(self.system_log, message)
    
    def log_update(self, count: int) -> None:
        """Log repository update."""
        message = f"Repository update: {count} packages available"
        self._write_log(self.install_log, message)
        self._write_log(self.system_log, message)
    
    def log_upgrade(self, packages: list) -> None:
        """Log package upgrades."""
        message = f"Package upgrade: {len(packages)} packages upgraded"
        self._write_log(self.install_log, message)
        self._write_log(self.system_log, message)
    
    def log_mount(self, device: str, path: str, success: bool = True) -> None:
        """Log device mount."""
        status = "SUCCESS" if success else "FAILED"
        message = f"Mount: {device} -> {path} [{status}]"
        self._write_log(self.mount_log, message)
        self._write_log(self.system_log, message)
    
    def log_unmount(self, path: str, success: bool = True) -> None:
        """Log device unmount."""
        status = "SUCCESS" if success else "FAILED"
        message = f"Unmount: {path} [{status}]"
        self._write_log(self.mount_log, message)
        self._write_log(self.system_log, message)
    
    def log_git(self, operation: str, repo: str, success: bool = True) -> None:
        """Log git operation."""
        status = "SUCCESS" if success else "FAILED"
        message = f"Git {operation}: {repo} [{status}]"
        self._write_log(self.git_log, message)
        self._write_log(self.system_log, message)
    
    def log_system(self, message: str, level: str = "INFO") -> None:
        """Log general system message."""
        self._write_log(self.system_log, message, level)
    
    def read_log(self, log_type: str = "system", lines: Optional[int] = None) -> str:
        """
        Read log file.
        
        Args:
            log_type: Type of log (system, install, mount, git)
            lines: Number of lines to read (None = all)
            
        Returns:
            Log content
        """
        log_files = {
            'system': self.system_log,
            'install': self.install_log,
            'mount': self.mount_log,
            'git': self.git_log
        }
        
        log_file = log_files.get(log_type, self.system_log)
        
        if not os.path.exists(log_file):
            return f"No {log_type} log found"
        
        try:
            with open(log_file, 'r') as f:
                if lines:
                    all_lines = f.readlines()
                    return ''.join(all_lines[-lines:])
                return f.read()
        except Exception as e:
            return f"Error reading log: {e}"
    
    def clear_logs(self) -> bool:
        """Clear all log files."""
        try:
            for log_file in [self.install_log, self.mount_log, self.git_log, self.system_log]:
                if os.path.exists(log_file):
                    with open(log_file, 'w') as f:
                        f.write("")
            return True
        except Exception as e:
            print(f"Error clearing logs: {e}")
            return False

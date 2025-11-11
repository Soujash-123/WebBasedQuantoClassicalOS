"""
Console Device
Handles terminal input/output operations.
"""

from typing import Dict, Any, Optional
from .base_device import BaseDevice
import sys


class ConsoleDevice(BaseDevice):
    """Virtual console device for terminal I/O."""
    
    def __init__(self, name: str = "Console"):
        """Initialize the console device."""
        super().__init__(name, "io")
        self.input_buffer = []
        self.output_buffer = []
        self.max_buffer_size = 1000
    
    def initialize(self) -> bool:
        """Initialize the console device."""
        result = super().initialize()
        self.set_metadata("encoding", sys.stdout.encoding or "utf-8")
        self.set_metadata("interactive", sys.stdin.isatty())
        return result
    
    def write(self, message: str, end: str = "\n") -> bool:
        """
        Write a message to the console.
        
        Args:
            message: Message to write
            end: String to append at the end
            
        Returns:
            True if write successful
        """
        try:
            print(message, end=end)
            self._add_to_buffer(self.output_buffer, message)
            return True
        except Exception as e:
            print(f"[ConsoleDevice] Error writing to console: {e}", file=sys.stderr)
            return False
    
    def read(self, prompt: str = "> ") -> Optional[str]:
        """
        Read input from the console.
        
        Args:
            prompt: Prompt to display
            
        Returns:
            User input string or None if error
        """
        try:
            user_input = input(prompt)
            self._add_to_buffer(self.input_buffer, user_input)
            return user_input
        except EOFError:
            print("\n[ConsoleDevice] EOF received")
            return None
        except KeyboardInterrupt:
            print("\n[ConsoleDevice] Interrupted by user")
            return None
        except Exception as e:
            print(f"[ConsoleDevice] Error reading from console: {e}", file=sys.stderr)
            return None
    
    def write_error(self, message: str) -> bool:
        """
        Write an error message to stderr.
        
        Args:
            message: Error message to write
            
        Returns:
            True if write successful
        """
        try:
            print(f"ERROR: {message}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"[ConsoleDevice] Error writing error message: {e}", file=sys.stderr)
            return False
    
    def clear(self) -> bool:
        """
        Clear the console screen.
        
        Returns:
            True if clear successful
        """
        try:
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            return True
        except Exception as e:
            print(f"[ConsoleDevice] Error clearing console: {e}")
            return False
    
    def _add_to_buffer(self, buffer: list, item: str) -> None:
        """Add item to buffer with size limit."""
        buffer.append(item)
        if len(buffer) > self.max_buffer_size:
            buffer.pop(0)
    
    def get_input_history(self, count: int = 10) -> list:
        """Get recent input history."""
        return self.input_buffer[-count:]
    
    def get_output_history(self, count: int = 10) -> list:
        """Get recent output history."""
        return self.output_buffer[-count:]
    
    def get_info(self) -> Dict[str, Any]:
        """Get detailed console information."""
        return {
            "name": self.name,
            "type": self.device_type,
            "status": self.status_flag,
            "encoding": self.get_metadata("encoding"),
            "interactive": self.get_metadata("interactive"),
            "input_buffer_size": len(self.input_buffer),
            "output_buffer_size": len(self.output_buffer)
        }

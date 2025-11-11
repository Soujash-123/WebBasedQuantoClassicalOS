"""
Error Handler
Graceful error messages and exception handling for CLI.
"""

import traceback
from typing import Optional, Callable


class ErrorHandler:
    """Handles errors gracefully in the CLI."""
    
    def __init__(self, debug_mode: bool = False):
        """
        Initialize error handler.
        
        Args:
            debug_mode: Show full tracebacks
        """
        self.debug_mode = debug_mode
        self.error_count = 0
        self.last_error: Optional[str] = None
    
    def handle_error(self, error: Exception, context: str = "") -> str:
        """
        Handle an error and return user-friendly message.
        
        Args:
            error: Exception object
            context: Context where error occurred
            
        Returns:
            Error message
        """
        self.error_count += 1
        
        # Format error message
        error_type = type(error).__name__
        error_msg = str(error)
        
        if context:
            message = f"Error in {context}: {error_msg}"
        else:
            message = f"{error_type}: {error_msg}"
        
        self.last_error = message
        
        # Show traceback in debug mode
        if self.debug_mode:
            message += "\n\nTraceback:\n"
            message += traceback.format_exc()
        
        return message
    
    def handle_command_error(self, command: str, error: Exception) -> str:
        """Handle command execution error."""
        error_msg = self.handle_error(error, f"command '{command}'")
        
        # Provide helpful suggestions
        suggestions = self._get_suggestions(command, error)
        if suggestions:
            error_msg += f"\n\nSuggestion: {suggestions}"
        
        return error_msg
    
    def _get_suggestions(self, command: str, error: Exception) -> Optional[str]:
        """Get helpful suggestions based on error type."""
        error_type = type(error).__name__
        
        if error_type == "FileNotFoundError":
            return "Check if the file exists using 'ls' or 'find'"
        elif error_type == "PermissionError":
            return "You may not have permission. Try with elevated privileges."
        elif error_type == "ValueError":
            return "Check the command syntax with 'help <command>'"
        elif error_type == "KeyError":
            return "The specified key or option doesn't exist"
        elif "command not found" in str(error).lower():
            return "Type 'help' to see available commands"
        
        return None
    
    def handle_parse_error(self, input_line: str, error: str) -> str:
        """Handle command parsing error."""
        message = f"Parse error: {error}\n"
        message += f"Input: {input_line}\n"
        message += "Check your syntax and try again"
        return message
    
    def handle_missing_argument(self, command: str, argument: str) -> str:
        """Handle missing argument error."""
        message = f"Missing required argument: {argument}\n"
        message += f"Usage: help {command}"
        return message
    
    def handle_invalid_argument(self, command: str, argument: str, expected: str) -> str:
        """Handle invalid argument error."""
        message = f"Invalid argument '{argument}'\n"
        message += f"Expected: {expected}\n"
        message += f"Usage: help {command}"
        return message
    
    def safe_execute(self, func: Callable, *args, **kwargs):
        """
        Safely execute a function with error handling.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result or None on error
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(self.handle_error(e, func.__name__))
            return None
    
    def get_stats(self) -> dict:
        """Get error statistics."""
        return {
            'total_errors': self.error_count,
            'last_error': self.last_error,
            'debug_mode': self.debug_mode
        }
    
    def reset_stats(self) -> None:
        """Reset error statistics."""
        self.error_count = 0
        self.last_error = None
    
    def set_debug_mode(self, enabled: bool) -> None:
        """Enable or disable debug mode."""
        self.debug_mode = enabled

"""
Output Handler
Manages output operations to various destinations.
"""

from typing import Optional, Any, Dict, List
import json


class OutputHandler:
    """Handles output operations for the system."""
    
    def __init__(self, console_device=None):
        """
        Initialize the output handler.
        
        Args:
            console_device: Console device for output operations
        """
        self.console = console_device
        self.output_history: List[str] = []
        self.max_history = 100
        self.verbosity_level = 1  # 0=quiet, 1=normal, 2=verbose
        print("[OutputHandler] Output Handler initialized")
    
    def set_console(self, console_device) -> None:
        """Set the console device for output operations."""
        self.console = console_device
        print("[OutputHandler] Console device set")
    
    def write(self, message: str, end: str = "\n") -> bool:
        """
        Write a message to output.
        
        Args:
            message: Message to write
            end: String to append at end
            
        Returns:
            True if write successful
        """
        if not self.console:
            print(message, end=end)
            return True
        
        result = self.console.write(message, end=end)
        if result:
            self._add_to_history(message)
        return result
    
    def writeln(self, message: str = "") -> bool:
        """
        Write a message with newline.
        
        Args:
            message: Message to write
            
        Returns:
            True if write successful
        """
        return self.write(message, end="\n")
    
    def print_info(self, message: str) -> bool:
        """
        Print an informational message.
        
        Args:
            message: Info message
            
        Returns:
            True if write successful
        """
        return self.writeln(f"[INFO] {message}")
    
    def print_success(self, message: str) -> bool:
        """
        Print a success message.
        
        Args:
            message: Success message
            
        Returns:
            True if write successful
        """
        return self.writeln(f"[SUCCESS] {message}")
    
    def print_warning(self, message: str) -> bool:
        """
        Print a warning message.
        
        Args:
            message: Warning message
            
        Returns:
            True if write successful
        """
        return self.writeln(f"[WARNING] {message}")
    
    def print_error(self, message: str) -> bool:
        """
        Print an error message.
        
        Args:
            message: Error message
            
        Returns:
            True if write successful
        """
        if self.console:
            return self.console.write_error(message)
        else:
            return self.writeln(f"[ERROR] {message}")
    
    def print_header(self, title: str, width: int = 60, char: str = "=") -> bool:
        """
        Print a formatted header.
        
        Args:
            title: Header title
            width: Width of header
            char: Character to use for border
            
        Returns:
            True if write successful
        """
        border = char * width
        self.writeln(border)
        self.writeln(title.center(width))
        self.writeln(border)
        return True
    
    def print_separator(self, width: int = 60, char: str = "-") -> bool:
        """
        Print a separator line.
        
        Args:
            width: Width of separator
            char: Character to use
            
        Returns:
            True if write successful
        """
        return self.writeln(char * width)
    
    def print_table(self, headers: List[str], rows: List[List[str]], spacing: int = 15) -> bool:
        """
        Print a formatted table.
        
        Args:
            headers: Column headers
            rows: Table rows
            spacing: Column spacing
            
        Returns:
            True if write successful
        """
        # Print headers
        header_line = "".join(h.ljust(spacing) for h in headers)
        self.writeln(header_line)
        self.print_separator(len(header_line), "-")
        
        # Print rows
        for row in rows:
            row_line = "".join(str(cell).ljust(spacing) for cell in row)
            self.writeln(row_line)
        
        return True
    
    def print_dict(self, data: Dict[str, Any], indent: int = 0) -> bool:
        """
        Print a dictionary in formatted style.
        
        Args:
            data: Dictionary to print
            indent: Indentation level
            
        Returns:
            True if write successful
        """
        indent_str = "  " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                self.writeln(f"{indent_str}{key}:")
                self.print_dict(value, indent + 1)
            elif isinstance(value, list):
                self.writeln(f"{indent_str}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        self.print_dict(item, indent + 1)
                    else:
                        self.writeln(f"{indent_str}  - {item}")
            else:
                self.writeln(f"{indent_str}{key}: {value}")
        
        return True
    
    def print_json(self, data: Any, indent: int = 2) -> bool:
        """
        Print data as formatted JSON.
        
        Args:
            data: Data to print as JSON
            indent: JSON indentation
            
        Returns:
            True if write successful
        """
        try:
            json_str = json.dumps(data, indent=indent)
            return self.writeln(json_str)
        except Exception as e:
            return self.print_error(f"Error formatting JSON: {e}")
    
    def print_list(self, items: List[Any], numbered: bool = False, bullet: str = "-") -> bool:
        """
        Print a list of items.
        
        Args:
            items: List of items to print
            numbered: Whether to number items
            bullet: Bullet character for unnumbered lists
            
        Returns:
            True if write successful
        """
        for i, item in enumerate(items, 1):
            if numbered:
                self.writeln(f"{i}. {item}")
            else:
                self.writeln(f"{bullet} {item}")
        return True
    
    def display(self, data: Any, format_type: str = "auto") -> bool:
        """
        Display data in appropriate format.
        
        Args:
            data: Data to display
            format_type: Format type ('auto', 'json', 'dict', 'list', 'text')
            
        Returns:
            True if display successful
        """
        if format_type == "auto":
            if isinstance(data, dict):
                return self.print_dict(data)
            elif isinstance(data, list):
                return self.print_list(data)
            else:
                return self.writeln(str(data))
        elif format_type == "json":
            return self.print_json(data)
        elif format_type == "dict":
            return self.print_dict(data)
        elif format_type == "list":
            return self.print_list(data)
        else:
            return self.writeln(str(data))
    
    def clear(self) -> bool:
        """Clear the output screen."""
        if self.console:
            return self.console.clear()
        return False
    
    def set_verbosity(self, level: int) -> None:
        """
        Set verbosity level.
        
        Args:
            level: Verbosity level (0=quiet, 1=normal, 2=verbose)
        """
        self.verbosity_level = max(0, min(2, level))
        print(f"[OutputHandler] Verbosity set to {self.verbosity_level}")
    
    def verbose(self, message: str) -> bool:
        """Print message only in verbose mode."""
        if self.verbosity_level >= 2:
            return self.writeln(f"[VERBOSE] {message}")
        return True
    
    def get_history(self, count: int = 10) -> List[str]:
        """Get recent output history."""
        return self.output_history[-count:]
    
    def clear_history(self) -> None:
        """Clear output history."""
        self.output_history.clear()
        print("[OutputHandler] Output history cleared")
    
    def _add_to_history(self, output_text: str) -> None:
        """Add output to history."""
        self.output_history.append(output_text)
        if len(self.output_history) > self.max_history:
            self.output_history.pop(0)

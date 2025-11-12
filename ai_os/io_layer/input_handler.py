"""
Input Handler
Manages input operations from various sources.
"""

from typing import Optional, Callable, Dict, Any, List


class InputHandler:
    """Handles input operations for the system."""
    
    def __init__(self, console_device=None):
        """
        Initialize the input handler.
        
        Args:
            console_device: Console device for input operations
        """
        self.console = console_device
        self.input_history: List[str] = []
        self.max_history = 100
        self.input_callbacks: Dict[str, List[Callable]] = {}
        print("[InputHandler] Input Handler initialized")
    
    def set_console(self, console_device) -> None:
        """Set the console device for input operations."""
        self.console = console_device
        print("[InputHandler] Console device set")
    
    def read_input(self, prompt: str = "> ") -> Optional[str]:
        """
        Read input from the console.
        
        Args:
            prompt: Prompt to display
            
        Returns:
            User input string or None if error
        """
        if not self.console:
            print("[InputHandler] Error: No console device available")
            return None
        
        user_input = self.console.read(prompt)
        
        if user_input is not None:
            self._add_to_history(user_input)
            self._trigger_callbacks("input_received", user_input)
        
        return user_input
    
    def read_line(self, prompt: str = "") -> Optional[str]:
        """
        Read a single line of input.
        
        Args:
            prompt: Prompt to display
            
        Returns:
            Input line or None if error
        """
        return self.read_input(prompt)
    
    def read_multiline(self, prompt: str = "Enter text (empty line to finish):\n") -> Optional[str]:
        """
        Read multiple lines of input until empty line.
        
        Args:
            prompt: Initial prompt
            
        Returns:
            Combined input string or None if error
        """
        if not self.console:
            print("[InputHandler] Error: No console device available")
            return None
        
        print(prompt)
        lines = []
        
        while True:
            line = self.console.read("")
            if line is None:
                return None
            if line.strip() == "":
                break
            lines.append(line)
        
        result = "\n".join(lines)
        self._add_to_history(result)
        return result
    
    def read_confirmation(self, prompt: str = "Confirm? (y/n): ") -> bool:
        """
        Read a yes/no confirmation.
        
        Args:
            prompt: Confirmation prompt
            
        Returns:
            True for yes, False for no
        """
        while True:
            response = self.read_input(prompt)
            if response is None:
                return False
            
            response = response.lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def read_choice(self, prompt: str, choices: List[str]) -> Optional[str]:
        """
        Read a choice from a list of options.
        
        Args:
            prompt: Prompt to display
            choices: List of valid choices
            
        Returns:
            Selected choice or None if cancelled
        """
        print(prompt)
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        while True:
            response = self.read_input("Select option: ")
            if response is None:
                return None
            
            # Try numeric selection
            try:
                index = int(response) - 1
                if 0 <= index < len(choices):
                    return choices[index]
            except ValueError:
                pass
            
            # Try text match
            if response in choices:
                return response
            
            print("Invalid choice. Please try again.")
    
    def get_history(self, count: int = 10) -> List[str]:
        """
        Get recent input history.
        
        Args:
            count: Number of history items to return
            
        Returns:
            List of recent inputs
        """
        return self.input_history[-count:]
    
    def clear_history(self) -> None:
        """Clear input history."""
        self.input_history.clear()
        print("[InputHandler] Input history cleared")
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """
        Register a callback for input events.
        
        Args:
            event_type: Type of event (e.g., 'input_received')
            callback: Callback function
        """
        if event_type not in self.input_callbacks:
            self.input_callbacks[event_type] = []
        self.input_callbacks[event_type].append(callback)
    
    def _add_to_history(self, input_text: str) -> None:
        """Add input to history."""
        self.input_history.append(input_text)
        if len(self.input_history) > self.max_history:
            self.input_history.pop(0)
    
    def _trigger_callbacks(self, event_type: str, data: Any) -> None:
        """Trigger registered callbacks."""
        if event_type in self.input_callbacks:
            for callback in self.input_callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"[InputHandler] Error in callback: {e}")

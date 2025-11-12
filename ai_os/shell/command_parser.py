"""
Command Parser
Tokenizes and validates CLI input with support for piping, redirection, and chaining.
"""

import re
import shlex
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """Represents a parsed command."""
    command: str
    args: List[str]
    redirect_output: Optional[str] = None
    redirect_append: bool = False
    redirect_input: Optional[str] = None
    pipe_to: Optional['ParsedCommand'] = None
    background: bool = False
    chain_operator: Optional[str] = None  # '&&' or '||'
    next_command: Optional['ParsedCommand'] = None


class CommandParser:
    """Parses command-line input."""
    
    def __init__(self):
        """Initialize command parser."""
        self.history: List[str] = []
        self.max_history = 1000
    
    def parse(self, input_line: str) -> Optional[ParsedCommand]:
        """
        Parse a command line input.
        
        Args:
            input_line: Raw command line string
            
        Returns:
            ParsedCommand object or None if empty
        """
        if not input_line or not input_line.strip():
            return None
        
        # Add to history
        self.add_to_history(input_line)
        
        # Handle command chaining (&&, ||)
        if '&&' in input_line or '||' in input_line:
            return self._parse_chained_commands(input_line)
        
        # Handle piping
        if '|' in input_line:
            return self._parse_piped_commands(input_line)
        
        # Parse single command
        return self._parse_single_command(input_line)
    
    def _parse_single_command(self, input_line: str) -> Optional[ParsedCommand]:
        """Parse a single command without piping or chaining."""
        input_line = input_line.strip()
        
        # Check for background execution
        background = False
        if input_line.endswith('&'):
            background = True
            input_line = input_line[:-1].strip()
        
        # Check for output redirection
        redirect_output = None
        redirect_append = False
        
        if '>>' in input_line:
            parts = input_line.split('>>', 1)
            input_line = parts[0].strip()
            redirect_output = parts[1].strip()
            redirect_append = True
        elif '>' in input_line:
            parts = input_line.split('>', 1)
            input_line = parts[0].strip()
            redirect_output = parts[1].strip()
        
        # Check for input redirection
        redirect_input = None
        if '<' in input_line:
            parts = input_line.split('<', 1)
            input_line = parts[0].strip()
            redirect_input = parts[1].strip()
        
        # Tokenize the command
        try:
            tokens = shlex.split(input_line)
        except ValueError as e:
            print(f"[Parser] Error parsing command: {e}")
            return None
        
        if not tokens:
            return None
        
        command = tokens[0]
        args = tokens[1:] if len(tokens) > 1 else []
        
        return ParsedCommand(
            command=command,
            args=args,
            redirect_output=redirect_output,
            redirect_append=redirect_append,
            redirect_input=redirect_input,
            background=background
        )
    
    def _parse_piped_commands(self, input_line: str) -> Optional[ParsedCommand]:
        """Parse commands connected with pipes."""
        pipe_parts = input_line.split('|')
        
        if not pipe_parts:
            return None
        
        # Parse first command
        first_cmd = self._parse_single_command(pipe_parts[0])
        if not first_cmd:
            return None
        
        # Chain piped commands
        current = first_cmd
        for pipe_part in pipe_parts[1:]:
            next_cmd = self._parse_single_command(pipe_part)
            if next_cmd:
                current.pipe_to = next_cmd
                current = next_cmd
        
        return first_cmd
    
    def _parse_chained_commands(self, input_line: str) -> Optional[ParsedCommand]:
        """Parse commands connected with && or ||."""
        # Find the first chain operator
        and_pos = input_line.find('&&')
        or_pos = input_line.find('||')
        
        if and_pos == -1 and or_pos == -1:
            return self._parse_single_command(input_line)
        
        # Determine which operator comes first
        if and_pos != -1 and (or_pos == -1 or and_pos < or_pos):
            split_pos = and_pos
            operator = '&&'
        else:
            split_pos = or_pos
            operator = '||'
        
        # Split at the operator
        first_part = input_line[:split_pos].strip()
        rest_part = input_line[split_pos + 2:].strip()
        
        # Parse first command
        first_cmd = self.parse(first_part)
        if not first_cmd:
            return None
        
        # Parse rest recursively
        next_cmd = self.parse(rest_part)
        
        # Link commands
        first_cmd.chain_operator = operator
        first_cmd.next_command = next_cmd
        
        return first_cmd
    
    def add_to_history(self, command: str) -> None:
        """Add command to history."""
        if command and command.strip():
            self.history.append(command.strip())
            if len(self.history) > self.max_history:
                self.history.pop(0)
    
    def get_history(self, limit: Optional[int] = None) -> List[str]:
        """
        Get command history.
        
        Args:
            limit: Maximum number of commands to return
            
        Returns:
            List of command strings
        """
        if limit:
            return self.history[-limit:]
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear command history."""
        self.history.clear()
    
    def save_history(self, filepath: str) -> bool:
        """
        Save history to file.
        
        Args:
            filepath: Path to save history
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w') as f:
                for cmd in self.history:
                    f.write(cmd + '\n')
            return True
        except Exception as e:
            print(f"[Parser] Error saving history: {e}")
            return False
    
    def load_history(self, filepath: str) -> bool:
        """
        Load history from file.
        
        Args:
            filepath: Path to load history from
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'r') as f:
                self.history = [line.strip() for line in f if line.strip()]
            return True
        except FileNotFoundError:
            return True  # Not an error if file doesn't exist
        except Exception as e:
            print(f"[Parser] Error loading history: {e}")
            return False

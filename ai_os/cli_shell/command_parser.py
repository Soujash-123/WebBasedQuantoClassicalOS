"""
Command Parser
Enhanced command parsing with piping, redirection, and autocomplete.
"""

import shlex
import re
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """Represents a parsed command."""
    command: str
    args: List[str]
    raw_input: str
    redirect_output: Optional[str] = None
    redirect_append: bool = False
    redirect_input: Optional[str] = None
    pipe_to: Optional['ParsedCommand'] = None
    background: bool = False
    chain_operator: Optional[str] = None  # '&&' or '||'
    next_command: Optional['ParsedCommand'] = None


class CommandParser:
    """Enhanced command parser with autocomplete."""
    
    def __init__(self, available_commands: Optional[List[str]] = None):
        """
        Initialize command parser.
        
        Args:
            available_commands: List of available commands for autocomplete
        """
        self.available_commands = available_commands or []
    
    def set_available_commands(self, commands: List[str]) -> None:
        """Set available commands for autocomplete."""
        self.available_commands = commands
    
    def parse(self, input_line: str) -> Optional[ParsedCommand]:
        """
        Parse command line input.
        
        Args:
            input_line: Raw command line string
            
        Returns:
            ParsedCommand object or None
        """
        if not input_line or not input_line.strip():
            return None
        
        # Handle command chaining (&&, ||)
        if '&&' in input_line or '||' in input_line:
            return self._parse_chained_commands(input_line)
        
        # Handle piping
        if '|' in input_line:
            return self._parse_piped_commands(input_line)
        
        # Parse single command
        return self._parse_single_command(input_line)
    
    def _parse_single_command(self, input_line: str) -> Optional[ParsedCommand]:
        """Parse a single command."""
        original_input = input_line
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
        
        # Tokenize command
        try:
            tokens = shlex.split(input_line)
        except ValueError as e:
            print(f"Parse error: {e}")
            return None
        
        if not tokens:
            return None
        
        command = tokens[0]
        args = tokens[1:] if len(tokens) > 1 else []
        
        return ParsedCommand(
            command=command,
            args=args,
            raw_input=original_input,
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
    
    def autocomplete(self, partial: str) -> List[str]:
        """
        Get autocomplete suggestions.
        
        Args:
            partial: Partial command string
            
        Returns:
            List of matching commands
        """
        if not partial:
            return self.available_commands
        
        partial_lower = partial.lower()
        matches = [
            cmd for cmd in self.available_commands
            if cmd.lower().startswith(partial_lower)
        ]
        
        return sorted(matches)
    
    def get_completion(self, partial: str) -> Optional[str]:
        """
        Get single completion if unique.
        
        Args:
            partial: Partial command
            
        Returns:
            Completed command or None
        """
        matches = self.autocomplete(partial)
        
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            # Find common prefix
            common = matches[0]
            for match in matches[1:]:
                while not match.startswith(common):
                    common = common[:-1]
                    if not common:
                        return None
            return common if len(common) > len(partial) else None
        
        return None
    
    def validate_syntax(self, input_line: str) -> Tuple[bool, Optional[str]]:
        """
        Validate command syntax.
        
        Args:
            input_line: Command line
            
        Returns:
            (is_valid, error_message)
        """
        # Check for unmatched quotes
        try:
            shlex.split(input_line)
        except ValueError as e:
            return False, f"Syntax error: {e}"
        
        # Check for empty pipes
        if '|' in input_line:
            parts = input_line.split('|')
            for part in parts:
                if not part.strip():
                    return False, "Empty pipe segment"
        
        # Check for empty redirections
        if '>' in input_line:
            if input_line.rstrip().endswith('>'):
                return False, "Missing redirection target"
        
        return True, None
    
    def expand_variables(self, text: str, env_vars: dict) -> str:
        """
        Expand environment variables in text.
        
        Args:
            text: Text with variables
            env_vars: Environment variables dict
            
        Returns:
            Expanded text
        """
        # Expand ${VAR} format
        def replace_braced(match):
            var_name = match.group(1)
            return env_vars.get(var_name, match.group(0))
        
        text = re.sub(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}', replace_braced, text)
        
        # Expand $VAR format
        def replace_simple(match):
            var_name = match.group(1)
            return env_vars.get(var_name, match.group(0))
        
        text = re.sub(r'\$([A-Za-z_][A-Za-z0-9_]*)', replace_simple, text)
        
        return text

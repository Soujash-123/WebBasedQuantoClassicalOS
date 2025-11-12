"""
Shell Core
Interactive command-line shell with history, aliases, and context-aware prompts.
"""

import os
import sys
from typing import Optional, Dict, Any, List
from .command_parser import CommandParser, ParsedCommand
from .command_registry import CommandRegistry


class ShellCore:
    """Core interactive shell."""
    
    def __init__(
        self,
        registry: CommandRegistry,
        context: Any = None,
        prompt_template: str = "[{user}@AIOS:{path}]$ "
    ):
        """
        Initialize shell core.
        
        Args:
            registry: Command registry
            context: Execution context
            prompt_template: Prompt template string
        """
        self.registry = registry
        self.context = context
        self.prompt_template = prompt_template
        
        # Parser
        self.parser = CommandParser()
        
        # Shell state
        self.running = False
        self.exit_code = 0
        
        # Aliases
        self.aliases: Dict[str, str] = {}
        
        # Macros
        self.macros: Dict[str, str] = {}
        
        # Output capture for piping
        self.captured_output: List[str] = []
        self.capture_mode = False
        
        print("[ShellCore] Shell Core initialized")
    
    def get_prompt(self) -> str:
        """
        Generate context-aware prompt.
        
        Returns:
            Prompt string
        """
        try:
            # Get context values
            user = "user"
            path = "/"
            
            if self.context:
                # Try to get user
                if hasattr(self.context, 'user_layer'):
                    username = self.context.user_layer.whoami()
                    if username:
                        user = username
                
                # Try to get current path
                if hasattr(self.context, 'vfs_layer'):
                    path = self.context.vfs_layer.pwd()
            
            # Format prompt
            prompt = self.prompt_template.format(user=user, path=path)
            return prompt
            
        except Exception as e:
            return "$ "
    
    def start(self) -> None:
        """Start the interactive shell."""
        self.running = True
        
        print("\n" + "=" * 60)
        print("Welcome to AI OS Shell")
        print("Type 'help' for available commands, 'exit' to quit")
        print("=" * 60 + "\n")
        
        # Load history if available
        if self.context and hasattr(self.context, 'user_layer'):
            username = self.context.user_layer.whoami()
            if username:
                history_file = f".history_{username}"
                self.parser.load_history(history_file)
        
        # Main input loop
        while self.running:
            try:
                # Get prompt
                prompt = self.get_prompt()
                
                # Read input
                try:
                    user_input = input(prompt)
                except EOFError:
                    print()
                    break
                except KeyboardInterrupt:
                    print("\n(Use 'exit' to quit)")
                    continue
                
                # Execute command
                self.execute_line(user_input)
                
            except Exception as e:
                print(f"Shell error: {e}")
                import traceback
                traceback.print_exc()
        
        # Save history
        if self.context and hasattr(self.context, 'user_layer'):
            username = self.context.user_layer.whoami()
            if username:
                history_file = f".history_{username}"
                self.parser.save_history(history_file)
        
        print("\nGoodbye!")
    
    def execute_line(self, line: str) -> Any:
        """
        Execute a command line.
        
        Args:
            line: Command line string
            
        Returns:
            Command result
        """
        if not line or not line.strip():
            return None
        
        # Check for alias expansion
        line = self.expand_aliases(line)
        
        # Parse command
        parsed = self.parser.parse(line)
        if not parsed:
            return None
        
        # Execute command chain
        return self.execute_command(parsed)
    
    def execute_command(self, cmd: ParsedCommand, input_data: Optional[str] = None) -> Any:
        """
        Execute a parsed command.
        
        Args:
            cmd: Parsed command
            input_data: Input data from pipe
            
        Returns:
            Command result
        """
        # Handle input redirection
        if cmd.redirect_input and not input_data:
            input_data = self._read_file(cmd.redirect_input)
        
        # Set up output capture for piping
        original_stdout = None
        if cmd.pipe_to or cmd.redirect_output:
            self.captured_output = []
            self.capture_mode = True
            original_stdout = sys.stdout
            sys.stdout = self
        
        try:
            # Add input data to context if piped
            if input_data:
                if not hasattr(self.context, 'pipe_input'):
                    self.context.pipe_input = input_data
            
            # Execute the command
            result = self.registry.execute(cmd.command, cmd.args, self.context)
            
            # Restore stdout
            if original_stdout:
                sys.stdout = original_stdout
                self.capture_mode = False
            
            # Handle output redirection
            if cmd.redirect_output:
                output = '\n'.join(self.captured_output)
                self._write_file(cmd.redirect_output, output, cmd.redirect_append)
                self.captured_output = []
            
            # Handle piping
            if cmd.pipe_to:
                piped_data = '\n'.join(self.captured_output)
                self.captured_output = []
                return self.execute_command(cmd.pipe_to, piped_data)
            
            # Handle command chaining
            if cmd.next_command:
                # && - execute next if current succeeded
                # || - execute next if current failed
                should_execute_next = False
                
                if cmd.chain_operator == '&&':
                    should_execute_next = (result is not None and result != False)
                elif cmd.chain_operator == '||':
                    should_execute_next = (result is None or result == False)
                
                if should_execute_next:
                    return self.execute_command(cmd.next_command)
            
            return result
            
        except Exception as e:
            if original_stdout:
                sys.stdout = original_stdout
                self.capture_mode = False
            print(f"Error executing command: {e}")
            return None
    
    def write(self, text: str) -> None:
        """Capture output for piping (stdout replacement)."""
        if self.capture_mode:
            self.captured_output.append(text.rstrip('\n'))
        else:
            sys.__stdout__.write(text)
    
    def flush(self) -> None:
        """Flush output (for stdout compatibility)."""
        pass
    
    def _read_file(self, filepath: str) -> Optional[str]:
        """Read file for input redirection."""
        try:
            if self.context and hasattr(self.context, 'vfs_layer'):
                return self.context.vfs_layer.read(filepath)
            else:
                with open(filepath, 'r') as f:
                    return f.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return None
    
    def _write_file(self, filepath: str, content: str, append: bool = False) -> bool:
        """Write file for output redirection."""
        try:
            if self.context and hasattr(self.context, 'vfs_layer'):
                if append:
                    return self.context.vfs_layer.append(filepath, content)
                else:
                    return self.context.vfs_layer.write(filepath, content)
            else:
                mode = 'a' if append else 'w'
                with open(filepath, mode) as f:
                    f.write(content)
                return True
        except Exception as e:
            print(f"Error writing file {filepath}: {e}")
            return False
    
    def expand_aliases(self, line: str) -> str:
        """
        Expand aliases in command line.
        
        Args:
            line: Command line
            
        Returns:
            Expanded command line
        """
        parts = line.split()
        if parts and parts[0] in self.aliases:
            parts[0] = self.aliases[parts[0]]
            return ' '.join(parts)
        return line
    
    def add_alias(self, name: str, command: str) -> None:
        """Add a command alias."""
        self.aliases[name] = command
        print(f"Alias created: {name} -> {command}")
    
    def remove_alias(self, name: str) -> bool:
        """Remove a command alias."""
        if name in self.aliases:
            del self.aliases[name]
            print(f"Alias removed: {name}")
            return True
        print(f"Alias not found: {name}")
        return False
    
    def list_aliases(self) -> Dict[str, str]:
        """Get all aliases."""
        return self.aliases.copy()
    
    def stop(self) -> None:
        """Stop the shell."""
        self.running = False
    
    def set_exit_code(self, code: int) -> None:
        """Set shell exit code."""
        self.exit_code = code

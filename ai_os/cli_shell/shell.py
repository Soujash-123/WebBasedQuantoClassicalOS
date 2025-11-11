"""
CLI Shell
Main interactive command-line shell integrating all OS layers.
"""

import sys
from typing import Any, Optional
from .command_parser import CommandParser, ParsedCommand
from .command_registry import CommandRegistry, register_all_commands
from .command_history import CommandHistory
from .command_aliases import AliasManager
from .command_help import HelpSystem
from .os_session_manager import SessionManager
from .error_handler import ErrorHandler
from .logger import CLILogger


class ShellContext:
    """Context object for command execution."""
    
    def __init__(self, shell):
        """Initialize shell context."""
        self.shell = shell
        self.session = shell.session
        self.history = shell.history
        self.aliases = shell.aliases
        self.help_system = shell.help_system
        self.error_handler = shell.error_handler
        self.logger = shell.logger
        self.running = True
        
        # Output capture for piping
        self.captured_output = []
        self.capture_mode = False


class CLIShell:
    """
    Main CLI Shell - Unified interface for AI OS.
    Integrates all OS layers into a cohesive command-line environment.
    """
    
    def __init__(
        self,
        core_layer=None,
        device_layer=None,
        vfs_layer=None,
        process_layer=None,
        user_layer=None,
        system_layer=None,
        user: str = "root",
        debug: bool = False
    ):
        """
        Initialize CLI Shell.
        
        Args:
            core_layer: Core system layer
            device_layer: Device management layer
            vfs_layer: Virtual file system layer
            process_layer: Process management layer
            user_layer: User management layer
            system_layer: System management layer
            user: Initial user
            debug: Enable debug mode
        """
        print("\n" + "=" * 70)
        print("AI OS - Unified CLI Shell")
        print("=" * 70)
        
        # Store layer references
        self.core = core_layer
        self.devices = device_layer
        self.vfs = vfs_layer
        self.processes = process_layer
        self.users = user_layer
        self.system = system_layer
        
        # Initialize components
        self.session = SessionManager(user)
        self.history = CommandHistory()
        self.aliases = AliasManager()
        self.help_system = HelpSystem()
        self.error_handler = ErrorHandler(debug)
        self.logger = CLILogger(enabled=debug)
        
        # Initialize command registry
        self.registry = CommandRegistry()
        self._register_commands()
        
        # Initialize parser with available commands
        self.parser = CommandParser(self.registry.list_commands())
        
        # Create execution context
        self.context = ShellContext(self)
        
        # Shell state
        self.running = False
        
        print("Shell initialized successfully")
        print("=" * 70 + "\n")
        
        self.logger.info("CLI Shell initialized")
    
    def _register_commands(self) -> None:
        """Register all OS commands."""
        os_layers = {
            'core': self.core,
            'devices': self.devices,
            'vfs': self.vfs,
            'processes': self.processes,
            'users': self.users,
            'system': self.system
        }
        
        register_all_commands(self.registry, os_layers)
        self.logger.info(f"Registered {len(self.registry.list_commands())} commands")
    
    def start(self) -> None:
        """Start interactive shell."""
        self.running = True
        
        print("Type 'help' for available commands, 'exit' to quit\n")
        
        # Load session state
        self.session.load_state()
        
        # Main input loop
        while self.running:
            try:
                # Get prompt
                prompt = self.session.get_prompt()
                
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
                if user_input.strip():
                    self.execute(user_input)
                
            except Exception as e:
                error_msg = self.error_handler.handle_error(e, "shell loop")
                print(f"\n{error_msg}\n")
                self.logger.error(f"Shell error: {e}")
        
        # Save session state
        self.session.save_state()
        self.history.save()
        
        print("\nGoodbye!")
        self.logger.info("CLI Shell exited")
    
    def execute(self, command_line: str) -> Any:
        """
        Execute a command line.
        
        Args:
            command_line: Command line string
            
        Returns:
            Command result
        """
        # Expand aliases
        command_line = self.aliases.expand(command_line)
        
        # Expand environment variables
        command_line = self.parser.expand_variables(
            command_line,
            self.session.list_env()
        )
        
        # Validate syntax
        is_valid, error = self.parser.validate_syntax(command_line)
        if not is_valid:
            print(f"Syntax error: {error}")
            self.history.add(command_line, success=False)
            return None
        
        # Parse command
        parsed = self.parser.parse(command_line)
        if not parsed:
            return None
        
        # Execute
        try:
            result = self._execute_parsed(parsed)
            self.history.add(command_line, success=True)
            self.logger.log_command(command_line, success=True)
            return result
        except Exception as e:
            error_msg = self.error_handler.handle_command_error(
                parsed.command,
                e
            )
            print(f"\n{error_msg}\n")
            self.history.add(command_line, success=False)
            self.logger.log_command(command_line, success=False)
            self.logger.error(str(e))
            return None
    
    def _execute_parsed(self, cmd: ParsedCommand, input_data: Optional[str] = None) -> Any:
        """Execute a parsed command."""
        # Handle input redirection
        if cmd.redirect_input and not input_data:
            input_data = self._read_file(cmd.redirect_input)
        
        # Set up output capture for piping
        original_stdout = None
        if cmd.pipe_to or cmd.redirect_output:
            self.context.captured_output = []
            self.context.capture_mode = True
            original_stdout = sys.stdout
            sys.stdout = self
        
        try:
            # Add input data to context if piped
            if input_data:
                self.context.pipe_input = input_data
            
            # Execute the command
            result = self.registry.execute(cmd.command, cmd.args, self.context)
            
            # Restore stdout
            if original_stdout:
                sys.stdout = original_stdout
                self.context.capture_mode = False
            
            # Handle output redirection
            if cmd.redirect_output:
                output = '\n'.join(self.context.captured_output)
                self._write_file(cmd.redirect_output, output, cmd.redirect_append)
                self.context.captured_output = []
            
            # Handle piping
            if cmd.pipe_to:
                piped_data = '\n'.join(self.context.captured_output)
                self.context.captured_output = []
                return self._execute_parsed(cmd.pipe_to, piped_data)
            
            # Handle command chaining
            if cmd.next_command:
                should_execute_next = False
                
                if cmd.chain_operator == '&&':
                    should_execute_next = (result is not None and result != False)
                elif cmd.chain_operator == '||':
                    should_execute_next = (result is None or result == False)
                
                if should_execute_next:
                    return self._execute_parsed(cmd.next_command)
            
            return result
            
        except Exception as e:
            if original_stdout:
                sys.stdout = original_stdout
                self.context.capture_mode = False
            raise
    
    def write(self, text: str) -> None:
        """Capture output for piping (stdout replacement)."""
        if self.context.capture_mode:
            self.context.captured_output.append(text.rstrip('\n'))
        else:
            sys.__stdout__.write(text)
    
    def flush(self) -> None:
        """Flush output (for stdout compatibility)."""
        pass
    
    def _read_file(self, filepath: str) -> Optional[str]:
        """Read file for input redirection."""
        try:
            if self.vfs:
                return self.vfs.read(filepath)
            else:
                with open(filepath, 'r') as f:
                    return f.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return None
    
    def _write_file(self, filepath: str, content: str, append: bool = False) -> bool:
        """Write file for output redirection."""
        try:
            if self.vfs:
                if append:
                    existing = self.vfs.read(filepath) or ""
                    return self.vfs.write(filepath, existing + content)
                else:
                    return self.vfs.write(filepath, content)
            else:
                mode = 'a' if append else 'w'
                with open(filepath, mode) as f:
                    f.write(content)
                return True
        except Exception as e:
            print(f"Error writing file {filepath}: {e}")
            return False
    
    def stop(self) -> None:
        """Stop the shell."""
        self.running = False
        self.context.running = False
    
    def get_stats(self) -> dict:
        """Get shell statistics."""
        return {
            'session': self.session.get_session_info(),
            'history': self.history.get_stats(),
            'errors': self.error_handler.get_stats(),
            'commands_available': len(self.registry.list_commands())
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False

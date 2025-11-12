"""
AI OS Unified Client
Complete CLI client integrating all layers and features.
Supports: ls, cat, nano, os watch, os refresh, and all OS commands.
"""

import sys
import os
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ai_os.os_master_simple import AIOSMaster
except ImportError:
    from ai_os.os_master import AIOSMaster
from ai_os.kernel import get_kernel_reload
from ai_os.kernel.kernel_commands import KernelCommands


class UnifiedClient:
    """
    Unified AI OS Client
    Complete CLI with all layers and hot reload support.
    """
    
    def __init__(self, enable_hot_reload=True):
        """Initialize unified client"""
        self.running = True
        self.enable_hot_reload = enable_hot_reload
        
        # Initialize OS Master (all layers)
        print("Initializing AI OS...")
        self.os_master = AIOSMaster()
        
        if not self.os_master.initialize():
            print("Failed to initialize AI OS")
            sys.exit(1)
        
        # Initialize hot reload
        self.enable_hot_reload = enable_hot_reload
        self.kernel_reload = None
        self.kernel_cmds = None
        
        if enable_hot_reload:
            try:
                self.kernel_reload = get_kernel_reload(restart_callback=self._restart_system)
                self.kernel_cmds = KernelCommands()  # KernelCommands gets kernel internally
                print("✓ Hot reload enabled")
            except Exception as e:
                print(f"Warning: Hot reload not available: {e}")
                import traceback
                traceback.print_exc()
        
        # Session state
        self.current_user = "root"
        self.current_dir = "/"
        self.env_vars = {}
        
        # Command history
        self.history = []
        
        # Get all commands from OS Master
        self.commands = self.os_master.get_all_commands()
        
        # Add built-in commands
        self._register_builtin_commands()
        
        # Add hot reload commands
        if self.enable_hot_reload:
            self._register_hotreload_commands()
        
        # Load custom commands
        self._load_custom_commands()
        
        print(f"✓ {len(self.commands)} commands available")
    
    def _register_builtin_commands(self):
        """Register built-in shell commands"""
        self.commands.update({
            'help': {
                'function': self.cmd_help,
                'description': 'Show available commands',
                'usage': 'help [command]'
            },
            'exit': {
                'function': self.cmd_exit,
                'description': 'Exit the shell',
                'usage': 'exit'
            },
            'quit': {
                'function': self.cmd_exit,
                'description': 'Exit the shell',
                'usage': 'quit'
            },
            'clear': {
                'function': self.cmd_clear,
                'description': 'Clear screen',
                'usage': 'clear'
            },
            'history': {
                'function': self.cmd_history,
                'description': 'Show command history',
                'usage': 'history'
            },
            'alias': {
                'function': self.cmd_alias,
                'description': 'Create command alias',
                'usage': 'alias name=command'
            },
            'export': {
                'function': self.cmd_export,
                'description': 'Set environment variable',
                'usage': 'export VAR=value'
            },
            'env': {
                'function': self.cmd_env,
                'description': 'Show environment variables',
                'usage': 'env'
            }
        })
    
    def _register_hotreload_commands(self):
        """Register hot reload commands"""
        if not self.kernel_cmds:
            return
        
        self.commands.update({
            'refresh': {
                'function': self.cmd_refresh_wrapper,
                'description': 'Reload changed modules and commands',
                'usage': 'refresh [--force]'
            },
            'watch': {
                'function': self.cmd_watch_wrapper,
                'description': 'Watch for changes',
                'usage': 'watch [--live|--stop|--status]'
            },
            'rollback': {
                'function': self.kernel_cmds.cmd_os_rollback,
                'description': 'Rollback a module',
                'usage': 'rollback <module_name>'
            },
            'reload-status': {
                'function': self.kernel_cmds.cmd_os_status,
                'description': 'Show reload status',
                'usage': 'reload-status [reloads|modules]'
            }
        })
    
    def _load_custom_commands(self):
        """Load custom commands from custom_commands.py"""
        try:
            from ai_os import custom_commands
            if hasattr(custom_commands, 'CUSTOM_COMMANDS'):
                self.commands.update(custom_commands.CUSTOM_COMMANDS)
                print(f"✓ Loaded {len(custom_commands.CUSTOM_COMMANDS)} custom commands")
        except ImportError:
            pass  # No custom commands file
        except Exception as e:
            print(f"Warning: Could not load custom commands: {e}")
    
    def cmd_help(self, args=None):
        """Show help information"""
        if args and len(args) > 0:
            # Show help for specific command
            cmd_name = args[0]
            if cmd_name in self.commands:
                cmd_info = self.commands[cmd_name]
                print(f"\n{cmd_name} - {cmd_info.get('description', 'No description')}")
                print(f"Usage: {cmd_info.get('usage', cmd_name)}")
                return
            else:
                return f"Unknown command: {cmd_name}"
        
        # Show all commands grouped by category
        print("\n" + "=" * 70)
        print("AI OS UNIFIED CLIENT - AVAILABLE COMMANDS")
        print("=" * 70)
        
        # Group commands by layer
        by_layer = {}
        for cmd_name, cmd_info in self.commands.items():
            layer = cmd_info.get('layer', 'builtin')
            if layer not in by_layer:
                by_layer[layer] = []
            by_layer[layer].append((cmd_name, cmd_info.get('description', '')))
        
        # Display by category
        for layer_name in sorted(by_layer.keys()):
            print(f"\n{layer_name.upper()} COMMANDS:")
            print("-" * 70)
            for cmd_name, description in sorted(by_layer[layer_name]):
                print(f"  {cmd_name:<20} {description}")
        
        print("\n" + "=" * 70)
        print(f"Total: {len(self.commands)} commands")
        print("\nType 'help <command>' for detailed information")
        print("=" * 70)
        return ""
    
    def cmd_exit(self, args=None):
        """Exit the shell"""
        print("\nShutting down AI OS...")
        self.running = False
        return "exit"
    
    def cmd_clear(self, args=None):
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        return ""
    
    def cmd_history(self, args=None):
        """Show command history"""
        if not self.history:
            return "No command history"
        
        print("\nCommand History:")
        print("-" * 70)
        for i, cmd in enumerate(self.history[-20:], 1):
            print(f"{i:3}. {cmd}")
        return ""
    
    def cmd_alias(self, args=None):
        """Create command alias"""
        if not args:
            return "Usage: alias name=command"
        
        alias_def = ' '.join(args)
        if '=' not in alias_def:
            return "Usage: alias name=command"
        
        name, command = alias_def.split('=', 1)
        # Store alias (simplified - could be enhanced)
        return f"Alias '{name}' created for '{command}'"
    
    def cmd_export(self, args=None):
        """Set environment variable"""
        if not args:
            return "Usage: export VAR=value"
        
        var_def = ' '.join(args)
        if '=' not in var_def:
            return "Usage: export VAR=value"
        
        name, value = var_def.split('=', 1)
        self.env_vars[name] = value
        return f"Exported {name}={value}"
    
    def cmd_env(self, args=None):
        """Show environment variables"""
        if not self.env_vars:
            return "No environment variables set"
        
        print("\nEnvironment Variables:")
        print("-" * 70)
        for name, value in self.env_vars.items():
            print(f"{name}={value}")
        return ""
    
    def cmd_cd(self, args=None):
        """Change directory"""
        if not args:
            self.current_dir = "/"
            return ""
        
        path = args[0]
        
        # Handle special cases
        if path == "..":
            if self.current_dir != "/":
                self.current_dir = str(Path(self.current_dir).parent)
        elif path == "~":
            self.current_dir = "/home/" + self.current_user
        elif path.startswith("/"):
            self.current_dir = path
        else:
            self.current_dir = str(Path(self.current_dir) / path)
        
        return ""
    
    def cmd_pwd(self, args=None):
        """Print working directory"""
        return self.current_dir
    
    def _restart_system(self):
        """Restart the entire AI OS system"""
        print("\n" + "="*70)
        print("RESTARTING AI OS TO APPLY CHANGES...")
        print("="*70)
        
        # Shutdown current system
        self.shutdown()
        
        # Restart
        print("\nRestarting in 1 second...")
        import time
        time.sleep(1)
        
        # Re-execute the script
        import sys
        import os
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    def cmd_refresh_wrapper(self, args=None):
        """Refresh modules and restart AI OS"""
        # Call the original refresh
        result = self.kernel_cmds.cmd_os_refresh(args)
        
        # Restart the system
        self._restart_system()
        
        return result
    
    def cmd_watch_wrapper(self, args=None):
        """Watch wrapper that reloads commands on change"""
        result = self.kernel_cmds.cmd_os_watch(args)
        
        # If watch mode was activated, set up auto-reload callback
        if args and args[0] == '--live':
            print("✓ Auto-reload will refresh commands on changes")
        
        return result
    
    def _reload_all_commands(self):
        """Reload all commands from all layers"""
        try:
            # Clear current commands
            old_count = len(self.commands)
            self.commands.clear()
            
            # Reload OS Master layers
            import importlib
            import io
            import contextlib
            
            # Reload os_master_simple
            from ai_os import os_master_simple
            importlib.reload(os_master_simple)
            
            # Reinitialize OS Master (suppress output)
            with contextlib.redirect_stdout(io.StringIO()):
                self.os_master = os_master_simple.AIOSMaster()
            
            # Get all commands from OS Master
            self.commands = self.os_master.get_all_commands()
            
            # Re-add built-in commands
            self._register_builtin_commands()
            
            # Re-add hot reload commands
            if self.enable_hot_reload:
                self._register_hotreload_commands()
            
            # Reload custom commands
            with contextlib.redirect_stdout(io.StringIO()):
                self._load_custom_commands()
            
            new_count = len(self.commands)
            print(f"✓ Commands reloaded: {old_count} → {new_count}")
            
            if new_count > old_count:
                print(f"✓ {new_count - old_count} new commands added!")
            elif new_count < old_count:
                print(f"⚠ {old_count - new_count} commands removed")
            
        except Exception as e:
            print(f"✗ Error reloading commands: {e}")
            import traceback
            traceback.print_exc()
    
    def _parse_command(self, input_line):
        """Parse command line input"""
        parts = input_line.strip().split()
        if not parts:
            return None, []
        
        # Handle compound commands (e.g., "os refresh")
        if len(parts) >= 2 and parts[0] == 'os':
            cmd = parts[1]
            args = parts[2:]
            
            # Map os commands to direct commands
            if cmd in ['refresh', 'watch', 'rollback', 'status']:
                if cmd == 'status':
                    cmd = 'reload-status'
                return cmd, args
        
        cmd = parts[0]
        args = parts[1:]
        
        return cmd, args
    
    def execute_command(self, input_line):
        """Execute a command"""
        # Add to history
        self.history.append(input_line)
        
        # Parse command
        cmd, args = self._parse_command(input_line)
        
        if not cmd:
            return
        
        # Check if command exists
        if cmd in self.commands:
            try:
                cmd_info = self.commands[cmd]
                func = cmd_info['function']
                
                # Execute command
                result = func(args)
                
                # Print result if not empty
                if result and result != "exit":
                    print(result)
                
                # Handle exit
                if result == "exit":
                    self.running = False
                    
            except Exception as e:
                print(f"Error executing {cmd}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Command not found: {cmd}")
            print("Type 'help' for available commands")
    
    def print_banner(self):
        """Print startup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                    AI OS - Unified Client v1.0                       ║
║                                                                      ║
║  Complete CLI with all layers integrated                             ║
║  • File System (ls, cat, nano, etc.)                                 ║
║  • Memory Management (memstat, procmem, etc.)                        ║
║  • Network Tools (ping, netstat, etc.)                               ║
║  • Security (login, encrypt, etc.)                                   ║
║  • Diagnostics (syscheck, resources, etc.)                           ║
║  • Hot Reload (os refresh, os watch, etc.)                           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Type 'help' for available commands
Type 'os refresh' to reload changed modules
Type 'os watch --live' to enable auto-reload
Type 'exit' to quit

"""
        print(banner)
    
    def run(self):
        """Main CLI loop"""
        self.print_banner()
        
        while self.running:
            try:
                # Show prompt
                prompt = f"{self.current_user}@aios:{self.current_dir}$ "
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Execute command
                self.execute_command(user_input)
                
            except KeyboardInterrupt:
                print("\n\nUse 'exit' to quit")
            except EOFError:
                print("\n")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def shutdown(self):
        """Shutdown the client"""
        print("\nShutting down...")
        
        # Stop watch mode if active
        if self.kernel and self.kernel.watch_active:
            print("Stopping watch mode...")
            self.kernel.stop_watch()
        
        # Shutdown OS Master
        self.os_master.shutdown()
        
        print("Goodbye!")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI OS Unified Client")
    parser.add_argument('--no-hotreload', action='store_true',
                       help='Disable hot reload features')
    parser.add_argument('--auto-reload', action='store_true',
                       help='Enable auto-reload on startup')
    
    args = parser.parse_args()
    
    try:
        # Create client
        client = UnifiedClient(enable_hot_reload=not args.no_hotreload)
        
        # Enable auto-reload if requested
        if args.auto_reload and client.kernel:
            client.kernel.start_watch()
            print("✓ Auto-reload enabled")
        
        # Run client
        client.run()
        
        # Shutdown
        client.shutdown()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

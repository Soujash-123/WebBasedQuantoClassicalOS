"""
AI OS Main CLI with Hot Reload Support
Persistent CLI that can reload modules without restarting.
"""

import sys
import os
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_os.kernel import get_kernel_reload
from ai_os.kernel.kernel_commands import KernelCommands


class HotReloadCLI:
    """
    CLI Shell with Hot Reload Capabilities
    """
    
    def __init__(self):
        self.running = True
        self.kernel = get_kernel_reload()
        self.kernel_cmds = KernelCommands()
        self.commands = {}
        self.current_user = "root"
        self.current_dir = "/"
        
        # Initialize
        self._register_commands()
        self._print_banner()
    
    def _print_banner(self):
        """Print startup banner"""
        print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                    AI OS v1.0 - Hot Reload CLI                       ║
║                                                                      ║
║  Self-Updating Kernel - Code changes apply without restart!         ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Type 'help' for available commands
Type 'os refresh' to reload changed modules
Type 'os watch --live' to enable auto-reload
Type 'exit' to quit

""")
    
    def _register_commands(self):
        """Register all CLI commands"""
        # Basic commands
        self.commands['help'] = self.cmd_help
        self.commands['exit'] = self.cmd_exit
        self.commands['clear'] = self.cmd_clear
        self.commands['whoami'] = self.cmd_whoami
        self.commands['pwd'] = self.cmd_pwd
        
        # Kernel hot reload commands
        self.commands['refresh'] = self.kernel_cmds.cmd_os_refresh
        self.commands['watch'] = self.kernel_cmds.cmd_os_watch
        self.commands['rollback'] = self.kernel_cmds.cmd_os_rollback
        self.commands['reload-status'] = self.kernel_cmds.cmd_os_status
        
        # Demo commands
        self.commands['demo'] = self.cmd_demo
        self.commands['test-reload'] = self.cmd_test_reload
    
    def cmd_help(self, args=None):
        """Show help information"""
        help_text = """
╔══════════════════════════════════════════════════════════════════════╗
║                         AVAILABLE COMMANDS                           ║
╚══════════════════════════════════════════════════════════════════════╝

BASIC COMMANDS:
  help                  - Show this help message
  exit                  - Exit the CLI
  clear                 - Clear screen
  whoami                - Show current user
  pwd                   - Show current directory

HOT RELOAD COMMANDS:
  refresh [--force]     - Reload modified modules
  watch [--live|--stop] - Enable/disable auto-reload
  rollback <module>     - Rollback a module to previous version
  reload-status         - Show reload status and history

DEMO COMMANDS:
  demo                  - Run hot reload demonstration
  test-reload           - Test reload functionality

COMPOUND COMMANDS:
  os refresh            - Same as 'refresh'
  os watch --live       - Same as 'watch --live'
  os rollback <module>  - Same as 'rollback <module>'
  os status reloads     - Same as 'reload-status'

═══════════════════════════════════════════════════════════════════════

HOT RELOAD WORKFLOW:
  1. Make changes to any Python file in ai_os/
  2. Run: refresh
  3. Changes are immediately active!
  
  Or enable auto-reload:
  1. Run: watch --live
  2. Make changes to files
  3. Changes auto-reload every 2 seconds!

═══════════════════════════════════════════════════════════════════════
"""
        return help_text
    
    def cmd_exit(self, args=None):
        """Exit the CLI"""
        print("\nShutting down AI OS...")
        
        # Stop watch mode if active
        if self.kernel.watch_active:
            print("Stopping watch mode...")
            self.kernel.stop_watch()
        
        print("Goodbye!\n")
        self.running = False
        return "exit"
    
    def cmd_clear(self, args=None):
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        return ""
    
    def cmd_whoami(self, args=None):
        """Show current user"""
        return f"Current user: {self.current_user}"
    
    def cmd_pwd(self, args=None):
        """Show current directory"""
        return f"Current directory: {self.current_dir}"
    
    def cmd_demo(self, args=None):
        """Run hot reload demonstration"""
        print("\n" + "=" * 70)
        print("HOT RELOAD DEMONSTRATION")
        print("=" * 70)
        
        print("""
This CLI supports hot-reloading! Here's how it works:

SCENARIO 1: Manual Reload
  1. Edit a file (e.g., add a new command to this file)
  2. Run: refresh
  3. Your changes are live!

SCENARIO 2: Auto-Reload
  1. Run: watch --live
  2. Edit any file
  3. Changes auto-reload every 2 seconds
  4. Run: watch --stop (to disable)

SCENARIO 3: Rollback
  1. If a reload breaks something
  2. Run: rollback <module_name>
  3. Previous version is restored

Try it now:
  1. Keep this CLI running
  2. Edit ai_os/kernel/example_usage.py
  3. Add a print statement in any function
  4. Run: refresh
  5. Import and call that function - see your changes!

""")
        
        return "Demo complete. Try it yourself!"
    
    def cmd_test_reload(self, args=None):
        """Test reload functionality"""
        print("\n" + "=" * 70)
        print("TESTING HOT RELOAD")
        print("=" * 70)
        
        print("\n1. Detecting changes...")
        changed = self.kernel.detect_changes()
        print(f"   Changed modules: {len(changed)}")
        
        if changed:
            print("\n   Changed files:")
            for mod in changed[:10]:
                print(f"   - {mod}")
        
        print("\n2. Running refresh...")
        result = self.kernel.refresh()
        
        print(f"\n3. Results:")
        print(f"   ✓ Success: {result['success']}")
        print(f"   ✗ Failed: {result['failed']}")
        print(f"   Duration: {result['elapsed_seconds']:.2f}s")
        
        print("\n" + "=" * 70)
        
        return "Test complete"
    
    def _parse_command(self, input_line: str):
        """Parse command line input"""
        parts = input_line.strip().split()
        if not parts:
            return None, []
        
        # Handle compound commands (e.g., "os refresh")
        if len(parts) >= 2 and parts[0] == 'os':
            cmd = parts[1]
            args = parts[2:]
        else:
            cmd = parts[0]
            args = parts[1:]
        
        return cmd, args
    
    def execute_command(self, input_line: str):
        """Execute a command"""
        cmd, args = self._parse_command(input_line)
        
        if not cmd:
            return
        
        if cmd in self.commands:
            try:
                result = self.commands[cmd](args)
                if result and result != "exit":
                    print(result)
            except Exception as e:
                print(f"Error executing {cmd}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands")
    
    def run(self):
        """Main CLI loop"""
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


def main():
    """Main entry point"""
    print("Initializing AI OS with Hot Reload...")
    
    try:
        cli = HotReloadCLI()
        cli.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""
Kernel Hot Reload CLI Commands
Integration with AI OS CLI Shell
"""

from .kernel_hot_reload import get_kernel_reload


class KernelCommands:
    """CLI commands for kernel hot reload management"""
    
    def __init__(self):
        self.kernel = get_kernel_reload()
    
    def cmd_os_refresh(self, args=None):
        """
        Reload all modified modules
        
        Usage: os refresh [--force]
        
        Options:
            --force    Reload all modules regardless of changes
        """
        force = args and '--force' in args
        
        print("\n" + "=" * 70)
        print("KERNEL MODULE REFRESH")
        print("=" * 70)
        
        if force:
            print("Mode: FORCE RELOAD (all modules)")
        else:
            print("Mode: SMART RELOAD (changed modules only)")
        
        print("\nScanning for changes...")
        
        result = self.kernel.refresh(force_all=force)
        
        print(f"\nResults:")
        print(f"  Total Modules: {result['total_modules']}")
        print(f"  ✓ Success: {result['success']}")
        print(f"  ✗ Failed: {result['failed']}")
        print(f"  Duration: {result['elapsed_seconds']:.2f}s")
        
        if result['failed_modules']:
            print(f"\nFailed Modules:")
            for mod in result['failed_modules']:
                print(f"  - {mod}")
        
        print("=" * 70)
        
        return f"Refresh complete: {result['success']} modules reloaded"
    
    def cmd_os_watch(self, args=None):
        """
        Enable/disable auto-reload watch mode
        
        Usage: os watch [--live|--stop|--status]
        
        Options:
            --live     Start watching for changes
            --stop     Stop watching
            --status   Show watch status
        """
        if not args:
            args = ['--status']
        
        if '--live' in args:
            if self.kernel.start_watch():
                return "✓ Watch mode ACTIVATED - Auto-reloading enabled"
            else:
                return "⚠ Watch mode already active"
        
        elif '--stop' in args:
            if self.kernel.stop_watch():
                return "✓ Watch mode DEACTIVATED"
            else:
                return "⚠ Watch mode not active"
        
        elif '--status' in args:
            status = self.kernel.get_status()
            if status['watch_active']:
                return "Watch mode: ACTIVE ✓"
            else:
                return "Watch mode: INACTIVE"
        
        return "Usage: os watch [--live|--stop|--status]"
    
    def cmd_os_rollback(self, args=None):
        """
        Rollback a module to previous version
        
        Usage: os rollback <module_name>
        
        Example:
            os rollback cli_shell.command_registry
        """
        if not args or len(args) == 0:
            return "Usage: os rollback <module_name>"
        
        module_name = args[0]
        
        print(f"\nAttempting rollback of: {module_name}")
        
        if self.kernel.rollback(module_name):
            return f"✓ Successfully rolled back {module_name}"
        else:
            return f"✗ Rollback failed - no backup available for {module_name}"
    
    def cmd_os_status(self, args=None):
        """
        Show kernel reload status
        
        Usage: os status [reloads|modules]
        
        Options:
            reloads    Show reload history
            modules    Show module registry
        """
        if args and 'reloads' in args:
            return self.kernel.format_status_report()
        
        elif args and 'modules' in args:
            status = self.kernel.get_status()
            output = []
            output.append("=" * 70)
            output.append("MODULE REGISTRY")
            output.append("=" * 70)
            output.append(f"Total Modules: {status['total_modules']}")
            output.append("")
            
            # Show first 20 modules
            for i, (name, snapshot) in enumerate(list(self.kernel.module_registry.items())[:20]):
                output.append(f"{i+1}. {name}")
                output.append(f"   Status: {snapshot.status}")
                output.append(f"   Checksum: {snapshot.checksum[:16]}...")
                output.append("")
            
            if status['total_modules'] > 20:
                output.append(f"... and {status['total_modules'] - 20} more modules")
            
            output.append("=" * 70)
            return "\n".join(output)
        
        else:
            return self.kernel.format_status_report()
    
    def get_commands(self):
        """Get all kernel commands for registration"""
        return {
            'os': {
                'refresh': {
                    'function': self.cmd_os_refresh,
                    'description': 'Reload modified modules',
                    'usage': 'os refresh [--force]'
                },
                'watch': {
                    'function': self.cmd_os_watch,
                    'description': 'Enable/disable auto-reload',
                    'usage': 'os watch [--live|--stop|--status]'
                },
                'rollback': {
                    'function': self.cmd_os_rollback,
                    'description': 'Rollback a module',
                    'usage': 'os rollback <module_name>'
                },
                'status': {
                    'function': self.cmd_os_status,
                    'description': 'Show kernel status',
                    'usage': 'os status [reloads|modules]'
                }
            }
        }


def register_kernel_commands(shell):
    """
    Register kernel commands with the shell
    
    Args:
        shell: Shell instance with command registry
    """
    kernel_cmds = KernelCommands()
    
    # Register compound commands (os refresh, os watch, etc.)
    if hasattr(shell, 'register_compound_command'):
        commands = kernel_cmds.get_commands()
        for prefix, subcmds in commands.items():
            for subcmd, info in subcmds.items():
                shell.register_compound_command(
                    f"{prefix} {subcmd}",
                    info['function'],
                    info['description']
                )
    else:
        # Fallback: register as simple commands
        shell.commands['refresh'] = kernel_cmds.cmd_os_refresh
        shell.commands['watch'] = kernel_cmds.cmd_os_watch
        shell.commands['rollback'] = kernel_cmds.cmd_os_rollback
        shell.commands['reload-status'] = kernel_cmds.cmd_os_status


def on_reload():
    """Hook called when this module is reloaded"""
    print("✓ Kernel commands module reloaded!")

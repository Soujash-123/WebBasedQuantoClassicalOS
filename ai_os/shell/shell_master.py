"""
Shell Master
Integrates shell with all OS layers and registers all CLI commands.
"""

from typing import Any, Optional
from .command_registry import CommandRegistry, register_command
from .shell_core import ShellCore


class ShellContext:
    """Context object passed to all commands."""
    
    def __init__(
        self,
        core_layer=None,
        device_layer=None,
        vfs_layer=None,
        io_layer=None,
        process_layer=None,
        user_layer=None,
        system_layer=None
    ):
        """Initialize shell context with all layers."""
        self.core_layer = core_layer
        self.device_layer = device_layer
        self.vfs_layer = vfs_layer
        self.io_layer = io_layer
        self.process_layer = process_layer
        self.user_layer = user_layer
        self.system_layer = system_layer
        self.pipe_input = None


class ShellLayer:
    """
    Main interface for the Command Shell Layer.
    Integrates with all OS layers and provides interactive CLI.
    """
    
    def __init__(
        self,
        core_layer=None,
        device_layer=None,
        vfs_layer=None,
        io_layer=None,
        process_layer=None,
        user_layer=None,
        system_layer=None
    ):
        """
        Initialize the Shell Layer.
        
        Args:
            core_layer: Core system layer
            device_layer: Device management layer
            vfs_layer: Virtual file system layer
            io_layer: I/O layer
            process_layer: Process management layer
            user_layer: User management layer
            system_layer: System management layer
        """
        print("=" * 60)
        print("Initializing Command Shell Layer")
        print("=" * 60)
        
        # Store layer references
        self.core = core_layer
        self.device_layer = device_layer
        self.vfs_layer = vfs_layer
        self.io_layer = io_layer
        self.process_layer = process_layer
        self.user_layer = user_layer
        self.system_layer = system_layer
        
        # Create context
        self.context = ShellContext(
            core_layer=core_layer,
            device_layer=device_layer,
            vfs_layer=vfs_layer,
            io_layer=io_layer,
            process_layer=process_layer,
            user_layer=user_layer,
            system_layer=system_layer
        )
        
        # Initialize registry
        self.registry = CommandRegistry()
        
        # Register all commands
        self._register_all_commands()
        
        # Initialize shell core
        self.shell = ShellCore(self.registry, self.context)
        
        # Register with core if available
        if self.core:
            self.core.system_registry.register_module("shell_layer", self)
            self.event_bus = self.core.event_bus
            self._setup_event_handlers()
        else:
            self.event_bus = None
        
        print("=" * 60)
        print("Command Shell Layer initialized successfully")
        print("=" * 60)
    
    def _setup_event_handlers(self) -> None:
        """Setup event handlers."""
        if not self.event_bus:
            return
        self.event_bus.subscribe("system.shutdown", self._on_system_shutdown)
    
    def _on_system_shutdown(self, data: Any) -> None:
        """Handle system shutdown event."""
        self.shutdown()
    
    def _register_all_commands(self) -> None:
        """Register all CLI commands."""
        # System commands
        self._register_system_commands()
        
        # Filesystem commands
        if self.vfs_layer:
            self._register_vfs_commands()
        
        # Process commands
        if self.process_layer:
            self._register_process_commands()
        
        # User commands
        if self.user_layer:
            self._register_user_commands()
        
        # Device commands
        if self.device_layer:
            self._register_device_commands()
        
        # System management commands
        if self.system_layer:
            self._register_system_mgmt_commands()
    
    def _register_system_commands(self) -> None:
        """Register system commands."""
        
        def cmd_help(args, ctx):
            """Show help for commands."""
            if args:
                print(self.registry.get_help(args[0]))
            else:
                print(self.registry.get_help())
            return True
        
        def cmd_exit(args, ctx):
            """Exit the shell."""
            self.shell.stop()
            return True
        
        def cmd_clear(args, ctx):
            """Clear the terminal."""
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            return True
        
        def cmd_history(args, ctx):
            """Show command history."""
            limit = int(args[0]) if args else None
            history = self.shell.parser.get_history(limit)
            for i, cmd in enumerate(history, 1):
                print(f"{i:4d}  {cmd}")
            return True
        
        def cmd_alias(args, ctx):
            """Create or list aliases."""
            if not args:
                # List aliases
                aliases = self.shell.list_aliases()
                if aliases:
                    for name, cmd in aliases.items():
                        print(f"{name}='{cmd}'")
                else:
                    print("No aliases defined")
            elif '=' in args[0]:
                # Create alias
                parts = args[0].split('=', 1)
                name = parts[0]
                command = parts[1]
                self.shell.add_alias(name, command)
            else:
                print("Usage: alias name=command")
            return True
        
        def cmd_unalias(args, ctx):
            """Remove an alias."""
            if not args:
                print("Usage: unalias <name>")
                return False
            return self.shell.remove_alias(args[0])
        
        def cmd_echo(args, ctx):
            """Echo arguments."""
            print(' '.join(args))
            return True
        
        # Register commands
        self.registry.register("help", cmd_help, "Show help for commands", "help [command]", "system")
        self.registry.register("exit", cmd_exit, "Exit the shell", "exit", "system", ["quit", "logout"])
        self.registry.register("clear", cmd_clear, "Clear the terminal", "clear", "system", ["cls"])
        self.registry.register("history", cmd_history, "Show command history", "history [limit]", "system")
        self.registry.register("alias", cmd_alias, "Create or list aliases", "alias [name=command]", "system")
        self.registry.register("unalias", cmd_unalias, "Remove an alias", "unalias <name>", "system")
        self.registry.register("echo", cmd_echo, "Echo arguments", "echo <text>", "system")
    
    def _register_vfs_commands(self) -> None:
        """Register VFS commands."""
        vfs = self.vfs_layer
        
        def cmd_ls(args, ctx):
            path = args[0] if args else None
            files = vfs.ls(path)
            for f in files:
                type_indicator = '/' if f['type'] == 'folder' else ''
                print(f"{f['name']}{type_indicator}")
            return True
        
        def cmd_cd(args, ctx):
            if not args:
                print("Usage: cd <path>")
                return False
            return vfs.cd(args[0])
        
        def cmd_pwd(args, ctx):
            print(vfs.pwd())
            return True
        
        def cmd_mkdir(args, ctx):
            if not args:
                print("Usage: mkdir <directory>")
                return False
            return vfs.mkdir(args[0])
        
        def cmd_rmdir(args, ctx):
            if not args:
                print("Usage: rmdir <directory>")
                return False
            return vfs.rmdir(args[0])
        
        def cmd_cat(args, ctx):
            if not args:
                print("Usage: cat <file>")
                return False
            content = vfs.cat(args[0])
            if content:
                print(content)
                return True
            return False
        
        def cmd_rm(args, ctx):
            if not args:
                print("Usage: rm <file>")
                return False
            return vfs.rm(args[0])
        
        def cmd_cp(args, ctx):
            if len(args) < 2:
                print("Usage: cp <source> <dest>")
                return False
            return vfs.cp(args[0], args[1])
        
        def cmd_mv(args, ctx):
            if len(args) < 2:
                print("Usage: mv <source> <dest>")
                return False
            return vfs.mv(args[0], args[1])
        
        def cmd_touch(args, ctx):
            if not args:
                print("Usage: touch <file>")
                return False
            return vfs.write(args[0], "")
        
        def cmd_tree(args, ctx):
            path = args[0] if args else None
            vfs.tree(path)
            return True
        
        def cmd_find(args, ctx):
            if not args:
                print("Usage: find <pattern>")
                return False
            results = vfs.search(args[0])
            for r in results:
                print(r['path'])
            return True
        
        # Register commands
        self.registry.register("ls", cmd_ls, "List directory contents", "ls [path]", "filesystem", ["dir"])
        self.registry.register("cd", cmd_cd, "Change directory", "cd <path>", "filesystem")
        self.registry.register("pwd", cmd_pwd, "Print working directory", "pwd", "filesystem")
        self.registry.register("mkdir", cmd_mkdir, "Create directory", "mkdir <directory>", "filesystem")
        self.registry.register("rmdir", cmd_rmdir, "Remove directory", "rmdir <directory>", "filesystem")
        self.registry.register("cat", cmd_cat, "Display file contents", "cat <file>", "filesystem")
        self.registry.register("rm", cmd_rm, "Remove file", "rm <file>", "filesystem", ["del"])
        self.registry.register("cp", cmd_cp, "Copy file", "cp <source> <dest>", "filesystem", ["copy"])
        self.registry.register("mv", cmd_mv, "Move file", "mv <source> <dest>", "filesystem", ["move"])
        self.registry.register("touch", cmd_touch, "Create empty file", "touch <file>", "filesystem")
        self.registry.register("tree", cmd_tree, "Show directory tree", "tree [path]", "filesystem")
        self.registry.register("find", cmd_find, "Find files", "find <pattern>", "filesystem", ["search"])
    
    def _register_process_commands(self) -> None:
        """Register process commands."""
        proc = self.process_layer
        
        def cmd_ps(args, ctx):
            processes = proc.ps()
            print(f"{'PID':>5} {'NAME':20} {'STATE':12} {'OWNER':10} {'CPU':>8}")
            print("-" * 60)
            for p in processes:
                print(f"{p['pid']:>5} {p['name']:20} {p['state']:12} {p['owner']:10} {p['cpu_time']:>8.2f}s")
            return True
        
        def cmd_kill(args, ctx):
            if not args:
                print("Usage: kill <pid>")
                return False
            try:
                pid = int(args[0])
                owner = ctx.user_layer.whoami() if ctx.user_layer else None
                return proc.kill(pid, owner)
            except ValueError:
                print("Invalid PID")
                return False
        
        def cmd_top(args, ctx):
            limit = int(args[0]) if args else 10
            processes = proc.top(limit)
            print(f"{'PID':>5} {'NAME':20} {'CPU':>10} {'STATE':12}")
            print("-" * 50)
            for p in processes:
                print(f"{p['pid']:>5} {p['name']:20} {p['cpu_time']:>10.2f}s {p['state']:12}")
            return True
        
        # Register commands
        self.registry.register("ps", cmd_ps, "List processes", "ps", "process")
        self.registry.register("kill", cmd_kill, "Terminate process", "kill <pid>", "process")
        self.registry.register("top", cmd_top, "Show top processes", "top [limit]", "process")
    
    def _register_user_commands(self) -> None:
        """Register user commands."""
        users = self.user_layer
        
        def cmd_whoami(args, ctx):
            username = users.whoami()
            if username:
                print(username)
                return True
            print("Not logged in")
            return False
        
        def cmd_adduser(args, ctx):
            if len(args) < 2:
                print("Usage: adduser <username> <password>")
                return False
            from users import UserRole
            return users.adduser(args[0], args[1], UserRole.USER)
        
        def cmd_deluser(args, ctx):
            if not args:
                print("Usage: deluser <username>")
                return False
            return users.deluser(args[0])
        
        def cmd_passwd(args, ctx):
            if len(args) < 2:
                print("Usage: passwd <username> <new_password>")
                return False
            return users.passwd(args[0], args[1])
        
        def cmd_users(args, ctx):
            user_list = users.listusers()
            print(f"{'USERNAME':15} {'ROLE':10} {'LOGINS':>8} {'ACTIVE':>8}")
            print("-" * 45)
            for u in user_list:
                active = "Yes" if u['is_active'] else "No"
                print(f"{u['username']:15} {u['role']:10} {u['login_count']:>8} {active:>8}")
            return True
        
        # Register commands
        self.registry.register("whoami", cmd_whoami, "Show current user", "whoami", "user")
        self.registry.register("adduser", cmd_adduser, "Create user", "adduser <username> <password>", "user")
        self.registry.register("deluser", cmd_deluser, "Delete user", "deluser <username>", "user")
        self.registry.register("passwd", cmd_passwd, "Change password", "passwd <username> <password>", "user")
        self.registry.register("users", cmd_users, "List users", "users", "user")
    
    def _register_device_commands(self) -> None:
        """Register device commands."""
        devices = self.device_layer
        
        def cmd_devices(args, ctx):
            device_list = devices.manager.list_devices()
            print(f"{'NAME':20} {'TYPE':15} {'STATUS':10}")
            print("-" * 50)
            for d in device_list:
                status = d.status()
                print(f"{status['name']:20} {status['type']:15} {status['status']:10}")
            return True
        
        def cmd_battery(args, ctx):
            info = devices.check_battery()
            if info:
                print(f"Battery: {info.get('percent', 'N/A')}%")
                print(f"Charging: {info.get('charging', False)}")
                return True
            print("Battery information not available")
            return False
        
        # Register commands
        self.registry.register("devices", cmd_devices, "List devices", "devices", "device")
        self.registry.register("battery", cmd_battery, "Show battery status", "battery", "device")
    
    def _register_system_mgmt_commands(self) -> None:
        """Register system management commands."""
        if not self.system_layer:
            return
        
        sys_layer = self.system_layer
        
        def cmd_printenv(args, ctx):
            env_vars = sys_layer.env_manager.list_all()
            for key, value in sorted(env_vars.items()):
                print(f"{key}={value}")
            return True
        
        def cmd_setenv(args, ctx):
            if not args or '=' not in args[0]:
                print("Usage: setenv VAR=value")
                return False
            parts = args[0].split('=', 1)
            sys_layer.env_manager.set(parts[0], parts[1])
            return True
        
        def cmd_unsetenv(args, ctx):
            if not args:
                print("Usage: unsetenv <VAR>")
                return False
            sys_layer.env_manager.unset(args[0])
            return True
        
        # Register commands
        self.registry.register("printenv", cmd_printenv, "Print environment variables", "printenv", "system")
        self.registry.register("setenv", cmd_setenv, "Set environment variable", "setenv VAR=value", "system")
        self.registry.register("unsetenv", cmd_unsetenv, "Unset environment variable", "unsetenv <VAR>", "system")
    
    def start_interactive(self) -> None:
        """Start interactive shell."""
        self.shell.start()
    
    def execute(self, command: str) -> Any:
        """
        Execute a single command.
        
        Args:
            command: Command string
            
        Returns:
            Command result
        """
        return self.shell.execute_line(command)
    
    def shutdown(self) -> None:
        """Shutdown the shell layer."""
        print("\n" + "=" * 60)
        print("Shutting down Command Shell Layer")
        print("=" * 60)
        
        self.shell.stop()
        
        print("=" * 60)
        print("Command Shell Layer shut down successfully")
        print("=" * 60 + "\n")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
        return False

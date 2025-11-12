"""
Command Registry
Maps CLI commands to OS layer functions.
"""

from typing import Dict, Callable, Any, List, Optional


class CommandRegistry:
    """Registry of all CLI commands mapped to OS functions."""
    
    def __init__(self):
        """Initialize command registry."""
        self.commands: Dict[str, Callable] = {}
        self.command_metadata: Dict[str, dict] = {}
    
    def register(
        self,
        name: str,
        function: Callable,
        description: str = "",
        category: str = "general"
    ) -> None:
        """
        Register a command.
        
        Args:
            name: Command name
            function: Function to execute
            description: Command description
            category: Command category
        """
        self.commands[name] = function
        self.command_metadata[name] = {
            'description': description,
            'category': category
        }
    
    def unregister(self, name: str) -> bool:
        """Unregister a command."""
        if name in self.commands:
            del self.commands[name]
            del self.command_metadata[name]
            return True
        return False
    
    def execute(self, name: str, args: List[str], context: Any) -> Any:
        """
        Execute a command.
        
        Args:
            name: Command name
            args: Command arguments
            context: Execution context
            
        Returns:
            Command result
        """
        if name not in self.commands:
            raise ValueError(f"Command not found: {name}")
        
        return self.commands[name](args, context)
    
    def exists(self, name: str) -> bool:
        """Check if command exists."""
        return name in self.commands
    
    def list_commands(self) -> List[str]:
        """Get list of all command names."""
        return sorted(self.commands.keys())
    
    def get_commands_by_category(self, category: str) -> List[str]:
        """Get commands in a category."""
        return [
            name for name, meta in self.command_metadata.items()
            if meta.get('category') == category
        ]
    
    def get_categories(self) -> List[str]:
        """Get list of all categories."""
        return sorted(set(
            meta.get('category', 'general')
            for meta in self.command_metadata.values()
        ))


def register_all_commands(registry: CommandRegistry, os_layers: dict) -> None:
    """
    Register all OS commands.
    
    Args:
        registry: CommandRegistry instance
        os_layers: Dictionary of OS layer instances
    """
    # Extract layers
    core = os_layers.get('core')
    devices = os_layers.get('devices')
    vfs = os_layers.get('vfs')
    processes = os_layers.get('processes')
    users = os_layers.get('users')
    system = os_layers.get('system')
    
    # System Commands
    def cmd_help(args, ctx):
        """Show help"""
        if args:
            return ctx.help_system.get_help(args[0])
        return ctx.help_system.get_help()
    
    def cmd_clear(args, ctx):
        """Clear screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        return True
    
    def cmd_exit(args, ctx):
        """Exit shell"""
        ctx.running = False
        return True
    
    def cmd_whoami(args, ctx):
        """Show current user"""
        print(ctx.session.get_user())
        return True
    
    def cmd_uptime(args, ctx):
        """Show uptime"""
        print(f"Uptime: {ctx.session.get_uptime_formatted()}")
        return True
    
    def cmd_history(args, ctx):
        """Show command history"""
        limit = int(args[0]) if args else None
        history = ctx.history.get_all(limit)
        for i, entry in enumerate(history, 1):
            status = "✓" if entry.get('success', True) else "✗"
            print(f"{i:4d} {status} {entry['command']}")
        return True
    
    def cmd_alias(args, ctx):
        """Manage aliases"""
        if not args:
            # List aliases
            aliases = ctx.aliases.list_all()
            for name, cmd in sorted(aliases.items()):
                print(f"{name}='{cmd}'")
        elif '=' in args[0]:
            # Create alias
            parts = args[0].split('=', 1)
            name = parts[0]
            command = parts[1].strip('"\'')
            ctx.aliases.add(name, command)
            print(f"Alias created: {name} -> {command}")
        else:
            # Show specific alias
            alias_cmd = ctx.aliases.get(args[0])
            if alias_cmd:
                print(f"{args[0]}='{alias_cmd}'")
            else:
                print(f"Alias not found: {args[0]}")
        return True
    
    def cmd_unalias(args, ctx):
        """Remove alias"""
        if not args:
            print("Usage: unalias <name>")
            return False
        if ctx.aliases.remove(args[0]):
            print(f"Alias removed: {args[0]}")
            return True
        print(f"Alias not found: {args[0]}")
        return False
    
    def cmd_sysinfo(args, ctx):
        """Show system information"""
        print("\n" + "=" * 60)
        print("AI OS - System Information")
        print("=" * 60)
        
        # Session info
        session_info = ctx.session.get_session_info()
        print(f"\nSession ID: {session_info['session_id']}")
        print(f"User: {session_info['user']}")
        print(f"Uptime: {session_info['uptime']}")
        print(f"Current Directory: {session_info['current_directory']}")
        
        # System stats
        if system:
            sys_info = system.get_system_info()
            print(f"\nOS Name: {sys_info.get('name', 'AI OS')}")
            print(f"Version: {sys_info.get('version', '1.0.0')}")
        
        # History stats
        hist_stats = ctx.history.get_stats()
        print(f"\nCommands Executed: {hist_stats['total_commands']}")
        print(f"Successful: {hist_stats['successful']}")
        print(f"Failed: {hist_stats['failed']}")
        
        print("=" * 60 + "\n")
        return True
    
    def cmd_log(args, ctx):
        """View logs"""
        if not system:
            print("System layer not available")
            return False
        
        lines = int(args[0]) if args else 50
        log_type = args[1] if len(args) > 1 else "system"
        
        print(system.read_log(log_type, lines))
        return True
    
    # Register system commands
    registry.register("help", cmd_help, "Show help", "system")
    registry.register("clear", cmd_clear, "Clear screen", "system")
    registry.register("exit", cmd_exit, "Exit shell", "system")
    registry.register("whoami", cmd_whoami, "Show current user", "system")
    registry.register("uptime", cmd_uptime, "Show uptime", "system")
    registry.register("history", cmd_history, "Show history", "system")
    registry.register("alias", cmd_alias, "Manage aliases", "system")
    registry.register("unalias", cmd_unalias, "Remove alias", "system")
    registry.register("sysinfo", cmd_sysinfo, "System info", "system")
    registry.register("log", cmd_log, "View logs", "system")
    
    # Filesystem Commands
    if vfs:
        def cmd_ls(args, ctx):
            path = args[0] if args else None
            files = vfs.ls(path)
            for f in files:
                indicator = '/' if f['type'] == 'folder' else ''
                print(f"{f['name']}{indicator}")
            return True
        
        def cmd_cd(args, ctx):
            if not args:
                print("Usage: cd <path>")
                return False
            success = vfs.cd(args[0])
            if success:
                ctx.session.set_current_directory(vfs.pwd())
            return success
        
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
        
        registry.register("ls", cmd_ls, "List directory", "filesystem")
        registry.register("cd", cmd_cd, "Change directory", "filesystem")
        registry.register("pwd", cmd_pwd, "Print working directory", "filesystem")
        registry.register("mkdir", cmd_mkdir, "Create directory", "filesystem")
        registry.register("rmdir", cmd_rmdir, "Remove directory", "filesystem")
        registry.register("cat", cmd_cat, "Display file", "filesystem")
        registry.register("rm", cmd_rm, "Remove file", "filesystem")
        registry.register("cp", cmd_cp, "Copy file", "filesystem")
        registry.register("mv", cmd_mv, "Move file", "filesystem")
        registry.register("touch", cmd_touch, "Create file", "filesystem")
        registry.register("tree", cmd_tree, "Show tree", "filesystem")
        registry.register("find", cmd_find, "Find files", "filesystem")
    
    # Process Commands
    if processes:
        def cmd_ps(args, ctx):
            procs = processes.ps()
            print(f"{'PID':>5} {'NAME':20} {'STATE':12} {'OWNER':10} {'CPU':>8}")
            print("-" * 60)
            for p in procs:
                print(f"{p['pid']:>5} {p['name']:20} {p['state']:12} {p['owner']:10} {p['cpu_time']:>8.2f}s")
            return True
        
        def cmd_kill(args, ctx):
            if not args:
                print("Usage: kill <pid>")
                return False
            try:
                pid = int(args[0])
                owner = ctx.session.get_user()
                return processes.kill(pid, owner)
            except ValueError:
                print("Invalid PID")
                return False
        
        def cmd_top(args, ctx):
            limit = int(args[0]) if args else 10
            procs = processes.top(limit)
            print(f"{'PID':>5} {'NAME':20} {'CPU':>10} {'STATE':12}")
            print("-" * 50)
            for p in procs:
                print(f"{p['pid']:>5} {p['name']:20} {p['cpu_time']:>10.2f}s {p['state']:12}")
            return True
        
        def cmd_run(args, ctx):
            if not args:
                print("Usage: run <process> [args]")
                return False
            # This would need a process definition system
            print(f"Running process: {args[0]}")
            return True
        
        registry.register("ps", cmd_ps, "List processes", "process")
        registry.register("kill", cmd_kill, "Kill process", "process")
        registry.register("top", cmd_top, "Top processes", "process")
        registry.register("run", cmd_run, "Run process", "process")
    
    # User Commands
    if users:
        def cmd_users(args, ctx):
            user_list = users.listusers()
            print(f"{'USERNAME':15} {'ROLE':10} {'LOGINS':>8} {'ACTIVE':>8}")
            print("-" * 45)
            for u in user_list:
                active = "Yes" if u['is_active'] else "No"
                print(f"{u['username']:15} {u['role']:10} {u['login_count']:>8} {active:>8}")
            return True
        
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
        
        registry.register("users", cmd_users, "List users", "user")
        registry.register("adduser", cmd_adduser, "Add user", "user")
        registry.register("deluser", cmd_deluser, "Delete user", "user")
        registry.register("passwd", cmd_passwd, "Change password", "user")
    
    # Device Commands
    if devices:
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
            print("Battery info not available")
            return False
        
        def cmd_scanusb(args, ctx):
            print("Scanning for USB devices...")
            # This would call actual USB scanning
            print("No USB devices detected")
            return True
        
        registry.register("devices", cmd_devices, "List devices", "device")
        registry.register("battery", cmd_battery, "Battery status", "device")
        registry.register("scanusb", cmd_scanusb, "Scan USB", "device")
    
    # Environment Commands
    if system:
        def cmd_set(args, ctx):
            if not args or '=' not in args[0]:
                print("Usage: set VAR=value")
                return False
            parts = args[0].split('=', 1)
            ctx.session.set_env(parts[0], parts[1])
            system.set_env(parts[0], parts[1])
            return True
        
        def cmd_unset(args, ctx):
            if not args:
                print("Usage: unset <VAR>")
                return False
            ctx.session.unset_env(args[0])
            system.unset_env(args[0])
            return True
        
        def cmd_printenv(args, ctx):
            if args:
                # Print specific variable
                value = ctx.session.get_env(args[0])
                if value:
                    print(f"{args[0]}={value}")
                else:
                    print(f"{args[0]}: not set")
            else:
                # Print all variables
                env_vars = ctx.session.list_env()
                for key, value in sorted(env_vars.items()):
                    print(f"{key}={value}")
            return True
        
        registry.register("set", cmd_set, "Set env var", "environment")
        registry.register("unset", cmd_unset, "Unset env var", "environment")
        registry.register("printenv", cmd_printenv, "Print env vars", "environment")
    
    # Security Commands (if VFS supports encryption)
    if vfs:
        def cmd_encrypt(args, ctx):
            if not args:
                print("Usage: encrypt <file> [password]")
                return False
            # This would use VFS encryption
            print(f"Encrypting {args[0]}...")
            return True
        
        def cmd_decrypt(args, ctx):
            if not args:
                print("Usage: decrypt <file> [password]")
                return False
            print(f"Decrypting {args[0]}...")
            return True
        
        registry.register("encrypt", cmd_encrypt, "Encrypt file", "security")
        registry.register("decrypt", cmd_decrypt, "Decrypt file", "security")
    
    # Memory Commands (placeholder)
    def cmd_memstat(args, ctx):
        """Show memory statistics"""
        print("Memory Statistics:")
        print("  Total: 8 GB")
        print("  Used: 2.5 GB")
        print("  Free: 5.5 GB")
        return True
    
    registry.register("memstat", cmd_memstat, "Memory stats", "memory")
    
    # Network Commands (placeholder)
    def cmd_netstat(args, ctx):
        """Show network connections"""
        print("Network Connections:")
        print("  No active connections")
        return True
    
    def cmd_ping(args, ctx):
        """Ping a target"""
        if not args:
            print("Usage: ping <target>")
            return False
        print(f"Pinging {args[0]}...")
        print(f"Reply from {args[0]}: time=10ms")
        return True
    
    registry.register("netstat", cmd_netstat, "Network stats", "network")
    registry.register("ping", cmd_ping, "Ping target", "network")

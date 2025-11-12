"""
Command Help System
Built-in help and documentation for all commands.
"""

from typing import Dict, List, Optional


class HelpSystem:
    """Provides help documentation for commands."""
    
    def __init__(self):
        """Initialize help system."""
        self.command_docs: Dict[str, dict] = {}
        self._initialize_docs()
    
    def _initialize_docs(self) -> None:
        """Initialize command documentation."""
        self.command_docs = {
            # System Commands
            'help': {
                'description': 'Show available commands and their usage',
                'usage': 'help [command]',
                'examples': ['help', 'help ls', 'help encrypt'],
                'category': 'system'
            },
            'clear': {
                'description': 'Clear the screen',
                'usage': 'clear',
                'examples': ['clear'],
                'category': 'system',
                'aliases': ['cls']
            },
            'exit': {
                'description': 'End the session',
                'usage': 'exit',
                'examples': ['exit'],
                'category': 'system',
                'aliases': ['quit', 'logout']
            },
            'whoami': {
                'description': 'Display current user',
                'usage': 'whoami',
                'examples': ['whoami'],
                'category': 'system'
            },
            'uptime': {
                'description': 'Display how long the OS has been active',
                'usage': 'uptime',
                'examples': ['uptime'],
                'category': 'system'
            },
            'history': {
                'description': 'Show previous commands',
                'usage': 'history [limit]',
                'examples': ['history', 'history 20'],
                'category': 'system'
            },
            'alias': {
                'description': 'Create or list aliases',
                'usage': 'alias [name=command]',
                'examples': ['alias', 'alias ll="ls -la"'],
                'category': 'system'
            },
            'unalias': {
                'description': 'Remove an alias',
                'usage': 'unalias <name>',
                'examples': ['unalias ll'],
                'category': 'system'
            },
            'sysinfo': {
                'description': 'Show overall OS statistics',
                'usage': 'sysinfo',
                'examples': ['sysinfo'],
                'category': 'system'
            },
            'log': {
                'description': 'View last n logs',
                'usage': 'log [n] [type]',
                'examples': ['log 50', 'log 100 error'],
                'category': 'system'
            },
            
            # Filesystem Commands
            'ls': {
                'description': 'List directory contents',
                'usage': 'ls [path]',
                'examples': ['ls', 'ls /home', 'ls -la'],
                'category': 'filesystem',
                'aliases': ['dir']
            },
            'cd': {
                'description': 'Change directory',
                'usage': 'cd <path>',
                'examples': ['cd /home', 'cd ..', 'cd ~'],
                'category': 'filesystem'
            },
            'pwd': {
                'description': 'Print working directory',
                'usage': 'pwd',
                'examples': ['pwd'],
                'category': 'filesystem'
            },
            'mkdir': {
                'description': 'Create directory',
                'usage': 'mkdir <directory>',
                'examples': ['mkdir test', 'mkdir /home/user/docs'],
                'category': 'filesystem',
                'aliases': ['md']
            },
            'rmdir': {
                'description': 'Remove directory',
                'usage': 'rmdir <directory>',
                'examples': ['rmdir test'],
                'category': 'filesystem',
                'aliases': ['rd']
            },
            'cat': {
                'description': 'Display file contents',
                'usage': 'cat <file>',
                'examples': ['cat file.txt', 'cat /etc/config'],
                'category': 'filesystem',
                'aliases': ['type']
            },
            'rm': {
                'description': 'Remove file',
                'usage': 'rm <file>',
                'examples': ['rm file.txt', 'rm /tmp/test'],
                'category': 'filesystem',
                'aliases': ['del']
            },
            'cp': {
                'description': 'Copy file',
                'usage': 'cp <source> <dest>',
                'examples': ['cp file.txt backup.txt'],
                'category': 'filesystem',
                'aliases': ['copy']
            },
            'mv': {
                'description': 'Move/rename file',
                'usage': 'mv <source> <dest>',
                'examples': ['mv old.txt new.txt'],
                'category': 'filesystem',
                'aliases': ['move']
            },
            'touch': {
                'description': 'Create empty file',
                'usage': 'touch <file>',
                'examples': ['touch newfile.txt'],
                'category': 'filesystem'
            },
            'tree': {
                'description': 'Show directory tree',
                'usage': 'tree [path]',
                'examples': ['tree', 'tree /home'],
                'category': 'filesystem'
            },
            'find': {
                'description': 'Find files',
                'usage': 'find <pattern>',
                'examples': ['find *.txt', 'find config'],
                'category': 'filesystem',
                'aliases': ['search']
            },
            
            # Process Commands
            'ps': {
                'description': 'List processes',
                'usage': 'ps',
                'examples': ['ps'],
                'category': 'process',
                'aliases': ['proc']
            },
            'kill': {
                'description': 'Terminate process',
                'usage': 'kill <pid>',
                'examples': ['kill 1234'],
                'category': 'process'
            },
            'top': {
                'description': 'Show top processes',
                'usage': 'top [limit]',
                'examples': ['top', 'top 5'],
                'category': 'process'
            },
            'run': {
                'description': 'Launch a new process',
                'usage': 'run <process> [args]',
                'examples': ['run myapp', 'run script.py arg1'],
                'category': 'process'
            },
            
            # Device Commands
            'devices': {
                'description': 'List connected devices',
                'usage': 'devices',
                'examples': ['devices'],
                'category': 'device'
            },
            'scanusb': {
                'description': 'Detect plugged-in USB devices',
                'usage': 'scanusb',
                'examples': ['scanusb'],
                'category': 'device'
            },
            'mount': {
                'description': 'Mount a drive',
                'usage': 'mount <device> <path>',
                'examples': ['mount /dev/sda1 /mnt'],
                'category': 'device'
            },
            'unmount': {
                'description': 'Unmount a drive',
                'usage': 'unmount <path>',
                'examples': ['unmount /mnt'],
                'category': 'device',
                'aliases': ['umount']
            },
            'battery': {
                'description': 'Show battery status',
                'usage': 'battery',
                'examples': ['battery'],
                'category': 'device'
            },
            
            # Security Commands
            'encrypt': {
                'description': 'Encrypt a file',
                'usage': 'encrypt <file> [password]',
                'examples': ['encrypt secret.txt', 'encrypt data.txt mypass'],
                'category': 'security'
            },
            'decrypt': {
                'description': 'Decrypt a file',
                'usage': 'decrypt <file> [password]',
                'examples': ['decrypt secret.txt.enc'],
                'category': 'security'
            },
            
            # User Commands
            'users': {
                'description': 'List all users',
                'usage': 'users',
                'examples': ['users'],
                'category': 'user'
            },
            'adduser': {
                'description': 'Create a new user',
                'usage': 'adduser <username> <password>',
                'examples': ['adduser alice password123'],
                'category': 'user'
            },
            'deluser': {
                'description': 'Delete a user',
                'usage': 'deluser <username>',
                'examples': ['deluser alice'],
                'category': 'user'
            },
            'passwd': {
                'description': 'Change password',
                'usage': 'passwd <username> <new_password>',
                'examples': ['passwd alice newpass'],
                'category': 'user'
            },
            
            # Environment Commands
            'set': {
                'description': 'Set environment variable',
                'usage': 'set <VAR>=<value>',
                'examples': ['set PATH=/usr/bin', 'set EDITOR=vim'],
                'category': 'environment',
                'aliases': ['setenv']
            },
            'unset': {
                'description': 'Clear environment variable',
                'usage': 'unset <VAR>',
                'examples': ['unset TEMP'],
                'category': 'environment',
                'aliases': ['unsetenv']
            },
            'printenv': {
                'description': 'Print environment variables',
                'usage': 'printenv [VAR]',
                'examples': ['printenv', 'printenv PATH'],
                'category': 'environment',
                'aliases': ['env']
            },
            
            # Memory Commands
            'memstat': {
                'description': 'Show current memory usage',
                'usage': 'memstat',
                'examples': ['memstat'],
                'category': 'memory',
                'aliases': ['mem']
            },
            
            # Network Commands (if implemented)
            'netstat': {
                'description': 'Show network connections',
                'usage': 'netstat',
                'examples': ['netstat'],
                'category': 'network',
                'aliases': ['net']
            },
            'ping': {
                'description': 'Ping a target',
                'usage': 'ping <target>',
                'examples': ['ping google.com', 'ping 192.168.1.1'],
                'category': 'network'
            }
        }
    
    def get_help(self, command: Optional[str] = None) -> str:
        """
        Get help text for a command or all commands.
        
        Args:
            command: Command name (None for all)
            
        Returns:
            Help text
        """
        if command:
            return self._get_command_help(command)
        return self._get_all_help()
    
    def _get_command_help(self, command: str) -> str:
        """Get help for a specific command."""
        if command not in self.command_docs:
            return f"No help available for '{command}'"
        
        doc = self.command_docs[command]
        help_text = f"\n{command} - {doc['description']}\n"
        help_text += f"\nUsage: {doc['usage']}\n"
        
        if 'aliases' in doc:
            help_text += f"Aliases: {', '.join(doc['aliases'])}\n"
        
        if 'examples' in doc:
            help_text += "\nExamples:\n"
            for example in doc['examples']:
                help_text += f"  {example}\n"
        
        return help_text
    
    def _get_all_help(self) -> str:
        """Get help for all commands."""
        categories = {}
        
        # Group by category
        for cmd, doc in self.command_docs.items():
            category = doc.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append((cmd, doc['description']))
        
        # Format output
        help_text = "\n" + "=" * 70 + "\n"
        help_text += "AI OS - Available Commands\n"
        help_text += "=" * 70 + "\n"
        
        for category in sorted(categories.keys()):
            help_text += f"\n{category.upper()}:\n"
            for cmd, desc in sorted(categories[category]):
                help_text += f"  {cmd:15} - {desc}\n"
        
        help_text += "\n" + "=" * 70 + "\n"
        help_text += "Type 'help <command>' for detailed information\n"
        help_text += "=" * 70 + "\n"
        
        return help_text
    
    def add_command(self, name: str, description: str, usage: str, 
                   category: str = 'other', examples: Optional[List[str]] = None,
                   aliases: Optional[List[str]] = None) -> None:
        """Add a new command to help system."""
        self.command_docs[name] = {
            'description': description,
            'usage': usage,
            'category': category,
            'examples': examples or [],
            'aliases': aliases or []
        }
    
    def get_categories(self) -> List[str]:
        """Get list of command categories."""
        return sorted(set(doc.get('category', 'other') for doc in self.command_docs.values()))
    
    def get_commands_by_category(self, category: str) -> List[str]:
        """Get commands in a category."""
        return [
            cmd for cmd, doc in self.command_docs.items()
            if doc.get('category') == category
        ]

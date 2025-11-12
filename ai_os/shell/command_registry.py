"""
Command Registry
Global registry for all system commands with decorator support.
"""

from typing import Dict, Callable, Optional, List, Any
from dataclasses import dataclass


@dataclass
class CommandInfo:
    """Information about a registered command."""
    name: str
    function: Callable
    description: str
    usage: str
    category: str
    aliases: List[str]


class CommandRegistry:
    """Registry for all CLI commands."""
    
    def __init__(self):
        """Initialize command registry."""
        self.commands: Dict[str, CommandInfo] = {}
        self.aliases: Dict[str, str] = {}
        print("[CommandRegistry] Command Registry initialized")
    
    def register(
        self,
        name: str,
        function: Callable,
        description: str = "",
        usage: str = "",
        category: str = "general",
        aliases: Optional[List[str]] = None
    ) -> None:
        """
        Register a command.
        
        Args:
            name: Command name
            function: Function to execute
            description: Command description
            usage: Usage string
            category: Command category
            aliases: List of command aliases
        """
        cmd_info = CommandInfo(
            name=name,
            function=function,
            description=description,
            usage=usage or f"{name} [args]",
            category=category,
            aliases=aliases or []
        )
        
        self.commands[name] = cmd_info
        
        # Register aliases
        if aliases:
            for alias in aliases:
                self.aliases[alias] = name
        
        print(f"[CommandRegistry] Registered command: {name}")
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a command.
        
        Args:
            name: Command name
            
        Returns:
            True if unregistered successfully
        """
        if name in self.commands:
            # Remove aliases
            cmd_info = self.commands[name]
            for alias in cmd_info.aliases:
                self.aliases.pop(alias, None)
            
            del self.commands[name]
            print(f"[CommandRegistry] Unregistered command: {name}")
            return True
        return False
    
    def get_command(self, name: str) -> Optional[CommandInfo]:
        """
        Get command info by name or alias.
        
        Args:
            name: Command name or alias
            
        Returns:
            CommandInfo or None
        """
        # Check if it's an alias
        if name in self.aliases:
            name = self.aliases[name]
        
        return self.commands.get(name)
    
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
        cmd_info = self.get_command(name)
        if not cmd_info:
            print(f"[CommandRegistry] Command not found: {name}")
            return None
        
        try:
            return cmd_info.function(args, context)
        except Exception as e:
            print(f"[CommandRegistry] Error executing {name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def list_commands(self, category: Optional[str] = None) -> List[CommandInfo]:
        """
        List all commands.
        
        Args:
            category: Filter by category
            
        Returns:
            List of CommandInfo objects
        """
        if category:
            return [cmd for cmd in self.commands.values() if cmd.category == category]
        return list(self.commands.values())
    
    def get_categories(self) -> List[str]:
        """Get list of all command categories."""
        categories = set(cmd.category for cmd in self.commands.values())
        return sorted(categories)
    
    def command_exists(self, name: str) -> bool:
        """Check if a command exists."""
        return name in self.commands or name in self.aliases
    
    def get_help(self, name: Optional[str] = None) -> str:
        """
        Get help text for a command or all commands.
        
        Args:
            name: Command name (None for all commands)
            
        Returns:
            Help text
        """
        if name:
            cmd_info = self.get_command(name)
            if not cmd_info:
                return f"Command not found: {name}"
            
            help_text = f"\n{cmd_info.name} - {cmd_info.description}\n"
            help_text += f"Usage: {cmd_info.usage}\n"
            if cmd_info.aliases:
                help_text += f"Aliases: {', '.join(cmd_info.aliases)}\n"
            return help_text
        
        # List all commands by category
        help_text = "\n" + "=" * 60 + "\n"
        help_text += "Available Commands\n"
        help_text += "=" * 60 + "\n"
        
        for category in self.get_categories():
            help_text += f"\n{category.upper()}:\n"
            commands = self.list_commands(category)
            for cmd in sorted(commands, key=lambda x: x.name):
                help_text += f"  {cmd.name:15} - {cmd.description}\n"
        
        help_text += "\n" + "=" * 60 + "\n"
        help_text += "Type 'help <command>' for detailed information\n"
        help_text += "=" * 60 + "\n"
        
        return help_text


# Global registry instance
_global_registry = None


def get_registry() -> CommandRegistry:
    """Get the global command registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = CommandRegistry()
    return _global_registry


def register_command(
    name: str,
    description: str = "",
    usage: str = "",
    category: str = "general",
    aliases: Optional[List[str]] = None
):
    """
    Decorator to register a command.
    
    Args:
        name: Command name
        description: Command description
        usage: Usage string
        category: Command category
        aliases: List of aliases
    
    Example:
        @register_command("ls", "List directory contents", category="filesystem")
        def cmd_ls(args, context):
            ...
    """
    def decorator(func: Callable) -> Callable:
        registry = get_registry()
        registry.register(
            name=name,
            function=func,
            description=description,
            usage=usage,
            category=category,
            aliases=aliases
        )
        return func
    return decorator

"""
OS Connector Service
Interface to the Core OS Layer - manages OS instance and provides access to all layers
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add ai_os to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try to import AIOSMaster - prefer full version, fallback to simple
try:
    from ai_os.os_master import AIOSMaster
    print("✓ Using full AI OS Master")
except ImportError as e:
    print(f"⚠ Could not import full OS Master: {e}")
    print("→ Falling back to simplified OS Master")
    try:
        from ai_os.os_master_simple import AIOSMaster
        print("✓ Using simplified AI OS Master")
    except ImportError as e2:
        print(f"✗ Critical: Could not import any OS Master: {e2}")
        raise


class OSConnector:
    """
    Singleton connector to the Core OS Layer
    Provides thread-safe access to OS functionality
    """
    
    _instance = None
    _os_master = None
    _initialized = False
    _start_time = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OSConnector, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize OS connector (singleton pattern)"""
        if not OSConnector._initialized:
            self._initialize_os()
    
    def _initialize_os(self):
        """Initialize the Core OS Master"""
        try:
            print("Initializing Core OS Layer...")
            OSConnector._os_master = AIOSMaster()
            
            if not OSConnector._os_master.initialize():
                raise Exception("Failed to initialize AI OS")
            
            OSConnector._initialized = True
            OSConnector._start_time = datetime.now()
            print("✓ Core OS Layer initialized successfully")
            
        except Exception as e:
            print(f"✗ Failed to initialize Core OS: {e}")
            raise
    
    def get_os(self) -> AIOSMaster:
        """Get the OS Master instance"""
        if not OSConnector._initialized:
            raise Exception("OS not initialized")
        return OSConnector._os_master
    
    def get_layer(self, layer_name: str):
        """Get a specific OS layer"""
        if not OSConnector._initialized:
            raise Exception("OS not initialized")
        return OSConnector._os_master.get_layer(layer_name)
    
    def execute_command(self, command: str, args: list = None) -> str:
        """Execute a command through the OS
        
        Args:
            command: The command to execute
            args: List of arguments (optional)
            
        Returns:
            Command output as string
        """
        if not OSConnector._initialized:
            raise Exception("OS not initialized")
            
        # Ensure args is a list
        if args is None:
            args = []
        elif isinstance(args, str):
            # If args is a string, split it into a list
            import shlex
            args = shlex.split(args)
            
        # Clean up the command and args
        command = command.strip()
        args = [str(arg).strip('"\'') for arg in args if arg.strip()]
        
        # Special handling for common shell commands
        if command == 'ls' and args:
            # For 'ls' command, join path arguments with spaces
            path = ' '.join(args)
            return OSConnector._os_master.execute_command('ls', [path])
        elif command == 'cat' and args:
            # For 'cat' command, join file arguments with spaces
            files = ' '.join(args)
            return OSConnector._os_master.execute_command('cat', [files])
            
        # For other commands, pass through as is
        return OSConnector._os_master.execute_command(command, args)
    
    def get_all_commands(self) -> Dict:
        """Get all registered commands"""
        if not OSConnector._initialized:
            raise Exception("OS not initialized")
        return OSConnector._os_master.get_all_commands()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        if not OSConnector._initialized:
            return {"error": "OS not initialized"}
        
        uptime = (datetime.now() - OSConnector._start_time).total_seconds()
        
        return {
            "version": OSConnector._os_master.VERSION,
            "initialized": OSConnector._initialized,
            "uptime_seconds": uptime,
            "start_time": OSConnector._start_time.isoformat(),
            "layers": list(OSConnector._os_master.layers.keys()),
            "total_commands": len(OSConnector._os_master.command_registry),
            "config": OSConnector._os_master.config
        }
    
    def reload_os(self):
        """Reload the OS (for hot reload functionality)"""
        if not OSConnector._initialized:
            raise Exception("OS not initialized")
        
        # Shutdown current instance
        OSConnector._os_master.shutdown()
        
        # Reinitialize
        OSConnector._initialized = False
        self._initialize_os()
        
        return {"status": "success", "message": "OS reloaded successfully"}
    
    def shutdown(self):
        """Shutdown the OS"""
        if OSConnector._initialized and OSConnector._os_master:
            OSConnector._os_master.shutdown()
            OSConnector._initialized = False
            OSConnector._os_master = None


# Global instance
os_connector = OSConnector()

# Expose methods at module level
get_os = os_connector.get_os
get_layer = os_connector.get_layer
execute_command = os_connector.execute_command
get_all_commands = os_connector.get_all_commands
get_system_info = os_connector.get_system_info
reload_os = os_connector.reload_os
shutdown = os_connector.shutdown

"""
AI OS Master Controller - Simplified Version
Initializes and manages all OS layers with graceful error handling.
"""

import os
import sys
from typing import Optional, Dict


class AIOSMaster:
    """Master controller for AI OS - manages all layers"""
    
    VERSION = "1.0.0"
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.layers = {}
        self.initialized = False
        self.command_registry = {}
        
        print(f"AI OS v{self.VERSION} - Initializing...")
    
    def _default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'memory': {
                'total_mb': 512,
                'page_size_kb': 4,
                'enable_monitoring': True
            },
            'network': {
                'enable_monitoring': True
            },
            'security': {
                'user_db_path': 'users.json',
                'session_timeout': 3600
            },
            'filesystem': {
                'root_path': './vfs_storage'
            },
            'diagnostics': {
                'enable_monitoring': True
            }
        }
    
    def initialize(self) -> bool:
        """Initialize all OS layers"""
        if self.initialized:
            print("AI OS already initialized")
            return True
        
        try:
            print("\n" + "="*60)
            print("AI OS INITIALIZATION")
            print("="*60)
            
            # Initialize layers in dependency order
            self._init_layer('core', 'ai_os.core.core_master', 'CoreLayer')
            self._init_layer('system', 'ai_os.system.system_master', 'SystemLayer')
            self._init_layer('device', 'ai_os.devices.device_master', 'DeviceLayer')
            self._init_layer('filesystem', 'ai_os.filesystem.vfs_master', 'VFSLayer')
            self._init_layer('memory', 'ai_os.memory_layer.memory_master', 'MemoryLayer')
            self._init_layer('network', 'ai_os.network_layer.network_master', 'NetworkLayer')
            self._init_layer('security', 'ai_os.security_layer.security_master', 'SecurityLayer')
            self._init_layer('process', 'ai_os.processes.process_master', 'ProcessLayer')
            self._init_layer('user', 'ai_os.users.user_master', 'UserLayer')
            self._init_layer('diagnostics', 'ai_os.diagnostics.diagnostics_master', 'DiagnosticsLayer')
            
            # Register all commands
            self._register_commands()
            
            self.initialized = True
            
            print("\n" + "="*60)
            print("AI OS INITIALIZATION COMPLETE")
            print("="*60)
            print(f"Total Layers: {len(self.layers)}")
            print(f"Total Commands: {len(self.command_registry)}")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _init_layer(self, name: str, module_path: str, class_name: str):
        """Initialize a single layer with error handling"""
        try:
            print(f"Initializing {name.title()} Layer...", end=" ", flush=True)
            
            # Suppress layer initialization output
            import io
            import contextlib
            
            # Import the module
            module = __import__(module_path, fromlist=[class_name])
            layer_class = getattr(module, class_name)
            
            # Create instance with suppressed output
            with contextlib.redirect_stdout(io.StringIO()):
                if name == 'memory':
                    mem_config = self.config.get('memory', {})
                    layer = layer_class(
                        total_memory_mb=mem_config.get('total_mb', 512),
                        page_size_kb=mem_config.get('page_size_kb', 4),
                        enable_monitoring=mem_config.get('enable_monitoring', True)
                    )
                elif name == 'network':
                    net_config = self.config.get('network', {})
                    layer = layer_class(
                        enable_monitoring=net_config.get('enable_monitoring', True)
                    )
                elif name == 'security':
                    sec_config = self.config.get('security', {})
                    layer = layer_class(
                        user_db_path=sec_config.get('user_db_path', 'users.json')
                    )
                else:
                    layer = layer_class()
                
                # Initialize if method exists
                if hasattr(layer, 'initialize'):
                    layer.initialize()
            
            self.layers[name] = layer
            print("✓")
            
        except Exception as e:
            print(f"✗ ({e})")
            # Continue with other layers
    
    def _register_commands(self):
        """Register all layer commands"""
        print("\nRegistering commands...")
        
        for layer_name, layer in self.layers.items():
            if hasattr(layer, 'get_commands'):
                try:
                    commands = layer.get_commands()
                    for cmd_name, cmd_info in commands.items():
                        self.command_registry[cmd_name] = {
                            'layer': layer_name,
                            'function': cmd_info['function'],
                            'description': cmd_info.get('description', ''),
                            'usage': cmd_info.get('usage', '')
                        }
                    print(f"  {layer_name}: {len(commands)} commands")
                except Exception as e:
                    print(f"  {layer_name}: Error registering commands ({e})")
    
    def shutdown(self):
        """Shutdown all layers"""
        if not self.initialized:
            return
        
        print("\n" + "="*60)
        print("AI OS SHUTDOWN")
        print("="*60)
        
        # Shutdown in reverse order
        for layer_name in reversed(list(self.layers.keys())):
            try:
                print(f"Shutting down {layer_name}...", end=" ")
                if hasattr(self.layers[layer_name], 'shutdown'):
                    self.layers[layer_name].shutdown()
                print("✓")
            except Exception as e:
                print(f"✗ ({e})")
        
        self.initialized = False
        print("="*60)
        print("AI OS SHUTDOWN COMPLETE")
        print("="*60 + "\n")
    
    def execute_command(self, command: str, args: list = None) -> str:
        """Execute a command"""
        if command not in self.command_registry:
            return f"Command not found: {command}"
        
        try:
            cmd_info = self.command_registry[command]
            result = cmd_info['function'](args)
            return result if result else ""
        except Exception as e:
            return f"Error executing {command}: {e}"
    
    def get_layer(self, layer_name: str):
        """Get a specific layer"""
        return self.layers.get(layer_name)
    
    def get_all_commands(self) -> Dict:
        """Get all registered commands"""
        return self.command_registry
    
    def print_banner(self):
        """Print AI OS banner"""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    AI Operating System                       ║
║                        Version {self.VERSION}                         ║
║                                                              ║
║  A Python-based simulated OS with CLI interface             ║
║  Memory • Network • Security • Diagnostics                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Type 'help' for available commands
Type 'syscheck' to run system diagnostics
Type 'exit' to quit

"""
        print(banner)
    
    def get_system_info(self) -> Dict:
        """Get system information"""
        return {
            'version': self.VERSION,
            'initialized': self.initialized,
            'layers': list(self.layers.keys()),
            'total_commands': len(self.command_registry),
            'config': self.config
        }


def main():
    """Main entry point"""
    # Create and initialize OS
    os_master = AIOSMaster()
    
    if not os_master.initialize():
        print("Failed to initialize AI OS")
        return 1
    
    # Print banner
    os_master.print_banner()
    
    # Example: Run system check if available
    if 'syscheck' in os_master.get_all_commands():
        print("\nRunning system diagnostics...\n")
        result = os_master.execute_command('syscheck')
        print(result)
    
    # Keep running (in production, would start CLI shell here)
    print("\nAI OS is ready. Press Ctrl+C to shutdown.")
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutdown requested...")
        os_master.shutdown()
        return 0


if __name__ == '__main__':
    sys.exit(main())

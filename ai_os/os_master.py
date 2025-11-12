"""
AI OS Master Controller
Initializes and manages all OS layers.
"""

import os
import sys
from typing import Optional, Dict

# Import all layers
try:
    from .core.core_master import CoreLayer
    from .memory_layer.memory_master import MemoryLayer
    from .network_layer.network_master import NetworkLayer
    from .security_layer.security_master import SecurityLayer
    from .filesystem.vfs_master import VFSLayer
    from .processes.process_master import ProcessLayer
    from .devices.device_master import DeviceLayer
    from .system.system_master import SystemLayer
    from .users.user_master import UserLayer
    from .system_simulation_layer import package_manager, git_interface
    from .diagnostics.diagnostics_master import DiagnosticsLayer
except ImportError as e:
    print(f"Warning: Some layers could not be imported: {e}")
    print("Attempting relative imports...")
    try:
        from core.core_master import CoreLayer
        from memory_layer.memory_master import MemoryLayer
        from network_layer.network_master import NetworkLayer
        from security_layer.security_master import SecurityLayer
        from filesystem.vfs_master import VFSLayer
        from processes.process_master import ProcessLayer
        from devices.device_master import DeviceLayer
        from system.system_master import SystemLayer
        from users.user_master import UserLayer
        from diagnostics.diagnostics_master import DiagnosticsLayer
    except ImportError as e2:
        print(f"Critical: Could not import required layers: {e2}")
        sys.exit(1)


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
            self._init_core_layer()
            self._init_system_layer()
            self._init_device_layer()
            self._init_filesystem_layer()
            self._init_memory_layer()
            self._init_network_layer()
            self._init_security_layer()
            self._init_process_layer()
            self._init_user_layer()
            self._init_diagnostics_layer()
            
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
    
    def _init_core_layer(self):
        """Initialize core layer"""
        try:
            print("Initializing Core Layer...", end=" ")
            self.layers['core'] = CoreLayer()
            self.layers['core'].initialize()
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
    
    def _init_system_layer(self):
        """Initialize system layer"""
        try:
            print("Initializing System Layer...", end=" ")
            self.layers['system'] = SystemLayer()
            self.layers['system'].initialize()
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
    
    def _init_device_layer(self):
        """Initialize device layer"""
        try:
            print("Initializing Device Layer...", end=" ")
            self.layers['device'] = DeviceLayer()
            self.layers['device'].initialize()
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
    
    def _init_filesystem_layer(self):
        """Initialize filesystem layer"""
        try:
            print("Initializing Filesystem Layer...", end=" ")
            self.layers['filesystem'] = VFSLayer()
            self.layers['filesystem'].initialize()
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
    
    def _init_memory_layer(self):
        """Initialize memory layer"""
        try:
            print("Initializing Memory Layer...", end=" ")
            mem_config = self.config.get('memory', {})
            self.layers['memory'] = MemoryLayer(
                total_memory_mb=mem_config.get('total_mb', 512),
                page_size_kb=mem_config.get('page_size_kb', 4),
                enable_monitoring=mem_config.get('enable_monitoring', True)
            )
            self.layers['memory'].initialize()
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
    
    def _init_network_layer(self):
        """Initialize network layer"""
        try:
            print("Initializing Network Layer...", end=" ")
            net_config = self.config.get('network', {})
            self.layers['network'] = NetworkLayer(
                enable_monitoring=net_config.get('enable_monitoring', True)
            )
            self.layers['network'].initialize()
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
    
    def _init_security_layer(self):
        """Initialize security layer"""
        try:
            print("Initializing Security Layer...", end=" ")
            sec_config = self.config.get('security', {})
            self.layers['security'] = SecurityLayer(
                user_db_path=sec_config.get('user_db_path', 'users.json')
            )
            self.layers['security'].initialize()
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
    
    def _init_process_layer(self):
        """Initialize process layer"""
        try:
            print("Initializing Process Layer...", end=" ")
            self.layers['process'] = ProcessLayer()
            self.layers['process'].initialize()
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
    
    def _init_user_layer(self):
        """Initialize user layer"""
        try:
            print("Initializing User Layer...", end=" ")
            self.layers['user'] = UserLayer()
            self.layers['user'].initialize()
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
    
    def _init_diagnostics_layer(self):
        """Initialize diagnostics layer"""
        try:
            print("Initializing Diagnostics Layer...", end=" ")
            self.layers['diagnostics'] = DiagnosticsLayer()
            self.layers['diagnostics'].initialize()
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
    
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
            return result
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
    
    # Example: Run system check
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

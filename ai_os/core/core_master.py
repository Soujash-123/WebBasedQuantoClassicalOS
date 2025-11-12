"""
Core Master
Integrates all core components into a unified interface.
"""

from typing import Optional
from .config_manager import ConfigManager
from .system_registry import SystemRegistry
from .event_bus import EventBus


class AIOSCore:
    """
    Main interface for the AI OS Core Layer.
    Integrates ConfigManager, SystemRegistry, and EventBus.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the AI OS Core.
        
        Args:
            config_file: Optional path to configuration file
        """
        print("=" * 60)
        print("Initializing AI OS Core Layer")
        print("=" * 60)
        
        # Initialize core components
        self.config_manager = ConfigManager(config_file)
        self.system_registry = SystemRegistry()
        self.event_bus = EventBus()
        
        # Register core components in the registry
        self.system_registry.register_module("config_manager", self.config_manager)
        self.system_registry.register_module("system_registry", self.system_registry)
        self.system_registry.register_module("event_bus", self.event_bus)
        
        self._is_running = True
        
        print("=" * 60)
        print("AI OS Core Layer initialized successfully")
        print("=" * 60)
    
    def get_config_manager(self) -> ConfigManager:
        """Get the Configuration Manager instance."""
        return self.config_manager
    
    def get_system_registry(self) -> SystemRegistry:
        """Get the System Registry instance."""
        return self.system_registry
    
    def get_event_bus(self) -> EventBus:
        """Get the Event Bus instance."""
        return self.event_bus
    
    def is_running(self) -> bool:
        """Check if the core system is running."""
        return self._is_running
    
    def shutdown(self) -> None:
        """Gracefully shutdown the core system."""
        if not self._is_running:
            print("[AIOSCore] System already shut down")
            return
        
        print("=" * 60)
        print("Shutting down AI OS Core Layer")
        print("=" * 60)
        
        # Publish shutdown event
        self.event_bus.publish("system.shutdown", {"message": "System is shutting down"})
        
        # Save configuration
        self.config_manager.save_config()
        
        # Clear event bus
        self.event_bus.clear_all()
        
        # Clear registry (except core components)
        modules_to_remove = [
            name for name in self.system_registry.list_modules()
            if name not in ["config_manager", "system_registry", "event_bus"]
        ]
        for module_name in modules_to_remove:
            self.system_registry.deregister_module(module_name)
        
        self._is_running = False
        
        print("=" * 60)
        print("AI OS Core Layer shut down successfully")
        print("=" * 60)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
        return False


class CoreLayer(AIOSCore):
    """Alias for AIOSCore to match layer naming convention"""
    
    def initialize(self):
        """Initialize the core layer"""
        return True
    
    def get_commands(self):
        """Get available commands"""
        return {
            'core-status': {
                'function': self.cmd_status,
                'description': 'Show core system status',
                'usage': 'core-status'
            },
            'core-config': {
                'function': self.cmd_config,
                'description': 'Show core configuration',
                'usage': 'core-config'
            }
        }
    
    def cmd_status(self, args=None):
        """Show core status"""
        status = f"""
Core System Status:
  Running: {self.is_running()}
  Registered Modules: {len(self.system_registry.list_modules())}
  Event Subscribers: {len(self.event_bus._subscribers)}
"""
        return status
    
    def cmd_config(self, args=None):
        """Show configuration"""
        config = self.config_manager.get_all()
        result = "Core Configuration:\n"
        for key, value in config.items():
            result += f"  {key}: {value}\n"
        return result

"""
System Master
Integrates configuration, environment, and logging.
"""

from typing import Any, Optional
from .config_manager import ConfigManager
from .env_manager import EnvManager
from .logger import Logger, LogLevel


class SystemLayer:
    """
    Main interface for the System Management Layer.
    Provides configuration, environment variables, and logging.
    """
    
    def __init__(
        self,
        core_layer=None,
        config_file: str = "./system_config.json",
        log_dir: str = "./system/logs",
        log_level: str = "INFO"
    ):
        """
        Initialize the System Layer.
        
        Args:
            core_layer: Core system layer
            config_file: Configuration file path
            log_dir: Log directory path
            log_level: Minimum log level
        """
        print("=" * 60)
        print("Initializing System Management Layer")
        print("=" * 60)
        
        self.core = core_layer
        
        # Initialize config manager
        self.config_manager = ConfigManager(config_file)
        
        # Initialize environment manager
        self.env_manager = EnvManager(self.config_manager)
        
        # Initialize logger
        level_map = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARN": LogLevel.WARN,
            "ERROR": LogLevel.ERROR,
            "CRITICAL": LogLevel.CRITICAL
        }
        min_level = level_map.get(log_level.upper(), LogLevel.INFO)
        self.logger = Logger(log_dir, min_level)
        
        # Log initialization
        self.logger.info("System Management Layer initialized", "SYSTEM")
        
        # Register with core if available
        if self.core:
            self.core.system_registry.register_module("system_layer", self)
            self.event_bus = self.core.event_bus
            self._setup_event_handlers()
        else:
            self.event_bus = None
        
        print("=" * 60)
        print("System Management Layer initialized successfully")
        print("=" * 60)
    
    def _setup_event_handlers(self) -> None:
        """Setup event handlers."""
        if not self.event_bus:
            return
        
        # Subscribe to system events
        self.event_bus.subscribe("system.shutdown", self._on_system_shutdown)
        
        # Log all events
        def log_event(data):
            event_name = data.get('event', 'unknown') if isinstance(data, dict) else 'event'
            self.logger.debug(f"Event: {event_name}", "EVENT")
        
        # Subscribe to all events for logging
        self.event_bus.subscribe("*", log_event)
    
    def _on_system_shutdown(self, data: Any) -> None:
        """Handle system shutdown event."""
        self.logger.info("System shutdown initiated", "SYSTEM")
        self.shutdown()
    
    # Configuration methods
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config_manager.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config_manager.set(key, value)
        self.logger.info(f"Config updated: {key}", "CONFIG")
    
    def save_config(self) -> bool:
        """Save configuration."""
        success = self.config_manager.save()
        if success:
            self.logger.info("Configuration saved", "CONFIG")
        return success
    
    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        self.config_manager.reset()
        self.logger.info("Configuration reset", "CONFIG")
    
    # Environment methods
    
    def get_env(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable."""
        return self.env_manager.get(name, default)
    
    def set_env(self, name: str, value: str, persist: bool = True) -> None:
        """Set environment variable."""
        self.env_manager.set(name, value, persist)
        self.logger.debug(f"Environment variable set: {name}", "ENV")
    
    def unset_env(self, name: str) -> bool:
        """Unset environment variable."""
        success = self.env_manager.unset(name)
        if success:
            self.logger.debug(f"Environment variable unset: {name}", "ENV")
        return success
    
    def list_env(self) -> dict:
        """List all environment variables."""
        return self.env_manager.list_all()
    
    # Logging methods
    
    def log_debug(self, message: str, category: str = "SYSTEM") -> None:
        """Log debug message."""
        self.logger.debug(message, category)
    
    def log_info(self, message: str, category: str = "SYSTEM") -> None:
        """Log info message."""
        self.logger.info(message, category)
    
    def log_warn(self, message: str, category: str = "SYSTEM") -> None:
        """Log warning message."""
        self.logger.warn(message, category)
    
    def log_error(self, message: str, category: str = "SYSTEM") -> None:
        """Log error message."""
        self.logger.error(message, category)
    
    def log_security(self, message: str) -> None:
        """Log security event."""
        self.logger.security(message)
    
    def read_log(
        self,
        log_type: str = "system",
        lines: Optional[int] = None
    ) -> str:
        """Read log file."""
        return self.logger.read_log(log_type, lines)
    
    def clear_log(self, log_type: str = "system") -> bool:
        """Clear log file."""
        return self.logger.clear_log(log_type)
    
    def get_log_stats(self) -> dict:
        """Get log statistics."""
        return self.logger.get_log_stats()
    
    # System commands
    
    def reboot(self) -> None:
        """Reboot the system (restart shell)."""
        self.logger.info("System reboot requested", "SYSTEM")
        print("\n" + "=" * 60)
        print("System Rebooting...")
        print("=" * 60)
        # In a real implementation, this would restart the shell
        print("(Reboot simulation - restart the application)")
    
    def shutdown(self) -> None:
        """Shutdown the system layer."""
        print("\n" + "=" * 60)
        print("Shutting down System Management Layer")
        print("=" * 60)
        
        # Save configuration
        self.save_config()
        
        # Log shutdown
        self.logger.info("System Management Layer shut down", "SYSTEM")
        
        print("=" * 60)
        print("System Management Layer shut down successfully")
        print("=" * 60 + "\n")
    
    def get_system_info(self) -> dict:
        """Get system information."""
        return {
            "name": self.get_config("system.name", "AI OS"),
            "version": self.get_config("system.version", "1.0.0"),
            "config_file": self.config_manager.config_file,
            "log_dir": self.logger.log_dir,
            "log_level": self.logger.min_level.name,
            "env_vars_count": len(self.env_manager.env_vars),
            "log_stats": self.get_log_stats()
        }
    
    def help(self) -> None:
        """Display available system commands."""
        commands = {
            "Configuration": [
                "get_config(key, [default]) - Get configuration value",
                "set_config(key, value) - Set configuration value",
                "save_config() - Save configuration",
                "reset_config() - Reset to defaults"
            ],
            "Environment": [
                "get_env(name, [default]) - Get environment variable",
                "set_env(name, value) - Set environment variable",
                "unset_env(name) - Unset environment variable",
                "list_env() - List all environment variables"
            ],
            "Logging": [
                "log_info(message, [category]) - Log info message",
                "log_warn(message, [category]) - Log warning",
                "log_error(message, [category]) - Log error",
                "log_security(message) - Log security event",
                "read_log([type], [lines]) - Read log file",
                "clear_log([type]) - Clear log file",
                "get_log_stats() - Get log statistics"
            ],
            "System": [
                "reboot() - Reboot system",
                "shutdown() - Shutdown system",
                "get_system_info() - Get system information"
            ]
        }
        
        print("\n" + "=" * 60)
        print("System Management Layer - Available Commands")
        print("=" * 60)
        
        for category, cmds in commands.items():
            print(f"\n{category}:")
            for cmd in cmds:
                print(f"  {cmd}")
        
        print("\n" + "=" * 60)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
        return False

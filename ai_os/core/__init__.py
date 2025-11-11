"""
Core Layer of the Web-Based AI OS
Provides foundational components for the OS backbone.
"""

from .config_manager import ConfigManager
from .system_registry import SystemRegistry
from .event_bus import EventBus
from .core_master import AIOSCore

__all__ = ['ConfigManager', 'SystemRegistry', 'EventBus', 'AIOSCore']

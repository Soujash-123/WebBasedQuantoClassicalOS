"""
Base Device Class
Abstract base class for all device types.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseDevice(ABC):
    """Abstract base class for all devices in the system."""
    
    def __init__(self, name: str, device_type: str):
        """
        Initialize a device.
        
        Args:
            name: Unique name for the device
            device_type: Type of device (e.g., 'io', 'storage', 'network')
        """
        self.name = name
        self.device_type = device_type
        self.status_flag = "disconnected"
        self.metadata: Dict[str, Any] = {}
    
    def initialize(self) -> bool:
        """
        Initialize the device.
        
        Returns:
            True if initialization successful
        """
        self.status_flag = "active"
        print(f"[{self.__class__.__name__}] Device '{self.name}' initialized")
        return True
    
    def shutdown(self) -> bool:
        """
        Shutdown the device.
        
        Returns:
            True if shutdown successful
        """
        self.status_flag = "disconnected"
        print(f"[{self.__class__.__name__}] Device '{self.name}' shut down")
        return True
    
    def status(self) -> Dict[str, Any]:
        """
        Get device status information.
        
        Returns:
            Dictionary containing device status
        """
        return {
            "name": self.name,
            "type": self.device_type,
            "status": self.status_flag,
            "metadata": self.metadata
        }
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata for the device."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from the device."""
        return self.metadata.get(key, default)
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        Get detailed device information.
        Must be implemented by subclasses.
        """
        pass

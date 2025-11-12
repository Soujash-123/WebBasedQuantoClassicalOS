"""
Device Manager
Manages all virtual and real devices in the system.
"""

from typing import Dict, List, Optional, Any
from .base_device import BaseDevice
from .system_device_monitor import SystemDeviceMonitor


class DeviceManager:
    """Central manager for all system devices."""
    
    def __init__(self):
        """Initialize the device manager."""
        self.devices: Dict[str, BaseDevice] = {}
        self.system_monitor = SystemDeviceMonitor()
        self.system_devices_cache: Dict[str, Any] = {}
        print("[DeviceManager] Device Manager initialized")
    
    def register_device(self, device: BaseDevice) -> bool:
        """
        Register a device in the system.
        
        Args:
            device: Device instance to register
            
        Returns:
            True if registration successful
        """
        if device.name in self.devices:
            print(f"[DeviceManager] Warning: Device '{device.name}' already registered")
            return False
        
        self.devices[device.name] = device
        print(f"[DeviceManager] Device '{device.name}' registered")
        return True
    
    def get_device(self, name: str) -> Optional[BaseDevice]:
        """
        Get a registered device by name.
        
        Args:
            name: Name of the device
            
        Returns:
            Device instance or None if not found
        """
        if name not in self.devices:
            print(f"[DeviceManager] Warning: Device '{name}' not found")
            return None
        
        return self.devices[name]
    
    def unregister_device(self, name: str) -> bool:
        """
        Unregister a device from the system.
        
        Args:
            name: Name of the device to unregister
            
        Returns:
            True if unregistration successful
        """
        if name not in self.devices:
            print(f"[DeviceManager] Warning: Device '{name}' not found")
            return False
        
        device = self.devices[name]
        device.shutdown()
        del self.devices[name]
        print(f"[DeviceManager] Device '{name}' unregistered")
        return True
    
    def list_devices(self) -> List[BaseDevice]:
        """
        Get list of all registered devices.
        
        Returns:
            List of device instances
        """
        return list(self.devices.values())
    
    def list_device_names(self) -> List[str]:
        """
        Get list of all registered device names.
        
        Returns:
            List of device names
        """
        return list(self.devices.keys())
    
    def get_device_status(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific device.
        
        Args:
            name: Name of the device
            
        Returns:
            Device status dictionary or None if not found
        """
        device = self.get_device(name)
        if device:
            return device.status()
        return None
    
    def get_all_device_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all registered devices.
        
        Returns:
            List of device status dictionaries
        """
        return [device.status() for device in self.devices.values()]
    
    def refresh_system_devices(self) -> Dict[str, Any]:
        """
        Refresh and get real system device information.
        
        Returns:
            Dictionary with system device information
        """
        print("[DeviceManager] Refreshing system device information...")
        self.system_devices_cache = self.system_monitor.get_system_summary()
        return self.system_devices_cache
    
    def get_system_devices(self) -> Dict[str, Any]:
        """
        Get cached system device information.
        
        Returns:
            Dictionary with system device information
        """
        if not self.system_devices_cache:
            return self.refresh_system_devices()
        return self.system_devices_cache
    
    def get_battery_status(self) -> Optional[Dict[str, Any]]:
        """Get battery status from system monitor."""
        return self.system_monitor.get_battery_status()
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get network status from system monitor."""
        return self.system_monitor.get_network_interfaces()
    
    def get_usb_devices(self) -> Dict[str, Any]:
        """Get USB devices from system monitor."""
        return self.system_monitor.get_usb_devices()
    
    def initialize_all(self) -> int:
        """
        Initialize all registered devices.
        
        Returns:
            Number of devices successfully initialized
        """
        count = 0
        for device in self.devices.values():
            if device.initialize():
                count += 1
        print(f"[DeviceManager] {count}/{len(self.devices)} devices initialized")
        return count
    
    def shutdown_all(self) -> int:
        """
        Shutdown all registered devices.
        
        Returns:
            Number of devices successfully shut down
        """
        count = 0
        for device in self.devices.values():
            if device.shutdown():
                count += 1
        print(f"[DeviceManager] {count}/{len(self.devices)} devices shut down")
        return count
    
    def get_device_count(self) -> int:
        """Get total number of registered devices."""
        return len(self.devices)
    
    def device_exists(self, name: str) -> bool:
        """Check if a device is registered."""
        return name in self.devices

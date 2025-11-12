"""
Device Master
Integrates all device components and provides unified interface.
"""

from typing import Optional, Dict, Any
from .device_manager import DeviceManager
from .console_device import ConsoleDevice
from .storage_device import StorageDevice


class DeviceLayer:
    """
    Main interface for the Device Management Layer.
    Integrates DeviceManager with virtual devices.
    """
    
    def __init__(self, core_system=None, auto_init: bool = True):
        """
        Initialize the Device Layer.
        
        Args:
            core_system: Reference to AIOSCore instance
            auto_init: Whether to automatically initialize default devices
        """
        print("=" * 60)
        print("Initializing Device Management Layer")
        print("=" * 60)
        
        self.core = core_system
        self.manager = DeviceManager()
        
        # Create default virtual devices
        self.console = None
        self.storage = None
        
        if auto_init:
            self._initialize_default_devices()
        
        # Register with core if available
        if self.core:
            self.core.system_registry.register_module("device_layer", self)
            self.event_bus = self.core.event_bus
            self._setup_event_handlers()
        else:
            self.event_bus = None
        
        print("=" * 60)
        print("Device Management Layer initialized successfully")
        print("=" * 60)
    
    def _initialize_default_devices(self) -> None:
        """Initialize default virtual devices."""
        print("\n[DeviceLayer] Initializing default devices...")
        
        # Create and register console device
        self.console = ConsoleDevice("Console")
        self.manager.register_device(self.console)
        self.console.initialize()
        
        # Create and register storage device
        self.storage = StorageDevice("StorageDisk")
        self.manager.register_device(self.storage)
        self.storage.initialize()
        
        print("[DeviceLayer] Default devices initialized\n")
    
    def _setup_event_handlers(self) -> None:
        """Setup event handlers for device events."""
        if not self.event_bus:
            return
        
        # Subscribe to system events
        self.event_bus.subscribe("system.shutdown", self._on_system_shutdown)
        self.event_bus.subscribe("device.refresh", self._on_device_refresh)
    
    def _on_system_shutdown(self, data: Any) -> None:
        """Handle system shutdown event."""
        print("[DeviceLayer] Received shutdown signal, shutting down devices...")
        self.shutdown()
    
    def _on_device_refresh(self, data: Any) -> None:
        """Handle device refresh event."""
        print("[DeviceLayer] Received refresh signal, refreshing system devices...")
        system_info = self.manager.refresh_system_devices()
        
        # Publish device status event
        if self.event_bus:
            self.event_bus.publish("device.status_updated", system_info)
    
    def get_console(self) -> Optional[ConsoleDevice]:
        """Get the console device."""
        return self.console
    
    def get_storage(self) -> Optional[StorageDevice]:
        """Get the storage device."""
        return self.storage
    
    def get_device_manager(self) -> DeviceManager:
        """Get the device manager instance."""
        return self.manager
    
    def scan_system_devices(self) -> Dict[str, Any]:
        """
        Scan and get information about real system devices.
        
        Returns:
            Dictionary with system device information
        """
        print("\n[DeviceLayer] Scanning system devices...")
        system_info = self.manager.refresh_system_devices()
        
        # Publish event if event bus available
        if self.event_bus:
            self.event_bus.publish("device.scan_complete", system_info)
        
        return system_info
    
    def check_battery(self) -> Optional[Dict[str, Any]]:
        """Check battery status."""
        return self.manager.get_battery_status()
    
    def check_network(self) -> Dict[str, Any]:
        """Check network interfaces."""
        return self.manager.get_network_status()
    
    def check_usb(self) -> Dict[str, Any]:
        """Check USB devices."""
        return self.manager.get_usb_devices()
    
    def get_device_summary(self) -> Dict[str, Any]:
        """
        Get summary of all devices (virtual and real).
        
        Returns:
            Dictionary with device summary
        """
        return {
            "virtual_devices": {
                "count": self.manager.get_device_count(),
                "devices": self.manager.get_all_device_status()
            },
            "system_devices": self.manager.get_system_devices()
        }
    
    def publish_device_event(self, event_name: str, data: Any) -> None:
        """
        Publish a device-related event.
        
        Args:
            event_name: Name of the event
            data: Event data
        """
        if self.event_bus:
            full_event_name = f"device.{event_name}"
            self.event_bus.publish(full_event_name, data)
    
    def monitor_battery(self) -> None:
        """Monitor battery and publish events if low."""
        battery = self.check_battery()
        if battery and battery.get("available"):
            percent = battery.get("percent", 100)
            if percent < 20 and not battery.get("charging"):
                self.publish_device_event("battery_low", battery)
                print(f"[DeviceLayer] WARNING: Battery low ({percent}%)")
    
    def shutdown(self) -> None:
        """Shutdown the device layer."""
        print("\n" + "=" * 60)
        print("Shutting down Device Management Layer")
        print("=" * 60)
        
        # Shutdown all devices
        self.manager.shutdown_all()
        
        print("=" * 60)
        print("Device Management Layer shut down successfully")
        print("=" * 60 + "\n")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
        return False

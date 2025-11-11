"""
I/O Master
Integrates input and output handlers into unified interface.
"""

from typing import Optional, Any
from .input_handler import InputHandler
from .output_handler import OutputHandler


class IOLayer:
    """
    Main interface for the Input/Output Layer.
    Integrates InputHandler and OutputHandler.
    """
    
    def __init__(self, core_system=None, device_layer=None):
        """
        Initialize the I/O Layer.
        
        Args:
            core_system: Reference to AIOSCore instance
            device_layer: Reference to DeviceLayer instance
        """
        print("=" * 60)
        print("Initializing I/O Layer")
        print("=" * 60)
        
        self.core = core_system
        self.device_layer = device_layer
        
        # Get console device from device layer
        console = None
        if device_layer:
            console = device_layer.get_console()
        
        # Initialize handlers
        self.input = InputHandler(console)
        self.output = OutputHandler(console)
        
        # Register with core if available
        if self.core:
            self.core.system_registry.register_module("io_layer", self)
            self.event_bus = self.core.event_bus
            self._setup_event_handlers()
        else:
            self.event_bus = None
        
        print("=" * 60)
        print("I/O Layer initialized successfully")
        print("=" * 60)
    
    def _setup_event_handlers(self) -> None:
        """Setup event handlers for I/O events."""
        if not self.event_bus:
            return
        
        # Subscribe to system events
        self.event_bus.subscribe("system.shutdown", self._on_system_shutdown)
        
        # Setup input callback to publish events
        self.input.register_callback("input_received", self._on_input_received)
    
    def _on_system_shutdown(self, data: Any) -> None:
        """Handle system shutdown event."""
        print("[IOLayer] Received shutdown signal")
    
    def _on_input_received(self, input_text: str) -> None:
        """Handle input received event."""
        if self.event_bus:
            self.event_bus.publish("io.input_received", {"text": input_text})
    
    def get_input_handler(self) -> InputHandler:
        """Get the input handler instance."""
        return self.input
    
    def get_output_handler(self) -> OutputHandler:
        """Get the output handler instance."""
        return self.output
    
    def read(self, prompt: str = "> ") -> Optional[str]:
        """
        Read input from user.
        
        Args:
            prompt: Prompt to display
            
        Returns:
            User input or None
        """
        return self.input.read_input(prompt)
    
    def write(self, message: str, end: str = "\n") -> bool:
        """
        Write output to user.
        
        Args:
            message: Message to write
            end: String to append at end
            
        Returns:
            True if successful
        """
        return self.output.write(message, end)
    
    def display(self, data: Any, format_type: str = "auto") -> bool:
        """
        Display data in appropriate format.
        
        Args:
            data: Data to display
            format_type: Format type
            
        Returns:
            True if successful
        """
        return self.output.display(data, format_type)
    
    def print_header(self, title: str, width: int = 60) -> bool:
        """Print a formatted header."""
        return self.output.print_header(title, width)
    
    def print_info(self, message: str) -> bool:
        """Print an info message."""
        return self.output.print_info(message)
    
    def print_success(self, message: str) -> bool:
        """Print a success message."""
        return self.output.print_success(message)
    
    def print_warning(self, message: str) -> bool:
        """Print a warning message."""
        return self.output.print_warning(message)
    
    def print_error(self, message: str) -> bool:
        """Print an error message."""
        return self.output.print_error(message)
    
    def confirm(self, prompt: str = "Confirm? (y/n): ") -> bool:
        """Get user confirmation."""
        return self.input.read_confirmation(prompt)
    
    def clear_screen(self) -> bool:
        """Clear the screen."""
        return self.output.clear()
    
    def display_device_info(self) -> bool:
        """Display device information from device layer."""
        if not self.device_layer:
            self.print_error("Device layer not available")
            return False
        
        self.print_header("Device Information")
        
        # Display virtual devices
        self.output.writeln("\n=== Virtual Devices ===")
        devices = self.device_layer.manager.list_devices()
        for device in devices:
            info = device.get_info()
            self.output.print_dict(info)
            self.output.writeln()
        
        # Display system devices
        self.output.writeln("=== System Devices ===")
        system_info = self.device_layer.manager.get_system_devices()
        if not system_info:
            system_info = self.device_layer.scan_system_devices()
        
        self.output.print_dict(system_info)
        
        return True
    
    def display_battery_status(self) -> bool:
        """Display battery status."""
        if not self.device_layer:
            self.print_error("Device layer not available")
            return False
        
        battery = self.device_layer.check_battery()
        if battery:
            self.print_header("Battery Status", 40)
            self.output.print_dict(battery)
        else:
            self.print_info("No battery information available")
        
        return True
    
    def display_network_status(self) -> bool:
        """Display network status."""
        if not self.device_layer:
            self.print_error("Device layer not available")
            return False
        
        network = self.device_layer.check_network()
        if network:
            self.print_header("Network Status", 40)
            self.output.print_dict(network)
        else:
            self.print_info("No network information available")
        
        return True
    
    def display_usb_devices(self) -> bool:
        """Display USB devices."""
        if not self.device_layer:
            self.print_error("Device layer not available")
            return False
        
        usb = self.device_layer.check_usb()
        if usb:
            self.print_header("USB Devices", 40)
            self.output.print_dict(usb)
        else:
            self.print_info("No USB information available")
        
        return True
    
    def shutdown(self) -> None:
        """Shutdown the I/O layer."""
        print("\n[IOLayer] Shutting down I/O Layer")
        self.input.clear_history()
        self.output.clear_history()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
        return False

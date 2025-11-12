"""
Comprehensive Example Usage - Layers 1, 2, and 3
Demonstrates Core Layer, Device Layer, and I/O Layer integration.
"""

from core import AIOSCore
from devices import DeviceLayer
from io_layer import IOLayer


def demo_core_layer(core):
    """Demonstrate core layer functionality."""
    print("\n" + "=" * 60)
    print("DEMO 1: Core Layer")
    print("=" * 60)
    
    # Configuration
    print("\n--- Configuration Management ---")
    core.config_manager.set_config("system.name", "AI OS Demo")
    core.config_manager.set_config("system.version", "2.0.0")
    core.config_manager.set_config("features.devices", True)
    core.config_manager.set_config("features.io", True)
    
    print(f"System Name: {core.config_manager.get_config('system.name')}")
    print(f"System Version: {core.config_manager.get_config('system.version')}")
    
    # Registry
    print("\n--- System Registry ---")
    modules = core.system_registry.list_modules()
    print(f"Registered Modules: {modules}")
    
    # Event Bus
    print("\n--- Event Bus ---")
    
    def demo_handler(data):
        print(f"  [Event Handler] Received: {data}")
    
    core.event_bus.subscribe("demo.event", demo_handler)
    core.event_bus.publish("demo.event", {"message": "Core layer working!"})


def demo_device_layer(devices, io_layer):
    """Demonstrate device layer functionality."""
    print("\n" + "=" * 60)
    print("DEMO 2: Device Layer")
    print("=" * 60)
    
    # Virtual Devices
    print("\n--- Virtual Devices ---")
    io_layer.output.writeln("Registered Virtual Devices:")
    for device in devices.manager.list_devices():
        info = device.get_info()
        io_layer.output.writeln(f"  - {info['name']} ({info['type']}): {info['status']}")
    
    # Console Device
    print("\n--- Console Device ---")
    console = devices.get_console()
    if console:
        console.write("Console device is working!")
        console_info = console.get_info()
        io_layer.output.writeln(f"Console encoding: {console_info.get('encoding')}")
    
    # Storage Device
    print("\n--- Storage Device ---")
    storage = devices.get_storage()
    if storage:
        # Write a file
        storage.write_file("demo.txt", "Hello from AI OS!")
        storage.write_file("config.txt", "system=active\nmode=demo")
        
        # List files
        files = storage.list_files()
        io_layer.output.writeln(f"Files in storage: {files}")
        
        # Read a file
        content = storage.read_file("demo.txt")
        io_layer.output.writeln(f"Content of demo.txt: {content}")
        
        # Storage info
        storage_info = storage.get_info()
        io_layer.output.writeln(f"Storage usage: {storage_info['usage_percent']}%")
    
    # System Devices
    print("\n--- System Device Detection ---")
    io_layer.output.writeln("Scanning system devices...")
    system_info = devices.scan_system_devices()
    
    # Platform info
    io_layer.output.writeln("\nPlatform:")
    io_layer.output.writeln(f"  System: {system_info['platform']['system']}")
    io_layer.output.writeln(f"  Machine: {system_info['platform']['machine']}")
    io_layer.output.writeln(f"  Processor: {system_info['platform']['processor']}")
    
    # Battery info
    battery = system_info['battery']
    io_layer.output.writeln("\nBattery:")
    if battery.get('available'):
        io_layer.output.writeln(f"  Charge: {battery.get('percent')}%")
        io_layer.output.writeln(f"  Charging: {battery.get('charging')}")
    else:
        io_layer.output.writeln(f"  {battery.get('message', 'Not available')}")
    
    # Network info
    network = system_info['network']
    io_layer.output.writeln("\nNetwork:")
    if network.get('available'):
        io_layer.output.writeln(f"  Interfaces: {network.get('count')}")
        if network.get('interfaces'):
            for name, info in list(network['interfaces'].items())[:2]:
                io_layer.output.writeln(f"    - {name}: {'UP' if info['is_up'] else 'DOWN'}")
    else:
        io_layer.output.writeln(f"  {network.get('message', 'Not available')}")
    
    # USB info
    usb = system_info['usb']
    io_layer.output.writeln("\nUSB Devices:")
    if usb.get('available'):
        io_layer.output.writeln(f"  Count: {usb.get('count')}")
        if usb.get('devices'):
            for device in usb['devices'][:3]:
                io_layer.output.writeln(f"    - {device}")
    else:
        io_layer.output.writeln(f"  {usb.get('message', 'Not available')}")
    
    # CPU info
    cpu = system_info['cpu']
    io_layer.output.writeln("\nCPU:")
    if cpu.get('available'):
        io_layer.output.writeln(f"  Cores: {cpu.get('physical_cores')} physical, {cpu.get('logical_cores')} logical")
        io_layer.output.writeln(f"  Usage: {cpu.get('usage_percent')}%")
    else:
        io_layer.output.writeln(f"  {cpu.get('message', 'Limited info')}")
    
    # Memory info
    memory = system_info['memory']
    io_layer.output.writeln("\nMemory:")
    if memory.get('available'):
        total_gb = memory.get('total', 0) / (1024**3)
        used_gb = memory.get('used', 0) / (1024**3)
        io_layer.output.writeln(f"  Total: {total_gb:.2f} GB")
        io_layer.output.writeln(f"  Used: {used_gb:.2f} GB ({memory.get('percent')}%)")
    else:
        io_layer.output.writeln(f"  {memory.get('message', 'Not available')}")


def demo_io_layer(io_layer):
    """Demonstrate I/O layer functionality."""
    print("\n" + "=" * 60)
    print("DEMO 3: I/O Layer")
    print("=" * 60)
    
    # Output formatting
    print("\n--- Output Formatting ---")
    io_layer.print_info("This is an informational message")
    io_layer.print_success("Operation completed successfully")
    io_layer.print_warning("This is a warning message")
    
    # Headers and separators
    print("\n--- Headers and Separators ---")
    io_layer.print_header("Sample Header", 50)
    io_layer.output.writeln("Content goes here")
    io_layer.output.print_separator(50)
    
    # Dictionary display
    print("\n--- Dictionary Display ---")
    sample_data = {
        "user": "admin",
        "permissions": ["read", "write", "execute"],
        "settings": {
            "theme": "dark",
            "language": "en"
        }
    }
    io_layer.display(sample_data)
    
    # List display
    print("\n--- List Display ---")
    tasks = ["Initialize system", "Load modules", "Start services"]
    io_layer.output.print_list(tasks, numbered=True)
    
    # Table display
    print("\n--- Table Display ---")
    headers = ["Name", "Status", "CPU%"]
    rows = [
        ["Process1", "Running", "15.2"],
        ["Process2", "Stopped", "0.0"],
        ["Process3", "Running", "8.5"]
    ]
    io_layer.output.print_table(headers, rows)


def demo_integration(core, devices, io_layer):
    """Demonstrate integration between all layers."""
    print("\n" + "=" * 60)
    print("DEMO 4: Layer Integration")
    print("=" * 60)
    
    # Event-driven communication
    print("\n--- Event-Driven Communication ---")
    
    def on_device_scan(data):
        io_layer.print_info("Device scan completed via event!")
    
    core.event_bus.subscribe("device.scan_complete", on_device_scan)
    devices.scan_system_devices()
    
    # Config-driven behavior
    print("\n--- Config-Driven Behavior ---")
    if core.config_manager.get_config("features.devices"):
        io_layer.print_success("Device features are enabled")
    
    if core.config_manager.get_config("features.io"):
        io_layer.print_success("I/O features are enabled")
    
    # Module interaction
    print("\n--- Module Interaction ---")
    io_layer.output.writeln("Modules registered in system:")
    for module_name in core.system_registry.list_modules():
        io_layer.output.writeln(f"  ✓ {module_name}")
    
    # Device status via I/O
    print("\n--- Device Status Display ---")
    io_layer.print_header("All Device Status", 50)
    for device in devices.manager.list_devices():
        status = device.status()
        io_layer.output.writeln(f"  {status['name']}: {status['status']}")


def demo_commands(devices, io_layer):
    """Demonstrate command-like operations."""
    print("\n" + "=" * 60)
    print("DEMO 5: Command Operations")
    print("=" * 60)
    
    # Simulate 'devices list' command
    print("\n--- Command: devices list ---")
    io_layer.print_header("Registered Devices", 50)
    for device in devices.manager.list_devices():
        info = device.get_info()
        io_layer.output.writeln(f"{info['name']:15} {info['type']:10} {info['status']}")
    
    # Simulate 'devices status battery' command
    print("\n--- Command: devices status battery ---")
    battery = devices.check_battery()
    if battery:
        io_layer.display(battery)
    
    # Simulate 'devices usb scan' command
    print("\n--- Command: devices usb scan ---")
    usb = devices.check_usb()
    if usb:
        io_layer.display(usb)
    
    # Simulate 'storage list' command
    print("\n--- Command: storage list ---")
    storage = devices.get_storage()
    if storage:
        files = storage.list_files()
        if files:
            io_layer.output.print_list(files, bullet="•")
        else:
            io_layer.print_info("No files in storage")


def main():
    """Main demonstration function."""
    print("\n" + "#" * 60)
    print("# AI OS - Comprehensive Layer Demonstration")
    print("# Layers 1-3: Core, Device, and I/O")
    print("#" * 60)
    
    # Initialize all layers
    core = AIOSCore("demo_config.json")
    devices = DeviceLayer(core)
    io_layer = IOLayer(core, devices)
    
    # Run demonstrations
    demo_core_layer(core)
    demo_device_layer(devices, io_layer)
    demo_io_layer(io_layer)
    demo_integration(core, devices, io_layer)
    demo_commands(devices, io_layer)
    
    # Shutdown
    print("\n" + "=" * 60)
    print("DEMO Complete - Shutting Down")
    print("=" * 60)
    
    io_layer.shutdown()
    devices.shutdown()
    core.shutdown()
    
    print("\n" + "#" * 60)
    print("# All Demonstrations Complete!")
    print("#" * 60 + "\n")


if __name__ == "__main__":
    main()

# AI OS - Layers 1, 2, and 3

Complete implementation of the foundational layers of the Web-Based AI Operating System.

## 📋 Overview

This implementation includes:

1. **Layer 1 - Core Layer**: Configuration management, system registry, and event bus
2. **Layer 2 - Device Layer**: Virtual and real device management with system monitoring
3. **Layer 3 - I/O Layer**: Input/output handling with formatted display capabilities

## 📁 Project Structure

```
ai_os/
│
├── core/                          # Layer 1: Core System
│   ├── __init__.py
│   ├── config_manager.py          # Configuration management
│   ├── system_registry.py         # Module registry
│   ├── event_bus.py               # Event messaging
│   └── core_master.py             # Core integration
│
├── devices/                       # Layer 2: Device Management
│   ├── __init__.py
│   ├── base_device.py             # Abstract device class
│   ├── console_device.py          # Virtual console
│   ├── storage_device.py          # Virtual storage
│   ├── system_device_monitor.py   # Real device detection
│   ├── device_manager.py          # Device registry
│   └── device_master.py           # Device layer integration
│
├── io_layer/                      # Layer 3: Input/Output
│   ├── __init__.py
│   ├── input_handler.py           # Input operations
│   ├── output_handler.py          # Output formatting
│   └── io_master.py               # I/O integration
│
├── tests/manual_tests/
│   ├── test_core_layer.py         # Core layer tests
│   ├── test_devices.py            # Device layer tests
│   └── test_io.py                 # I/O layer tests
│
├── example_usage.py               # Core layer demo
├── example_usage_layers.py        # All layers demo
├── requirements.txt               # Optional dependencies
└── README_LAYERS.md               # This file
```

## 🚀 Quick Start

### Installation

```bash
cd ai_os

# Optional: Install psutil for full system device detection
pip install -r requirements.txt
```

**Note**: The system works without any dependencies, but `psutil` is recommended for full device monitoring capabilities.

### Running Examples

```bash
# Run comprehensive demo of all layers
python example_usage_layers.py

# Run core layer demo only
python example_usage.py
```

### Running Tests

```bash
# Test all layers
python tests/manual_tests/test_core_layer.py
python tests/manual_tests/test_devices.py
python tests/manual_tests/test_io.py
```

## 📚 Layer Details

### Layer 1: Core Layer

**Purpose**: Foundational OS-level backbone

**Components**:
- `ConfigManager`: Global configuration with JSON persistence
- `SystemRegistry`: Module tracking and management
- `EventBus`: Inter-module communication
- `AIOSCore`: Unified core interface

**Example**:
```python
from core import AIOSCore

core = AIOSCore("config.json")
core.config_manager.set_config("system.mode", "production")
core.event_bus.publish("system.ready", {"status": "ok"})
core.shutdown()
```

### Layer 2: Device Layer

**Purpose**: Manage virtual and real system devices

**Virtual Devices**:
- `ConsoleDevice`: Terminal I/O operations
- `StorageDevice`: Virtual file storage

**System Monitoring**:
- Battery status (charge %, charging state)
- Network interfaces (IPs, status)
- USB devices (connected devices)
- CPU info (cores, usage)
- Memory info (total, used, available)
- Disk info (partitions, usage)

**Example**:
```python
from core import AIOSCore
from devices import DeviceLayer

core = AIOSCore()
devices = DeviceLayer(core)

# Use virtual devices
devices.console.write("Hello!")
devices.storage.write_file("test.txt", "content")

# Check system devices
battery = devices.check_battery()
network = devices.check_network()
usb = devices.check_usb()

devices.shutdown()
core.shutdown()
```

### Layer 3: I/O Layer

**Purpose**: Handle input/output operations with formatting

**Features**:
- Formatted output (headers, tables, lists, dicts)
- Input handling (single line, multiline, confirmations)
- Message types (info, success, warning, error)
- Device information display
- History tracking

**Example**:
```python
from core import AIOSCore
from devices import DeviceLayer
from io_layer import IOLayer

core = AIOSCore()
devices = DeviceLayer(core)
io_layer = IOLayer(core, devices)

# Output
io_layer.print_header("Welcome")
io_layer.print_success("System initialized")
io_layer.display({"key": "value"})

# Input (interactive)
# user_input = io_layer.read("Enter command: ")
# confirmed = io_layer.confirm("Continue?")

io_layer.shutdown()
devices.shutdown()
core.shutdown()
```

## 🔧 Command-Like Operations

The system supports command-like operations:

### Device Commands

```python
# devices list
for device in devices.manager.list_devices():
    print(device.status())

# devices status battery
battery = devices.check_battery()
io_layer.display(battery)

# devices usb scan
usb = devices.check_usb()
io_layer.display(usb)

# devices status network
network = devices.check_network()
io_layer.display(network)
```

### Storage Commands

```python
storage = devices.get_storage()

# storage list
files = storage.list_files()

# storage write <filename>
storage.write_file("file.txt", "content")

# storage read <filename>
content = storage.read_file("file.txt")

# storage delete <filename>
storage.delete_file("file.txt")

# storage info
info = storage.get_info()
```

## 🎯 Key Features

### Event-Driven Architecture

```python
# Subscribe to events
def on_device_scan(data):
    print(f"Devices scanned: {data}")

core.event_bus.subscribe("device.scan_complete", on_device_scan)

# Publish events
devices.scan_system_devices()  # Triggers event
```

### Configuration Management

```python
# Set configurations
core.config_manager.set_config("features.ai", True)
core.config_manager.set_config("system.theme", "dark")

# Get configurations
ai_enabled = core.config_manager.get_config("features.ai")

# Save to file
core.config_manager.save_config()
```

### Module Registry

```python
# Register custom modules
class MyModule:
    def process(self):
        return "processed"

my_mod = MyModule()
core.system_registry.register_module("my_module", my_mod)

# Retrieve modules
module = core.system_registry.get_module("my_module")
```

## 🔍 System Device Detection

### With psutil (Recommended)

When `psutil` is installed, you get full system monitoring:

- ✅ Battery percentage and charging status
- ✅ Network interfaces with IP addresses
- ✅ CPU cores and usage percentage
- ✅ Memory total, used, and available
- ✅ Disk partitions and usage
- ✅ USB device detection (platform-specific)

### Without psutil

The system still works but with limited capabilities:

- ⚠️ Basic platform information only
- ⚠️ USB detection via system commands (may not work on all platforms)
- ⚠️ No battery, CPU, memory, or disk monitoring

## 📊 Example Output

```
============================================================
Initializing AI OS Core Layer
============================================================
[ConfigManager] No config file found. Starting with empty config.
[SystemRegistry] System Registry initialized
[EventBus] Event Bus initialized
============================================================

============================================================
Initializing Device Management Layer
============================================================
[DeviceManager] Device Manager initialized
[ConsoleDevice] Console initialized
[StorageDevice] StorageDisk initialized
============================================================

Platform:
  System: Windows
  Machine: AMD64
  Processor: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel

Battery:
  Charge: 85%
  Charging: True

Network:
  Interfaces: 3
    - Ethernet: UP
    - Wi-Fi: UP

USB Devices:
  Count: 5
    - USB Composite Device
    - USB Input Device
    - USB Mass Storage Device
```

## 🧪 Testing

All layers include comprehensive manual tests:

```bash
# Core layer tests
python tests/manual_tests/test_core_layer.py

# Device layer tests
python tests/manual_tests/test_devices.py

# I/O layer tests
python tests/manual_tests/test_io.py
```

Tests verify:
- Component initialization
- Core functionality
- Integration between layers
- Error handling
- Graceful shutdown

## 🔄 Integration Example

```python
from core import AIOSCore
from devices import DeviceLayer
from io_layer import IOLayer

# Initialize all layers
core = AIOSCore("config.json")
devices = DeviceLayer(core)
io_layer = IOLayer(core, devices)

# Use integrated functionality
io_layer.print_header("System Status")

# Display device information
for device in devices.manager.list_devices():
    io_layer.display(device.get_info())

# Display system information
system_info = devices.scan_system_devices()
io_layer.display(system_info['platform'])

# Graceful shutdown
io_layer.shutdown()
devices.shutdown()
core.shutdown()
```

## 🎓 Next Steps

With Layers 1-3 complete, you can now build:

1. **Command Layer**: CLI interface for user commands
2. **Process Layer**: Task and process management
3. **AI Layer**: AI model integration and inference
4. **API Layer**: REST/WebSocket APIs
5. **Web Layer**: Frontend interface

## 📝 Notes

- All layers use only Python standard library except for optional `psutil`
- System is designed to be modular and extensible
- Event bus enables loose coupling between components
- Configuration system supports nested keys with dot notation
- Device layer gracefully handles missing system features
- I/O layer provides rich formatting options

## 🐛 Troubleshooting

**Issue**: System device detection not working
- **Solution**: Install psutil: `pip install psutil`

**Issue**: USB devices not detected
- **Solution**: USB detection is platform-specific and may require admin privileges

**Issue**: Virtual storage files not persisting
- **Solution**: Check write permissions in the `virtual_storage` directory

**Issue**: Events not firing
- **Solution**: Ensure event bus is properly initialized and subscriptions are set before publishing

## 📄 License

Part of the AI OS project.

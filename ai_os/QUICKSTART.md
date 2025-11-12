# AI OS - Quick Start Guide

## 🚀 Installation & Setup

### Step 1: Navigate to the Project

```bash
cd c:\Users\SBA859\Downloads\WebBasedOS-college\ai_os
```

### Step 2: Install Optional Dependencies (Recommended)

```bash
# Install psutil for full system device detection
pip install psutil
```

**Note**: The system works without psutil, but you'll get limited device detection.

### Step 3: Run the Demo

```bash
# Run comprehensive demo of all 3 layers
python example_usage_layers.py
```

## 🧪 Run Tests

```bash
# Test Core Layer
python tests\manual_tests\test_core_layer.py

# Test Device Layer
python tests\manual_tests\test_devices.py

# Test I/O Layer
python tests\manual_tests\test_io.py
```

## 📖 What You Get

### ✅ Layer 1: Core System
- Configuration management with JSON persistence
- System registry for module tracking
- Event bus for inter-module communication

### ✅ Layer 2: Device Management
- **Virtual Devices**:
  - Console (terminal I/O)
  - Storage (virtual file system)
  
- **Real Device Detection**:
  - Battery status
  - Network interfaces
  - USB devices
  - CPU info
  - Memory info
  - Disk info

### ✅ Layer 3: I/O Layer
- Formatted output (headers, tables, lists, dicts)
- Input handling (prompts, confirmations, choices)
- Message types (info, success, warning, error)
- Device information display

## 💡 Quick Examples

### Example 1: Basic Usage

```python
from core import AIOSCore
from devices import DeviceLayer
from io_layer import IOLayer

# Initialize
core = AIOSCore()
devices = DeviceLayer(core)
io = IOLayer(core, devices)

# Use it
io.print_header("Welcome to AI OS")
io.print_success("System initialized!")

# Cleanup
io.shutdown()
devices.shutdown()
core.shutdown()
```

### Example 2: Device Operations

```python
# Check battery
battery = devices.check_battery()
io.display(battery)

# List USB devices
usb = devices.check_usb()
io.display(usb)

# Use virtual storage
storage = devices.get_storage()
storage.write_file("test.txt", "Hello World")
content = storage.read_file("test.txt")
print(content)
```

### Example 3: Configuration

```python
# Set config
core.config_manager.set_config("app.name", "My App")
core.config_manager.set_config("app.version", "1.0")

# Get config
name = core.config_manager.get_config("app.name")

# Save to file
core.config_manager.save_config()
```

### Example 4: Events

```python
# Subscribe to event
def on_scan(data):
    print(f"Scan complete: {data}")

core.event_bus.subscribe("device.scan_complete", on_scan)

# Trigger event
devices.scan_system_devices()
```

## 🎯 Command-Like Operations

```python
# List devices
for device in devices.manager.list_devices():
    print(device.status())

# Check battery
battery = devices.check_battery()

# Check network
network = devices.check_network()

# Scan USB
usb = devices.check_usb()

# Storage operations
storage = devices.get_storage()
storage.write_file("file.txt", "content")
files = storage.list_files()
content = storage.read_file("file.txt")
```

## 📊 Expected Output

When you run `example_usage_layers.py`, you'll see:

```
############################################################
# AI OS - Comprehensive Layer Demonstration
# Layers 1-3: Core, Device, and I/O
############################################################

============================================================
Initializing AI OS Core Layer
============================================================
[ConfigManager] No config file found. Starting with empty config.
[SystemRegistry] System Registry initialized
[EventBus] Event Bus initialized
...

============================================================
DEMO 1: Core Layer
============================================================
...

============================================================
DEMO 2: Device Layer
============================================================
...

Platform:
  System: Windows
  Machine: AMD64
  Processor: ...

Battery:
  Charge: 85%
  Charging: True

Network:
  Interfaces: 3
...
```

## 🔍 Troubleshooting

### psutil not installed?
```bash
pip install psutil
```

### Tests failing?
Make sure you're in the correct directory:
```bash
cd c:\Users\SBA859\Downloads\WebBasedOS-college\ai_os
```

### Import errors?
Check that all `__init__.py` files exist in:
- `core/`
- `devices/`
- `io_layer/`
- `tests/`
- `tests/manual_tests/`

## 📚 Next Steps

1. ✅ Run the demos to see everything in action
2. ✅ Run the tests to verify functionality
3. ✅ Read `README_LAYERS.md` for detailed documentation
4. 🔜 Build additional layers (Command, Process, AI, API, Web)

## 🎓 Learn More

- **Core Layer**: See `core/` directory
- **Device Layer**: See `devices/` directory
- **I/O Layer**: See `io_layer/` directory
- **Tests**: See `tests/manual_tests/` directory
- **Examples**: See `example_usage_layers.py`

## ✨ Features Highlights

- 🔧 **Zero dependencies** for core functionality
- 📦 **Optional psutil** for enhanced device detection
- 🎯 **Event-driven** architecture
- 💾 **Persistent** configuration
- 🖥️ **Cross-platform** device detection
- 📝 **Rich formatting** for output
- 🧪 **Comprehensive** test suite
- 🔌 **Modular** and extensible design

---

**Ready to build the future of AI Operating Systems!** 🚀

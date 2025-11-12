from core import AIOSCore
from devices import DeviceLayer
from io_layer import IOLayer

# Initialize all layers
core = AIOSCore()
devices = DeviceLayer(core)
io = IOLayer(core, devices)

# Use them
io.print_header("System Ready")
battery = devices.check_battery()
io.display(battery)
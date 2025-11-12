"""
Manual Test Suite for I/O Layer
Tests input and output handling.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core import AIOSCore
from devices import DeviceLayer
from io_layer import IOLayer


def test_io_initialization():
    """Test I/O layer initialization."""
    print("\n" + "=" * 60)
    print("TEST: I/O Layer Initialization")
    print("=" * 60)
    
    core = AIOSCore("test_io_config.json")
    devices = DeviceLayer(core)
    io_layer = IOLayer(core, devices)
    
    assert io_layer.input is not None, "Input handler not initialized"
    assert io_layer.output is not None, "Output handler not initialized"
    
    print("✓ I/O layer initialized successfully")
    
    io_layer.shutdown()
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_io_config.json"):
        os.remove("test_io_config.json")
    
    print("\n✓ I/O Initialization tests PASSED")


def test_output_handler():
    """Test output handler functionality."""
    print("\n" + "=" * 60)
    print("TEST: Output Handler")
    print("=" * 60)
    
    core = AIOSCore("test_output_config.json")
    devices = DeviceLayer(core)
    io_layer = IOLayer(core, devices)
    
    output = io_layer.get_output_handler()
    
    # Test basic write
    print("\n[TEST] Testing basic write...")
    result = output.write("Test message")
    assert result, "Write failed"
    print("✓ Basic write works")
    
    # Test formatted output
    print("\n[TEST] Testing formatted output...")
    output.print_info("This is an info message")
    output.print_success("This is a success message")
    output.print_warning("This is a warning message")
    print("✓ Formatted output works")
    
    # Test header
    print("\n[TEST] Testing header...")
    output.print_header("Test Header", 40)
    print("✓ Header works")
    
    # Test separator
    print("\n[TEST] Testing separator...")
    output.print_separator(40)
    print("✓ Separator works")
    
    # Test dict printing
    print("\n[TEST] Testing dict printing...")
    test_dict = {"key1": "value1", "key2": {"nested": "value"}}
    output.print_dict(test_dict)
    print("✓ Dict printing works")
    
    # Test list printing
    print("\n[TEST] Testing list printing...")
    test_list = ["item1", "item2", "item3"]
    output.print_list(test_list, numbered=True)
    print("✓ List printing works")
    
    io_layer.shutdown()
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_output_config.json"):
        os.remove("test_output_config.json")
    
    print("\n✓ Output Handler tests PASSED")


def test_io_integration():
    """Test I/O layer integration with devices."""
    print("\n" + "=" * 60)
    print("TEST: I/O Integration")
    print("=" * 60)
    
    core = AIOSCore("test_integration_config.json")
    devices = DeviceLayer(core)
    io_layer = IOLayer(core, devices)
    
    # Test device info display
    print("\n[TEST] Testing device info display...")
    io_layer.print_header("Device Information Test")
    
    # Display virtual device info
    console = devices.get_console()
    if console:
        io_layer.output.print_dict(console.get_info())
    
    storage = devices.get_storage()
    if storage:
        io_layer.output.print_dict(storage.get_info())
    
    print("✓ Device info display works")
    
    # Test system device display
    print("\n[TEST] Testing system device display...")
    system_info = devices.scan_system_devices()
    io_layer.output.writeln("\nPlatform Info:")
    io_layer.output.print_dict(system_info['platform'])
    print("✓ System device display works")
    
    io_layer.shutdown()
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_integration_config.json"):
        os.remove("test_integration_config.json")
    
    print("\n✓ I/O Integration tests PASSED")


def test_io_display_methods():
    """Test I/O display methods."""
    print("\n" + "=" * 60)
    print("TEST: I/O Display Methods")
    print("=" * 60)
    
    core = AIOSCore("test_display_config.json")
    devices = DeviceLayer(core)
    io_layer = IOLayer(core, devices)
    
    # Test display method with different types
    print("\n[TEST] Testing display with dict...")
    test_data = {"name": "test", "value": 123}
    io_layer.display(test_data)
    print("✓ Dict display works")
    
    print("\n[TEST] Testing display with list...")
    test_list = ["item1", "item2", "item3"]
    io_layer.display(test_list)
    print("✓ List display works")
    
    print("\n[TEST] Testing display with string...")
    io_layer.display("Simple string message")
    print("✓ String display works")
    
    io_layer.shutdown()
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_display_config.json"):
        os.remove("test_display_config.json")
    
    print("\n✓ I/O Display Methods tests PASSED")


def run_all_tests():
    """Run all I/O layer tests."""
    print("\n" + "#" * 60)
    print("# I/O LAYER - MANUAL TEST SUITE")
    print("#" * 60)
    
    try:
        test_io_initialization()
        test_output_handler()
        test_io_integration()
        test_io_display_methods()
        
        print("\n" + "#" * 60)
        print("# ALL I/O TESTS PASSED ✓")
        print("#" * 60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        print("\n" + "#" * 60)
        print("# TESTS FAILED ✗")
        print("#" * 60 + "\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()

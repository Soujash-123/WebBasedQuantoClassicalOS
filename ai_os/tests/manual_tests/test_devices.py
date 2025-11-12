"""
Manual Test Suite for Device Management Layer
Tests virtual devices and system device detection.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core import AIOSCore
from devices import DeviceLayer


def test_device_initialization():
    """Test device layer initialization."""
    print("\n" + "=" * 60)
    print("TEST: Device Layer Initialization")
    print("=" * 60)
    
    core = AIOSCore("test_device_config.json")
    devices = DeviceLayer(core)
    
    assert devices.console is not None, "Console device not initialized"
    assert devices.storage is not None, "Storage device not initialized"
    assert devices.manager.get_device_count() >= 2, "Not enough devices registered"
    
    print("✓ Device layer initialized successfully")
    
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_device_config.json"):
        os.remove("test_device_config.json")
    
    print("\n✓ Device Initialization tests PASSED")


def test_console_device():
    """Test console device functionality."""
    print("\n" + "=" * 60)
    print("TEST: Console Device")
    print("=" * 60)
    
    core = AIOSCore("test_console_config.json")
    devices = DeviceLayer(core)
    
    console = devices.get_console()
    assert console is not None, "Console device not available"
    
    # Test write
    print("\n[TEST] Testing console write...")
    result = console.write("Test message")
    assert result, "Console write failed"
    print("✓ Console write works")
    
    # Test status
    print("\n[TEST] Testing console status...")
    status = console.status()
    assert status["status"] == "active", "Console not active"
    print(f"✓ Console status: {status}")
    
    # Test info
    print("\n[TEST] Testing console info...")
    info = console.get_info()
    assert "name" in info, "Console info incomplete"
    print(f"✓ Console info: {info}")
    
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_console_config.json"):
        os.remove("test_console_config.json")
    
    print("\n✓ Console Device tests PASSED")


def test_storage_device():
    """Test storage device functionality."""
    print("\n" + "=" * 60)
    print("TEST: Storage Device")
    print("=" * 60)
    
    core = AIOSCore("test_storage_config.json")
    devices = DeviceLayer(core)
    
    storage = devices.get_storage()
    assert storage is not None, "Storage device not available"
    
    # Test write file
    print("\n[TEST] Testing file write...")
    result = storage.write_file("test.txt", "Hello, World!")
    assert result, "File write failed"
    print("✓ File write successful")
    
    # Test read file
    print("\n[TEST] Testing file read...")
    content = storage.read_file("test.txt")
    assert content == "Hello, World!", "File content mismatch"
    print("✓ File read successful")
    
    # Test list files
    print("\n[TEST] Testing file listing...")
    files = storage.list_files()
    assert "test.txt" in files, "File not in list"
    print(f"✓ Files: {files}")
    
    # Test file info
    print("\n[TEST] Testing file info...")
    info = storage.get_file_info("test.txt")
    assert info is not None, "File info not available"
    print(f"✓ File info: {info}")
    
    # Test delete file
    print("\n[TEST] Testing file delete...")
    result = storage.delete_file("test.txt")
    assert result, "File delete failed"
    assert not storage.file_exists("test.txt"), "File still exists"
    print("✓ File delete successful")
    
    # Test storage info
    print("\n[TEST] Testing storage info...")
    storage_info = storage.get_info()
    assert "capacity" in storage_info, "Storage info incomplete"
    print(f"✓ Storage info: {storage_info}")
    
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_storage_config.json"):
        os.remove("test_storage_config.json")
    if os.path.exists("virtual_storage"):
        import shutil
        shutil.rmtree("virtual_storage", ignore_errors=True)
    
    print("\n✓ Storage Device tests PASSED")


def test_system_device_monitor():
    """Test system device monitoring."""
    print("\n" + "=" * 60)
    print("TEST: System Device Monitor")
    print("=" * 60)
    
    core = AIOSCore("test_monitor_config.json")
    devices = DeviceLayer(core)
    
    print("\n[TEST] Testing system device scan...")
    system_info = devices.scan_system_devices()
    
    assert "platform" in system_info, "Platform info missing"
    assert "battery" in system_info, "Battery info missing"
    assert "network" in system_info, "Network info missing"
    assert "usb" in system_info, "USB info missing"
    assert "cpu" in system_info, "CPU info missing"
    assert "memory" in system_info, "Memory info missing"
    
    print("✓ System device scan successful")
    
    print("\n[TEST] Platform Info:")
    print(f"  System: {system_info['platform']['system']}")
    print(f"  Machine: {system_info['platform']['machine']}")
    
    print("\n[TEST] Battery Status:")
    battery = system_info['battery']
    if battery.get('available'):
        print(f"  Percent: {battery.get('percent')}%")
        print(f"  Charging: {battery.get('charging')}")
    else:
        print(f"  {battery.get('message', 'Not available')}")
    
    print("\n[TEST] Network Interfaces:")
    network = system_info['network']
    if network.get('available'):
        print(f"  Count: {network.get('count')}")
    else:
        print(f"  {network.get('message', 'Not available')}")
    
    print("\n[TEST] USB Devices:")
    usb = system_info['usb']
    if usb.get('available'):
        print(f"  Count: {usb.get('count')}")
        if usb.get('devices'):
            for device in usb['devices'][:3]:  # Show first 3
                print(f"    - {device}")
    else:
        print(f"  {usb.get('message', 'Not available')}")
    
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_monitor_config.json"):
        os.remove("test_monitor_config.json")
    
    print("\n✓ System Device Monitor tests PASSED")


def test_device_manager():
    """Test device manager functionality."""
    print("\n" + "=" * 60)
    print("TEST: Device Manager")
    print("=" * 60)
    
    core = AIOSCore("test_manager_config.json")
    devices = DeviceLayer(core)
    
    manager = devices.get_device_manager()
    
    print("\n[TEST] Testing device listing...")
    device_list = manager.list_devices()
    assert len(device_list) >= 2, "Not enough devices"
    print(f"✓ Devices: {[d.name for d in device_list]}")
    
    print("\n[TEST] Testing device status...")
    all_status = manager.get_all_device_status()
    assert len(all_status) >= 2, "Status list incomplete"
    for status in all_status:
        print(f"  - {status['name']}: {status['status']}")
    print("✓ Device status retrieved")
    
    print("\n[TEST] Testing device retrieval...")
    console = manager.get_device("Console")
    assert console is not None, "Console not found"
    assert console.name == "Console", "Wrong device retrieved"
    print("✓ Device retrieval works")
    
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_manager_config.json"):
        os.remove("test_manager_config.json")
    
    print("\n✓ Device Manager tests PASSED")


def run_all_tests():
    """Run all device layer tests."""
    print("\n" + "#" * 60)
    print("# DEVICE MANAGEMENT LAYER - MANUAL TEST SUITE")
    print("#" * 60)
    
    try:
        test_device_initialization()
        test_console_device()
        test_storage_device()
        test_system_device_monitor()
        test_device_manager()
        
        print("\n" + "#" * 60)
        print("# ALL DEVICE TESTS PASSED ✓")
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

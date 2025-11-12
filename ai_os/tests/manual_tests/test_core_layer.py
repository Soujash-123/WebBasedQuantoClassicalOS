"""
Manual Test Suite for AI OS Core Layer
Simple print-based tests to verify core functionality.
"""

import sys
import os

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core import ConfigManager, SystemRegistry, EventBus, AIOSCore


def test_config_manager():
    """Test Configuration Manager functionality."""
    print("\n" + "=" * 60)
    print("TEST: Configuration Manager")
    print("=" * 60)
    
    config = ConfigManager("test_config.json")
    
    # Test setting and getting config
    print("\n[TEST] Setting configuration values...")
    config.set_config("test.key1", "value1")
    config.set_config("test.nested.key2", "value2")
    config.set_config("test.number", 42)
    
    print("\n[TEST] Getting configuration values...")
    assert config.get_config("test.key1") == "value1", "Failed to get simple key"
    assert config.get_config("test.nested.key2") == "value2", "Failed to get nested key"
    assert config.get_config("test.number") == 42, "Failed to get number value"
    assert config.get_config("nonexistent", "default") == "default", "Failed to return default"
    print("✓ All config get/set operations passed")
    
    # Test saving config
    print("\n[TEST] Saving configuration...")
    success = config.save_config()
    assert success, "Failed to save config"
    print("✓ Configuration saved successfully")
    
    # Test loading config
    print("\n[TEST] Loading configuration...")
    config2 = ConfigManager("test_config.json")
    assert config2.get_config("test.key1") == "value1", "Failed to load saved config"
    print("✓ Configuration loaded successfully")
    
    # Cleanup
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
    
    print("\n✓ Configuration Manager tests PASSED")


def test_system_registry():
    """Test System Registry functionality."""
    print("\n" + "=" * 60)
    print("TEST: System Registry")
    print("=" * 60)
    
    registry = SystemRegistry()
    
    # Test module registration
    print("\n[TEST] Registering modules...")
    class DummyModule:
        def __init__(self, name):
            self.name = name
    
    module1 = DummyModule("Module1")
    module2 = DummyModule("Module2")
    
    assert registry.register_module("module1", module1), "Failed to register module1"
    assert registry.register_module("module2", module2), "Failed to register module2"
    assert not registry.register_module("module1", module1), "Allowed duplicate registration"
    print("✓ Module registration works correctly")
    
    # Test module retrieval
    print("\n[TEST] Retrieving modules...")
    retrieved = registry.get_module("module1")
    assert retrieved is module1, "Failed to retrieve correct module"
    assert retrieved.name == "Module1", "Retrieved module has wrong data"
    assert registry.get_module("nonexistent") is None, "Should return None for nonexistent module"
    print("✓ Module retrieval works correctly")
    
    # Test module listing
    print("\n[TEST] Listing modules...")
    modules = registry.list_modules()
    assert "module1" in modules and "module2" in modules, "Module list incomplete"
    assert len(modules) == 2, "Wrong number of modules"
    print(f"✓ Module list correct: {modules}")
    
    # Test deregistration
    print("\n[TEST] Deregistering modules...")
    assert registry.deregister_module("module1"), "Failed to deregister module"
    assert not registry.is_registered("module1"), "Module still registered after deregistration"
    assert registry.is_registered("module2"), "Wrong module deregistered"
    print("✓ Module deregistration works correctly")
    
    print("\n✓ System Registry tests PASSED")


def test_event_bus():
    """Test Event Bus functionality."""
    print("\n" + "=" * 60)
    print("TEST: Event Bus")
    print("=" * 60)
    
    bus = EventBus()
    
    # Test event subscription and publishing
    print("\n[TEST] Event subscription and publishing...")
    received_data = []
    
    def handler1(data):
        received_data.append(("handler1", data))
    
    def handler2(data):
        received_data.append(("handler2", data))
    
    assert bus.subscribe("test.event", handler1), "Failed to subscribe handler1"
    assert bus.subscribe("test.event", handler2), "Failed to subscribe handler2"
    assert not bus.subscribe("test.event", handler1), "Allowed duplicate subscription"
    print("✓ Event subscription works correctly")
    
    print("\n[TEST] Publishing events...")
    count = bus.publish("test.event", {"message": "test"})
    assert count == 2, f"Expected 2 subscribers notified, got {count}"
    assert len(received_data) == 2, "Not all handlers received the event"
    assert received_data[0][1]["message"] == "test", "Handler received wrong data"
    print("✓ Event publishing works correctly")
    
    # Test unsubscription
    print("\n[TEST] Unsubscribing from events...")
    received_data.clear()
    assert bus.unsubscribe("test.event", handler1), "Failed to unsubscribe"
    count = bus.publish("test.event", {"message": "test2"})
    assert count == 1, "Wrong number of subscribers after unsubscribe"
    assert len(received_data) == 1, "Wrong number of handlers called"
    print("✓ Event unsubscription works correctly")
    
    # Test event listing
    print("\n[TEST] Listing events...")
    events = bus.list_events()
    assert "test.event" in events, "Event not in list"
    print(f"✓ Event list correct: {events}")
    
    print("\n✓ Event Bus tests PASSED")


def test_aios_core():
    """Test integrated AI OS Core."""
    print("\n" + "=" * 60)
    print("TEST: AI OS Core Integration")
    print("=" * 60)
    
    # Test initialization
    print("\n[TEST] Initializing AI OS Core...")
    core = AIOSCore("test_core_config.json")
    assert core.is_running(), "Core should be running after initialization"
    print("✓ Core initialization successful")
    
    # Test component access
    print("\n[TEST] Accessing core components...")
    config = core.get_config_manager()
    registry = core.get_system_registry()
    bus = core.get_event_bus()
    
    assert config is not None, "Failed to get config manager"
    assert registry is not None, "Failed to get system registry"
    assert bus is not None, "Failed to get event bus"
    print("✓ All core components accessible")
    
    # Test integrated functionality
    print("\n[TEST] Testing integrated functionality...")
    
    # Config
    config.set_config("test.value", "integrated")
    assert config.get_config("test.value") == "integrated", "Config integration failed"
    
    # Registry
    class TestModule:
        pass
    test_mod = TestModule()
    registry.register_module("test_module", test_mod)
    assert registry.get_module("test_module") is test_mod, "Registry integration failed"
    
    # Event Bus
    event_received = []
    def test_handler(data):
        event_received.append(data)
    
    bus.subscribe("test.integration", test_handler)
    bus.publish("test.integration", "test_data")
    assert len(event_received) == 1, "Event bus integration failed"
    
    print("✓ Integrated functionality works correctly")
    
    # Test shutdown
    print("\n[TEST] Testing graceful shutdown...")
    core.shutdown()
    assert not core.is_running(), "Core should not be running after shutdown"
    print("✓ Graceful shutdown successful")
    
    # Cleanup
    if os.path.exists("test_core_config.json"):
        os.remove("test_core_config.json")
    
    print("\n✓ AI OS Core Integration tests PASSED")


def run_all_tests():
    """Run all manual tests."""
    print("\n" + "#" * 60)
    print("# AI OS CORE LAYER - MANUAL TEST SUITE")
    print("#" * 60)
    
    try:
        test_config_manager()
        test_system_registry()
        test_event_bus()
        test_aios_core()
        
        print("\n" + "#" * 60)
        print("# ALL TESTS PASSED ✓")
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

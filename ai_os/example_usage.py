"""
Example Usage of the AI OS Core Layer
Demonstrates initialization, module registration, configuration, and event handling.
"""

from core import AIOSCore


class MockModule:
    """A simple mock module for demonstration purposes."""
    
    def __init__(self, name: str):
        self.name = name
        print(f"[MockModule] {name} initialized")
    
    def process_data(self, data):
        """Process some data."""
        print(f"[MockModule] {self.name} processing data: {data}")
        return f"Processed by {self.name}: {data}"


def event_handler(data):
    """Sample event handler function."""
    print(f"[EventHandler] Received event data: {data}")


def main():
    """Main demonstration function."""
    print("\n" + "=" * 60)
    print("AI OS Core Layer - Example Usage")
    print("=" * 60 + "\n")
    
    # Initialize the core system
    core = AIOSCore(config_file="ai_os_config.json")
    
    print("\n" + "-" * 60)
    print("1. Configuration Management Demo")
    print("-" * 60)
    
    # Set some configuration values
    core.config_manager.set_config("system.mode", "development")
    core.config_manager.set_config("system.version", "1.0.0")
    core.config_manager.set_config("ai.model", "gpt-4")
    core.config_manager.set_config("runtime.max_threads", 4)
    
    # Get configuration values
    mode = core.config_manager.get_config("system.mode")
    version = core.config_manager.get_config("system.version")
    model = core.config_manager.get_config("ai.model")
    
    print(f"\nCurrent Configuration:")
    print(f"  - System Mode: {mode}")
    print(f"  - System Version: {version}")
    print(f"  - AI Model: {model}")
    
    # Save configuration
    core.config_manager.save_config()
    
    print("\n" + "-" * 60)
    print("2. Module Registration Demo")
    print("-" * 60)
    
    # Create and register mock modules
    data_processor = MockModule("DataProcessor")
    task_manager = MockModule("TaskManager")
    
    core.system_registry.register_module("data_processor", data_processor)
    core.system_registry.register_module("task_manager", task_manager)
    
    # List all registered modules
    print(f"\nRegistered Modules: {core.system_registry.list_modules()}")
    
    # Retrieve and use a module
    processor = core.system_registry.get_module("data_processor")
    if processor:
        result = processor.process_data("Sample Data")
        print(f"Result: {result}")
    
    print("\n" + "-" * 60)
    print("3. Event Bus Demo")
    print("-" * 60)
    
    # Subscribe to events
    core.event_bus.subscribe("data.processed", event_handler)
    core.event_bus.subscribe("task.completed", event_handler)
    
    # Create a custom event handler
    def custom_handler(data):
        print(f"[CustomHandler] Task completed with status: {data.get('status')}")
    
    core.event_bus.subscribe("task.completed", custom_handler)
    
    # Publish events
    print("\nPublishing events:")
    core.event_bus.publish("data.processed", {"item": "user_data", "count": 100})
    core.event_bus.publish("task.completed", {"task_id": "T123", "status": "success"})
    
    # List active events
    print(f"\nActive Events: {core.event_bus.list_events()}")
    
    print("\n" + "-" * 60)
    print("4. System Status")
    print("-" * 60)
    
    print(f"\nSystem Running: {core.is_running()}")
    print(f"Total Modules: {len(core.system_registry.list_modules())}")
    print(f"Active Events: {len(core.event_bus.list_events())}")
    
    # Shutdown the system
    print("\n" + "-" * 60)
    print("5. Graceful Shutdown")
    print("-" * 60 + "\n")
    
    core.shutdown()
    
    print(f"\nSystem Running After Shutdown: {core.is_running()}")
    
    print("\n" + "=" * 60)
    print("Example Usage Complete")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

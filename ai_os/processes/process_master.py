"""
Process Master
Integrates process management with other OS layers.
"""

from typing import Optional, Callable, Any
from .process import Process
from .scheduler import Scheduler
from .process_manager import ProcessManager


class ProcessLayer:
    """
    Main interface for the Process Management Layer.
    Integrates with Core, Device, VFS, and I/O layers.
    """
    
    def __init__(
        self,
        core_system=None,
        device_layer=None,
        vfs_layer=None,
        io_layer=None,
        algorithm: str = "fifo"
    ):
        """
        Initialize the Process Layer.
        
        Args:
            core_system: Reference to AIOSCore instance
            device_layer: Reference to DeviceLayer instance
            vfs_layer: Reference to VirtualFileSystem instance
            io_layer: Reference to IOLayer instance
            algorithm: Scheduling algorithm ('fifo' or 'round_robin')
        """
        print("=" * 60)
        print("Initializing Process Management Layer")
        print("=" * 60)
        
        self.core = core_system
        self.device_layer = device_layer
        self.vfs_layer = vfs_layer
        self.io_layer = io_layer
        
        # Initialize scheduler
        self.scheduler = Scheduler(algorithm=algorithm)
        
        # Initialize process manager
        self.process_manager = ProcessManager(self.scheduler)
        
        # Start scheduler
        self.scheduler.start()
        
        # Register with core if available
        if self.core:
            self.core.system_registry.register_module("process_layer", self)
            self.event_bus = self.core.event_bus
            self._setup_event_handlers()
        else:
            self.event_bus = None
        
        print("=" * 60)
        print("Process Management Layer initialized successfully")
        print("=" * 60)
    
    def _setup_event_handlers(self) -> None:
        """Setup event handlers for process events."""
        if not self.event_bus:
            return
        
        # Subscribe to system events
        self.event_bus.subscribe("system.shutdown", self._on_system_shutdown)
    
    def _on_system_shutdown(self, data: Any) -> None:
        """Handle system shutdown event."""
        print("[ProcessLayer] Received shutdown signal...")
        self.shutdown()
    
    # Convenience methods that delegate to process_manager
    
    def run(
        self,
        name: str,
        runtime_function: Callable,
        priority: int = 5,
        args: tuple = (),
        kwargs: dict = None,
        owner: Optional[str] = None,
        background: bool = False
    ) -> Optional[Process]:
        """Run a new process."""
        return self.process_manager.run(
            name=name,
            runtime_function=runtime_function,
            priority=priority,
            args=args,
            kwargs=kwargs,
            owner=owner,
            background=background
        )
    
    def kill(self, pid: int, owner: Optional[str] = None) -> bool:
        """Terminate a process."""
        return self.process_manager.kill(pid, owner)
    
    def suspend(self, pid: int, owner: Optional[str] = None) -> bool:
        """Suspend a process."""
        return self.process_manager.suspend(pid, owner)
    
    def resume(self, pid: int, owner: Optional[str] = None) -> bool:
        """Resume a process."""
        return self.process_manager.resume(pid, owner)
    
    def ps(self, owner: Optional[str] = None, show_all: bool = False) -> list:
        """List processes."""
        return self.process_manager.ps(owner, show_all)
    
    def top(self, limit: int = 10) -> list:
        """Get top processes by CPU time."""
        return self.process_manager.top(limit)
    
    def get_process(self, pid: int) -> Optional[Process]:
        """Get process by PID."""
        return self.process_manager.get_process(pid)
    
    def cleanup_terminated(self) -> int:
        """Remove terminated processes."""
        return self.process_manager.cleanup_terminated()
    
    def killall(self, owner: Optional[str] = None) -> int:
        """Terminate all processes."""
        return self.process_manager.killall(owner)
    
    def get_statistics(self) -> dict:
        """Get process layer statistics."""
        return self.process_manager.get_statistics()
    
    def help(self) -> None:
        """Display available process commands."""
        commands = {
            "Process Management": [
                "run(name, function, ...) - Run a new process",
                "ps([owner], [show_all]) - List processes",
                "top([limit]) - Show top processes by CPU",
                "kill(pid, [owner]) - Terminate a process",
                "suspend(pid, [owner]) - Suspend a process",
                "resume(pid, [owner]) - Resume a process",
                "killall([owner]) - Terminate all processes",
                "cleanup_terminated() - Remove terminated processes",
                "get_process(pid) - Get process by PID",
                "get_statistics() - Get process statistics"
            ]
        }
        
        print("\n" + "=" * 60)
        print("Process Management Layer - Available Commands")
        print("=" * 60)
        
        for category, cmds in commands.items():
            print(f"\n{category}:")
            for cmd in cmds:
                print(f"  {cmd}")
        
        print("\n" + "=" * 60)
    
    def shutdown(self) -> None:
        """Shutdown the process layer."""
        print("\n" + "=" * 60)
        print("Shutting down Process Management Layer")
        print("=" * 60)
        
        # Terminate all processes
        self.killall()
        
        # Stop scheduler
        self.scheduler.stop()
        
        print("=" * 60)
        print("Process Management Layer shut down successfully")
        print("=" * 60 + "\n")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
        return False

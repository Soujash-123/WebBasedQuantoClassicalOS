"""
Memory Layer Master
Unified interface for the memory management layer.
"""

import os
from typing import Optional
from .memory_manager import MemoryManager
from .memory_monitor import MemoryMonitor


class MemoryLayer:
    """Master controller for memory layer"""
    
    def __init__(self, total_memory_mb: int = 512, page_size_kb: int = 4, 
                 enable_monitoring: bool = True):
        self.memory_manager = MemoryManager(total_memory_mb, page_size_kb)
        self.memory_monitor = MemoryMonitor(self.memory_manager)
        self.initialized = False
        self.enable_monitoring = enable_monitoring
    
    def initialize(self):
        """Initialize memory layer"""
        if self.initialized:
            return
        
        if self.enable_monitoring:
            self.memory_monitor.start_monitoring()
        
        self.initialized = True
        print(f"[Memory Layer] Initialized with {self.memory_manager.virtual_memory.total_memory / (1024*1024):.0f} MB")
    
    def shutdown(self):
        """Shutdown memory layer"""
        if not self.initialized:
            return
        
        self.memory_monitor.stop_monitoring()
        self.initialized = False
        print("[Memory Layer] Shutdown complete")
    
    # Memory Management Commands
    
    def cmd_memstat(self, args: list = None) -> str:
        """Display memory statistics"""
        return self.memory_manager.format_memory_stats()
    
    def cmd_memdump(self, args: list = None) -> str:
        """Dump memory state to file"""
        output_file = args[0] if args else "memory_dump.json"
        
        # Ensure proper path
        if not os.path.isabs(output_file):
            output_file = os.path.join(os.getcwd(), output_file)
        
        dump = self.memory_manager.dump_memory_state(output_file)
        
        lines = [
            f"Memory dump saved to: {output_file}",
            f"Total pages: {dump['stats']['total_pages']}",
            f"Allocated pages: {dump['stats']['allocated_pages']}",
            f"Active processes: {dump['stats']['active_processes']}"
        ]
        
        return "\n".join(lines)
    
    def cmd_flushmem(self, args: list = None) -> str:
        """Flush inactive memory pages"""
        inactive_seconds = int(args[0]) if args else 300
        flushed = self.memory_manager.flush_inactive_memory(inactive_seconds)
        
        return f"Flushed {flushed} inactive memory pages (inactive > {inactive_seconds}s)"
    
    def cmd_procmem(self, args: list = None) -> str:
        """Show memory usage for a process"""
        if not args:
            return "Usage: procmem <process_id>"
        
        try:
            process_id = int(args[0])
            return self.memory_manager.format_process_memory(process_id)
        except ValueError:
            return f"Error: Invalid process ID: {args[0]}"
    
    def cmd_memhistory(self, args: list = None) -> str:
        """Show memory allocation history"""
        limit = int(args[0]) if args else 20
        history = self.memory_manager.get_allocation_history(limit)
        
        if not history:
            return "No allocation history available"
        
        lines = ["=" * 80, "MEMORY ALLOCATION HISTORY", "=" * 80]
        
        for entry in history:
            status = "✓" if entry['success'] else "✗"
            lines.append(
                f"{status} [{entry['timestamp']}] PID:{entry['process_id']} "
                f"{entry['operation']} {entry['size_mb']:.2f}MB - {entry['description']}"
            )
        
        lines.append("=" * 80)
        return "\n".join(lines)
    
    def cmd_memmonitor(self, args: list = None) -> str:
        """Show memory monitoring report"""
        return self.memory_monitor.format_usage_report()
    
    # API Methods for other layers
    
    def allocate(self, process_id: int, size_mb: float, description: str = "") -> bool:
        """Allocate memory for a process"""
        return self.memory_manager.allocate_memory(process_id, size_mb, description)
    
    def free(self, process_id: int) -> int:
        """Free memory for a process"""
        return self.memory_manager.free_memory(process_id)
    
    def get_stats(self) -> dict:
        """Get memory statistics"""
        return self.memory_manager.get_memory_stats()
    
    def get_process_memory(self, process_id: int) -> dict:
        """Get process memory info"""
        return self.memory_manager.get_process_memory(process_id)
    
    def get_commands(self) -> dict:
        """Get available memory commands"""
        return {
            'memstat': {
                'function': self.cmd_memstat,
                'description': 'Display memory statistics',
                'usage': 'memstat'
            },
            'memdump': {
                'function': self.cmd_memdump,
                'description': 'Dump memory state to file',
                'usage': 'memdump [output_file]'
            },
            'flushmem': {
                'function': self.cmd_flushmem,
                'description': 'Flush inactive memory pages',
                'usage': 'flushmem [inactive_seconds]'
            },
            'procmem': {
                'function': self.cmd_procmem,
                'description': 'Show memory usage for a process',
                'usage': 'procmem <process_id>'
            },
            'memhistory': {
                'function': self.cmd_memhistory,
                'description': 'Show memory allocation history',
                'usage': 'memhistory [limit]'
            },
            'memmonitor': {
                'function': self.cmd_memmonitor,
                'description': 'Show memory monitoring report',
                'usage': 'memmonitor'
            }
        }

"""
Memory Manager
High-level interface for memory operations.
"""

import os
import json
from typing import Optional, Dict
from datetime import datetime
from .virtual_memory import VirtualMemory


class MemoryManager:
    """Manages memory allocation and tracking"""
    
    def __init__(self, total_memory_mb: int = 512, page_size_kb: int = 4):
        self.virtual_memory = VirtualMemory(total_memory_mb, page_size_kb)
        self.allocation_history = []
        self.max_history = 1000
    
    def allocate_memory(self, process_id: int, size_mb: float, description: str = "") -> bool:
        """Allocate memory for a process"""
        size_bytes = int(size_mb * 1024 * 1024)
        pages = self.virtual_memory.allocate(process_id, size_bytes)
        
        if pages:
            self._log_allocation(process_id, size_mb, description, 'allocate', True)
            return True
        else:
            self._log_allocation(process_id, size_mb, description, 'allocate', False)
            return False
    
    def free_memory(self, process_id: int) -> int:
        """Free memory for a process"""
        pages_freed = self.virtual_memory.free(process_id)
        
        if pages_freed > 0:
            size_mb = (pages_freed * self.virtual_memory.page_size) / (1024 * 1024)
            self._log_allocation(process_id, size_mb, "", 'free', True)
        
        return pages_freed
    
    def get_memory_stats(self) -> dict:
        """Get current memory statistics"""
        return self.virtual_memory.get_stats()
    
    def get_process_memory(self, process_id: int) -> dict:
        """Get memory info for a specific process"""
        return self.virtual_memory.get_process_memory(process_id)
    
    def dump_memory_state(self, output_file: Optional[str] = None) -> dict:
        """Dump complete memory state"""
        dump = self.virtual_memory.dump_memory()
        
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(dump, f, indent=2)
        
        return dump
    
    def flush_inactive_memory(self, inactive_seconds: int = 300) -> int:
        """Flush inactive memory pages"""
        flushed = self.virtual_memory.flush_inactive(inactive_seconds)
        self._log_allocation(0, 0, f"Flushed {flushed} pages", 'flush', True)
        return flushed
    
    def get_allocation_history(self, limit: int = 50) -> list:
        """Get recent allocation history"""
        return self.allocation_history[-limit:]
    
    def _log_allocation(self, process_id: int, size_mb: float, description: str, 
                       operation: str, success: bool):
        """Log memory allocation event"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'process_id': process_id,
            'size_mb': size_mb,
            'description': description,
            'operation': operation,
            'success': success
        }
        
        self.allocation_history.append(entry)
        
        # Limit history size
        if len(self.allocation_history) > self.max_history:
            self.allocation_history = self.allocation_history[-self.max_history:]
    
    def format_memory_stats(self) -> str:
        """Format memory statistics for display"""
        stats = self.get_memory_stats()
        
        lines = [
            "=" * 60,
            "MEMORY STATISTICS",
            "=" * 60,
            f"Total Memory:     {stats['total_memory_mb']:.2f} MB",
            f"Used Memory:      {stats['used_memory_mb']:.2f} MB ({stats['used_percent']:.1f}%)",
            f"Free Memory:      {stats['free_memory_mb']:.2f} MB",
            "",
            f"Total Pages:      {stats['total_pages']}",
            f"Allocated Pages:  {stats['allocated_pages']}",
            f"Free Pages:       {stats['free_pages']}",
            f"Page Size:        {stats['page_size_kb']:.0f} KB",
            "",
            f"Active Processes: {stats['active_processes']}",
            f"Swap Pages:       {stats['swap_pages']}",
            "=" * 60
        ]
        
        return "\n".join(lines)
    
    def format_process_memory(self, process_id: int) -> str:
        """Format process memory info for display"""
        info = self.get_process_memory(process_id)
        
        if info['allocated_pages'] == 0:
            return f"Process {process_id}: No memory allocated"
        
        lines = [
            f"Process {process_id} Memory Usage:",
            f"  Allocated Pages: {info['allocated_pages']}",
            f"  Memory: {info['memory_mb']:.2f} MB ({info['memory_kb']:.2f} KB)"
        ]
        
        return "\n".join(lines)

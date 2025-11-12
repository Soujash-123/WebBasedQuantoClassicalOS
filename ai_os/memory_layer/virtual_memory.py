"""
Virtual Memory System
Manages memory allocation, pages, and swapping.
"""

import json
import os
from typing import Dict, Optional, List
from datetime import datetime


class MemoryPage:
    """Represents a single memory page"""
    
    def __init__(self, page_id: int, size: int, process_id: Optional[int] = None):
        self.page_id = page_id
        self.size = size
        self.process_id = process_id
        self.data = {}
        self.allocated = process_id is not None
        self.last_accessed = datetime.now()
        self.dirty = False
    
    def allocate(self, process_id: int, data: dict = None):
        """Allocate page to a process"""
        self.process_id = process_id
        self.allocated = True
        self.data = data or {}
        self.last_accessed = datetime.now()
        self.dirty = True
    
    def free(self):
        """Free the page"""
        self.process_id = None
        self.allocated = False
        self.data = {}
        self.dirty = False
    
    def access(self):
        """Mark page as accessed"""
        self.last_accessed = datetime.now()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'page_id': self.page_id,
            'size': self.size,
            'process_id': self.process_id,
            'allocated': self.allocated,
            'last_accessed': self.last_accessed.isoformat(),
            'dirty': self.dirty,
            'data_size': len(str(self.data))
        }


class VirtualMemory:
    """Virtual Memory Management System"""
    
    def __init__(self, total_memory_mb: int = 512, page_size_kb: int = 4):
        self.total_memory = total_memory_mb * 1024 * 1024  # Convert to bytes
        self.page_size = page_size_kb * 1024  # Convert to bytes
        self.num_pages = self.total_memory // self.page_size
        
        # Initialize memory pages
        self.pages: Dict[int, MemoryPage] = {}
        for i in range(self.num_pages):
            self.pages[i] = MemoryPage(i, self.page_size)
        
        # Process memory tracking
        self.process_allocations: Dict[int, List[int]] = {}  # process_id -> [page_ids]
        
        # Swap space (virtual disk)
        self.swap_space: Dict[int, dict] = {}  # page_id -> data
        self.swap_enabled = True
    
    def allocate(self, process_id: int, size_bytes: int) -> Optional[List[int]]:
        """Allocate memory for a process"""
        pages_needed = (size_bytes + self.page_size - 1) // self.page_size
        
        # Find free pages
        free_pages = [pid for pid, page in self.pages.items() if not page.allocated]
        
        if len(free_pages) < pages_needed:
            # Try to swap out inactive pages
            if self.swap_enabled:
                self._swap_out_inactive_pages(pages_needed - len(free_pages))
                free_pages = [pid for pid, page in self.pages.items() if not page.allocated]
            
            if len(free_pages) < pages_needed:
                return None  # Out of memory
        
        # Allocate pages
        allocated_pages = free_pages[:pages_needed]
        for page_id in allocated_pages:
            self.pages[page_id].allocate(process_id)
        
        # Track allocation
        if process_id not in self.process_allocations:
            self.process_allocations[process_id] = []
        self.process_allocations[process_id].extend(allocated_pages)
        
        return allocated_pages
    
    def free(self, process_id: int) -> int:
        """Free all memory allocated to a process"""
        if process_id not in self.process_allocations:
            return 0
        
        pages_freed = 0
        for page_id in self.process_allocations[process_id]:
            if page_id in self.pages:
                self.pages[page_id].free()
                pages_freed += 1
        
        del self.process_allocations[process_id]
        return pages_freed
    
    def get_stats(self) -> dict:
        """Get memory statistics"""
        allocated_pages = sum(1 for page in self.pages.values() if page.allocated)
        free_pages = self.num_pages - allocated_pages
        
        allocated_memory = allocated_pages * self.page_size
        free_memory = free_pages * self.page_size
        
        return {
            'total_memory_mb': self.total_memory / (1024 * 1024),
            'used_memory_mb': allocated_memory / (1024 * 1024),
            'free_memory_mb': free_memory / (1024 * 1024),
            'used_percent': (allocated_memory / self.total_memory) * 100,
            'total_pages': self.num_pages,
            'allocated_pages': allocated_pages,
            'free_pages': free_pages,
            'page_size_kb': self.page_size / 1024,
            'active_processes': len(self.process_allocations),
            'swap_pages': len(self.swap_space)
        }
    
    def get_process_memory(self, process_id: int) -> dict:
        """Get memory usage for a specific process"""
        if process_id not in self.process_allocations:
            return {'allocated_pages': 0, 'memory_mb': 0}
        
        pages = len(self.process_allocations[process_id])
        memory_bytes = pages * self.page_size
        
        return {
            'process_id': process_id,
            'allocated_pages': pages,
            'memory_mb': memory_bytes / (1024 * 1024),
            'memory_kb': memory_bytes / 1024
        }
    
    def dump_memory(self) -> dict:
        """Dump complete memory state for debugging"""
        return {
            'timestamp': datetime.now().isoformat(),
            'stats': self.get_stats(),
            'pages': {pid: page.to_dict() for pid, page in self.pages.items() if page.allocated},
            'process_allocations': {
                pid: {
                    'pages': page_list,
                    'memory_mb': len(page_list) * self.page_size / (1024 * 1024)
                }
                for pid, page_list in self.process_allocations.items()
            },
            'swap_space': list(self.swap_space.keys())
        }
    
    def flush_inactive(self, inactive_seconds: int = 300) -> int:
        """Flush inactive memory pages"""
        now = datetime.now()
        flushed = 0
        
        for page in self.pages.values():
            if page.allocated and not page.dirty:
                time_diff = (now - page.last_accessed).total_seconds()
                if time_diff > inactive_seconds:
                    page.free()
                    flushed += 1
        
        return flushed
    
    def _swap_out_inactive_pages(self, count: int):
        """Swap out inactive pages to disk"""
        # Find least recently used pages
        allocated_pages = [(pid, page) for pid, page in self.pages.items() if page.allocated]
        allocated_pages.sort(key=lambda x: x[1].last_accessed)
        
        swapped = 0
        for page_id, page in allocated_pages:
            if swapped >= count:
                break
            
            # Save to swap space
            self.swap_space[page_id] = {
                'process_id': page.process_id,
                'data': page.data,
                'timestamp': datetime.now().isoformat()
            }
            
            page.free()
            swapped += 1
    
    def _swap_in_page(self, page_id: int):
        """Swap in a page from disk"""
        if page_id in self.swap_space:
            swap_data = self.swap_space[page_id]
            self.pages[page_id].allocate(
                swap_data['process_id'],
                swap_data['data']
            )
            del self.swap_space[page_id]

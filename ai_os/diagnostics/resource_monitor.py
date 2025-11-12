"""
Resource Monitor
Monitors system resources (CPU, memory, processes).
"""

import time
import threading
from typing import Optional, List
from datetime import datetime


class ResourceMonitor:
    """Monitors system resources"""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.history = []
        self.max_history = 1000
        self.interval = 5  # seconds
        
        # Try to import psutil for real metrics
        try:
            import psutil
            self.psutil = psutil
            self.has_psutil = True
        except ImportError:
            self.psutil = None
            self.has_psutil = False
    
    def start_monitoring(self):
        """Start resource monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def get_current_stats(self) -> dict:
        """Get current resource statistics"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_used_mb': 0.0,
            'memory_total_mb': 0.0,
            'process_count': 0,
            'disk_usage_percent': 0.0
        }
        
        if self.has_psutil:
            try:
                stats['cpu_percent'] = self.psutil.cpu_percent(interval=0.1)
                
                mem = self.psutil.virtual_memory()
                stats['memory_percent'] = mem.percent
                stats['memory_used_mb'] = mem.used / (1024 * 1024)
                stats['memory_total_mb'] = mem.total / (1024 * 1024)
                
                stats['process_count'] = len(self.psutil.pids())
                
                disk = self.psutil.disk_usage('/')
                stats['disk_usage_percent'] = disk.percent
            except Exception as e:
                stats['error'] = str(e)
        
        return stats
    
    def get_history(self, limit: int = 100) -> List[dict]:
        """Get resource history"""
        return self.history[-limit:]
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                stats = self.get_current_stats()
                self.history.append(stats)
                
                if len(self.history) > self.max_history:
                    self.history = self.history[-self.max_history:]
                
                time.sleep(self.interval)
            except Exception as e:
                print(f"Resource monitor error: {e}")
                time.sleep(self.interval)
    
    def format_stats(self, stats: dict = None) -> str:
        """Format resource statistics"""
        if stats is None:
            stats = self.get_current_stats()
        
        lines = [
            "=" * 60,
            "RESOURCE STATISTICS",
            "=" * 60,
            f"Timestamp: {stats['timestamp']}",
            ""
        ]
        
        if self.has_psutil:
            lines.extend([
                f"CPU Usage: {stats['cpu_percent']:.1f}%",
                f"Memory Usage: {stats['memory_percent']:.1f}% "
                f"({stats['memory_used_mb']:.0f} MB / {stats['memory_total_mb']:.0f} MB)",
                f"Process Count: {stats['process_count']}",
                f"Disk Usage: {stats['disk_usage_percent']:.1f}%"
            ])
        else:
            lines.append("psutil not available - install for detailed metrics")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)

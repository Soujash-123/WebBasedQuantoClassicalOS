"""
Memory Monitor
Real-time memory monitoring and alerts.
"""

import time
from typing import Callable, Optional
from datetime import datetime
import threading


class MemoryMonitor:
    """Monitors memory usage and triggers alerts"""
    
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.monitoring = False
        self.monitor_thread = None
        self.alert_threshold = 80.0  # Alert when memory usage exceeds 80%
        self.alert_callbacks = []
        self.monitoring_interval = 5  # Check every 5 seconds
        self.history = []
        self.max_history = 100
    
    def start_monitoring(self):
        """Start memory monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def add_alert_callback(self, callback: Callable):
        """Add callback for memory alerts"""
        self.alert_callbacks.append(callback)
    
    def set_alert_threshold(self, threshold: float):
        """Set memory usage alert threshold (percentage)"""
        self.alert_threshold = max(0.0, min(100.0, threshold))
    
    def get_current_usage(self) -> dict:
        """Get current memory usage"""
        stats = self.memory_manager.get_memory_stats()
        return {
            'timestamp': datetime.now().isoformat(),
            'used_percent': stats['used_percent'],
            'used_mb': stats['used_memory_mb'],
            'free_mb': stats['free_memory_mb'],
            'active_processes': stats['active_processes']
        }
    
    def get_usage_history(self, limit: int = 50) -> list:
        """Get memory usage history"""
        return self.history[-limit:]
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                usage = self.get_current_usage()
                
                # Store in history
                self.history.append(usage)
                if len(self.history) > self.max_history:
                    self.history = self.history[-self.max_history:]
                
                # Check for alerts
                if usage['used_percent'] >= self.alert_threshold:
                    self._trigger_alert(usage)
                
                time.sleep(self.monitoring_interval)
            except Exception as e:
                print(f"Memory monitor error: {e}")
                time.sleep(self.monitoring_interval)
    
    def _trigger_alert(self, usage: dict):
        """Trigger memory alert"""
        alert_data = {
            'type': 'memory_high',
            'threshold': self.alert_threshold,
            'current': usage['used_percent'],
            'timestamp': usage['timestamp']
        }
        
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                print(f"Alert callback error: {e}")
    
    def format_usage_report(self) -> str:
        """Format memory usage report"""
        if not self.history:
            return "No monitoring data available"
        
        recent = self.history[-10:]
        avg_usage = sum(h['used_percent'] for h in recent) / len(recent)
        max_usage = max(h['used_percent'] for h in recent)
        min_usage = min(h['used_percent'] for h in recent)
        
        lines = [
            "=" * 60,
            "MEMORY USAGE REPORT (Last 10 samples)",
            "=" * 60,
            f"Average Usage: {avg_usage:.1f}%",
            f"Maximum Usage: {max_usage:.1f}%",
            f"Minimum Usage: {min_usage:.1f}%",
            f"Alert Threshold: {self.alert_threshold:.1f}%",
            f"Monitoring: {'Active' if self.monitoring else 'Inactive'}",
            "=" * 60
        ]
        
        return "\n".join(lines)

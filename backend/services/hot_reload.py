"""
Hot Reload Service
Monitors the Core OS folder for changes and dynamically reloads modules
"""

import sys
import importlib
import threading
from pathlib import Path
from typing import Callable, Optional, Set
from datetime import datetime

# Try to import watchdog - it's optional
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
    FileModifiedEvent = None
    print("⚠ watchdog not installed - hot reload will not be available")
    print("  Install with: pip install watchdog")


class OSReloadHandler(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
    """
    File system event handler for OS code changes
    Triggers reload when Python files in ai_os/ are modified
    """
    
    def __init__(self, reload_callback: Callable):
        if WATCHDOG_AVAILABLE:
            super().__init__()
        self.reload_callback = reload_callback
        self.last_reload_time = datetime.now()
        self.reload_cooldown = 2  # seconds
        self.modified_modules: Set[str] = set()
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        # Only process Python files
        if not event.src_path.endswith('.py'):
            return
        
        # Check cooldown to avoid rapid reloads
        now = datetime.now()
        if (now - self.last_reload_time).total_seconds() < self.reload_cooldown:
            return
        
        print(f"\n🔄 Detected change: {event.src_path}")
        
        # Extract module name
        module_path = Path(event.src_path)
        if 'ai_os' in module_path.parts:
            self.modified_modules.add(str(module_path))
            self._trigger_reload()
    
    def _trigger_reload(self):
        """Trigger the reload callback"""
        self.last_reload_time = datetime.now()
        
        print(f"📦 Reloading modules: {len(self.modified_modules)} changed")
        
        try:
            # Call the reload callback
            self.reload_callback()
            print("✓ Reload complete")
            self.modified_modules.clear()
            
        except Exception as e:
            print(f"✗ Reload failed: {e}")


class HotReloadService:
    """
    Hot Reload Service
    Monitors ai_os/ directory and triggers OS reload on changes
    """
    
    def __init__(self, watch_path: str, reload_callback: Callable):
        """
        Initialize hot reload service
        
        Args:
            watch_path: Path to watch for changes (ai_os directory)
            reload_callback: Function to call when reload is needed
        """
        self.watch_path = Path(watch_path)
        self.reload_callback = reload_callback
        self.observer = None
        self.running = False
        self.event_handler = OSReloadHandler(reload_callback)
    
    def start(self):
        """Start watching for file changes"""
        if not WATCHDOG_AVAILABLE:
            print("⚠ Hot reload not available (watchdog not installed)")
            return
        
        if self.running:
            print("Hot reload already running")
            return
        
        if not self.watch_path.exists():
            print(f"Warning: Watch path does not exist: {self.watch_path}")
            return
        
        try:
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                str(self.watch_path),
                recursive=True
            )
            self.observer.start()
            self.running = True
            print(f"🔍 Hot reload watching: {self.watch_path}")
            
        except Exception as e:
            print(f"Failed to start hot reload: {e}")
    
    def stop(self):
        """Stop watching for file changes"""
        if not self.running:
            return
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.running = False
            print("Hot reload stopped")
    
    def is_running(self) -> bool:
        """Check if hot reload is active"""
        return self.running
    
    def get_status(self) -> dict:
        """Get hot reload status"""
        return {
            "enabled": self.running,
            "watch_path": str(self.watch_path),
            "last_reload": self.event_handler.last_reload_time.isoformat() if self.running else None,
            "modified_modules": list(self.event_handler.modified_modules) if self.running else []
        }


def reload_module(module_name: str):
    """
    Reload a specific Python module
    
    Args:
        module_name: Full module name (e.g., 'ai_os.core.core_master')
    """
    try:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
            print(f"✓ Reloaded: {module_name}")
        else:
            print(f"Module not loaded: {module_name}")
    except Exception as e:
        print(f"✗ Failed to reload {module_name}: {e}")


def reload_ai_os_modules():
    """
    Reload all ai_os modules
    This is a comprehensive reload of the entire OS layer
    """
    print("\n" + "="*60)
    print("RELOADING AI OS MODULES")
    print("="*60)
    
    # Get all ai_os modules
    ai_os_modules = [name for name in sys.modules.keys() if name.startswith('ai_os')]
    
    print(f"Found {len(ai_os_modules)} ai_os modules")
    
    # Reload in reverse order (to handle dependencies)
    for module_name in reversed(ai_os_modules):
        try:
            importlib.reload(sys.modules[module_name])
        except Exception as e:
            print(f"Warning: Could not reload {module_name}: {e}")
    
    print("="*60)
    print("MODULE RELOAD COMPLETE")
    print("="*60 + "\n")

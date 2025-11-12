"""
Kernel Hot Reload Manager
Enables real-time code updates without restarting the OS.
"""

import os
import sys
import json
import time
import hashlib
import importlib
import importlib.util
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Callable
from collections import defaultdict


class ModuleSnapshot:
    """Represents a snapshot of a module's state"""
    
    def __init__(self, module_path: str, checksum: str, timestamp: float):
        self.module_path = module_path
        self.checksum = checksum
        self.timestamp = timestamp
        self.version = "v1.0.0"
        self.status = "active"
    
    def to_dict(self) -> dict:
        return {
            "module": self.module_path,
            "last_updated": datetime.fromtimestamp(self.timestamp).isoformat(),
            "status": self.status,
            "version": self.version,
            "checksum": self.checksum
        }


class KernelHotReload:
    """
    Self-Updating Kernel Manager
    Dynamically reloads modules without restarting the OS.
    """
    
    def __init__(self, base_path: str = None, manifest_path: str = None, restart_callback: Callable = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.manifest_path = manifest_path or str(self.base_path / "kernel_manifest.json")
        self.log_path = self.base_path / "var" / "log" / "kernel_hotreload.log"
        self.restart_callback = restart_callback  # Callback to restart the system
        
        # Ensure log directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Module tracking
        self.module_registry: Dict[str, ModuleSnapshot] = {}
        self.module_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.reload_history: List[Dict] = []
        self.backup_modules: Dict[str, any] = {}
        
        # Reload hooks
        self.reload_hooks: Dict[str, Callable] = {}
        
        # Thread safety
        self.reload_lock = threading.RLock()
        
        # Watch mode
        self.watch_active = False
        self.watch_thread = None
        
        # Monitored directories
        self.watched_dirs = [
            'core', 'filesystem', 'processes', 'network_layer',
            'cli_shell', 'security_layer', 'devices', 'system_simulation_layer',
            'memory_layer', 'diagnostics', 'users', 'system'
        ]
        
        # Initialize
        self._load_manifest()
        self._scan_modules()
        
        self._log("Kernel Hot Reload Manager initialized")
    
    def _log(self, message: str, level: str = "INFO"):
        """Log message to file and optionally console"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Failed to write log: {e}")
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            self._log(f"Failed to calculate checksum for {file_path}: {e}", "ERROR")
            return ""
    
    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name"""
        try:
            rel_path = file_path.relative_to(self.base_path)
            module_path = str(rel_path.with_suffix('')).replace(os.sep, '.')
            
            # Handle ai_os prefix
            if module_path.startswith('ai_os.'):
                return module_path
            else:
                return f"ai_os.{module_path}"
        except Exception:
            return str(file_path.with_suffix('')).replace(os.sep, '.')
    
    def _scan_modules(self):
        """Scan all Python modules in watched directories"""
        self._log("Scanning modules...")
        
        for dir_name in self.watched_dirs:
            dir_path = self.base_path / dir_name
            if not dir_path.exists():
                continue
            
            for py_file in dir_path.rglob("*.py"):
                if py_file.name.startswith('__') and py_file.name != '__init__.py':
                    continue
                
                module_name = self._get_module_name(py_file)
                checksum = self._calculate_checksum(str(py_file))
                timestamp = py_file.stat().st_mtime
                
                if module_name not in self.module_registry:
                    self.module_registry[module_name] = ModuleSnapshot(
                        module_name, checksum, timestamp
                    )
        
        self._log(f"Scanned {len(self.module_registry)} modules")
    
    def _load_manifest(self):
        """Load manifest from disk"""
        if os.path.exists(self.manifest_path):
            try:
                with open(self.manifest_path, 'r') as f:
                    data = json.load(f)
                    for entry in data.get('modules', []):
                        module_name = entry['module']
                        self.module_registry[module_name] = ModuleSnapshot(
                            module_name,
                            entry['checksum'],
                            datetime.fromisoformat(entry['last_updated']).timestamp()
                        )
                self._log("Manifest loaded successfully")
            except Exception as e:
                self._log(f"Failed to load manifest: {e}", "ERROR")
    
    def _save_manifest(self):
        """Save manifest to disk"""
        try:
            manifest_data = {
                "version": "1.0.0",
                "last_scan": datetime.now().isoformat(),
                "modules": [snap.to_dict() for snap in self.module_registry.values()]
            }
            
            with open(self.manifest_path, 'w') as f:
                json.dump(manifest_data, f, indent=2)
            
            self._log("Manifest saved successfully")
        except Exception as e:
            self._log(f"Failed to save manifest: {e}", "ERROR")
    
    def _find_module_file(self, module_name: str) -> Optional[Path]:
        """Find the file path for a module name"""
        # Remove ai_os prefix if present
        clean_name = module_name.replace('ai_os.', '').replace('.', os.sep)
        
        # Try with .py extension
        file_path = self.base_path / f"{clean_name}.py"
        if file_path.exists():
            return file_path
        
        # Try as __init__.py in directory
        dir_path = self.base_path / clean_name / "__init__.py"
        if dir_path.exists():
            return dir_path
        
        return None
    
    def detect_changes(self) -> List[str]:
        """Detect which modules have changed since last scan"""
        changed_modules = []
        
        for module_name, snapshot in self.module_registry.items():
            file_path = self._find_module_file(module_name)
            if not file_path:
                continue
            
            current_checksum = self._calculate_checksum(str(file_path))
            if current_checksum != snapshot.checksum:
                changed_modules.append(module_name)
                self._log(f"Detected change in {module_name}")
        
        return changed_modules
    
    def _backup_module(self, module_name: str):
        """Backup a module before reloading"""
        if module_name in sys.modules:
            self.backup_modules[module_name] = sys.modules[module_name]
            self._log(f"Backed up module: {module_name}")
    
    def _restore_module(self, module_name: str):
        """Restore a module from backup"""
        if module_name in self.backup_modules:
            sys.modules[module_name] = self.backup_modules[module_name]
            self._log(f"Restored module from backup: {module_name}", "WARNING")
            return True
        return False
    
    def _reload_module(self, module_name: str) -> bool:
        """Reload a single module"""
        try:
            # Backup current version
            self._backup_module(module_name)
            
            # Find module file
            file_path = self._find_module_file(module_name)
            if not file_path:
                self._log(f"Module file not found: {module_name}", "ERROR")
                return False
            
            # Reload the module
            if module_name in sys.modules:
                # Module already loaded, use importlib.reload
                module = sys.modules[module_name]
                importlib.reload(module)
                self._log(f"Reloaded existing module: {module_name}")
            else:
                # Load new module
                spec = importlib.util.spec_from_file_location(module_name, str(file_path))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    self._log(f"Loaded new module: {module_name}")
                else:
                    raise ImportError(f"Could not create spec for {module_name}")
            
            # Call reload hook if exists
            if hasattr(module, 'on_reload'):
                module.on_reload()
                self._log(f"Called on_reload() for {module_name}")
            
            # Update registry
            checksum = self._calculate_checksum(str(file_path))
            timestamp = file_path.stat().st_mtime
            self.module_registry[module_name] = ModuleSnapshot(
                module_name, checksum, timestamp
            )
            
            return True
            
        except Exception as e:
            self._log(f"Failed to reload {module_name}: {e}", "ERROR")
            # Attempt rollback
            self._restore_module(module_name)
            return False
    
    def refresh(self, force_all: bool = False) -> Dict[str, any]:
        """
        Refresh modules - reload changed modules
        
        Args:
            force_all: If True, reload all modules regardless of changes
        
        Returns:
            Dictionary with reload results
        """
        with self.reload_lock:
            self._log("=" * 60)
            self._log("Starting module refresh...")
            
            start_time = time.time()
            
            # Detect changes
            if force_all:
                modules_to_reload = list(self.module_registry.keys())
                self._log(f"Force reload: {len(modules_to_reload)} modules")
            else:
                modules_to_reload = self.detect_changes()
                self._log(f"Detected {len(modules_to_reload)} changed modules")
            
            # Reload modules
            success_count = 0
            failed_count = 0
            failed_modules = []
            
            for module_name in modules_to_reload:
                if self._reload_module(module_name):
                    success_count += 1
                else:
                    failed_count += 1
                    failed_modules.append(module_name)
            
            # Save manifest
            self._save_manifest()
            
            elapsed = time.time() - start_time
            
            # Record history
            reload_event = {
                "timestamp": datetime.now().isoformat(),
                "total_modules": len(modules_to_reload),
                "success": success_count,
                "failed": failed_count,
                "failed_modules": failed_modules,
                "elapsed_seconds": elapsed
            }
            self.reload_history.append(reload_event)
            
            self._log(f"Refresh complete: {success_count} success, {failed_count} failed in {elapsed:.2f}s")
            self._log("=" * 60)
            
            return reload_event
    
    def rollback(self, module_name: str) -> bool:
        """
        Rollback a module to its previous version
        
        Args:
            module_name: Name of module to rollback
        
        Returns:
            True if rollback successful
        """
        with self.reload_lock:
            self._log(f"Attempting rollback of {module_name}")
            
            if self._restore_module(module_name):
                self._log(f"Successfully rolled back {module_name}")
                return True
            else:
                self._log(f"No backup available for {module_name}", "WARNING")
                return False
    
    def register_hook(self, module_name: str, hook_func: Callable):
        """Register a reload hook for a module"""
        self.reload_hooks[module_name] = hook_func
        self._log(f"Registered reload hook for {module_name}")
    
    def _watch_loop(self):
        """Background watch loop"""
        self._log("Watch loop started")
        
        while self.watch_active:
            try:
                changed = self.detect_changes()
                if changed:
                    self._log(f"Auto-reload triggered: {len(changed)} modules changed")
                    self.refresh()
                    
                    # Trigger restart if callback is set
                    if self.restart_callback:
                        self._log("Triggering system restart...")
                        self.restart_callback()
                        break  # Exit watch loop as system is restarting
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                self._log(f"Watch loop error: {e}", "ERROR")
                time.sleep(5)
        
        self._log("Watch loop stopped")
    
    def start_watch(self):
        """Start watching for changes in background"""
        if self.watch_active:
            self._log("Watch mode already active", "WARNING")
            return False
        
        self.watch_active = True
        self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()
        
        self._log("Watch mode activated")
        return True
    
    def stop_watch(self):
        """Stop watching for changes"""
        if not self.watch_active:
            return False
        
        self.watch_active = False
        if self.watch_thread:
            self.watch_thread.join(timeout=5)
        
        self._log("Watch mode deactivated")
        return True
    
    def get_status(self) -> Dict:
        """Get current status of reload system"""
        return {
            "total_modules": len(self.module_registry),
            "watch_active": self.watch_active,
            "reload_history_count": len(self.reload_history),
            "recent_reloads": self.reload_history[-5:] if self.reload_history else [],
            "backed_up_modules": len(self.backup_modules)
        }
    
    def get_reload_history(self, limit: int = 10) -> List[Dict]:
        """Get recent reload history"""
        return self.reload_history[-limit:]
    
    def format_status_report(self) -> str:
        """Format a human-readable status report"""
        status = self.get_status()
        
        report = []
        report.append("=" * 70)
        report.append("KERNEL HOT RELOAD STATUS")
        report.append("=" * 70)
        report.append(f"Total Modules Tracked: {status['total_modules']}")
        report.append(f"Watch Mode: {'ACTIVE' if status['watch_active'] else 'INACTIVE'}")
        report.append(f"Backed Up Modules: {status['backed_up_modules']}")
        report.append(f"Total Reload Events: {status['reload_history_count']}")
        report.append("")
        
        if status['recent_reloads']:
            report.append("Recent Reload Events:")
            report.append("-" * 70)
            for event in status['recent_reloads']:
                report.append(f"  Time: {event['timestamp']}")
                report.append(f"  Modules: {event['total_modules']} "
                            f"(✓ {event['success']}, ✗ {event['failed']})")
                report.append(f"  Duration: {event['elapsed_seconds']:.2f}s")
                if event['failed_modules']:
                    report.append(f"  Failed: {', '.join(event['failed_modules'])}")
                report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


# Global instance
_kernel_reload_instance = None


def get_kernel_reload(restart_callback: Callable = None) -> KernelHotReload:
    """Get or create global kernel reload instance"""
    global _kernel_reload_instance
    if _kernel_reload_instance is None:
        _kernel_reload_instance = KernelHotReload(restart_callback=restart_callback)
    elif restart_callback and not _kernel_reload_instance.restart_callback:
        # Update callback if not set
        _kernel_reload_instance.restart_callback = restart_callback
    return _kernel_reload_instance


def on_reload():
    """Hook called when this module is reloaded"""
    print("✓ Kernel Hot Reload module reloaded successfully!")

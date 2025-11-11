"""
Diagnostics Layer Master
Unified interface for diagnostics.
"""

from .system_check import SystemCheck
from .dependency_checker import DependencyChecker
from .resource_monitor import ResourceMonitor


class DiagnosticsLayer:
    """Master controller for diagnostics layer"""
    
    def __init__(self):
        self.system_check = SystemCheck()
        self.dependency_checker = DependencyChecker()
        self.resource_monitor = ResourceMonitor()
        self.initialized = False
    
    def initialize(self):
        """Initialize diagnostics layer"""
        if self.initialized:
            return
        
        self.resource_monitor.start_monitoring()
        self.initialized = True
        print("[Diagnostics Layer] Initialized")
    
    def shutdown(self):
        """Shutdown diagnostics layer"""
        if not self.initialized:
            return
        
        self.resource_monitor.stop_monitoring()
        self.initialized = False
        print("[Diagnostics Layer] Shutdown complete")
    
    def cmd_syscheck(self, args: list = None) -> str:
        """Run system diagnostics"""
        summary = self.system_check.run_all_checks()
        return self.system_check.format_report(summary)
    
    def cmd_depcheck(self, args: list = None) -> str:
        """Check dependencies"""
        results = self.dependency_checker.check_all_dependencies()
        return self.dependency_checker.format_report(results)
    
    def cmd_resources(self, args: list = None) -> str:
        """Show resource statistics"""
        return self.resource_monitor.format_stats()
    
    def cmd_reshistory(self, args: list = None) -> str:
        """Show resource history"""
        limit = int(args[0]) if args else 10
        history = self.resource_monitor.get_history(limit)
        
        if not history:
            return "No resource history available"
        
        lines = ["=" * 80, "RESOURCE HISTORY", "=" * 80]
        
        for entry in history[-limit:]:
            lines.append(f"[{entry['timestamp']}] "
                        f"CPU: {entry['cpu_percent']:.1f}% | "
                        f"MEM: {entry['memory_percent']:.1f}% | "
                        f"PROC: {entry['process_count']}")
        
        lines.append("=" * 80)
        return "\n".join(lines)
    
    def get_commands(self) -> dict:
        """Get available diagnostic commands"""
        return {
            'syscheck': {
                'function': self.cmd_syscheck,
                'description': 'Run system diagnostics',
                'usage': 'syscheck'
            },
            'depcheck': {
                'function': self.cmd_depcheck,
                'description': 'Check dependencies',
                'usage': 'depcheck'
            },
            'resources': {
                'function': self.cmd_resources,
                'description': 'Show resource statistics',
                'usage': 'resources'
            },
            'reshistory': {
                'function': self.cmd_reshistory,
                'description': 'Show resource history',
                'usage': 'reshistory [limit]'
            }
        }

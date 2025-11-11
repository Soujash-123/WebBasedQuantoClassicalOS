"""
System Check
Performs comprehensive system diagnostics.
"""

import os
import sys
import importlib
from typing import Dict, List
from datetime import datetime


class SystemCheck:
    """Performs system diagnostics"""
    
    def __init__(self):
        self.results = {}
        self.errors = []
        self.warnings = []
    
    def run_all_checks(self) -> dict:
        """Run all diagnostic checks"""
        self.results = {}
        self.errors = []
        self.warnings = []
        
        checks = [
            ('Python Version', self.check_python_version),
            ('Core Layer', self.check_core_layer),
            ('Memory Layer', self.check_memory_layer),
            ('Network Layer', self.check_network_layer),
            ('Security Layer', self.check_security_layer),
            ('File System Layer', self.check_filesystem_layer),
            ('Process Layer', self.check_process_layer),
            ('Device Layer', self.check_device_layer),
            ('CLI Shell', self.check_cli_shell),
            ('System Simulation', self.check_system_simulation),
            ('Dependencies', self.check_dependencies)
        ]
        
        for name, check_func in checks:
            try:
                result = check_func()
                self.results[name] = result
            except Exception as e:
                self.results[name] = {'status': 'ERROR', 'message': str(e)}
                self.errors.append(f"{name}: {e}")
        
        return self.get_summary()
    
    def check_python_version(self) -> dict:
        """Check Python version"""
        version = sys.version_info
        
        if version.major >= 3 and version.minor >= 8:
            return {
                'status': 'OK',
                'version': f"{version.major}.{version.minor}.{version.micro}",
                'message': 'Python version is compatible'
            }
        else:
            self.warnings.append(f"Python {version.major}.{version.minor} may not be fully compatible")
            return {
                'status': 'WARNING',
                'version': f"{version.major}.{version.minor}.{version.micro}",
                'message': 'Python 3.8+ recommended'
            }
    
    def check_core_layer(self) -> dict:
        """Check core layer"""
        try:
            from ai_os.core import core_master, event_bus, system_registry
            return {
                'status': 'OK',
                'modules': ['core_master', 'event_bus', 'system_registry'],
                'message': 'Core layer operational'
            }
        except ImportError as e:
            return {'status': 'ERROR', 'message': f'Import failed: {e}'}
    
    def check_memory_layer(self) -> dict:
        """Check memory layer"""
        try:
            from ai_os.memory_layer import MemoryLayer
            return {
                'status': 'OK',
                'message': 'Memory layer operational'
            }
        except ImportError as e:
            return {'status': 'ERROR', 'message': f'Import failed: {e}'}
    
    def check_network_layer(self) -> dict:
        """Check network layer"""
        try:
            from ai_os.network_layer import NetworkLayer
            return {
                'status': 'OK',
                'message': 'Network layer operational'
            }
        except ImportError as e:
            return {'status': 'ERROR', 'message': f'Import failed: {e}'}
    
    def check_security_layer(self) -> dict:
        """Check security layer"""
        try:
            from ai_os.security_layer import SecurityLayer
            return {
                'status': 'OK',
                'message': 'Security layer operational'
            }
        except ImportError as e:
            return {'status': 'ERROR', 'message': f'Import failed: {e}'}
    
    def check_filesystem_layer(self) -> dict:
        """Check filesystem layer"""
        try:
            from ai_os.filesystem import vfs_master
            return {
                'status': 'OK',
                'message': 'Filesystem layer operational'
            }
        except ImportError as e:
            return {'status': 'ERROR', 'message': f'Import failed: {e}'}
    
    def check_process_layer(self) -> dict:
        """Check process layer"""
        try:
            from ai_os.processes import process_master
            return {
                'status': 'OK',
                'message': 'Process layer operational'
            }
        except ImportError as e:
            return {'status': 'ERROR', 'message': f'Import failed: {e}'}
    
    def check_device_layer(self) -> dict:
        """Check device layer"""
        try:
            from ai_os.devices import device_master
            return {
                'status': 'OK',
                'message': 'Device layer operational'
            }
        except ImportError as e:
            return {'status': 'ERROR', 'message': f'Import failed: {e}'}
    
    def check_cli_shell(self) -> dict:
        """Check CLI shell"""
        try:
            from ai_os.cli_shell import shell
            return {
                'status': 'OK',
                'message': 'CLI shell operational'
            }
        except ImportError as e:
            return {'status': 'ERROR', 'message': f'Import failed: {e}'}
    
    def check_system_simulation(self) -> dict:
        """Check system simulation layer"""
        try:
            from ai_os.system_simulation_layer import package_manager, git_interface
            return {
                'status': 'OK',
                'message': 'System simulation layer operational'
            }
        except ImportError as e:
            return {'status': 'ERROR', 'message': f'Import failed: {e}'}
    
    def check_dependencies(self) -> dict:
        """Check required dependencies"""
        required = ['cryptography']
        optional = ['psutil', 'requests']
        
        missing_required = []
        missing_optional = []
        
        for dep in required:
            try:
                importlib.import_module(dep)
            except ImportError:
                missing_required.append(dep)
        
        for dep in optional:
            try:
                importlib.import_module(dep)
            except ImportError:
                missing_optional.append(dep)
        
        if missing_required:
            return {
                'status': 'ERROR',
                'missing_required': missing_required,
                'missing_optional': missing_optional,
                'message': f'Missing required dependencies: {", ".join(missing_required)}'
            }
        elif missing_optional:
            self.warnings.append(f"Missing optional dependencies: {', '.join(missing_optional)}")
            return {
                'status': 'WARNING',
                'missing_optional': missing_optional,
                'message': 'Some optional dependencies missing'
            }
        else:
            return {
                'status': 'OK',
                'message': 'All dependencies installed'
            }
    
    def get_summary(self) -> dict:
        """Get diagnostic summary"""
        total = len(self.results)
        ok_count = sum(1 for r in self.results.values() if r.get('status') == 'OK')
        warning_count = sum(1 for r in self.results.values() if r.get('status') == 'WARNING')
        error_count = sum(1 for r in self.results.values() if r.get('status') == 'ERROR')
        
        overall_status = 'OK'
        if error_count > 0:
            overall_status = 'ERROR'
        elif warning_count > 0:
            overall_status = 'WARNING'
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status,
            'total_checks': total,
            'ok': ok_count,
            'warnings': warning_count,
            'errors': error_count,
            'results': self.results,
            'error_messages': self.errors,
            'warning_messages': self.warnings
        }
    
    def format_report(self, summary: dict = None) -> str:
        """Format diagnostic report"""
        if summary is None:
            summary = self.get_summary()
        
        lines = [
            "=" * 80,
            "SYSTEM DIAGNOSTIC REPORT",
            "=" * 80,
            f"Timestamp: {summary['timestamp']}",
            f"Overall Status: {summary['overall_status']}",
            "",
            f"Total Checks: {summary['total_checks']}",
            f"  ✓ OK: {summary['ok']}",
            f"  ⚠ Warnings: {summary['warnings']}",
            f"  ✗ Errors: {summary['errors']}",
            "",
            "=" * 80,
            "DETAILED RESULTS",
            "=" * 80
        ]
        
        for name, result in summary['results'].items():
            status = result.get('status', 'UNKNOWN')
            message = result.get('message', 'No message')
            
            if status == 'OK':
                symbol = '✓'
            elif status == 'WARNING':
                symbol = '⚠'
            else:
                symbol = '✗'
            
            lines.append(f"{symbol} {name}: {status}")
            lines.append(f"  {message}")
            lines.append("")
        
        if summary['error_messages']:
            lines.append("=" * 80)
            lines.append("ERRORS")
            lines.append("=" * 80)
            for error in summary['error_messages']:
                lines.append(f"  ✗ {error}")
            lines.append("")
        
        if summary['warning_messages']:
            lines.append("=" * 80)
            lines.append("WARNINGS")
            lines.append("=" * 80)
            for warning in summary['warning_messages']:
                lines.append(f"  ⚠ {warning}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)

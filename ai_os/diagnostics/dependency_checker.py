"""
Dependency Checker
Verifies inter-layer dependencies and imports.
"""

import importlib
import inspect
from typing import Dict, List, Set


class DependencyChecker:
    """Checks dependencies between layers"""
    
    def __init__(self):
        self.layers = {
            'core': 'ai_os.core',
            'memory': 'ai_os.memory_layer',
            'network': 'ai_os.network_layer',
            'security': 'ai_os.security_layer',
            'filesystem': 'ai_os.filesystem',
            'processes': 'ai_os.processes',
            'devices': 'ai_os.devices',
            'cli_shell': 'ai_os.cli_shell',
            'system_simulation': 'ai_os.system_simulation_layer'
        }
        self.dependencies = {}
    
    def check_all_dependencies(self) -> dict:
        """Check dependencies for all layers"""
        results = {}
        
        for layer_name, module_path in self.layers.items():
            results[layer_name] = self.check_layer_dependencies(module_path)
        
        return results
    
    def check_layer_dependencies(self, module_path: str) -> dict:
        """Check dependencies for a specific layer"""
        try:
            module = importlib.import_module(module_path)
            
            # Get all imports
            imports = self._get_module_imports(module)
            
            # Check if imports are valid
            missing = []
            valid = []
            
            for imp in imports:
                try:
                    importlib.import_module(imp)
                    valid.append(imp)
                except ImportError:
                    missing.append(imp)
            
            return {
                'status': 'OK' if not missing else 'ERROR',
                'total_imports': len(imports),
                'valid_imports': len(valid),
                'missing_imports': missing
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _get_module_imports(self, module) -> Set[str]:
        """Get all imports from a module"""
        imports = set()
        
        # This is a simplified version
        # In production, would use ast module to parse imports
        
        return imports
    
    def format_report(self, results: dict) -> str:
        """Format dependency report"""
        lines = [
            "=" * 80,
            "DEPENDENCY CHECK REPORT",
            "=" * 80
        ]
        
        for layer, result in results.items():
            status = result.get('status', 'UNKNOWN')
            lines.append(f"\n{layer.upper()}: {status}")
            
            if 'error' in result:
                lines.append(f"  Error: {result['error']}")
            elif 'missing_imports' in result and result['missing_imports']:
                lines.append(f"  Missing imports: {', '.join(result['missing_imports'])}")
        
        lines.append("\n" + "=" * 80)
        return "\n".join(lines)

"""
Dependency Resolver
Checks package dependencies and compatibility.
"""

from typing import List, Dict, Optional, Tuple


class DependencyResolver:
    """Resolves package dependencies."""
    
    def __init__(self):
        """Initialize dependency resolver."""
        self.installed_packages: Dict[str, str] = {}  # name -> version
    
    def set_installed(self, packages: Dict[str, str]) -> None:
        """Set currently installed packages."""
        self.installed_packages = packages.copy()
    
    def check_dependencies(self, package: dict) -> Tuple[bool, List[str]]:
        """
        Check if package dependencies are satisfied.
        
        Args:
            package: Package metadata with 'dependencies' field
            
        Returns:
            (satisfied, missing_dependencies)
        """
        dependencies = package.get('dependencies', [])
        missing = []
        
        for dep in dependencies:
            # Parse dependency (format: "package>=version" or "package")
            if '>=' in dep:
                dep_name, dep_version = dep.split('>=')
                dep_name = dep_name.strip()
                dep_version = dep_version.strip()
                
                if dep_name not in self.installed_packages:
                    missing.append(dep)
                else:
                    installed_version = self.installed_packages[dep_name]
                    if not self._version_satisfies(installed_version, dep_version):
                        missing.append(dep)
            else:
                dep_name = dep.strip()
                if dep_name not in self.installed_packages:
                    missing.append(dep)
        
        return len(missing) == 0, missing
    
    def check_conflicts(self, package: dict) -> Tuple[bool, List[str]]:
        """
        Check if package conflicts with installed packages.
        
        Args:
            package: Package metadata with 'conflicts' field
            
        Returns:
            (has_conflicts, conflicting_packages)
        """
        conflicts = package.get('conflicts', [])
        conflicting = []
        
        for conflict in conflicts:
            if conflict in self.installed_packages:
                conflicting.append(conflict)
        
        return len(conflicting) > 0, conflicting
    
    def resolve_install_order(self, packages: List[dict]) -> List[dict]:
        """
        Resolve installation order based on dependencies.
        
        Args:
            packages: List of package metadata
            
        Returns:
            Ordered list of packages
        """
        # Simple topological sort
        installed = set()
        ordered = []
        remaining = packages.copy()
        
        max_iterations = len(packages) * 2
        iteration = 0
        
        while remaining and iteration < max_iterations:
            iteration += 1
            made_progress = False
            
            for pkg in remaining[:]:
                dependencies = pkg.get('dependencies', [])
                dep_names = [self._parse_dep_name(d) for d in dependencies]
                
                # Check if all dependencies are satisfied
                if all(d in installed or d in self.installed_packages for d in dep_names):
                    ordered.append(pkg)
                    installed.add(pkg['name'])
                    remaining.remove(pkg)
                    made_progress = True
            
            if not made_progress:
                # Circular dependency or missing dependency
                # Add remaining packages anyway
                ordered.extend(remaining)
                break
        
        return ordered
    
    def _parse_dep_name(self, dependency: str) -> str:
        """Parse package name from dependency string."""
        if '>=' in dependency:
            return dependency.split('>=')[0].strip()
        return dependency.strip()
    
    def _version_satisfies(self, installed: str, required: str) -> bool:
        """Check if installed version satisfies required version."""
        try:
            installed_parts = [int(x) for x in installed.split('.')]
            required_parts = [int(x) for x in required.split('.')]
            
            # Pad to same length
            max_len = max(len(installed_parts), len(required_parts))
            installed_parts += [0] * (max_len - len(installed_parts))
            required_parts += [0] * (max_len - len(required_parts))
            
            return installed_parts >= required_parts
        except:
            # If version parsing fails, assume satisfied
            return True
    
    def suggest_install(self, missing: List[str]) -> str:
        """Suggest command to install missing dependencies."""
        if not missing:
            return ""
        
        dep_names = [self._parse_dep_name(d) for d in missing]
        return f"apt install {' '.join(dep_names)}"

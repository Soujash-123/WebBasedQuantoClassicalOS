"""
Package Manager
APT-like package management system.
"""

import os
import json
import shutil
from typing import List, Dict, Optional, Tuple
from .system_logger import SystemLogger
from .system_environment import SystemEnvironment
from .dependency_resolver import DependencyResolver


class PackageManager:
    """APT-like package manager."""
    
    def __init__(
        self,
        repo_file: str = "./system_simulation_layer/repo_registry.json",
        packages_dir: str = "./virtual_packages",
        logger: Optional[SystemLogger] = None,
        environment: Optional[SystemEnvironment] = None
    ):
        """
        Initialize package manager.
        
        Args:
            repo_file: Repository registry file
            packages_dir: Directory for installed packages
            logger: System logger
            environment: System environment
        """
        self.repo_file = repo_file
        self.packages_dir = packages_dir
        self.logger = logger or SystemLogger()
        self.environment = environment or SystemEnvironment()
        self.resolver = DependencyResolver()
        
        # Create packages directory
        os.makedirs(packages_dir, exist_ok=True)
        
        # Load repository data
        self.repo_data = self._load_repo()
        self.available_packages = self.repo_data.get('packages', {})
        
        # Update resolver with installed packages
        self._update_resolver()
    
    def _load_repo(self) -> dict:
        """Load repository data."""
        if not os.path.exists(self.repo_file):
            return {'repositories': [], 'packages': {}}
        
        try:
            with open(self.repo_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading repository: {e}")
            return {'repositories': [], 'packages': {}}
    
    def _save_repo(self) -> bool:
        """Save repository data."""
        try:
            with open(self.repo_file, 'w') as f:
                json.dump(self.repo_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving repository: {e}")
            return False
    
    def _update_resolver(self) -> None:
        """Update dependency resolver with installed packages."""
        installed = {}
        for name, info in self.environment.list_modules().items():
            installed[name] = info['version']
        self.resolver.set_installed(installed)
    
    def update(self) -> bool:
        """Update package repository (apt update)."""
        print("Reading package lists...")
        
        # Reload repository
        self.repo_data = self._load_repo()
        self.available_packages = self.repo_data.get('packages', {})
        
        count = len(self.available_packages)
        print(f"Fetched {count} packages from repositories")
        
        self.logger.log_update(count)
        return True
    
    def install(self, package_name: str, auto_deps: bool = True) -> bool:
        """
        Install a package (apt install).
        
        Args:
            package_name: Package to install
            auto_deps: Automatically install dependencies
            
        Returns:
            True if successful
        """
        # Check if package exists
        if package_name not in self.available_packages:
            print(f"E: Unable to locate package {package_name}")
            return False
        
        package = self.available_packages[package_name]
        
        # Check if already installed
        if self.environment.get_module(package_name):
            installed_version = self.environment.get_module(package_name)['version']
            print(f"{package_name} is already the newest version ({installed_version})")
            return True
        
        # Check dependencies
        satisfied, missing = self.resolver.check_dependencies(package)
        if not satisfied:
            print(f"The following packages have unmet dependencies:")
            print(f"  {package_name}: Depends: {', '.join(missing)}")
            
            if auto_deps:
                print(f"\nInstalling dependencies: {', '.join([self.resolver._parse_dep_name(d) for d in missing])}")
                for dep in missing:
                    dep_name = self.resolver._parse_dep_name(dep)
                    if not self.install(dep_name, auto_deps=True):
                        print(f"Failed to install dependency: {dep_name}")
                        return False
            else:
                print(f"\nTry: {self.resolver.suggest_install(missing)}")
                return False
        
        # Check conflicts
        has_conflicts, conflicting = self.resolver.check_conflicts(package)
        if has_conflicts:
            print(f"E: Package {package_name} conflicts with: {', '.join(conflicting)}")
            print(f"   Remove conflicting packages first")
            return False
        
        # Simulate installation
        print(f"Reading package lists... Done")
        print(f"Building dependency tree... Done")
        print(f"The following NEW packages will be installed:")
        print(f"  {package_name}")
        print(f"0 upgraded, 1 newly installed, 0 to remove")
        print(f"Need to get {package['size']} of archives")
        print(f"Get:1 {package['repository']} {package_name} {package['version']} [{package['size']}]")
        print(f"Fetched {package['size']} in 0s")
        
        # Create package directory
        package_path = os.path.join(self.packages_dir, package_name)
        os.makedirs(package_path, exist_ok=True)
        
        # Create package metadata
        metadata = {
            'name': package_name,
            'version': package['version'],
            'description': package['description'],
            'commands': package.get('commands', []),
            'installed': True
        }
        
        metadata_file = os.path.join(package_path, 'package.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create dummy command files
        for cmd in package.get('commands', []):
            cmd_file = os.path.join(package_path, cmd)
            with open(cmd_file, 'w') as f:
                f.write(f"#!/bin/bash\n# {cmd} from {package_name}\n")
        
        print(f"Unpacking {package_name} ({package['version']})...")
        print(f"Setting up {package_name} ({package['version']})...")
        
        # Register in environment
        self.environment.register_module(
            package_name,
            package['version'],
            package_path,
            package.get('commands', [])
        )
        
        # Update resolver
        self._update_resolver()
        
        # Log installation
        self.logger.log_install(package_name, package['version'], success=True)
        
        print(f"✓ {package_name} installed successfully")
        return True
    
    def remove(self, package_name: str) -> bool:
        """
        Remove a package (apt remove).
        
        Args:
            package_name: Package to remove
            
        Returns:
            True if successful
        """
        # Check if installed
        if not self.environment.get_module(package_name):
            print(f"E: Package '{package_name}' is not installed")
            return False
        
        print(f"Reading package lists... Done")
        print(f"Building dependency tree... Done")
        print(f"The following packages will be REMOVED:")
        print(f"  {package_name}")
        print(f"0 upgraded, 0 newly installed, 1 to remove")
        
        # Remove package directory
        package_path = os.path.join(self.packages_dir, package_name)
        if os.path.exists(package_path):
            shutil.rmtree(package_path)
        
        print(f"Removing {package_name}...")
        
        # Unregister from environment
        self.environment.unregister_module(package_name)
        
        # Update resolver
        self._update_resolver()
        
        # Log removal
        self.logger.log_remove(package_name, success=True)
        
        print(f"✓ {package_name} removed successfully")
        return True
    
    def list_packages(self, installed_only: bool = False) -> None:
        """
        List packages (apt list).
        
        Args:
            installed_only: Show only installed packages
        """
        if installed_only:
            print("Listing installed packages...")
            installed = self.environment.list_modules()
            
            if not installed:
                print("No packages installed")
                return
            
            for name, info in sorted(installed.items()):
                print(f"{name}/{info.get('version', 'unknown')} [installed]")
        else:
            print("Listing available packages...")
            
            installed = self.environment.list_modules()
            
            for name, pkg in sorted(self.available_packages.items()):
                status = "[installed]" if name in installed else ""
                print(f"{name}/{pkg['version']} {status}")
                print(f"  {pkg['description']}")
    
    def search(self, query: str) -> None:
        """
        Search for packages (apt search).
        
        Args:
            query: Search query
        """
        print(f"Searching for: {query}")
        results = []
        
        query_lower = query.lower()
        for name, pkg in self.available_packages.items():
            if (query_lower in name.lower() or 
                query_lower in pkg.get('description', '').lower() or
                query_lower in pkg.get('category', '').lower()):
                results.append((name, pkg))
        
        if not results:
            print("No packages found")
            return
        
        for name, pkg in sorted(results):
            installed = self.environment.get_module(name)
            status = "[installed]" if installed else ""
            print(f"{name}/{pkg['version']} {status}")
            print(f"  {pkg['description']}")
    
    def show(self, package_name: str) -> None:
        """
        Show package details (apt show).
        
        Args:
            package_name: Package name
        """
        if package_name not in self.available_packages:
            print(f"E: Unable to locate package {package_name}")
            return
        
        pkg = self.available_packages[package_name]
        installed = self.environment.get_module(package_name)
        
        print(f"Package: {package_name}")
        print(f"Version: {pkg['version']}")
        print(f"Status: {'installed' if installed else 'not installed'}")
        print(f"Size: {pkg['size']}")
        print(f"Category: {pkg.get('category', 'unknown')}")
        print(f"Repository: {pkg.get('repository', 'unknown')}")
        print(f"Description: {pkg['description']}")
        
        if pkg.get('dependencies'):
            print(f"Depends: {', '.join(pkg['dependencies'])}")
        
        if pkg.get('conflicts'):
            print(f"Conflicts: {', '.join(pkg['conflicts'])}")
        
        if pkg.get('commands'):
            print(f"Provides: {', '.join(pkg['commands'])}")
    
    def upgrade(self) -> bool:
        """
        Upgrade all packages (apt upgrade).
        
        Returns:
            True if successful
        """
        print("Reading package lists... Done")
        print("Building dependency tree... Done")
        print("Calculating upgrade...")
        
        installed = self.environment.list_modules()
        upgradeable = []
        
        for name, info in installed.items():
            if name in self.available_packages:
                available_version = self.available_packages[name]['version']
                installed_version = info['version']
                
                if available_version != installed_version:
                    upgradeable.append((name, installed_version, available_version))
        
        if not upgradeable:
            print("0 upgraded, 0 newly installed, 0 to remove")
            print("All packages are up to date")
            return True
        
        print(f"The following packages will be upgraded:")
        for name, old_ver, new_ver in upgradeable:
            print(f"  {name} ({old_ver} -> {new_ver})")
        
        print(f"{len(upgradeable)} upgraded, 0 newly installed, 0 to remove")
        
        # Perform upgrades
        upgraded_packages = []
        for name, old_ver, new_ver in upgradeable:
            print(f"\nUpgrading {name}...")
            # Remove old version
            self.remove(name)
            # Install new version
            if self.install(name):
                upgraded_packages.append(name)
        
        self.logger.log_upgrade(upgraded_packages)
        
        print(f"\n✓ {len(upgraded_packages)} packages upgraded")
        return True
    
    def run_command(self, args: List[str], context) -> bool:
        """
        Run apt command.
        
        Args:
            args: Command arguments
            context: Execution context
            
        Returns:
            True if successful
        """
        if not args:
            print("Usage: apt <command> [options]")
            print("Commands:")
            print("  update          - Update package lists")
            print("  install <pkg>   - Install package")
            print("  remove <pkg>    - Remove package")
            print("  list            - List packages")
            print("  search <query>  - Search packages")
            print("  show <pkg>      - Show package details")
            print("  upgrade         - Upgrade all packages")
            return False
        
        command = args[0]
        
        if command == 'update':
            return self.update()
        
        elif command == 'install':
            if len(args) < 2:
                print("E: Missing package name")
                return False
            return self.install(args[1])
        
        elif command == 'remove':
            if len(args) < 2:
                print("E: Missing package name")
                return False
            return self.remove(args[1])
        
        elif command == 'list':
            installed_only = '--installed' in args
            self.list_packages(installed_only)
            return True
        
        elif command == 'search':
            if len(args) < 2:
                print("E: Missing search query")
                return False
            self.search(args[1])
            return True
        
        elif command == 'show':
            if len(args) < 2:
                print("E: Missing package name")
                return False
            self.show(args[1])
            return True
        
        elif command == 'upgrade':
            return self.upgrade()
        
        else:
            print(f"E: Unknown command: {command}")
            return False

"""
System Simulation Layer Entrypoint
Run with: python -m system_simulation_layer
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from system_simulation_layer.package_manager import PackageManager
from system_simulation_layer.git_interface import GitInterface
from system_simulation_layer.mount_manager import MountManager
from system_simulation_layer.system_environment import SystemEnvironment
from system_simulation_layer.system_logger import SystemLogger


def main():
    """Test system simulation layer."""
    print("\n" + "=" * 70)
    print("System Simulation Layer - Test")
    print("=" * 70 + "\n")
    
    # Initialize components
    logger = SystemLogger()
    environment = SystemEnvironment()
    package_manager = PackageManager(logger=logger, environment=environment)
    git_interface = GitInterface(logger=logger)
    mount_manager = MountManager(logger=logger, environment=environment)
    
    # Test package manager
    print("\n--- Testing Package Manager ---\n")
    package_manager.update()
    print()
    package_manager.list_packages()
    print()
    package_manager.install('textutils')
    print()
    package_manager.list_packages(installed_only=True)
    
    # Test git interface
    print("\n--- Testing Git Interface ---\n")
    git_interface.clone('https://github.com/example/testrepo')
    print()
    git_interface.status('./testrepo')
    print()
    git_interface.log('./testrepo')
    
    # Test mount manager
    print("\n--- Testing Mount Manager ---\n")
    mount_manager.mount('usb0', '/mnt/usb')
    print()
    mount_manager.disk_usage()
    print()
    mount_manager.list_devices()
    print()
    mount_manager.unmount('/mnt/usb')
    
    print("\n" + "=" * 70)
    print("✓ System Simulation Layer tests complete")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

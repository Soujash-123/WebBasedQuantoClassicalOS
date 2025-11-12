"""
CLI Shell Entrypoint
Run with: python -m cli_shell
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core import AIOSCore
from devices import DeviceLayer
from filesystem import VirtualFileSystem
from processes import ProcessLayer
from users import UserLayer, UserRole
from system import SystemLayer
from cli_shell.shell import CLIShell


def main():
    """Main entrypoint for CLI shell."""
    print("\n" + "#" * 70)
    print("# AI OS - Complete Operating System")
    print("# Unified CLI Shell - All Layers Integrated")
    print("#" * 70 + "\n")
    
    # Initialize all OS layers
    print("Initializing OS layers...")
    
    # Layer 1: Core
    core = AIOSCore("aios_config.json")
    
    # Layer 8: System (early for logging)
    system = SystemLayer(core)
    system.log_info("AI OS starting up", "STARTUP")
    
    # Layer 2: Devices
    devices = DeviceLayer(core)
    
    # Layer 4: VFS
    vfs = VirtualFileSystem(core, devices)
    
    # Layer 5: Processes
    processes = ProcessLayer(core, devices, vfs, algorithm="fifo")
    
    # Layer 6: Users
    users = UserLayer(core, processes, vfs)
    
    # Auto-login as root
    print("\nLogging in as root...")
    session = users.login("root", "root")
    if session:
        print("✓ Logged in successfully")
        system.log_security("User 'root' logged in")
    
    # Create demo workspace
    print("\nSetting up workspace...")
    try:
        vfs.mkdir("/demo")
        vfs.write("/demo/welcome.txt", "Welcome to AI OS CLI!\nType 'help' for commands.")
        vfs.write("/demo/readme.txt", "This is a unified CLI shell integrating all OS layers.")
        print("✓ Demo workspace created")
    except:
        pass  # Directory may already exist
    
    # Initialize CLI Shell
    print("\nInitializing CLI Shell...")
    shell = CLIShell(
        core_layer=core,
        device_layer=devices,
        vfs_layer=vfs,
        process_layer=processes,
        user_layer=users,
        system_layer=system,
        user="root",
        debug=False
    )
    
    # Show quick start
    print("\n" + "=" * 70)
    print("Quick Start:")
    print("  help          - Show all commands")
    print("  ls            - List files")
    print("  cd /demo      - Change directory")
    print("  cat welcome.txt - Read file")
    print("  ps            - List processes")
    print("  whoami        - Show current user")
    print("  sysinfo       - System information")
    print("  history       - Command history")
    print("  exit          - Quit")
    print("=" * 70 + "\n")
    
    # Start interactive shell
    try:
        shell.start()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    
    # Cleanup
    print("\n" + "=" * 70)
    print("Shutting down AI OS...")
    print("=" * 70)
    
    system.log_info("AI OS shutting down", "SHUTDOWN")
    
    users.shutdown()
    processes.shutdown()
    vfs.shutdown()
    devices.shutdown()
    system.shutdown()
    core.shutdown()
    
    print("\n" + "#" * 70)
    print("# AI OS Shutdown Complete")
    print("# Thank you for using AI OS!")
    print("#" * 70 + "\n")


if __name__ == "__main__":
    main()

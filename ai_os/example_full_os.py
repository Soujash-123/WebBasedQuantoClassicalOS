"""
Full AI OS - Interactive Shell Demo
Demonstrates all 8 layers working together.
"""

from core import AIOSCore
from devices import DeviceLayer
from filesystem import VirtualFileSystem
from processes import ProcessLayer
from users import UserLayer, UserRole
from system import SystemLayer
from shell import ShellLayer


def main():
    """Initialize and run the full AI OS."""
    
    print("\n" + "#" * 60)
    print("# AI OS - Full System Initialization")
    print("# Layers 1-8: Complete Operating System")
    print("#" * 60 + "\n")
    
    # Layer 1: Core
    print("Initializing Layer 1: Core...")
    core = AIOSCore("aios_config.json")
    
    # Layer 8: System Management (initialize early for logging)
    print("\nInitializing Layer 8: System Management...")
    system = SystemLayer(core)
    system.log_info("AI OS starting up", "STARTUP")
    
    # Layer 2: Devices
    print("\nInitializing Layer 2: Devices...")
    devices = DeviceLayer(core)
    system.log_info("Device layer initialized", "DEVICES")
    
    # Layer 4: Virtual File System
    print("\nInitializing Layer 4: Virtual File System...")
    vfs = VirtualFileSystem(core, devices)
    system.log_info("VFS layer initialized", "VFS")
    
    # Layer 5: Process Management
    print("\nInitializing Layer 5: Process Management...")
    processes = ProcessLayer(core, devices, vfs, algorithm="fifo")
    system.log_info("Process layer initialized", "PROCESSES")
    
    # Layer 6: User Management
    print("\nInitializing Layer 6: User Management...")
    users = UserLayer(core, processes, vfs)
    system.log_info("User layer initialized", "USERS")
    
    # Layer 7: Command Shell
    print("\nInitializing Layer 7: Command Shell...")
    shell = ShellLayer(
        core_layer=core,
        device_layer=devices,
        vfs_layer=vfs,
        process_layer=processes,
        user_layer=users,
        system_layer=system
    )
    system.log_info("Shell layer initialized", "SHELL")
    
    # Auto-login as root for demo
    print("\n" + "=" * 60)
    print("Auto-login as root...")
    print("=" * 60)
    users.login("root", "root")
    system.log_security("User 'root' logged in")
    
    # Create demo workspace
    print("\nSetting up demo workspace...")
    vfs.mkdir("/demo")
    vfs.write("/demo/welcome.txt", "Welcome to AI OS!\nA full-featured CLI operating system.")
    vfs.write("/demo/readme.txt", "This is a demonstration of all 8 layers working together.")
    system.log_info("Demo workspace created", "SETUP")
    
    # Set some environment variables
    system.set_env("DEMO_MODE", "true")
    system.set_env("EDITOR", "nano")
    
    # Show system info
    print("\n" + "=" * 60)
    print("System Information")
    print("=" * 60)
    info = system.get_system_info()
    print(f"Name: {info['name']}")
    print(f"Version: {info['version']}")
    print(f"Current User: {users.whoami()}")
    print(f"Current Path: {vfs.pwd()}")
    print(f"Environment Variables: {info['env_vars_count']}")
    print("=" * 60)
    
    # Show available commands
    print("\n" + "=" * 60)
    print("Quick Start Guide")
    print("=" * 60)
    print("\nFilesystem Commands:")
    print("  ls, cd, pwd, mkdir, cat, rm, cp, mv, tree, find")
    print("\nProcess Commands:")
    print("  ps, kill, top")
    print("\nUser Commands:")
    print("  whoami, users, adduser, deluser, passwd")
    print("\nSystem Commands:")
    print("  help, history, alias, clear, printenv, setenv")
    print("\nType 'help' for full command list")
    print("Type 'exit' to quit")
    print("=" * 60 + "\n")
    
    # Start interactive shell
    try:
        shell.start_interactive()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    
    # Shutdown sequence
    print("\n" + "=" * 60)
    print("Shutdown Sequence")
    print("=" * 60)
    
    system.log_info("AI OS shutting down", "SHUTDOWN")
    
    shell.shutdown()
    users.shutdown()
    processes.shutdown()
    vfs.shutdown()
    devices.shutdown()
    system.shutdown()
    core.shutdown()
    
    print("\n" + "#" * 60)
    print("# AI OS Shutdown Complete")
    print("# Thank you for using AI OS!")
    print("#" * 60 + "\n")


if __name__ == "__main__":
    main()

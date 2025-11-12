"""
Example CLI Shell Usage
Demonstrates programmatic use of the CLI shell.
"""

from core import AIOSCore
from devices import DeviceLayer
from filesystem import VirtualFileSystem
from processes import ProcessLayer
from users import UserLayer
from system import SystemLayer
from cli_shell.shell import CLIShell


def main():
    """Demonstrate programmatic CLI usage."""
    
    print("\n" + "=" * 70)
    print("AI OS - Programmatic CLI Usage Example")
    print("=" * 70 + "\n")
    
    # Initialize OS layers
    print("Initializing OS...")
    core = AIOSCore("example_config.json")
    system = SystemLayer(core)
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices)
    processes = ProcessLayer(core, devices, vfs)
    users = UserLayer(core, processes, vfs)
    
    # Login
    users.login("root", "root")
    
    # Initialize CLI Shell
    shell = CLIShell(
        core_layer=core,
        device_layer=devices,
        vfs_layer=vfs,
        process_layer=processes,
        user_layer=users,
        system_layer=system,
        user="root"
    )
    
    # Execute commands programmatically
    print("\n" + "=" * 70)
    print("Executing Commands Programmatically")
    print("=" * 70 + "\n")
    
    commands = [
        "whoami",
        "pwd",
        "mkdir /test",
        "cd /test",
        "pwd",
        "touch file1.txt",
        "touch file2.txt",
        "ls",
        "echo 'Hello World' > greeting.txt",
        "cat greeting.txt",
        "ls | grep txt",
        "tree /test",
        "cd ..",
        "pwd",
        "ps",
        "sysinfo",
        "history 5"
    ]
    
    for cmd in commands:
        print(f"\n> {cmd}")
        print("-" * 70)
        shell.execute(cmd)
    
    # Show statistics
    print("\n" + "=" * 70)
    print("Shell Statistics")
    print("=" * 70)
    
    stats = shell.get_stats()
    print(f"\nSession:")
    print(f"  User: {stats['session']['user']}")
    print(f"  Uptime: {stats['session']['uptime']}")
    print(f"  Current Dir: {stats['session']['current_directory']}")
    
    print(f"\nHistory:")
    print(f"  Total Commands: {stats['history']['total_commands']}")
    print(f"  Successful: {stats['history']['successful']}")
    print(f"  Failed: {stats['history']['failed']}")
    
    print(f"\nCommands Available: {stats['commands_available']}")
    
    # Cleanup
    print("\n" + "=" * 70)
    print("Cleaning up...")
    print("=" * 70)
    
    users.shutdown()
    processes.shutdown()
    vfs.shutdown()
    devices.shutdown()
    system.shutdown()
    core.shutdown()
    
    # Cleanup config file
    import os
    if os.path.exists("example_config.json"):
        os.remove("example_config.json")
    
    print("\n✓ Example complete!\n")


if __name__ == "__main__":
    main()

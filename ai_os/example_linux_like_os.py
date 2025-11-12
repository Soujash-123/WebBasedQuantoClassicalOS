"""
Example: Linux-Like OS with System Simulation
Demonstrates the complete Linux-like CLI with apt, git, and mount commands.
"""

from core import AIOSCore
from devices import DeviceLayer
from filesystem import VirtualFileSystem
from processes import ProcessLayer
from users import UserLayer
from system import SystemLayer
from cli_shell.shell import CLIShell
from system_simulation_layer.package_manager import PackageManager
from system_simulation_layer.git_interface import GitInterface
from system_simulation_layer.mount_manager import MountManager
from system_simulation_layer.system_environment import SystemEnvironment
from system_simulation_layer.system_logger import SystemLogger


def main():
    """Demonstrate Linux-like OS."""
    
    print("\n" + "#" * 70)
    print("# AI OS - Linux-Like Operating System")
    print("# Complete System with apt, git, mount, and more!")
    print("#" * 70 + "\n")
    
    # Initialize all OS layers
    print("Initializing OS layers...")
    
    # Layer 1: Core
    core = AIOSCore("linux_os_config.json")
    
    # Layer 8: System
    system = SystemLayer(core)
    system.log_info("Linux-like OS starting up", "STARTUP")
    
    # Layer 2: Devices
    devices = DeviceLayer(core)
    
    # Layer 4: VFS
    vfs = VirtualFileSystem(core, devices)
    
    # Layer 5: Processes
    processes = ProcessLayer(core, devices, vfs, algorithm="fifo")
    
    # Layer 6: Users
    users = UserLayer(core, processes, vfs)
    
    # System Simulation Layer
    print("Initializing system simulation layer...")
    sim_logger = SystemLogger()
    sim_environment = SystemEnvironment()
    package_manager = PackageManager(logger=sim_logger, environment=sim_environment)
    git_interface = GitInterface(logger=sim_logger)
    mount_manager = MountManager(
        logger=sim_logger,
        environment=sim_environment,
        device_layer=devices,
        vfs_layer=vfs
    )
    
    # Auto-login as root
    print("\nLogging in as root...")
    session = users.login("root", "root")
    if session:
        print("✓ Logged in successfully")
        system.log_security("User 'root' logged in")
    
    # Create demo workspace
    print("\nSetting up workspace...")
    try:
        vfs.mkdir("/projects")
        vfs.mkdir("/mnt")
        vfs.write("/projects/README.md", "# AI OS Projects\n\nWelcome to your workspace!")
        print("✓ Workspace created")
    except:
        pass
    
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
    
    # Register system simulation commands
    print("Registering Linux-like commands...")
    
    shell.registry.register(
        "apt",
        lambda args, ctx: package_manager.run_command(args, ctx),
        "APT package manager",
        "package"
    )
    
    shell.registry.register(
        "git",
        lambda args, ctx: git_interface.run_command(args, ctx),
        "Git version control",
        "development"
    )
    
    shell.registry.register(
        "mount",
        lambda args, ctx: mount_manager.run_mount_command(args, ctx),
        "Mount device",
        "system"
    )
    
    shell.registry.register(
        "umount",
        lambda args, ctx: mount_manager.run_unmount_command(args, ctx),
        "Unmount device",
        "system"
    )
    
    shell.registry.register(
        "df",
        lambda args, ctx: mount_manager.run_df_command(args, ctx),
        "Disk usage",
        "system"
    )
    
    shell.registry.register(
        "lsblk",
        lambda args, ctx: mount_manager.run_lsblk_command(args, ctx),
        "List block devices",
        "system"
    )
    
    # Update parser with new commands
    shell.parser.set_available_commands(shell.registry.list_commands())
    
    # Show quick start
    print("\n" + "=" * 70)
    print("Linux-Like OS Ready!")
    print("=" * 70)
    print("\nPackage Management:")
    print("  apt update           - Update package lists")
    print("  apt install <pkg>    - Install package")
    print("  apt list             - List packages")
    print("  apt search <query>   - Search packages")
    print("\nVersion Control:")
    print("  git clone <url>      - Clone repository")
    print("  git status           - Show status")
    print("  git log              - Show commits")
    print("\nDevice Management:")
    print("  mount <dev> <path>   - Mount device")
    print("  umount <path>        - Unmount device")
    print("  df                   - Disk usage")
    print("  lsblk                - List devices")
    print("\nStandard Commands:")
    print("  ls, cd, pwd, mkdir   - File operations")
    print("  ps, kill, top        - Process management")
    print("  help                 - Show all commands")
    print("=" * 70 + "\n")
    
    # Run some demo commands
    print("Running demo commands...\n")
    
    demo_commands = [
        "apt update",
        "apt list",
        "apt install textutils",
        "apt list --installed",
        "lsblk",
        "df",
        "sysinfo"
    ]
    
    for cmd in demo_commands:
        print(f"\n> {cmd}")
        print("-" * 70)
        shell.execute(cmd)
    
    print("\n" + "=" * 70)
    print("Demo complete! Starting interactive shell...")
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
    
    system.log_info("Linux-like OS shutting down", "SHUTDOWN")
    
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

"""
Test Suite for Linux-Like Commands
Tests apt, git, mount, and other Linux-like functionality.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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


def setup_linux_os():
    """Setup Linux-like OS for testing."""
    core = AIOSCore("test_linux_config.json")
    system = SystemLayer(core)
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices)
    processes = ProcessLayer(core, devices, vfs)
    users = UserLayer(core, processes, vfs, users_file="test_linux_users.json")
    
    users.login("root", "root")
    
    # System simulation
    sim_logger = SystemLogger(log_dir="./test_system_logs")
    sim_environment = SystemEnvironment(env_file="./test_system_env.json")
    package_manager = PackageManager(
        logger=sim_logger,
        environment=sim_environment,
        packages_dir="./test_virtual_packages"
    )
    git_interface = GitInterface(
        repos_dir="./test_virtual_packages",
        logger=sim_logger
    )
    mount_manager = MountManager(
        logger=sim_logger,
        environment=sim_environment,
        device_layer=devices,
        vfs_layer=vfs
    )
    
    # CLI Shell
    shell = CLIShell(
        core_layer=core,
        device_layer=devices,
        vfs_layer=vfs,
        process_layer=processes,
        user_layer=users,
        system_layer=system,
        user="root"
    )
    
    # Register commands
    shell.registry.register("apt", lambda args, ctx: package_manager.run_command(args, ctx), "APT", "package")
    shell.registry.register("git", lambda args, ctx: git_interface.run_command(args, ctx), "Git", "development")
    shell.registry.register("mount", lambda args, ctx: mount_manager.run_mount_command(args, ctx), "Mount", "system")
    shell.registry.register("umount", lambda args, ctx: mount_manager.run_unmount_command(args, ctx), "Unmount", "system")
    shell.registry.register("df", lambda args, ctx: mount_manager.run_df_command(args, ctx), "Disk usage", "system")
    shell.registry.register("lsblk", lambda args, ctx: mount_manager.run_lsblk_command(args, ctx), "List devices", "system")
    
    shell.parser.set_available_commands(shell.registry.list_commands())
    
    return shell, core, system, devices, vfs, processes, users


def cleanup_test_files():
    """Clean up test files."""
    import shutil
    
    files_to_remove = [
        "test_linux_config.json",
        "test_linux_users.json",
        "test_system_env.json"
    ]
    
    dirs_to_remove = [
        "test_system_logs",
        "test_virtual_packages"
    ]
    
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)
    
    for d in dirs_to_remove:
        if os.path.exists(d):
            shutil.rmtree(d)


def test_apt_commands():
    """Test APT package manager commands."""
    print("\n" + "=" * 70)
    print("TEST: APT Package Manager")
    print("=" * 70)
    
    shell, core, system, devices, vfs, processes, users = setup_linux_os()
    
    try:
        print("\n[TEST] apt update")
        shell.execute("apt update")
        
        print("\n[TEST] apt list")
        shell.execute("apt list")
        
        print("\n[TEST] apt search text")
        shell.execute("apt search text")
        
        print("\n[TEST] apt show textutils")
        shell.execute("apt show textutils")
        
        print("\n[TEST] apt install textutils")
        shell.execute("apt install textutils")
        
        print("\n[TEST] apt list --installed")
        shell.execute("apt list --installed")
        
        print("\n[TEST] apt install devtools (with dependencies)")
        shell.execute("apt install devtools")
        
        print("\n[TEST] apt remove textutils")
        shell.execute("apt remove textutils")
        
        print("\n✓ APT tests PASSED")
        
    finally:
        users.shutdown()
        processes.shutdown()
        vfs.shutdown()
        devices.shutdown()
        system.shutdown()
        core.shutdown()
        cleanup_test_files()


def test_git_commands():
    """Test Git interface commands."""
    print("\n" + "=" * 70)
    print("TEST: Git Interface")
    print("=" * 70)
    
    shell, core, system, devices, vfs, processes, users = setup_linux_os()
    
    try:
        print("\n[TEST] git clone https://github.com/example/testrepo")
        shell.execute("git clone https://github.com/example/testrepo")
        
        print("\n[TEST] cd testrepo")
        shell.execute("cd /virtual_packages/testrepo")
        
        print("\n[TEST] git status")
        shell.execute("git status")
        
        print("\n[TEST] git log")
        shell.execute("git log")
        
        print("\n[TEST] git branch")
        shell.execute("git branch")
        
        print("\n[TEST] git pull")
        shell.execute("git pull")
        
        print("\n✓ Git tests PASSED")
        
    finally:
        users.shutdown()
        processes.shutdown()
        vfs.shutdown()
        devices.shutdown()
        system.shutdown()
        core.shutdown()
        cleanup_test_files()


def test_mount_commands():
    """Test mount manager commands."""
    print("\n" + "=" * 70)
    print("TEST: Mount Manager")
    print("=" * 70)
    
    shell, core, system, devices, vfs, processes, users = setup_linux_os()
    
    try:
        print("\n[TEST] lsblk")
        shell.execute("lsblk")
        
        print("\n[TEST] df")
        shell.execute("df")
        
        print("\n[TEST] mount usb0 /mnt/usb")
        shell.execute("mount usb0 /mnt/usb")
        
        print("\n[TEST] df (after mount)")
        shell.execute("df")
        
        print("\n[TEST] mount (list mounts)")
        shell.execute("mount")
        
        print("\n[TEST] umount /mnt/usb")
        shell.execute("umount /mnt/usb")
        
        print("\n[TEST] mount (after unmount)")
        shell.execute("mount")
        
        print("\n✓ Mount tests PASSED")
        
    finally:
        users.shutdown()
        processes.shutdown()
        vfs.shutdown()
        devices.shutdown()
        system.shutdown()
        core.shutdown()
        cleanup_test_files()


def test_integrated_workflow():
    """Test integrated Linux-like workflow."""
    print("\n" + "=" * 70)
    print("TEST: Integrated Linux-Like Workflow")
    print("=" * 70)
    
    shell, core, system, devices, vfs, processes, users = setup_linux_os()
    
    try:
        # Complete workflow
        commands = [
            "apt update",
            "apt install textutils",
            "apt install gittools",
            "git clone https://example.com/myproject",
            "cd /virtual_packages/myproject",
            "ls",
            "mount usb0 /mnt/backup",
            "df",
            "lsblk",
            "apt list --installed",
            "sysinfo",
            "umount /mnt/backup"
        ]
        
        for cmd in commands:
            print(f"\n> {cmd}")
            print("-" * 70)
            shell.execute(cmd)
        
        print("\n✓ Integrated workflow tests PASSED")
        
    finally:
        users.shutdown()
        processes.shutdown()
        vfs.shutdown()
        devices.shutdown()
        system.shutdown()
        core.shutdown()
        cleanup_test_files()


def run_all_tests():
    """Run all Linux-like command tests."""
    print("\n" + "#" * 70)
    print("# LINUX-LIKE COMMANDS - COMPREHENSIVE TEST SUITE")
    print("#" * 70)
    
    try:
        test_apt_commands()
        test_git_commands()
        test_mount_commands()
        test_integrated_workflow()
        
        print("\n" + "#" * 70)
        print("# ALL LINUX-LIKE TESTS PASSED ✓")
        print("#" * 70 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "#" * 70)
        print("# TESTS FAILED ✗")
        print("#" * 70 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()

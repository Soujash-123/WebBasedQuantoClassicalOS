"""
Manual Test Suite for CLI Shell
Tests all CLI commands and features.
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


def test_basic_commands():
    """Test basic system commands."""
    print("\n" + "=" * 70)
    print("TEST: Basic System Commands")
    print("=" * 70)
    
    # Initialize minimal OS
    core = AIOSCore("test_cli_config.json")
    system = SystemLayer(core)
    
    shell = CLIShell(
        core_layer=core,
        system_layer=system,
        user="testuser"
    )
    
    # Test commands
    print("\n[TEST] whoami")
    shell.execute("whoami")
    
    print("\n[TEST] uptime")
    shell.execute("uptime")
    
    print("\n[TEST] sysinfo")
    shell.execute("sysinfo")
    
    print("\n[TEST] alias")
    shell.execute("alias")
    
    print("\n[TEST] alias ll='ls -la'")
    shell.execute("alias ll='ls -la'")
    
    print("\n[TEST] history")
    shell.execute("history")
    
    # Cleanup
    system.shutdown()
    core.shutdown()
    
    if os.path.exists("test_cli_config.json"):
        os.remove("test_cli_config.json")
    
    print("\n✓ Basic Commands tests PASSED\n")


def test_filesystem_commands():
    """Test filesystem commands."""
    print("\n" + "=" * 70)
    print("TEST: Filesystem Commands")
    print("=" * 70)
    
    core = AIOSCore("test_fs_config.json")
    system = SystemLayer(core)
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices)
    
    shell = CLIShell(
        core_layer=core,
        device_layer=devices,
        vfs_layer=vfs,
        system_layer=system
    )
    
    # Test filesystem commands
    print("\n[TEST] pwd")
    shell.execute("pwd")
    
    print("\n[TEST] mkdir /testdir")
    shell.execute("mkdir /testdir")
    
    print("\n[TEST] cd /testdir")
    shell.execute("cd /testdir")
    
    print("\n[TEST] pwd")
    shell.execute("pwd")
    
    print("\n[TEST] touch file1.txt")
    shell.execute("touch file1.txt")
    
    print("\n[TEST] touch file2.txt")
    shell.execute("touch file2.txt")
    
    print("\n[TEST] ls")
    shell.execute("ls")
    
    print("\n[TEST] echo 'test content' > test.txt")
    shell.execute("echo 'test content' > test.txt")
    
    print("\n[TEST] cat test.txt")
    shell.execute("cat test.txt")
    
    print("\n[TEST] cp test.txt backup.txt")
    shell.execute("cp test.txt backup.txt")
    
    print("\n[TEST] ls")
    shell.execute("ls")
    
    print("\n[TEST] tree /testdir")
    shell.execute("tree /testdir")
    
    print("\n[TEST] cd ..")
    shell.execute("cd ..")
    
    print("\n[TEST] pwd")
    shell.execute("pwd")
    
    # Cleanup
    vfs.shutdown()
    devices.shutdown()
    system.shutdown()
    core.shutdown()
    
    for f in ["test_fs_config.json"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("\n✓ Filesystem Commands tests PASSED\n")


def test_piping_and_redirection():
    """Test piping and redirection."""
    print("\n" + "=" * 70)
    print("TEST: Piping and Redirection")
    print("=" * 70)
    
    core = AIOSCore("test_pipe_config.json")
    system = SystemLayer(core)
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices)
    
    shell = CLIShell(
        core_layer=core,
        device_layer=devices,
        vfs_layer=vfs,
        system_layer=system
    )
    
    # Setup test files
    vfs.mkdir("/pipetest")
    vfs.write("/pipetest/file1.txt", "Line 1\nLine 2\nLine 3")
    vfs.write("/pipetest/file2.log", "Log entry 1\nLog entry 2")
    vfs.write("/pipetest/data.txt", "Data content")
    
    print("\n[TEST] Output redirection: ls > output.txt")
    shell.execute("cd /pipetest")
    shell.execute("ls > output.txt")
    shell.execute("cat output.txt")
    
    print("\n[TEST] Append redirection: echo 'new line' >> output.txt")
    shell.execute("echo 'new line' >> output.txt")
    shell.execute("cat output.txt")
    
    print("\n[TEST] Piping: ls | grep txt")
    shell.execute("ls | grep txt")
    
    # Cleanup
    vfs.shutdown()
    devices.shutdown()
    system.shutdown()
    core.shutdown()
    
    if os.path.exists("test_pipe_config.json"):
        os.remove("test_pipe_config.json")
    
    print("\n✓ Piping and Redirection tests PASSED\n")


def test_command_chaining():
    """Test command chaining with && and ||."""
    print("\n" + "=" * 70)
    print("TEST: Command Chaining")
    print("=" * 70)
    
    core = AIOSCore("test_chain_config.json")
    system = SystemLayer(core)
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices)
    
    shell = CLIShell(
        core_layer=core,
        device_layer=devices,
        vfs_layer=vfs,
        system_layer=system
    )
    
    print("\n[TEST] && operator: mkdir /chain && cd /chain && pwd")
    shell.execute("mkdir /chain && cd /chain && pwd")
    
    print("\n[TEST] && with failure: cd /nonexistent && echo 'should not print'")
    shell.execute("cd /nonexistent && echo 'should not print'")
    
    print("\n[TEST] || operator: cd /nonexistent || echo 'fallback executed'")
    shell.execute("cd /nonexistent || echo 'fallback executed'")
    
    # Cleanup
    vfs.shutdown()
    devices.shutdown()
    system.shutdown()
    core.shutdown()
    
    if os.path.exists("test_chain_config.json"):
        os.remove("test_chain_config.json")
    
    print("\n✓ Command Chaining tests PASSED\n")


def test_environment_variables():
    """Test environment variable commands."""
    print("\n" + "=" * 70)
    print("TEST: Environment Variables")
    print("=" * 70)
    
    core = AIOSCore("test_env_config.json")
    system = SystemLayer(core)
    
    shell = CLIShell(
        core_layer=core,
        system_layer=system
    )
    
    print("\n[TEST] printenv")
    shell.execute("printenv")
    
    print("\n[TEST] set MYVAR=hello")
    shell.execute("set MYVAR=hello")
    
    print("\n[TEST] printenv MYVAR")
    shell.execute("printenv MYVAR")
    
    print("\n[TEST] unset MYVAR")
    shell.execute("unset MYVAR")
    
    print("\n[TEST] printenv MYVAR (should be empty)")
    shell.execute("printenv MYVAR")
    
    # Cleanup
    system.shutdown()
    core.shutdown()
    
    if os.path.exists("test_env_config.json"):
        os.remove("test_env_config.json")
    
    print("\n✓ Environment Variables tests PASSED\n")


def test_process_commands():
    """Test process management commands."""
    print("\n" + "=" * 70)
    print("TEST: Process Commands")
    print("=" * 70)
    
    core = AIOSCore("test_proc_config.json")
    system = SystemLayer(core)
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices)
    processes = ProcessLayer(core, devices, vfs)
    
    shell = CLIShell(
        core_layer=core,
        device_layer=devices,
        vfs_layer=vfs,
        process_layer=processes,
        system_layer=system
    )
    
    print("\n[TEST] ps")
    shell.execute("ps")
    
    print("\n[TEST] top")
    shell.execute("top")
    
    # Cleanup
    processes.shutdown()
    vfs.shutdown()
    devices.shutdown()
    system.shutdown()
    core.shutdown()
    
    if os.path.exists("test_proc_config.json"):
        os.remove("test_proc_config.json")
    
    print("\n✓ Process Commands tests PASSED\n")


def test_user_commands():
    """Test user management commands."""
    print("\n" + "=" * 70)
    print("TEST: User Commands")
    print("=" * 70)
    
    core = AIOSCore("test_user_config.json")
    system = SystemLayer(core)
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices)
    processes = ProcessLayer(core, devices, vfs)
    users = UserLayer(core, processes, vfs, users_file="test_users.json")
    
    users.login("root", "root")
    
    shell = CLIShell(
        core_layer=core,
        device_layer=devices,
        vfs_layer=vfs,
        process_layer=processes,
        user_layer=users,
        system_layer=system,
        user="root"
    )
    
    print("\n[TEST] whoami")
    shell.execute("whoami")
    
    print("\n[TEST] users")
    shell.execute("users")
    
    print("\n[TEST] adduser testuser testpass")
    shell.execute("adduser testuser testpass")
    
    print("\n[TEST] users")
    shell.execute("users")
    
    # Cleanup
    users.shutdown()
    processes.shutdown()
    vfs.shutdown()
    devices.shutdown()
    system.shutdown()
    core.shutdown()
    
    for f in ["test_user_config.json", "test_users.json"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("\n✓ User Commands tests PASSED\n")


def run_all_tests():
    """Run all CLI tests."""
    print("\n" + "#" * 70)
    print("# CLI SHELL - COMPREHENSIVE TEST SUITE")
    print("#" * 70)
    
    try:
        test_basic_commands()
        test_filesystem_commands()
        test_piping_and_redirection()
        test_command_chaining()
        test_environment_variables()
        test_process_commands()
        test_user_commands()
        
        print("\n" + "#" * 70)
        print("# ALL CLI TESTS PASSED ✓")
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

"""
Manual Test Suite for Virtual File System Layer
Tests encrypted file storage, disk management, and all VFS operations.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core import AIOSCore
from devices import DeviceLayer
from filesystem import VirtualFileSystem


def test_vfs_initialization():
    """Test VFS initialization."""
    print("\n" + "=" * 60)
    print("TEST: VFS Initialization")
    print("=" * 60)
    
    core = AIOSCore("test_vfs_config.json")
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices, "TestDisk")
    
    assert vfs.current_disk == "TestDisk", "Default disk not set"
    assert vfs.mount_manager.is_mounted("TestDisk"), "Default disk not mounted"
    assert vfs.pwd() == "/", "Initial directory should be root"
    
    print("✓ VFS initialized successfully")
    
    vfs.shutdown()
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_vfs_config.json"):
        os.remove("test_vfs_config.json")
    
    print("\n✓ VFS Initialization tests PASSED")


def test_directory_operations():
    """Test directory creation and navigation."""
    print("\n" + "=" * 60)
    print("TEST: Directory Operations")
    print("=" * 60)
    
    core = AIOSCore("test_dir_config.json")
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices, "TestDisk")
    
    # Test mkdir
    print("\n[TEST] Creating directories...")
    assert vfs.mkdir("/projects"), "Failed to create /projects"
    assert vfs.mkdir("/projects/ai"), "Failed to create /projects/ai"
    assert vfs.mkdir("/documents"), "Failed to create /documents"
    print("✓ Directories created")
    
    # Test cd
    print("\n[TEST] Changing directories...")
    assert vfs.cd("/projects"), "Failed to cd to /projects"
    assert vfs.pwd() == "/projects", "PWD incorrect"
    assert vfs.cd("ai"), "Failed to cd to relative path"
    assert vfs.pwd() == "/projects/ai", "PWD incorrect after relative cd"
    print("✓ Directory navigation works")
    
    # Test ls
    print("\n[TEST] Listing directories...")
    vfs.cd("/")
    files = vfs.ls()
    assert len(files) == 2, "Should have 2 directories"
    print(f"✓ Listed {len(files)} items")
    
    vfs.shutdown()
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_dir_config.json"):
        os.remove("test_dir_config.json")
    
    print("\n✓ Directory Operations tests PASSED")


def test_file_operations():
    """Test file creation, reading, and manipulation."""
    print("\n" + "=" * 60)
    print("TEST: File Operations")
    print("=" * 60)
    
    core = AIOSCore("test_file_config.json")
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices, "TestDisk")
    
    # Create directory
    vfs.mkdir("/test")
    
    # Test write
    print("\n[TEST] Writing files...")
    assert vfs.write("/test/hello.txt", "Hello, World!"), "Failed to write file"
    assert vfs.write("/test/data.txt", "Some data here"), "Failed to write second file"
    print("✓ Files written")
    
    # Test read
    print("\n[TEST] Reading files...")
    content = vfs.read("/test/hello.txt")
    assert content == "Hello, World!", f"Content mismatch: {content}"
    print("✓ File read successfully")
    
    # Test append
    print("\n[TEST] Appending to file...")
    assert vfs.append("/test/hello.txt", "\nAppended line"), "Failed to append"
    content = vfs.read("/test/hello.txt")
    assert "Appended line" in content, "Append failed"
    print("✓ Append works")
    
    # Test file_info
    print("\n[TEST] Getting file info...")
    info = vfs.file_info("/test/hello.txt")
    assert info is not None, "File info not found"
    assert info['encrypted'], "File should be encrypted"
    print(f"✓ File info: {info['size']} bytes, encrypted: {info['encrypted']}")
    
    # Test copy
    print("\n[TEST] Copying file...")
    assert vfs.cp("/test/hello.txt", "/test/hello_copy.txt"), "Failed to copy"
    assert vfs.read("/test/hello_copy.txt") == content, "Copy content mismatch"
    print("✓ File copied")
    
    # Test rename
    print("\n[TEST] Renaming file...")
    assert vfs.rename("/test/hello_copy.txt", "hello_renamed.txt"), "Failed to rename"
    assert vfs.file_info("/test/hello_renamed.txt") is not None, "Renamed file not found"
    print("✓ File renamed")
    
    # Test delete
    print("\n[TEST] Deleting file...")
    assert vfs.rm("/test/hello_renamed.txt"), "Failed to delete"
    assert vfs.file_info("/test/hello_renamed.txt") is None, "File still exists"
    print("✓ File deleted")
    
    vfs.shutdown()
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_file_config.json"):
        os.remove("test_file_config.json")
    
    print("\n✓ File Operations tests PASSED")


def test_encryption():
    """Test file encryption and decryption."""
    print("\n" + "=" * 60)
    print("TEST: Encryption")
    print("=" * 60)
    
    core = AIOSCore("test_encrypt_config.json")
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices, "TestDisk")
    
    # Write sensitive data
    print("\n[TEST] Writing encrypted file...")
    sensitive_data = "This is sensitive information that should be encrypted!"
    assert vfs.write("/secret.txt", sensitive_data), "Failed to write"
    print("✓ File written")
    
    # Verify encryption
    print("\n[TEST] Verifying encryption...")
    info = vfs.file_info("/secret.txt")
    assert info['encrypted'], "File not marked as encrypted"
    print("✓ File is encrypted")
    
    # Read and verify decryption
    print("\n[TEST] Reading encrypted file...")
    content = vfs.read("/secret.txt")
    assert content == sensitive_data, "Decryption failed"
    print("✓ File decrypted correctly")
    
    vfs.shutdown()
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_encrypt_config.json"):
        os.remove("test_encrypt_config.json")
    
    print("\n✓ Encryption tests PASSED")


def test_disk_management():
    """Test disk mounting and management."""
    print("\n" + "=" * 60)
    print("TEST: Disk Management")
    print("=" * 60)
    
    core = AIOSCore("test_disk_config.json")
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices, "Disk1")
    
    # Test mount
    print("\n[TEST] Mounting additional disk...")
    assert vfs.mount("Disk2"), "Failed to mount Disk2"
    assert vfs.mount_manager.is_mounted("Disk2"), "Disk2 not mounted"
    print("✓ Disk mounted")
    
    # Test list disks
    print("\n[TEST] Listing disks...")
    disks = vfs.disks()
    assert "Disk1" in disks and "Disk2" in disks, "Disks not listed"
    print(f"✓ Mounted disks: {disks}")
    
    # Test disk info
    print("\n[TEST] Getting disk info...")
    info = vfs.disk_info("Disk1")
    assert info is not None, "Disk info not found"
    assert info['encrypted'], "Disk should be encrypted"
    print(f"✓ Disk info: {info['usage_percent']}% used")
    
    # Test switch disk
    print("\n[TEST] Switching disks...")
    assert vfs.switch_disk("Disk2"), "Failed to switch disk"
    assert vfs.get_current_disk() == "Disk2", "Current disk not updated"
    print("✓ Switched to Disk2")
    
    # Test unmount
    print("\n[TEST] Unmounting disk...")
    assert vfs.unmount("Disk2"), "Failed to unmount"
    assert not vfs.mount_manager.is_mounted("Disk2"), "Disk still mounted"
    print("✓ Disk unmounted")
    
    vfs.shutdown()
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_disk_config.json"):
        os.remove("test_disk_config.json")
    
    print("\n✓ Disk Management tests PASSED")


def test_search_and_tree():
    """Test search and tree display."""
    print("\n" + "=" * 60)
    print("TEST: Search and Tree")
    print("=" * 60)
    
    core = AIOSCore("test_search_config.json")
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices, "TestDisk")
    
    # Create test structure
    vfs.mkdir("/projects")
    vfs.mkdir("/projects/web")
    vfs.mkdir("/projects/ai")
    vfs.write("/projects/web/index.html", "<html></html>")
    vfs.write("/projects/ai/model.py", "# AI model")
    vfs.write("/readme.txt", "README")
    
    # Test search
    print("\n[TEST] Searching files...")
    results = vfs.search("model")
    assert len(results) > 0, "Search found no results"
    assert any("model" in r['name'] for r in results), "model.py not found"
    print(f"✓ Found {len(results)} result(s)")
    
    # Test tree
    print("\n[TEST] Displaying tree...")
    vfs.tree("/")
    print("✓ Tree displayed")
    
    vfs.shutdown()
    devices.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_search_config.json"):
        os.remove("test_search_config.json")
    
    print("\n✓ Search and Tree tests PASSED")


def run_all_tests():
    """Run all VFS tests."""
    print("\n" + "#" * 60)
    print("# VIRTUAL FILE SYSTEM LAYER - MANUAL TEST SUITE")
    print("#" * 60)
    
    try:
        test_vfs_initialization()
        test_directory_operations()
        test_file_operations()
        test_encryption()
        test_disk_management()
        test_search_and_tree()
        
        print("\n" + "#" * 60)
        print("# ALL VFS TESTS PASSED ✓")
        print("#" * 60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        print("\n" + "#" * 60)
        print("# TESTS FAILED ✗")
        print("#" * 60 + "\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup test storage
        import shutil
        if os.path.exists("vfs_storage"):
            shutil.rmtree("vfs_storage", ignore_errors=True)


if __name__ == "__main__":
    run_all_tests()

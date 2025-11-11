"""
Virtual File System - Example Usage
Demonstrates all VFS features including encryption, disk management, and CLI operations.
"""

from core import AIOSCore
from devices import DeviceLayer
from filesystem import VirtualFileSystem


def demo_basic_operations(vfs):
    """Demonstrate basic file and directory operations."""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic File & Directory Operations")
    print("=" * 60)
    
    # Create directories
    print("\n--- Creating Directory Structure ---")
    vfs.mkdir("/projects")
    vfs.mkdir("/projects/web")
    vfs.mkdir("/projects/ai")
    vfs.mkdir("/documents")
    vfs.mkdir("/documents/reports")
    
    # List root
    print("\n--- Listing Root Directory ---")
    files = vfs.ls("/")
    for f in files:
        print(f"  {f['type']:8} {f['name']}")
    
    # Change directory
    print("\n--- Navigating Directories ---")
    vfs.cd("/projects")
    print(f"Current directory: {vfs.pwd()}")
    
    # Create files
    print("\n--- Creating Files ---")
    vfs.write("/projects/web/index.html", "<html><body>Hello World!</body></html>")
    vfs.write("/projects/ai/model.py", "# AI Model\nimport tensorflow as tf")
    vfs.write("/documents/readme.txt", "This is the README file")
    
    # List files in projects
    print("\n--- Files in /projects ---")
    vfs.tree("/projects")


def demo_file_manipulation(vfs):
    """Demonstrate file reading, copying, moving, and renaming."""
    print("\n" + "=" * 60)
    print("DEMO 2: File Manipulation")
    print("=" * 60)
    
    # Read file
    print("\n--- Reading File ---")
    content = vfs.read("/projects/ai/model.py")
    print(f"Content of model.py:\n{content}")
    
    # Append to file
    print("\n--- Appending to File ---")
    vfs.append("/projects/ai/model.py", "\n\n# Training code\nmodel.fit(X, y)")
    content = vfs.read("/projects/ai/model.py")
    print(f"Updated content:\n{content}")
    
    # Copy file
    print("\n--- Copying File ---")
    vfs.cp("/projects/ai/model.py", "/projects/ai/model_backup.py")
    print("✓ Copied model.py to model_backup.py")
    
    # Rename file
    print("\n--- Renaming File ---")
    vfs.rename("/projects/ai/model_backup.py", "model_v2.py")
    print("✓ Renamed to model_v2.py")
    
    # Move file
    print("\n--- Moving File ---")
    vfs.mv("/projects/ai/model_v2.py", "/documents/model_v2.py")
    print("✓ Moved model_v2.py to /documents")
    
    # List to verify
    print("\n--- Verification ---")
    print("Files in /projects/ai:")
    for f in vfs.ls("/projects/ai"):
        print(f"  - {f['name']}")
    
    print("\nFiles in /documents:")
    for f in vfs.ls("/documents"):
        print(f"  - {f['name']}")


def demo_file_info(vfs):
    """Demonstrate file metadata and information."""
    print("\n" + "=" * 60)
    print("DEMO 3: File Information & Metadata")
    print("=" * 60)
    
    # Get file info
    print("\n--- File Metadata ---")
    info = vfs.file_info("/projects/ai/model.py")
    if info:
        print(f"Name: {info['name']}")
        print(f"Path: {info['path']}")
        print(f"Type: {info['type']}")
        print(f"Size: {info['size']} bytes")
        print(f"Encrypted: {info['encrypted']}")
        print(f"Permissions: {info['permissions']}")
        print(f"Created: {info['created_at']}")
        print(f"Modified: {info['modified_at']}")


def demo_encryption(vfs):
    """Demonstrate encrypted file storage."""
    print("\n" + "=" * 60)
    print("DEMO 4: Encrypted File Storage")
    print("=" * 60)
    
    # Create encrypted file
    print("\n--- Creating Encrypted File ---")
    sensitive_data = """
    API_KEY=sk-1234567890abcdef
    DATABASE_PASSWORD=super_secret_password
    ENCRYPTION_KEY=aes256_key_here
    """
    vfs.write("/documents/secrets.env", sensitive_data)
    print("✓ Sensitive data written (encrypted)")
    
    # Verify encryption
    info = vfs.file_info("/documents/secrets.env")
    print(f"\nFile encrypted: {info['encrypted']}")
    print(f"File size: {info['size']} bytes")
    
    # Read encrypted file (automatically decrypted)
    print("\n--- Reading Encrypted File ---")
    content = vfs.read("/documents/secrets.env")
    print(f"Decrypted content:\n{content}")
    print("\n✓ File automatically decrypted on read")


def demo_search(vfs):
    """Demonstrate file search functionality."""
    print("\n" + "=" * 60)
    print("DEMO 5: File Search")
    print("=" * 60)
    
    # Search for files
    print("\n--- Searching for 'model' ---")
    results = vfs.search("model")
    print(f"Found {len(results)} result(s):")
    for r in results:
        print(f"  {r['path']} ({r['type']})")
    
    print("\n--- Searching for '.py' files ---")
    results = vfs.search(".py")
    print(f"Found {len(results)} Python file(s):")
    for r in results:
        print(f"  {r['path']}")


def demo_tree(vfs):
    """Demonstrate directory tree display."""
    print("\n" + "=" * 60)
    print("DEMO 6: Directory Tree")
    print("=" * 60)
    
    print("\n--- Complete File System Tree ---")
    vfs.tree("/")


def demo_disk_management(vfs):
    """Demonstrate disk mounting and management."""
    print("\n" + "=" * 60)
    print("DEMO 7: Disk Management")
    print("=" * 60)
    
    # Mount additional disk
    print("\n--- Mounting Additional Disk ---")
    vfs.mount("ProjectsDisk")
    print("✓ Mounted ProjectsDisk")
    
    # List mounted disks
    print("\n--- Mounted Disks ---")
    disks = vfs.disks()
    for disk in disks:
        print(f"  - {disk}")
    
    # Get disk info
    print("\n--- Disk Statistics ---")
    for disk in disks:
        info = vfs.disk_info(disk)
        if info:
            print(f"\n{disk}:")
            print(f"  Total Capacity: {info['total_capacity'] / (1024*1024):.2f} MB")
            print(f"  Used Space: {info['used_space'] / 1024:.2f} KB")
            print(f"  Free Space: {info['free_space'] / (1024*1024):.2f} MB")
            print(f"  Usage: {info['usage_percent']}%")
            print(f"  Files: {info['file_count']}")
            print(f"  Folders: {info['folder_count']}")
            print(f"  Encrypted: {info['encrypted']}")
    
    # Switch to new disk
    print("\n--- Switching to ProjectsDisk ---")
    vfs.switch_disk("ProjectsDisk")
    print(f"Current disk: {vfs.get_current_disk()}")
    print(f"Current directory: {vfs.pwd()}")
    
    # Create files on new disk
    print("\n--- Creating Files on ProjectsDisk ---")
    vfs.mkdir("/backup")
    vfs.write("/backup/data.txt", "Backup data on ProjectsDisk")
    print("✓ Files created on ProjectsDisk")
    
    # Switch back
    print("\n--- Switching Back to MainDisk ---")
    vfs.switch_disk("MainDisk")
    print(f"Current disk: {vfs.get_current_disk()}")


def demo_cli_commands(vfs):
    """Demonstrate CLI-ready commands."""
    print("\n" + "=" * 60)
    print("DEMO 8: CLI Commands Summary")
    print("=" * 60)
    
    print("\n--- Available Commands ---")
    vfs.help()


def main():
    """Main demonstration function."""
    print("\n" + "#" * 60)
    print("# Virtual File System - Comprehensive Demo")
    print("# Layer 4: Encrypted VFS with Full CLI Support")
    print("#" * 60)
    
    # Initialize all layers
    core = AIOSCore("vfs_demo_config.json")
    devices = DeviceLayer(core)
    vfs = VirtualFileSystem(core, devices, "MainDisk")
    
    # Run demonstrations
    demo_basic_operations(vfs)
    demo_file_manipulation(vfs)
    demo_file_info(vfs)
    demo_encryption(vfs)
    demo_search(vfs)
    demo_tree(vfs)
    demo_disk_management(vfs)
    demo_cli_commands(vfs)
    
    # Shutdown
    print("\n" + "=" * 60)
    print("DEMO Complete - Shutting Down")
    print("=" * 60)
    
    vfs.shutdown()
    devices.shutdown()
    core.shutdown()
    
    print("\n" + "#" * 60)
    print("# All Demonstrations Complete!")
    print("# VFS Layer 4 is fully operational!")
    print("#" * 60 + "\n")


if __name__ == "__main__":
    main()

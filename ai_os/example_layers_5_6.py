"""
Layers 5 & 6 - Example Usage
Demonstrates Process Management and User Authentication integration.
"""

import time
from core import AIOSCore
from devices import DeviceLayer
from filesystem import VirtualFileSystem
from processes import ProcessLayer
from users import UserLayer, UserRole


# Sample process functions
def backup_task(vfs, source, dest):
    """Sample backup process."""
    print(f"[BackupTask] Backing up {source} to {dest}...")
    time.sleep(1)
    content = vfs.read(source)
    if content:
        vfs.write(dest, content)
        print(f"[BackupTask] Backup complete!")
        return f"Backed up {source}"
    return "Backup failed"


def system_monitor(duration=3):
    """Sample system monitoring process."""
    print("[SystemMonitor] Starting system monitoring...")
    for i in range(duration):
        print(f"[SystemMonitor] Monitoring... ({i+1}/{duration})")
        time.sleep(1)
    print("[SystemMonitor] Monitoring complete!")
    return "Monitoring finished"


def file_processor(vfs, filename, operation="read"):
    """Sample file processing."""
    print(f"[FileProcessor] Processing {filename}...")
    time.sleep(0.5)
    if operation == "read":
        content = vfs.read(filename)
        print(f"[FileProcessor] Read {len(content) if content else 0} bytes")
    return f"Processed {filename}"


def demo_user_authentication():
    """Demonstrate user authentication."""
    print("\n" + "=" * 60)
    print("DEMO 1: User Authentication")
    print("=" * 60)
    
    core = AIOSCore("demo_layers_config.json")
    users = UserLayer(core, users_file="demo_users.json")
    
    # Show default users
    print("\n--- Default Users ---")
    for user in users.listusers():
        print(f"  {user['username']:10} - {user['role']:10} (logins: {user['login_count']})")
    
    # Login as root
    print("\n--- Logging in as root ---")
    session = users.login("root", "root")
    if session:
        print(f"✓ Logged in as: {users.whoami()}")
        print(f"  Session ID: {session.session_id[:16]}...")
    
    # Create new user
    print("\n--- Creating New User ---")
    if users.adduser("alice", "alice123", UserRole.USER):
        print("✓ Created user: alice")
    
    # Switch user
    print("\n--- Switching to alice ---")
    if users.switch_user("alice", "alice123"):
        print(f"✓ Now logged in as: {users.whoami()}")
    
    # Check permissions
    print("\n--- Checking Permissions ---")
    print(f"  Can create users: {users.has_permission('user.create')}")
    print(f"  Can read own files: {users.has_permission('file.read_own')}")
    
    return core, users


def demo_process_management(core, users):
    """Demonstrate process management."""
    print("\n" + "=" * 60)
    print("DEMO 2: Process Management")
    print("=" * 60)
    
    processes = ProcessLayer(core, algorithm="fifo")
    
    # Run a simple process
    print("\n--- Running Simple Process ---")
    proc1 = processes.run(
        "SimpleTask",
        system_monitor,
        args=(2,),
        owner=users.whoami(),
        background=False
    )
    print(f"✓ Process {proc1.pid} completed")
    
    # Run background processes
    print("\n--- Running Background Processes ---")
    proc2 = processes.run(
        "BackgroundTask1",
        system_monitor,
        args=(3,),
        owner=users.whoami(),
        background=True
    )
    proc3 = processes.run(
        "BackgroundTask2",
        system_monitor,
        args=(3,),
        owner=users.whoami(),
        background=True
    )
    
    print(f"✓ Started process {proc2.pid}: {proc2.name}")
    print(f"✓ Started process {proc3.pid}: {proc3.name}")
    
    time.sleep(0.5)
    
    # List processes
    print("\n--- Active Processes ---")
    for proc_info in processes.ps(owner=users.whoami()):
        print(f"  PID {proc_info['pid']:3} | {proc_info['name']:20} | {proc_info['state']:10} | Owner: {proc_info['owner']}")
    
    # Wait for completion
    time.sleep(3)
    
    return processes


def demo_integrated_workflow(core, users, processes):
    """Demonstrate integrated workflow with VFS, processes, and users."""
    print("\n" + "=" * 60)
    print("DEMO 3: Integrated Workflow (VFS + Processes + Users)")
    print("=" * 60)
    
    vfs = VirtualFileSystem(core)
    
    # Create user workspace
    print("\n--- Setting Up User Workspace ---")
    current_user = users.whoami()
    user_dir = f"/home/{current_user}"
    
    vfs.mkdir(f"{user_dir}/documents")
    vfs.mkdir(f"{user_dir}/backups")
    
    # Create some files
    vfs.write(f"{user_dir}/documents/report.txt", "Important report data\nLine 2\nLine 3")
    vfs.write(f"{user_dir}/documents/notes.txt", "Meeting notes\nTodo items")
    
    print(f"✓ Created workspace for {current_user}")
    
    # Run file processing as background process
    print("\n--- Running File Processing Processes ---")
    proc1 = processes.run(
        "ProcessReport",
        file_processor,
        args=(vfs, f"{user_dir}/documents/report.txt", "read"),
        owner=current_user,
        background=True
    )
    
    proc2 = processes.run(
        "ProcessNotes",
        file_processor,
        args=(vfs, f"{user_dir}/documents/notes.txt", "read"),
        owner=current_user,
        background=True
    )
    
    print(f"✓ Started file processing (PIDs: {proc1.pid}, {proc2.pid})")
    
    # Run backup process
    print("\n--- Running Backup Process ---")
    proc3 = processes.run(
        "BackupReport",
        backup_task,
        args=(vfs, f"{user_dir}/documents/report.txt", f"{user_dir}/backups/report_backup.txt"),
        owner=current_user,
        background=True
    )
    
    print(f"✓ Started backup process (PID: {proc3.pid})")
    
    # Wait for processes
    time.sleep(2)
    
    # Show results
    print("\n--- Workspace Contents ---")
    print(f"\nDocuments:")
    for file in vfs.ls(f"{user_dir}/documents"):
        print(f"  {file['name']:20} - {file['size']} bytes")
    
    print(f"\nBackups:")
    for file in vfs.ls(f"{user_dir}/backups"):
        print(f"  {file['name']:20} - {file['size']} bytes")
    
    # Show process statistics
    print("\n--- Process Statistics ---")
    stats = processes.get_statistics()
    print(f"  Total processes: {stats['total_processes']}")
    print(f"  Running: {stats['running']}")
    print(f"  Terminated: {stats['terminated']}")
    
    return vfs


def demo_multi_user_scenario(core, users, processes, vfs):
    """Demonstrate multi-user scenario."""
    print("\n" + "=" * 60)
    print("DEMO 4: Multi-User Scenario")
    print("=" * 60)
    
    # Create another user
    print("\n--- Creating Second User ---")
    users.login("root", "root")
    users.adduser("bob", "bob123", UserRole.USER)
    print("✓ Created user: bob")
    
    # Switch to bob
    print("\n--- Bob's Session ---")
    users.switch_user("bob", "bob123")
    print(f"✓ Logged in as: {users.whoami()}")
    
    # Bob creates his workspace
    bob_dir = "/home/bob"
    vfs.mkdir(f"{bob_dir}/projects")
    vfs.write(f"{bob_dir}/projects/code.py", "# Bob's Python code\nprint('Hello')")
    
    # Bob runs a process
    proc = processes.run(
        "BobsTask",
        system_monitor,
        args=(2,),
        owner="bob",
        background=True
    )
    
    print(f"✓ Bob started process {proc.pid}")
    
    time.sleep(0.5)
    
    # Show all users' processes (as root)
    print("\n--- All Active Processes (Root View) ---")
    users.switch_user("root", "root")
    
    for proc_info in processes.ps(show_all=False):
        print(f"  PID {proc_info['pid']:3} | {proc_info['name']:20} | Owner: {proc_info['owner']:10}")
    
    # Show active sessions
    print("\n--- Active Sessions ---")
    for session in users.sessions():
        print(f"  {session['username']:10} - Session: {session['session_id'][:16]}... (Duration: {session['duration']:.1f}s)")
    
    time.sleep(2)


def demo_process_control(processes, users):
    """Demonstrate process control commands."""
    print("\n" + "=" * 60)
    print("DEMO 5: Process Control Commands")
    print("=" * 60)
    
    users.login("root", "root")
    
    # Start a long-running process
    print("\n--- Starting Long Process ---")
    proc = processes.run(
        "LongTask",
        system_monitor,
        args=(10,),
        owner="root",
        background=True
    )
    
    print(f"✓ Started process {proc.pid}")
    time.sleep(1)
    
    # Suspend process
    print(f"\n--- Suspending Process {proc.pid} ---")
    if processes.suspend(proc.pid, owner="root"):
        print(f"✓ Process {proc.pid} suspended")
    
    time.sleep(1)
    
    # Resume process
    print(f"\n--- Resuming Process {proc.pid} ---")
    if processes.resume(proc.pid, owner="root"):
        print(f"✓ Process {proc.pid} resumed")
    
    time.sleep(1)
    
    # Kill process
    print(f"\n--- Killing Process {proc.pid} ---")
    if processes.kill(proc.pid, owner="root"):
        print(f"✓ Process {proc.pid} terminated")
    
    # Cleanup terminated processes
    print("\n--- Cleaning Up ---")
    count = processes.cleanup_terminated()
    print(f"✓ Cleaned up {count} terminated process(es)")


def main():
    """Main demonstration function."""
    print("\n" + "#" * 60)
    print("# Layers 5 & 6 - Comprehensive Demo")
    print("# Process Management + User Authentication")
    print("#" * 60)
    
    # Demo 1: User Authentication
    core, users = demo_user_authentication()
    
    # Demo 2: Process Management
    processes = demo_process_management(core, users)
    
    # Demo 3: Integrated Workflow
    vfs = demo_integrated_workflow(core, users, processes)
    
    # Demo 4: Multi-User Scenario
    demo_multi_user_scenario(core, users, processes, vfs)
    
    # Demo 5: Process Control
    demo_process_control(processes, users)
    
    # Shutdown
    print("\n" + "=" * 60)
    print("DEMO Complete - Shutting Down")
    print("=" * 60)
    
    vfs.shutdown()
    processes.shutdown()
    users.shutdown()
    core.shutdown()
    
    print("\n" + "#" * 60)
    print("# All Demonstrations Complete!")
    print("# Layers 5 & 6 are fully operational!")
    print("#" * 60 + "\n")
    
    # Cleanup
    import os
    for f in ["demo_layers_config.json", "demo_users.json"]:
        if os.path.exists(f):
            os.remove(f)


if __name__ == "__main__":
    main()

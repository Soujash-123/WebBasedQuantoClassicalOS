"""
Manual Test Suite for Process Management Layer
Tests process creation, scheduling, and management.
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core import AIOSCore
from processes import ProcessLayer


def sample_task(name, duration=1):
    """Sample task for testing."""
    print(f"[Task {name}] Starting...")
    time.sleep(duration)
    print(f"[Task {name}] Completed!")
    return f"Result from {name}"


def test_process_creation():
    """Test process creation and execution."""
    print("\n" + "=" * 60)
    print("TEST: Process Creation and Execution")
    print("=" * 60)
    
    core = AIOSCore("test_process_config.json")
    processes = ProcessLayer(core, algorithm="fifo")
    
    # Create and run a process
    print("\n[TEST] Running a simple process...")
    proc = processes.run("TestProcess", sample_task, args=("Test1", 0.5))
    
    assert proc is not None, "Process not created"
    assert proc.pid > 0, "Invalid PID"
    assert proc.name == "TestProcess", "Process name mismatch"
    
    print(f"✓ Process created with PID {proc.pid}")
    
    processes.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_process_config.json"):
        os.remove("test_process_config.json")
    
    print("\n✓ Process Creation tests PASSED")


def test_process_control():
    """Test process control (kill, suspend, resume)."""
    print("\n" + "=" * 60)
    print("TEST: Process Control")
    print("=" * 60)
    
    core = AIOSCore("test_control_config.json")
    processes = ProcessLayer(core, algorithm="fifo")
    
    # Run background process
    print("\n[TEST] Running background process...")
    proc = processes.run("BackgroundTask", sample_task, args=("BG1", 2), background=True)
    
    time.sleep(0.2)
    
    # Test suspend
    print("\n[TEST] Suspending process...")
    assert processes.suspend(proc.pid), "Failed to suspend"
    print(f"✓ Process {proc.pid} suspended")
    
    # Test resume
    print("\n[TEST] Resuming process...")
    assert processes.resume(proc.pid), "Failed to resume"
    print(f"✓ Process {proc.pid} resumed")
    
    # Test kill
    print("\n[TEST] Killing process...")
    assert processes.kill(proc.pid), "Failed to kill"
    print(f"✓ Process {proc.pid} killed")
    
    processes.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_control_config.json"):
        os.remove("test_control_config.json")
    
    print("\n✓ Process Control tests PASSED")


def test_process_listing():
    """Test process listing (ps command)."""
    print("\n" + "=" * 60)
    print("TEST: Process Listing")
    print("=" * 60)
    
    core = AIOSCore("test_ps_config.json")
    processes = ProcessLayer(core, algorithm="fifo")
    
    # Run multiple processes
    print("\n[TEST] Running multiple processes...")
    proc1 = processes.run("Task1", sample_task, args=("T1", 1), background=True)
    proc2 = processes.run("Task2", sample_task, args=("T2", 1), background=True)
    proc3 = processes.run("Task3", sample_task, args=("T3", 1), background=True)
    
    time.sleep(0.2)
    
    # List processes
    print("\n[TEST] Listing processes...")
    process_list = processes.ps()
    
    assert len(process_list) >= 3, f"Expected at least 3 processes, got {len(process_list)}"
    print(f"✓ Found {len(process_list)} process(es)")
    
    for proc_info in process_list:
        print(f"  PID {proc_info['pid']}: {proc_info['name']} ({proc_info['state']})")
    
    processes.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_ps_config.json"):
        os.remove("test_ps_config.json")
    
    print("\n✓ Process Listing tests PASSED")


def test_scheduler():
    """Test process scheduler."""
    print("\n" + "=" * 60)
    print("TEST: Process Scheduler")
    print("=" * 60)
    
    core = AIOSCore("test_scheduler_config.json")
    
    # Test FIFO scheduler
    print("\n[TEST] Testing FIFO scheduler...")
    processes_fifo = ProcessLayer(core, algorithm="fifo")
    
    proc1 = processes_fifo.run("FIFO1", sample_task, args=("F1", 0.3), background=True)
    proc2 = processes_fifo.run("FIFO2", sample_task, args=("F2", 0.3), background=True)
    
    time.sleep(1)
    
    stats = processes_fifo.get_statistics()
    print(f"✓ FIFO Scheduler: {stats['scheduler_stats']['completed_processes']} completed")
    
    processes_fifo.shutdown()
    
    # Test Round-Robin scheduler
    print("\n[TEST] Testing Round-Robin scheduler...")
    processes_rr = ProcessLayer(core, algorithm="round_robin")
    
    proc3 = processes_rr.run("RR1", sample_task, args=("R1", 0.3), background=True)
    proc4 = processes_rr.run("RR2", sample_task, args=("R2", 0.3), background=True)
    
    time.sleep(1)
    
    stats = processes_rr.get_statistics()
    print(f"✓ Round-Robin Scheduler: {stats['scheduler_stats']['completed_processes']} completed")
    
    processes_rr.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_scheduler_config.json"):
        os.remove("test_scheduler_config.json")
    
    print("\n✓ Scheduler tests PASSED")


def test_process_statistics():
    """Test process statistics."""
    print("\n" + "=" * 60)
    print("TEST: Process Statistics")
    print("=" * 60)
    
    core = AIOSCore("test_stats_config.json")
    processes = ProcessLayer(core, algorithm="fifo")
    
    # Run some processes
    processes.run("StatTask1", sample_task, args=("S1", 0.2))
    processes.run("StatTask2", sample_task, args=("S2", 0.2))
    
    # Get statistics
    print("\n[TEST] Getting statistics...")
    stats = processes.get_statistics()
    
    print(f"Total processes: {stats['total_processes']}")
    print(f"Running: {stats['running']}")
    print(f"Terminated: {stats['terminated']}")
    
    assert stats['total_processes'] >= 2, "Statistics not tracking processes"
    print("✓ Statistics working correctly")
    
    processes.shutdown()
    core.shutdown()
    
    # Cleanup
    if os.path.exists("test_stats_config.json"):
        os.remove("test_stats_config.json")
    
    print("\n✓ Statistics tests PASSED")


def run_all_tests():
    """Run all process tests."""
    print("\n" + "#" * 60)
    print("# PROCESS MANAGEMENT LAYER - MANUAL TEST SUITE")
    print("#" * 60)
    
    try:
        test_process_creation()
        test_process_control()
        test_process_listing()
        test_scheduler()
        test_process_statistics()
        
        print("\n" + "#" * 60)
        print("# ALL PROCESS TESTS PASSED ✓")
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


if __name__ == "__main__":
    run_all_tests()

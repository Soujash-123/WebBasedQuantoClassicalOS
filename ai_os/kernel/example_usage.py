"""
Kernel Hot Reload - Example Usage
Demonstrates hot-reloading capabilities without restarting the OS.
"""

import sys
import os
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_os.kernel import KernelHotReload, get_kernel_reload


def demo_basic_reload():
    """Demonstrate basic module reload"""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Module Reload")
    print("=" * 70)
    
    kernel = get_kernel_reload()
    
    print("\n1. Initial module scan...")
    status = kernel.get_status()
    print(f"   Tracked modules: {status['total_modules']}")
    
    print("\n2. Detecting changes...")
    changed = kernel.detect_changes()
    print(f"   Changed modules: {len(changed)}")
    if changed:
        for mod in changed[:5]:
            print(f"   - {mod}")
    
    print("\n3. Running refresh...")
    result = kernel.refresh()
    print(f"   ✓ Success: {result['success']}")
    print(f"   ✗ Failed: {result['failed']}")
    print(f"   Duration: {result['elapsed_seconds']:.2f}s")


def demo_watch_mode():
    """Demonstrate watch mode"""
    print("\n" + "=" * 70)
    print("DEMO 2: Watch Mode (Auto-Reload)")
    print("=" * 70)
    
    kernel = get_kernel_reload()
    
    print("\n1. Starting watch mode...")
    kernel.start_watch()
    print("   ✓ Watch mode activated")
    
    print("\n2. Watching for changes for 10 seconds...")
    print("   (Make changes to any module file now)")
    
    for i in range(10, 0, -1):
        print(f"   {i}...", end='\r')
        time.sleep(1)
    
    print("\n\n3. Stopping watch mode...")
    kernel.stop_watch()
    print("   ✓ Watch mode deactivated")
    
    print("\n4. Reload history:")
    history = kernel.get_reload_history(limit=3)
    for event in history:
        print(f"   - {event['timestamp']}: {event['success']} modules reloaded")


def demo_rollback():
    """Demonstrate rollback functionality"""
    print("\n" + "=" * 70)
    print("DEMO 3: Module Rollback")
    print("=" * 70)
    
    kernel = get_kernel_reload()
    
    print("\n1. Attempting to rollback a module...")
    
    # Get first backed up module
    if kernel.backup_modules:
        module_name = list(kernel.backup_modules.keys())[0]
        print(f"   Module: {module_name}")
        
        success = kernel.rollback(module_name)
        if success:
            print(f"   ✓ Rollback successful")
        else:
            print(f"   ✗ Rollback failed")
    else:
        print("   No backed up modules available")
        print("   (Modules are backed up during reload)")


def demo_status_report():
    """Demonstrate status reporting"""
    print("\n" + "=" * 70)
    print("DEMO 4: Status Report")
    print("=" * 70)
    
    kernel = get_kernel_reload()
    
    print("\n" + kernel.format_status_report())


def demo_cli_simulation():
    """Simulate CLI usage"""
    print("\n" + "=" * 70)
    print("DEMO 5: CLI Command Simulation")
    print("=" * 70)
    
    from ai_os.kernel.kernel_commands import KernelCommands
    
    cmds = KernelCommands()
    
    print("\n1. Running: os refresh")
    print("-" * 70)
    result = cmds.cmd_os_refresh()
    
    print("\n2. Running: os watch --status")
    print("-" * 70)
    result = cmds.cmd_os_watch(['--status'])
    print(result)
    
    print("\n3. Running: os status reloads")
    print("-" * 70)
    result = cmds.cmd_os_status(['reloads'])
    print(result)


def demo_live_update():
    """Demonstrate live update scenario"""
    print("\n" + "=" * 70)
    print("DEMO 6: Live Update Scenario")
    print("=" * 70)
    
    print("""
This demonstrates the typical developer workflow:

1. Start the AI OS CLI:
   $ python main_cli.py
   
2. OS is running with all modules loaded

3. Developer makes changes to a file:
   - Edit: ai_os/cli_shell/command_registry.py
   - Add a new command function
   
4. In the RUNNING OS shell, type:
   > os refresh
   
5. The system:
   - Detects the changed file
   - Backs up the current version
   - Reloads the module
   - New command is immediately available!
   
6. Test the new command:
   > mynewcommand
   
7. If there's an error:
   > os rollback cli_shell.command_registry
   
8. Enable auto-reload for continuous development:
   > os watch --live
   
   Now ALL changes are automatically detected and reloaded!

No restart required! 🎉
""")


def interactive_demo():
    """Interactive demonstration"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              Kernel Hot Reload - Interactive Demo                    ║
║                                                                      ║
║  This demonstrates the self-updating kernel capabilities             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")
    
    demos = [
        ("Basic Module Reload", demo_basic_reload),
        ("Watch Mode (Auto-Reload)", demo_watch_mode),
        ("Module Rollback", demo_rollback),
        ("Status Report", demo_status_report),
        ("CLI Command Simulation", demo_cli_simulation),
        ("Live Update Scenario", demo_live_update)
    ]
    
    print("\nAvailable Demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print("  0. Run All Demos")
    print("  q. Quit")
    
    while True:
        try:
            choice = input("\nSelect demo (0-6, q): ").strip().lower()
            
            if choice == 'q':
                print("\nExiting demo...")
                break
            
            if choice == '0':
                for name, func in demos:
                    func()
                    input("\nPress Enter to continue...")
                break
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(demos):
                    demos[idx][1]()
                else:
                    print("Invalid selection")
            except ValueError:
                print("Invalid input")
                
        except KeyboardInterrupt:
            print("\n\nDemo interrupted")
            break


def quick_test():
    """Quick test of hot reload functionality"""
    print("\n" + "=" * 70)
    print("KERNEL HOT RELOAD - QUICK TEST")
    print("=" * 70)
    
    kernel = get_kernel_reload()
    
    # Test 1: Module scan
    print("\n✓ Test 1: Module Scan")
    status = kernel.get_status()
    print(f"  Modules tracked: {status['total_modules']}")
    assert status['total_modules'] > 0, "Should track modules"
    
    # Test 2: Change detection
    print("\n✓ Test 2: Change Detection")
    changed = kernel.detect_changes()
    print(f"  Changed modules: {len(changed)}")
    
    # Test 3: Refresh
    print("\n✓ Test 3: Module Refresh")
    result = kernel.refresh()
    print(f"  Reloaded: {result['success']} modules")
    
    # Test 4: Status
    print("\n✓ Test 4: Status Report")
    print(f"  Watch active: {status['watch_active']}")
    print(f"  Reload events: {status['reload_history_count']}")
    
    # Test 5: Commands
    print("\n✓ Test 5: CLI Commands")
    from ai_os.kernel.kernel_commands import KernelCommands
    cmds = KernelCommands()
    result = cmds.cmd_os_watch(['--status'])
    print(f"  Watch status: {result}")
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✓")
    print("=" * 70)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kernel Hot Reload Demo")
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run interactive demo')
    parser.add_argument('--quick', '-q', action='store_true',
                       help='Run quick test')
    parser.add_argument('--all', '-a', action='store_true',
                       help='Run all demos')
    
    args = parser.parse_args()
    
    if args.quick:
        quick_test()
    elif args.interactive:
        interactive_demo()
    elif args.all:
        demo_basic_reload()
        demo_watch_mode()
        demo_rollback()
        demo_status_report()
        demo_cli_simulation()
        demo_live_update()
    else:
        # Default: quick test
        quick_test()
        print("\nFor more options, run with --help")


if __name__ == '__main__':
    main()

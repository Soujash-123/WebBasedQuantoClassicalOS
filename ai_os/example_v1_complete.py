"""
AI OS v1.0 Complete Example
Demonstrates all features of the completed AI OS.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_os.os_master import AIOSMaster


def demo_memory_layer(os_master):
    """Demonstrate memory layer features"""
    print("\n" + "="*70)
    print("MEMORY LAYER DEMONSTRATION")
    print("="*70)
    
    # Memory statistics
    print("\n1. Memory Statistics:")
    print(os_master.execute_command('memstat'))
    
    # Allocate memory for a process
    print("\n2. Allocating memory for process...")
    memory_layer = os_master.get_layer('memory')
    if memory_layer:
        success = memory_layer.allocate(process_id=1001, size_mb=64, description="Test Process")
        print(f"Allocation result: {'Success' if success else 'Failed'}")
        
        # Check process memory
        print("\n3. Process Memory Usage:")
        print(os_master.execute_command('procmem', ['1001']))
        
        # Memory history
        print("\n4. Memory Allocation History:")
        print(os_master.execute_command('memhistory', ['5']))


def demo_network_layer(os_master):
    """Demonstrate network layer features"""
    print("\n" + "="*70)
    print("NETWORK LAYER DEMONSTRATION")
    print("="*70)
    
    # Network info
    print("\n1. Network Information:")
    print(os_master.execute_command('netinfo'))
    
    # Interface configuration
    print("\n2. Network Interfaces:")
    print(os_master.execute_command('ifconfig'))
    
    # Ping test
    print("\n3. Ping Test (google.com):")
    print(os_master.execute_command('ping', ['google.com', '2']))
    
    # Network statistics
    print("\n4. Network Statistics:")
    print(os_master.execute_command('netstats'))


def demo_security_layer(os_master):
    """Demonstrate security layer features"""
    print("\n" + "="*70)
    print("SECURITY LAYER DEMONSTRATION")
    print("="*70)
    
    # Create test user
    print("\n1. Creating test user...")
    print(os_master.execute_command('adduser', ['testuser', 'testpass123']))
    
    # List users
    print("\n2. User List:")
    print(os_master.execute_command('users'))
    
    # Login
    print("\n3. Login as testuser:")
    print(os_master.execute_command('login', ['testuser', 'testpass123']))
    
    # Check current user
    print("\n4. Current User:")
    print(os_master.execute_command('whoami'))
    
    # Generate encryption key
    print("\n5. Generate Encryption Key:")
    print(os_master.execute_command('genkey'))
    
    # Hash demonstration
    print("\n6. Hash Example:")
    print(os_master.execute_command('hash', ['Hello World', 'sha256']))
    
    # Sessions
    print("\n7. Active Sessions:")
    print(os_master.execute_command('sessions'))
    
    # Logout
    print("\n8. Logout:")
    print(os_master.execute_command('logout'))


def demo_diagnostics_layer(os_master):
    """Demonstrate diagnostics layer features"""
    print("\n" + "="*70)
    print("DIAGNOSTICS LAYER DEMONSTRATION")
    print("="*70)
    
    # System check
    print("\n1. System Diagnostics:")
    print(os_master.execute_command('syscheck'))
    
    # Resource monitoring
    print("\n2. Resource Statistics:")
    print(os_master.execute_command('resources'))
    
    # Dependency check
    print("\n3. Dependency Check:")
    print(os_master.execute_command('depcheck'))


def demo_integration(os_master):
    """Demonstrate integrated workflow"""
    print("\n" + "="*70)
    print("INTEGRATED WORKFLOW DEMONSTRATION")
    print("="*70)
    
    print("\n=== Scenario: New User Setup and Security Audit ===\n")
    
    # Step 1: Create user
    print("Step 1: Creating new user 'developer'...")
    print(os_master.execute_command('adduser', ['developer', 'devpass123']))
    
    # Step 2: Login
    print("\nStep 2: Logging in as developer...")
    print(os_master.execute_command('login', ['developer', 'devpass123']))
    
    # Step 3: Check system resources
    print("\nStep 3: Checking available resources...")
    print(os_master.execute_command('memstat'))
    
    # Step 4: Check network connectivity
    print("\nStep 4: Testing network connectivity...")
    print(os_master.execute_command('ping', ['8.8.8.8', '2']))
    
    # Step 5: Create encrypted file (simulated)
    print("\nStep 5: Generating encryption key for secure storage...")
    print(os_master.execute_command('genkey'))
    
    # Step 6: Run system diagnostics
    print("\nStep 6: Running system health check...")
    result = os_master.execute_command('syscheck')
    # Print only summary
    lines = result.split('\n')
    for line in lines[:20]:  # First 20 lines
        print(line)
    print("... (truncated)")
    
    # Step 7: Check resource usage
    print("\nStep 7: Monitoring resource usage...")
    print(os_master.execute_command('resources'))
    
    # Step 8: Logout
    print("\nStep 8: Logging out...")
    print(os_master.execute_command('logout'))
    
    print("\n=== Workflow Complete ===")


def demo_command_list(os_master):
    """Display all available commands"""
    print("\n" + "="*70)
    print("AVAILABLE COMMANDS")
    print("="*70)
    
    commands = os_master.get_all_commands()
    
    # Group by layer
    by_layer = {}
    for cmd_name, cmd_info in commands.items():
        layer = cmd_info['layer']
        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append((cmd_name, cmd_info['description']))
    
    for layer_name in sorted(by_layer.keys()):
        print(f"\n{layer_name.upper()} LAYER:")
        print("-" * 70)
        for cmd_name, description in sorted(by_layer[layer_name]):
            print(f"  {cmd_name:<20} - {description}")


def main():
    """Main demonstration"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              AI OS v1.0 - Complete Feature Demonstration             ║
║                                                                      ║
║  This script demonstrates all features of the completed AI OS        ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")
    
    # Initialize OS
    print("\nInitializing AI OS...")
    os_master = AIOSMaster()
    
    if not os_master.initialize():
        print("❌ Failed to initialize AI OS")
        return 1
    
    print("\n✓ AI OS initialized successfully!")
    
    # Run demonstrations
    try:
        # Show available commands
        demo_command_list(os_master)
        
        # Memory layer demo
        demo_memory_layer(os_master)
        
        # Network layer demo
        demo_network_layer(os_master)
        
        # Security layer demo
        demo_security_layer(os_master)
        
        # Diagnostics layer demo
        demo_diagnostics_layer(os_master)
        
        # Integrated workflow
        demo_integration(os_master)
        
        # Final summary
        print("\n" + "="*70)
        print("DEMONSTRATION COMPLETE")
        print("="*70)
        
        system_info = os_master.get_system_info()
        print(f"\nAI OS Version: {system_info['version']}")
        print(f"Total Layers: {len(system_info['layers'])}")
        print(f"Total Commands: {system_info['total_commands']}")
        print(f"Layers: {', '.join(system_info['layers'])}")
        
        print("\n✓ All demonstrations completed successfully!")
        print("\nTo use AI OS interactively, run:")
        print("  python -m ai_os.cli_shell")
        print("\nFor more information, see:")
        print("  documentation/COMMANDS.md")
        print("  documentation/ARCHITECTURE.md")
        
    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Shutdown
        print("\n\nShutting down AI OS...")
        os_master.shutdown()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

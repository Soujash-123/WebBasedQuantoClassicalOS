"""
Test All AI OS Commands
Comprehensive test script to verify all commands are working
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

import io
import contextlib

print("="*80)
print("AI OS COMMAND TEST SUITE")
print("="*80)
print("\nInitializing AI OS (this may take a moment)...\n")

# Initialize client (suppress verbose output)
from ai_os.unified_client import UnifiedClient

with contextlib.redirect_stdout(io.StringIO()):
    client = UnifiedClient(enable_hot_reload=True)

print(f"✓ AI OS initialized with {len(client.commands)} commands\n")

# Test results
results = {
    'passed': [],
    'failed': [],
    'skipped': []
}

def test_command(cmd_name, args=None, expect_error=False):
    """Test a single command"""
    try:
        cmd_info = client.commands.get(cmd_name)
        if not cmd_info:
            return False, "Command not found"
        
        func = cmd_info.get('function')
        if not func:
            return False, "No function defined"
        
        # Execute command
        result = func(args)
        
        if expect_error and result and "error" in str(result).lower():
            return True, "Expected error received"
        elif not expect_error:
            return True, "Success"
        else:
            return False, f"Unexpected result: {result}"
            
    except Exception as e:
        if expect_error:
            return True, f"Expected error: {str(e)}"
        return False, str(e)

# Define test cases
test_cases = [
    # Built-in commands
    ("help", None, False, "builtin"),
    ("history", None, False, "builtin"),
    ("clear", None, False, "builtin"),
    ("exit", None, True, "builtin"),  # Skip - would exit
    
    # Core commands
    ("version", None, False, "core"),
    ("uptime", None, False, "core"),
    
    # Memory commands
    ("memstat", None, False, "memory"),
    ("meminfo", None, False, "memory"),
    ("procmem", None, False, "memory"),
    ("memusage", None, False, "memory"),
    ("memclear", None, False, "memory"),
    ("memtest", None, False, "memory"),
    
    # Network commands
    ("ping", ["localhost"], False, "network"),
    ("netstat", None, False, "network"),
    ("ifconfig", None, False, "network"),
    ("route", None, False, "network"),
    ("dns", ["google.com"], False, "network"),
    ("traceroute", ["localhost"], False, "network"),
    ("portscan", ["localhost"], False, "network"),
    ("bandwidth", None, False, "network"),
    ("netinfo", None, False, "network"),
    
    # Diagnostics commands
    ("syscheck", None, False, "diagnostics"),
    ("resources", None, False, "diagnostics"),
    ("health", None, False, "diagnostics"),
    ("benchmark", None, False, "diagnostics"),
    
    # Filesystem commands
    ("ls", None, False, "filesystem"),
    ("pwd", None, False, "filesystem"),
    ("mkdir", ["test_dir"], False, "filesystem"),
    ("touch", ["test_file.txt"], False, "filesystem"),
    ("cat", ["test_file.txt"], True, "filesystem"),  # Expect error - empty file
    ("rm", ["test_file.txt"], False, "filesystem"),
    
    # Custom commands
    ("hello", None, False, "custom"),
    ("hello", ["World"], False, "custom"),
    ("greet", ["Alice"], False, "custom"),
    ("echo", ["Hello", "World"], False, "custom"),
    ("time", None, False, "custom"),
    ("calc", ["5", "+", "3"], False, "custom"),
    ("calc", ["10", "-", "2"], False, "custom"),
    ("calc", ["4", "*", "6"], False, "custom"),
    ("calc", ["20", "/", "4"], False, "custom"),
    
    # grep, find, wc (need files)
    ("grep", None, True, "custom"),  # Expect error - no args
    ("find", ["/"], False, "custom"),
    ("wc", None, True, "custom"),  # Expect error - no args
    
    # Hot reload commands
    ("refresh", None, True, "hotreload"),  # Skip - would restart
    ("watch", ["--status"], False, "hotreload"),
    ("reload-status", None, False, "hotreload"),
]

# Skip commands that would disrupt testing
skip_commands = ["exit", "refresh", "shutdown"]

print("="*80)
print("RUNNING TESTS")
print("="*80)
print()

for cmd_name, args, expect_error, layer in test_cases:
    # Skip disruptive commands
    if cmd_name in skip_commands:
        results['skipped'].append((cmd_name, layer, "Would disrupt testing"))
        print(f"⊘ {cmd_name:20} [{layer:15}] SKIPPED - Would disrupt testing")
        continue
    
    # Check if command exists
    if cmd_name not in client.commands:
        results['failed'].append((cmd_name, layer, "Command not found"))
        print(f"✗ {cmd_name:20} [{layer:15}] FAILED - Command not found")
        continue
    
    # Test the command
    success, message = test_command(cmd_name, args, expect_error)
    
    if success:
        results['passed'].append((cmd_name, layer, message))
        args_str = f" {args}" if args else ""
        print(f"✓ {cmd_name:20} [{layer:15}] PASSED{args_str}")
    else:
        results['failed'].append((cmd_name, layer, message))
        print(f"✗ {cmd_name:20} [{layer:15}] FAILED - {message}")

# Test grep with actual file
print("\n" + "="*80)
print("TESTING FILE OPERATIONS")
print("="*80)
print()

# Create test file for grep/wc
try:
    # Create a test file
    from ai_os.filesystem.vfs_master import VFSLayer
    vfs = VFSLayer()
    
    test_content = """Hello World
This is a test file
Hello again
Testing grep command
ERROR: This is an error line
INFO: This is an info line"""
    
    vfs.vfs_manager.write("/test_grep.txt", test_content)
    print("✓ Created test file: /test_grep.txt")
    
    # Test grep
    print("\nTesting grep command:")
    grep_tests = [
        (["Hello", "/test_grep.txt"], "Basic search"),
        (["-i", "hello", "/test_grep.txt"], "Case-insensitive"),
        (["-n", "Hello", "/test_grep.txt"], "With line numbers"),
        (["-c", "Hello", "/test_grep.txt"], "Count matches"),
        (["ERROR", "/test_grep.txt"], "Search for ERROR"),
    ]
    
    for args, desc in grep_tests:
        success, message = test_command("grep", args, False)
        if success:
            results['passed'].append(("grep", "custom", desc))
            print(f"  ✓ grep {' '.join(args):40} - {desc}")
        else:
            results['failed'].append(("grep", "custom", f"{desc}: {message}"))
            print(f"  ✗ grep {' '.join(args):40} - {desc} FAILED")
    
    # Test wc
    print("\nTesting wc command:")
    wc_tests = [
        (["/test_grep.txt"], "Count all"),
        (["-l", "/test_grep.txt"], "Count lines"),
        (["-w", "/test_grep.txt"], "Count words"),
        (["-c", "/test_grep.txt"], "Count characters"),
    ]
    
    for args, desc in wc_tests:
        success, message = test_command("wc", args, False)
        if success:
            results['passed'].append(("wc", "custom", desc))
            print(f"  ✓ wc {' '.join(args):40} - {desc}")
        else:
            results['failed'].append(("wc", "custom", f"{desc}: {message}"))
            print(f"  ✗ wc {' '.join(args):40} - {desc} FAILED")
    
    # Test find
    print("\nTesting find command:")
    find_tests = [
        (["/"], "Find all files"),
        (["/", "-name", "test_grep.txt"], "Find specific file"),
        (["/", "-name", "*.txt"], "Find with wildcard"),
    ]
    
    for args, desc in find_tests:
        success, message = test_command("find", args, False)
        if success:
            results['passed'].append(("find", "custom", desc))
            print(f"  ✓ find {' '.join(args):40} - {desc}")
        else:
            results['failed'].append(("find", "custom", f"{desc}: {message}"))
            print(f"  ✗ find {' '.join(args):40} - {desc} FAILED")
    
    # Cleanup
    vfs.vfs_manager.rm("/test_grep.txt")
    print("\n✓ Cleaned up test file")
    
except Exception as e:
    print(f"\n✗ File operations test failed: {e}")
    results['failed'].append(("file_ops", "filesystem", str(e)))

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print()

total_tests = len(results['passed']) + len(results['failed']) + len(results['skipped'])
print(f"Total Tests:   {total_tests}")
print(f"✓ Passed:      {len(results['passed'])} ({len(results['passed'])*100//total_tests if total_tests > 0 else 0}%)")
print(f"✗ Failed:      {len(results['failed'])} ({len(results['failed'])*100//total_tests if total_tests > 0 else 0}%)")
print(f"⊘ Skipped:     {len(results['skipped'])} ({len(results['skipped'])*100//total_tests if total_tests > 0 else 0}%)")

if results['failed']:
    print("\n" + "="*80)
    print("FAILED TESTS")
    print("="*80)
    for cmd, layer, reason in results['failed']:
        print(f"  ✗ {cmd:20} [{layer:15}] - {reason}")

if results['skipped']:
    print("\n" + "="*80)
    print("SKIPPED TESTS")
    print("="*80)
    for cmd, layer, reason in results['skipped']:
        print(f"  ⊘ {cmd:20} [{layer:15}] - {reason}")

# List all available commands
print("\n" + "="*80)
print("ALL AVAILABLE COMMANDS")
print("="*80)
print()

# Group by layer
layers = {}
for cmd_name, cmd_info in client.commands.items():
    layer = cmd_info.get('layer', 'builtin')
    if layer not in layers:
        layers[layer] = []
    layers[layer].append(cmd_name)

for layer_name in sorted(layers.keys()):
    cmds = sorted(layers[layer_name])
    print(f"\n{layer_name.upper()} ({len(cmds)} commands):")
    print(f"  {', '.join(cmds)}")

print("\n" + "="*80)
print(f"TOTAL: {len(client.commands)} commands available")
print("="*80)

# Exit code based on results
if results['failed']:
    print("\n⚠ Some tests failed!")
    sys.exit(1)
else:
    print("\n✓ All tests passed!")
    sys.exit(0)

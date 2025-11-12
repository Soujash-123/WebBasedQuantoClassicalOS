"""
List all available commands in AI OS
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_os.unified_client import UnifiedClient
import io
import contextlib

# Create client (suppress output)
print("Initializing AI OS to list commands...\n")
with contextlib.redirect_stdout(io.StringIO()):
    client = UnifiedClient(enable_hot_reload=True)

# Get all commands
commands = client.commands

# Group by layer
layers = {}
for cmd_name, cmd_info in commands.items():
    layer = cmd_info.get('layer', 'builtin')
    if layer not in layers:
        layers[layer] = []
    layers[layer].append({
        'name': cmd_name,
        'description': cmd_info.get('description', 'No description'),
        'usage': cmd_info.get('usage', cmd_name)
    })

# Print organized list
print("="*80)
print("ALL AVAILABLE COMMANDS IN AI OS")
print("="*80)
print(f"\nTotal Commands: {len(commands)}\n")

for layer_name in sorted(layers.keys()):
    cmds = sorted(layers[layer_name], key=lambda x: x['name'])
    print(f"\n{'='*80}")
    print(f"{layer_name.upper()} COMMANDS ({len(cmds)} commands)")
    print(f"{'='*80}")
    
    for cmd in cmds:
        print(f"\n  {cmd['name']}")
        print(f"    Description: {cmd['description']}")
        print(f"    Usage: {cmd['usage']}")

print(f"\n{'='*80}")
print(f"Total: {len(commands)} commands available")
print(f"{'='*80}\n")

# Test commands you asked about
print("\nTesting specific commands:")
print("-" * 80)

test_cmds = ['grep', 'find', 'wc', 'refresh', 'watch', 'hello', 'time', 'calc']
for cmd in test_cmds:
    if cmd in commands:
        print(f"✓ {cmd:15} - Available")
    else:
        print(f"✗ {cmd:15} - NOT FOUND")

print()

"""
Show all available commands in AI OS
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import io
import contextlib

print("Initializing AI OS...\n")

from ai_os.unified_client import UnifiedClient

with contextlib.redirect_stdout(io.StringIO()):
    client = UnifiedClient(enable_hot_reload=True)

print("="*80)
print(f"TOTAL COMMANDS: {len(client.commands)}")
print("="*80)
print()

# Group by layer
layers = {}
for cmd_name, cmd_info in client.commands.items():
    layer = cmd_info.get('layer', 'builtin')
    if layer not in layers:
        layers[layer] = []
    layers[layer].append({
        'name': cmd_name,
        'desc': cmd_info.get('description', 'No description'),
        'usage': cmd_info.get('usage', cmd_name)
    })

# Print by layer
for layer_name in sorted(layers.keys()):
    cmds = sorted(layers[layer_name], key=lambda x: x['name'])
    print(f"\n{'='*80}")
    print(f"{layer_name.upper()} LAYER - {len(cmds)} commands")
    print(f"{'='*80}")
    
    for cmd in cmds:
        print(f"  {cmd['name']:20} - {cmd['desc']}")

print(f"\n{'='*80}")
print(f"TOTAL: {len(client.commands)} commands")
print(f"{'='*80}\n")

# Check for specific commands
print("Checking for hot reload commands:")
print("-" * 80)
for cmd in ['refresh', 'watch', 'rollback', 'reload-status']:
    if cmd in client.commands:
        print(f"✓ {cmd:20} - FOUND")
    else:
        print(f"✗ {cmd:20} - NOT FOUND")

print("\nChecking kernel_cmds:")
print("-" * 80)
print(f"kernel_cmds exists: {client.kernel_cmds is not None}")
if client.kernel_cmds:
    print(f"kernel_cmds type: {type(client.kernel_cmds)}")
    print(f"Has cmd_os_refresh: {hasattr(client.kernel_cmds, 'cmd_os_refresh')}")
    print(f"Has cmd_os_watch: {hasattr(client.kernel_cmds, 'cmd_os_watch')}")
else:
    print("kernel_cmds is None - hot reload not initialized!")

print()

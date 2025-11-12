"""
Debug hot reload initialization
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing hot reload initialization...\n")

try:
    from ai_os.kernel import get_kernel_reload
    print("✓ Imported get_kernel_reload")
    
    kernel_reload = get_kernel_reload()
    print(f"✓ Created kernel_reload: {type(kernel_reload)}")
    
    from ai_os.kernel.kernel_commands import KernelCommands
    print("✓ Imported KernelCommands")
    
    kernel_cmds = KernelCommands(kernel_reload)
    print(f"✓ Created kernel_cmds: {type(kernel_cmds)}")
    
    print("\nHot reload should work!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

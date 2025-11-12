# Kernel Hot Reload - Integration Guide

## 🔌 Integrating with Your Existing AI OS

This guide shows how to add hot reload capabilities to your existing AI OS CLI.

---

## Option 1: Use the Standalone Hot Reload CLI

**Easiest option - no integration needed!**

```bash
# Just run the hot reload CLI
python ai_os/main_cli_hotreload.py
```

This gives you a working CLI with hot reload built-in.

---

## Option 2: Add to Existing Shell

### Step 1: Import the Kernel Commands

Edit your existing shell file (e.g., `ai_os/cli_shell/shell.py`):

```python
from ai_os.kernel import get_kernel_reload
from ai_os.kernel.kernel_commands import KernelCommands

class Shell:
    def __init__(self):
        # ... your existing code ...
        
        # Add kernel hot reload
        self.kernel = get_kernel_reload()
        self.kernel_cmds = KernelCommands()
        
        # Register kernel commands
        self._register_kernel_commands()
    
    def _register_kernel_commands(self):
        """Register hot reload commands"""
        self.commands['refresh'] = self.kernel_cmds.cmd_os_refresh
        self.commands['watch'] = self.kernel_cmds.cmd_os_watch
        self.commands['rollback'] = self.kernel_cmds.cmd_os_rollback
        self.commands['reload-status'] = self.kernel_cmds.cmd_os_status
```

### Step 2: Update Command Execution

If you have compound commands (e.g., "os refresh"):

```python
def execute_command(self, input_line):
    """Execute a command"""
    parts = input_line.strip().split()
    
    # Handle compound commands
    if len(parts) >= 2 and parts[0] == 'os':
        cmd = parts[1]
        args = parts[2:]
        
        # Map to kernel commands
        if cmd == 'refresh':
            return self.kernel_cmds.cmd_os_refresh(args)
        elif cmd == 'watch':
            return self.kernel_cmds.cmd_os_watch(args)
        elif cmd == 'rollback':
            return self.kernel_cmds.cmd_os_rollback(args)
        elif cmd == 'status':
            return self.kernel_cmds.cmd_os_status(args)
    
    # ... rest of your command handling ...
```

### Step 3: Add Shutdown Hook

```python
def shutdown(self):
    """Shutdown the shell"""
    # Stop watch mode if active
    if self.kernel.watch_active:
        self.kernel.stop_watch()
    
    # ... rest of your shutdown code ...
```

---

## Option 3: Integrate with OS Master

Edit `ai_os/os_master.py`:

```python
from ai_os.kernel import get_kernel_reload

class AIOSMaster:
    def __init__(self, config=None):
        # ... your existing code ...
        
        # Add kernel hot reload
        self.kernel = get_kernel_reload()
    
    def initialize(self):
        """Initialize all layers"""
        # ... your existing initialization ...
        
        # Optionally enable auto-reload in development
        if self.config.get('development_mode', False):
            self.kernel.start_watch()
            print("✓ Hot reload enabled (development mode)")
        
        return True
    
    def shutdown(self):
        """Shutdown all layers"""
        # Stop kernel watch
        if self.kernel.watch_active:
            self.kernel.stop_watch()
        
        # ... rest of your shutdown code ...
```

---

## Option 4: Add to example_full_os.py

Update your existing `example_full_os.py`:

```python
from ai_os.kernel import get_kernel_reload

def main():
    """Initialize and run the full AI OS."""
    
    print("\n" + "#" * 60)
    print("# AI OS - Full System Initialization")
    print("# Layers 1-8: Complete Operating System")
    print("# Hot Reload: ENABLED")
    print("#" * 60 + "\n")
    
    # Initialize kernel hot reload
    kernel = get_kernel_reload()
    print("✓ Kernel hot reload initialized")
    
    # ... rest of your initialization ...
    
    # Enable auto-reload for development
    kernel.start_watch()
    print("✓ Auto-reload enabled")
    
    # ... run your shell ...
    
    # Cleanup
    kernel.stop_watch()
```

---

## Quick Integration Examples

### Minimal Integration (Just Commands)

```python
# In your shell.py
from ai_os.kernel.kernel_commands import KernelCommands

class Shell:
    def __init__(self):
        self.kernel_cmds = KernelCommands()
        self.commands['refresh'] = self.kernel_cmds.cmd_os_refresh
```

### Full Integration (All Features)

```python
# In your shell.py
from ai_os.kernel import get_kernel_reload
from ai_os.kernel.kernel_commands import register_kernel_commands

class Shell:
    def __init__(self):
        # Initialize kernel
        self.kernel = get_kernel_reload()
        
        # Register all kernel commands
        register_kernel_commands(self)
        
        # Optionally enable auto-reload
        # self.kernel.start_watch()
```

---

## Testing Your Integration

### Test 1: Basic Commands

```bash
# Start your CLI
python ai_os/example_full_os.py

# Try refresh command
> refresh
# Should show reload results

# Try watch command
> watch --status
# Should show watch status
```

### Test 2: Live Reload

```bash
# Enable watch mode
> watch --live

# Edit a file (e.g., add a print statement)
# Wait 2 seconds

# Should see auto-reload message
# Test the change
```

### Test 3: Rollback

```bash
# Make a change that breaks something
> refresh

# Rollback
> rollback module_name

# Should restore previous version
```

---

## Configuration Options

### Enable Auto-Reload on Startup

```python
# In your config
config = {
    'kernel': {
        'auto_reload': True,
        'watch_interval': 2  # seconds
    }
}

# In initialization
if config['kernel']['auto_reload']:
    kernel.start_watch()
```

### Custom Watched Directories

```python
# In kernel initialization
kernel = KernelHotReload()
kernel.watched_dirs = [
    'core', 'cli_shell', 'custom_modules'
]
kernel._scan_modules()
```

### Custom Reload Hooks

```python
# In your module
def on_reload():
    """Called after this module is reloaded"""
    print("✓ My module reloaded!")
    # Re-initialize state
    init_my_state()
```

---

## Common Integration Patterns

### Pattern 1: Development vs Production

```python
import os

if os.getenv('AIOS_ENV') == 'development':
    kernel.start_watch()
    print("Development mode: Auto-reload enabled")
else:
    print("Production mode: Auto-reload disabled")
```

### Pattern 2: Conditional Commands

```python
# Only register in development
if development_mode:
    self.commands['refresh'] = kernel_cmds.cmd_os_refresh
    self.commands['watch'] = kernel_cmds.cmd_os_watch
```

### Pattern 3: Custom Command Prefix

```python
# Use different prefix
self.commands['dev-reload'] = kernel_cmds.cmd_os_refresh
self.commands['dev-watch'] = kernel_cmds.cmd_os_watch
```

---

## Troubleshooting Integration

### Issue: Commands Not Found

**Solution:**
```python
# Verify registration
print(self.commands.keys())

# Check if kernel_cmds exists
print(hasattr(self, 'kernel_cmds'))
```

### Issue: Import Errors

**Solution:**
```python
# Add to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Then import
from ai_os.kernel import get_kernel_reload
```

### Issue: Watch Mode Not Working

**Solution:**
```python
# Check if started
print(kernel.watch_active)

# Check logs
cat ai_os/var/log/kernel_hotreload.log
```

---

## Best Practices

1. **Start Simple**
   - Begin with just the `refresh` command
   - Add watch mode later

2. **Test Thoroughly**
   - Test each command individually
   - Verify reload actually works

3. **Use in Development Only**
   - Enable auto-reload in dev
   - Disable in production

4. **Monitor Logs**
   - Check `kernel_hotreload.log`
   - Identify issues early

5. **Add Reload Hooks**
   - Clean initialization
   - Proper state management

---

## Example: Complete Integration

Here's a complete example integrating with your existing shell:

```python
# ai_os/cli_shell/shell_with_hotreload.py

import os
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_os.kernel import get_kernel_reload
from ai_os.kernel.kernel_commands import KernelCommands

# Import your existing components
from ai_os.core import AIOSCore
from ai_os.devices import DeviceLayer
from ai_os.filesystem import VirtualFileSystem
# ... etc ...


class ShellWithHotReload:
    """Enhanced shell with hot reload support"""
    
    def __init__(self):
        # Initialize kernel hot reload
        self.kernel = get_kernel_reload()
        self.kernel_cmds = KernelCommands()
        
        # Your existing initialization
        self.core = AIOSCore()
        self.devices = DeviceLayer()
        # ... etc ...
        
        # Command registry
        self.commands = {}
        self._register_commands()
        
        # Enable auto-reload in development
        if os.getenv('AIOS_ENV') == 'development':
            self.kernel.start_watch()
            print("✓ Auto-reload enabled (development mode)")
    
    def _register_commands(self):
        """Register all commands"""
        # Your existing commands
        self.commands['help'] = self.cmd_help
        self.commands['exit'] = self.cmd_exit
        # ... etc ...
        
        # Kernel hot reload commands
        self.commands['refresh'] = self.kernel_cmds.cmd_os_refresh
        self.commands['watch'] = self.kernel_cmds.cmd_os_watch
        self.commands['rollback'] = self.kernel_cmds.cmd_os_rollback
        self.commands['reload-status'] = self.kernel_cmds.cmd_os_status
    
    def execute_command(self, input_line):
        """Execute a command"""
        parts = input_line.strip().split()
        if not parts:
            return
        
        # Handle compound commands (os refresh, os watch, etc.)
        if len(parts) >= 2 and parts[0] == 'os':
            cmd = parts[1]
            args = parts[2:]
            
            if cmd in ['refresh', 'watch', 'rollback', 'status']:
                full_cmd = f"{cmd}"
                if full_cmd in self.commands:
                    result = self.commands[full_cmd](args)
                    if result:
                        print(result)
                return
        
        # Regular command handling
        cmd = parts[0]
        args = parts[1:]
        
        if cmd in self.commands:
            result = self.commands[cmd](args)
            if result:
                print(result)
        else:
            print(f"Unknown command: {cmd}")
    
    def run(self):
        """Main shell loop"""
        print("\nAI OS Shell with Hot Reload")
        print("Type 'help' for commands\n")
        
        while True:
            try:
                user_input = input("aios> ").strip()
                if not user_input:
                    continue
                
                self.execute_command(user_input)
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                break
    
    def shutdown(self):
        """Shutdown the shell"""
        # Stop watch mode
        if self.kernel.watch_active:
            self.kernel.stop_watch()
        
        # Your existing shutdown
        print("Shutting down...")


def main():
    """Main entry point"""
    shell = ShellWithHotReload()
    
    try:
        shell.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        shell.shutdown()


if __name__ == '__main__':
    main()
```

---

## Summary

Choose the integration option that works best for you:

1. **Standalone CLI** - Use `main_cli_hotreload.py` as-is
2. **Add Commands** - Register kernel commands in existing shell
3. **Full Integration** - Add to OS Master and shell
4. **Custom Integration** - Use the examples above

All options give you hot reload capabilities without restarting! 🔥

---

*Integration Guide - Kernel Hot Reload System*

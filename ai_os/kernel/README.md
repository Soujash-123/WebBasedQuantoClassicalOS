# Kernel Hot Reload Module

## 🔥 Self-Updating Kernel Manager

This module enables **real-time code updates** without restarting the AI OS CLI.

---

## Quick Start

### 1. Run the Hot Reload CLI
```bash
python ai_os/main_cli_hotreload.py
```

### 2. Make Code Changes
Edit any Python file in `ai_os/`

### 3. Reload in Running CLI
```bash
root@aios:/$ refresh
```

### 4. Changes Are Live! 🎉

---

## Files

- **`kernel_hot_reload.py`** - Core hot reload manager
- **`kernel_commands.py`** - CLI command integration
- **`example_usage.py`** - Demonstrations and tests
- **`__init__.py`** - Module exports

---

## Commands

| Command | Description |
|---------|-------------|
| `refresh` | Reload modified modules |
| `watch --live` | Enable auto-reload |
| `watch --stop` | Disable auto-reload |
| `rollback <module>` | Revert to previous version |
| `reload-status` | Show reload history |

---

## Features

✅ **Persistent CLI** - No restarts needed  
✅ **Smart Reload** - Only changed modules  
✅ **Auto-Reload** - Background watching  
✅ **Rollback** - Safety net for failures  
✅ **Manifest** - Track all modules  
✅ **Hooks** - Custom reload handlers  

---

## Example Workflow

```bash
# Start CLI
$ python ai_os/main_cli_hotreload.py

# Enable auto-reload
root@aios:/$ watch --live
✓ Watch mode ACTIVATED

# Edit files (CLI keeps running)
# Changes auto-reload every 2 seconds

# Test changes immediately
root@aios:/$ mynewcommand
Success!

# Disable auto-reload
root@aios:/$ watch --stop
```

---

## Documentation

See: `documentation/KERNEL_HOT_RELOAD.md`

---

## Testing

```bash
# Quick test
python ai_os/kernel/example_usage.py --quick

# Interactive demo
python ai_os/kernel/example_usage.py --interactive

# All demos
python ai_os/kernel/example_usage.py --all
```

---

## Integration

### With Existing Shell

```python
from ai_os.kernel.kernel_commands import register_kernel_commands

# In your shell initialization
register_kernel_commands(shell)
```

### Programmatic Usage

```python
from ai_os.kernel import get_kernel_reload

kernel = get_kernel_reload()

# Detect changes
changed = kernel.detect_changes()

# Reload
result = kernel.refresh()

# Watch mode
kernel.start_watch()
kernel.stop_watch()
```

---

## Architecture

```
KernelHotReload
├── Module Scanner (detect Python files)
├── Change Detector (SHA256 checksums)
├── Reload Engine (importlib.reload)
├── Backup System (rollback support)
├── Watch Thread (auto-reload)
└── Manifest Manager (tracking)
```

---

## Safety

- ✅ Automatic backup before reload
- ✅ Rollback on failure
- ✅ Thread-safe operations
- ✅ Error logging
- ✅ Reload hooks

---

**Never restart your OS again! 🚀**

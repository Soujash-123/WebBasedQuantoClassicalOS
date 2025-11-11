# Kernel Hot Reload System

## Overview

The **Kernel Hot Reload System** enables real-time code updates in the AI OS without restarting the CLI. Developers can modify code, reload modules, and see changes immediately in the running session.

---

## 🎯 Key Features

### 1. **Persistent CLI Runtime**
- CLI runs continuously without restarts
- Code changes detected and applied in real-time
- No interruption to active sessions

### 2. **Smart Reload Mechanism**
- Detects file changes via SHA256 checksums
- Reloads only modified modules
- Recursive dependency reloading
- Module backup before reload

### 3. **Auto-Update Mode**
- Background watcher monitors file changes
- Automatic reload every 2 seconds
- Enable with `os watch --live`

### 4. **Rollback System**
- Automatic backup before reload
- Revert to previous version on failure
- Manual rollback with `os rollback <module>`

### 5. **Manifest Tracking**
- `kernel_manifest.json` tracks all modules
- Timestamps, checksums, and versions
- Reload history and statistics

---

## 📦 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Shell (Running)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │  Kernel Hot Reload    │
         │      Manager          │
         └───────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────┐    ┌─────▼─────┐   ┌─────▼──────┐
│ Module │    │  Change   │   │  Reload    │
│Scanner │    │ Detector  │   │  Engine    │
└────────┘    └───────────┘   └────────────┘
    │                │                │
    └────────────────┼────────────────┘
                     │
         ┌───────────▼───────────┐
         │  Module Registry      │
         │  (kernel_manifest)    │
         └───────────────────────┘
```

---

## 🚀 Quick Start

### 1. Start the Hot Reload CLI
```bash
python ai_os/main_cli_hotreload.py
```

### 2. Make Code Changes
Edit any file in `ai_os/`:
```python
# ai_os/kernel/example_usage.py
def my_new_function():
    print("This is a new function!")
```

### 3. Reload in Running CLI
```bash
root@aios:/$ refresh
```

### 4. Changes Are Live!
```python
>>> from ai_os.kernel.example_usage import my_new_function
>>> my_new_function()
This is a new function!
```

---

## 📋 CLI Commands

### `refresh` / `os refresh`
Reload all modified modules.

**Usage:**
```bash
refresh [--force]
os refresh [--force]
```

**Options:**
- `--force` - Reload all modules regardless of changes

**Example:**
```bash
root@aios:/$ refresh
============================================================
KERNEL MODULE REFRESH
============================================================
Mode: SMART RELOAD (changed modules only)

Scanning for changes...

Results:
  Total Modules: 3
  ✓ Success: 3
  ✗ Failed: 0
  Duration: 0.15s
============================================================
```

---

### `watch` / `os watch`
Enable/disable auto-reload watch mode.

**Usage:**
```bash
watch [--live|--stop|--status]
os watch [--live|--stop|--status]
```

**Options:**
- `--live` - Start watching for changes
- `--stop` - Stop watching
- `--status` - Show watch status

**Examples:**
```bash
# Enable auto-reload
root@aios:/$ watch --live
✓ Watch mode ACTIVATED - Auto-reloading enabled

# Check status
root@aios:/$ watch --status
Watch mode: ACTIVE ✓

# Disable auto-reload
root@aios:/$ watch --stop
✓ Watch mode DEACTIVATED
```

---

### `rollback` / `os rollback`
Rollback a module to its previous version.

**Usage:**
```bash
rollback <module_name>
os rollback <module_name>
```

**Example:**
```bash
root@aios:/$ rollback cli_shell.command_registry

Attempting rollback of: cli_shell.command_registry
✓ Successfully rolled back cli_shell.command_registry
```

---

### `reload-status` / `os status`
Show kernel reload status and history.

**Usage:**
```bash
reload-status
os status [reloads|modules]
```

**Options:**
- `reloads` - Show reload history
- `modules` - Show module registry

**Example:**
```bash
root@aios:/$ reload-status
======================================================================
KERNEL HOT RELOAD STATUS
======================================================================
Total Modules Tracked: 45
Watch Mode: ACTIVE
Backed Up Modules: 12
Total Reload Events: 5

Recent Reload Events:
----------------------------------------------------------------------
  Time: 2025-11-06T18:30:15
  Modules: 3 (✓ 3, ✗ 0)
  Duration: 0.15s

======================================================================
```

---

## 🔧 Developer Workflow

### Scenario 1: Add New Command

**Step 1:** Keep CLI running
```bash
python ai_os/main_cli_hotreload.py
```

**Step 2:** Edit command file
```python
# ai_os/cli_shell/custom_commands.py
def cmd_hello(args):
    """Say hello"""
    return "Hello, World!"
```

**Step 3:** Reload in running CLI
```bash
root@aios:/$ refresh
```

**Step 4:** Use new command immediately
```bash
root@aios:/$ hello
Hello, World!
```

---

### Scenario 2: Fix Bug in Running System

**Step 1:** Bug detected in running system
```bash
root@aios:/$ mycommand
Error: division by zero
```

**Step 2:** Fix the code (CLI still running)
```python
# ai_os/some_module.py
def buggy_function(x):
    # Fixed: added check
    if x == 0:
        return 0
    return 100 / x
```

**Step 3:** Reload the fix
```bash
root@aios:/$ refresh
```

**Step 4:** Test the fix
```bash
root@aios:/$ mycommand
Success!
```

---

### Scenario 3: Continuous Development

**Step 1:** Enable auto-reload
```bash
root@aios:/$ watch --live
✓ Watch mode ACTIVATED
```

**Step 2:** Make multiple changes
- Edit files
- Add functions
- Fix bugs

**Step 3:** Changes auto-reload every 2 seconds
```
[Auto-reload] Detected 2 changed modules
[Auto-reload] Reloaded successfully
```

**Step 4:** Test immediately - no manual reload needed!

---

## 🧪 Testing

### Run Example Usage
```bash
python ai_os/kernel/example_usage.py --quick
```

### Run Interactive Demo
```bash
python ai_os/kernel/example_usage.py --interactive
```

### Run All Demos
```bash
python ai_os/kernel/example_usage.py --all
```

---

## 📊 Module Manifest

The `kernel_manifest.json` tracks all modules:

```json
{
  "version": "1.0.0",
  "last_scan": "2025-11-06T18:30:00",
  "modules": [
    {
      "module": "ai_os.core.system_boot",
      "last_updated": "2025-11-06T18:20:00",
      "status": "active",
      "version": "v1.0.0",
      "checksum": "bdf64a3c..."
    },
    {
      "module": "ai_os.cli_shell.command_registry",
      "last_updated": "2025-11-06T18:25:00",
      "status": "active",
      "version": "v1.0.0",
      "checksum": "7f3e9a2b..."
    }
  ]
}
```

---

## 🔒 Safety Features

### 1. **Automatic Backup**
Every module is backed up before reload:
```python
# Backup created automatically
backup_modules[module_name] = current_module
```

### 2. **Error Handling**
Failed reloads automatically rollback:
```python
try:
    reload_module(module_name)
except Exception:
    restore_from_backup(module_name)
```

### 3. **Reload Hooks**
Modules can define cleanup/init hooks:
```python
def on_reload():
    """Called after module reload"""
    print("Module reloaded successfully!")
    # Re-initialize state
    # Re-register commands
```

### 4. **Thread Safety**
Reloads are thread-safe with locks:
```python
with reload_lock:
    reload_module(module_name)
```

---

## 🛠️ Advanced Usage

### Custom Reload Hooks

Add to your module:
```python
def on_reload():
    """Hook called after reload"""
    print("✓ My module reloaded!")
    # Re-initialize
    init_my_module()
```

### Programmatic Usage

```python
from ai_os.kernel import get_kernel_reload

kernel = get_kernel_reload()

# Detect changes
changed = kernel.detect_changes()
print(f"Changed: {changed}")

# Reload
result = kernel.refresh()
print(f"Reloaded: {result['success']} modules")

# Start watch mode
kernel.start_watch()

# Stop watch mode
kernel.stop_watch()

# Rollback
kernel.rollback('ai_os.my_module')
```

### Integration with Existing Shell

```python
from ai_os.kernel.kernel_commands import register_kernel_commands

# In your shell initialization
register_kernel_commands(shell)
```

---

## 📝 Logging

Logs are written to: `ai_os/var/log/kernel_hotreload.log`

**Example log:**
```
[2025-11-06T18:30:15] [INFO] Kernel Hot Reload Manager initialized
[2025-11-06T18:30:20] [INFO] Detected change in ai_os.cli_shell.commands
[2025-11-06T18:30:20] [INFO] Backed up module: ai_os.cli_shell.commands
[2025-11-06T18:30:20] [INFO] Reloaded existing module: ai_os.cli_shell.commands
[2025-11-06T18:30:20] [INFO] Refresh complete: 1 success, 0 failed in 0.12s
```

---

## ⚙️ Configuration

### Watched Directories
Edit in `kernel_hot_reload.py`:
```python
self.watched_dirs = [
    'core', 'filesystem', 'processes', 'network_layer',
    'cli_shell', 'security_layer', 'devices', 'system_simulation_layer',
    'memory_layer', 'diagnostics', 'users', 'system'
]
```

### Watch Interval
Change polling interval:
```python
# In _watch_loop()
time.sleep(2)  # Check every 2 seconds
```

---

## 🐛 Troubleshooting

### Issue: Module Not Reloading

**Solution:**
```bash
# Force reload all modules
root@aios:/$ refresh --force
```

### Issue: Reload Failed

**Solution:**
```bash
# Check logs
cat ai_os/var/log/kernel_hotreload.log

# Rollback
root@aios:/$ rollback <module_name>
```

### Issue: Watch Mode Not Working

**Solution:**
```bash
# Check status
root@aios:/$ watch --status

# Restart watch
root@aios:/$ watch --stop
root@aios:/$ watch --live
```

---

## 📈 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Module Scan | < 1s | Initial scan |
| Change Detection | < 0.1s | Per check |
| Single Reload | < 0.05s | Per module |
| Batch Reload | < 0.5s | 10 modules |
| Watch Interval | 2s | Configurable |

---

## 🎓 Best Practices

1. **Use Watch Mode During Development**
   - Enable with `watch --live`
   - Automatic reloads save time

2. **Test After Reload**
   - Always test reloaded modules
   - Check for side effects

3. **Use Rollback for Safety**
   - If reload breaks something
   - Quick recovery with rollback

4. **Monitor Logs**
   - Check `kernel_hotreload.log`
   - Identify reload issues

5. **Define Reload Hooks**
   - Add `on_reload()` to modules
   - Clean initialization after reload

---

## 🔮 Future Enhancements

- [ ] Dependency graph visualization
- [ ] Selective module watching
- [ ] Remote reload triggers
- [ ] Reload performance metrics
- [ ] Module version history
- [ ] Automated testing after reload

---

## 📞 Support

- **Example Usage:** `ai_os/kernel/example_usage.py`
- **Main CLI:** `ai_os/main_cli_hotreload.py`
- **Logs:** `ai_os/var/log/kernel_hotreload.log`
- **Manifest:** `kernel_manifest.json`

---

**Kernel Hot Reload - Never Restart Your OS Again! 🔥**

*Last Updated: November 6, 2025*

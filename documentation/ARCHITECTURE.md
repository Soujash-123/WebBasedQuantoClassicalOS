# AI OS Architecture Documentation v1.0

## Overview

AI OS is a Python-based simulated operating system with a CLI interface, featuring memory management, networking, security, file systems, process management, and Linux-like command utilities.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Shell Layer                          │
│  (Command Parsing, Execution, History, Session Management)  │
└──────────────────┬──────────────────────────────────────────┘
                   │
    ┌──────────────┴──────────────┐
    │                             │
┌───▼────────┐              ┌────▼─────────┐
│ User Layer │              │ System Layer │
│ (Auth,     │              │ (Config,     │
│  Perms)    │              │  Logging)    │
└───┬────────┘              └────┬─────────┘
    │                             │
┌───▼─────────────────────────────▼───────────────────────┐
│              Core Layer (Event Bus, Registry)            │
└──────┬──────┬──────┬──────┬──────┬──────┬──────┬────────┘
       │      │      │      │      │      │      │
   ┌───▼──┐ ┌─▼───┐ ┌▼────┐ ┌▼───┐ ┌▼───┐ ┌▼───┐ ┌▼────────┐
   │Memory│ │Net  │ │Sec  │ │VFS │ │Proc│ │Dev │ │Diag     │
   │Layer │ │Layer│ │Layer│ │    │ │    │ │    │ │Layer    │
   └──────┘ └─────┘ └─────┘ └────┘ └────┘ └────┘ └─────────┘
```

---

## Layer Descriptions

### 1. Core Layer
**Location:** `ai_os/core/`

**Purpose:** Provides fundamental OS infrastructure.

**Components:**
- **Event Bus** (`event_bus.py`): Inter-process communication system
- **System Registry** (`system_registry.py`): Component registration and discovery
- **Config Manager** (`config_manager.py`): Centralized configuration
- **Core Master** (`core_master.py`): Layer initialization and coordination

**Key Functions:**
- System initialization and shutdown
- Event-driven communication between layers
- Global state management
- Configuration persistence

---

### 2. Memory Layer
**Location:** `ai_os/memory_layer/`

**Purpose:** Virtual memory management and allocation tracking.

**Components:**
- **Virtual Memory** (`virtual_memory.py`): Page-based memory system
- **Memory Manager** (`memory_manager.py`): High-level memory operations
- **Memory Monitor** (`memory_monitor.py`): Real-time usage monitoring
- **Memory Master** (`memory_master.py`): Unified interface

**Features:**
- Virtual memory with paging (default: 512MB, 4KB pages)
- Process memory allocation and tracking
- Memory swapping to virtual disk
- Garbage collection for orphaned memory
- Usage monitoring and alerts

**Commands:** `memstat`, `memdump`, `flushmem`, `procmem`, `memhistory`, `memmonitor`

**Data Flow:**
```
Process Request → Memory Manager → Virtual Memory → Page Allocation
                                 ↓
                        Memory Monitor (tracking)
```

---

### 3. Network Layer
**Location:** `ai_os/network_layer/`

**Purpose:** Network interface management and connectivity tools.

**Components:**
- **Network Interface** (`network_interface.py`): Adapter management
- **Network Tools** (`network_tools.py`): Ping, port scanning utilities
- **Network Monitor** (`network_monitor.py`): Connection tracking
- **Network Master** (`network_master.py`): Unified interface

**Features:**
- Virtual and physical network adapter management
- Ping and connectivity testing
- Port scanning and service detection
- Connection monitoring and statistics
- Network interface configuration

**Commands:** `ping`, `netstat`, `ifconfig`, `ipconfig`, `hostname`, `netinfo`, `ports`, `netstats`, `checkport`

**Data Flow:**
```
Command → Network Tools → Socket Operations → Network Interface
                         ↓
                Network Monitor (logging)
```

---

### 4. Security Layer
**Location:** `ai_os/security_layer/`

**Purpose:** Authentication, encryption, and access control.

**Components:**
- **Encryption Manager** (`encryption.py`): AES/Fernet encryption
- **Hashing Manager** (`hashing.py`): SHA256, PBKDF2 hashing
- **Access Control** (`access_control.py`): Permission management
- **Auth Manager** (`auth_manager.py`): User authentication and sessions
- **Security Master** (`security_master.py`): Unified interface

**Features:**
- User authentication with session tokens
- File and data encryption/decryption
- Password hashing with salt
- Fine-grained access control (read, write, execute, delete, admin)
- Session management with expiration
- HMAC signing and verification

**Commands:** `login`, `logout`, `whoami`, `adduser`, `deluser`, `passwd`, `users`, `sessions`, `encrypt`, `decrypt`, `genkey`, `hash`, `hashfile`, `chmod`, `chown`, `getacl`

**Security Model:**
```
User → Authentication → Session Token → Access Control Check → Resource Access
                                       ↓
                              Encryption (if required)
```

---

### 5. File System Layer (VFS)
**Location:** `ai_os/filesystem/`

**Purpose:** Virtual file system with hierarchical structure.

**Components:**
- **VFS Manager** (`vfs_manager.py`): File operations
- **Mount Manager** (`mount_manager.py`): Device mounting
- **Storage Adapter** (`storage_adapter.py`): Backend storage
- **File Node** (`file_node.py`): File/directory representation
- **VFS Master** (`vfs_master.py`): Unified interface

**Features:**
- Hierarchical directory structure
- CRUD operations on files and directories
- Multiple storage backends
- Mount point management
- Metadata tracking (size, permissions, timestamps)
- Path navigation and resolution

**Commands:** `ls`, `cd`, `pwd`, `mkdir`, `rm`, `cp`, `mv`, `cat`, `touch`, `grep`, `head`, `tail`

---

### 6. Process Layer
**Location:** `ai_os/processes/`

**Purpose:** Process lifecycle management and scheduling.

**Components:**
- **Process** (`process.py`): Process representation
- **Process Manager** (`process_manager.py`): Process operations
- **Scheduler** (`scheduler.py`): Process scheduling
- **Process Master** (`process_master.py`): Unified interface

**Features:**
- Process creation and termination
- PID assignment and tracking
- Process states (Running, Waiting, Terminated)
- Basic scheduling algorithms
- Process table management

**Commands:** `ps`, `run`, `kill`, `killall`

---

### 7. Device Layer
**Location:** `ai_os/devices/`

**Purpose:** Hardware abstraction and device management.

**Components:**
- **Base Device** (`base_device.py`): Device interface
- **Device Manager** (`device_manager.py`): Device operations
- **Storage Device** (`storage_device.py`): Disk devices
- **Console Device** (`console_device.py`): I/O devices
- **Device Master** (`device_master.py`): Unified interface

**Features:**
- Device detection and registration
- Device drivers
- Power management
- Device status monitoring

---

### 8. CLI Shell Layer
**Location:** `ai_os/cli_shell/`

**Purpose:** Interactive command-line interface.

**Components:**
- **Shell** (`shell.py`): Main shell loop
- **Command Parser** (`command_parser.py`): Command parsing
- **Command Registry** (`command_registry.py`): Command mapping
- **Command History** (`command_history.py`): History management
- **Session Manager** (`os_session_manager.py`): Shell sessions
- **Error Handler** (`error_handler.py`): Error processing

**Features:**
- Command parsing and execution
- Command history with persistence
- Command aliasing
- Tab completion
- Error handling and formatting
- Colorized output
- Session management

---

### 9. System Simulation Layer
**Location:** `ai_os/system_simulation_layer/`

**Purpose:** Linux-like command utilities and package management.

**Components:**
- **Package Manager** (`package_manager.py`): APT-like system
- **Git Interface** (`git_interface.py`): Version control
- **Mount Manager** (`mount_manager.py`): Device mounting
- **System Environment** (`system_environment.py`): Environment variables
- **Dependency Resolver** (`dependency_resolver.py`): Package dependencies

**Features:**
- APT-style package management (install, remove, update, upgrade)
- Git operations (clone, pull, status, log)
- Device mounting and unmounting
- Environment variable management
- Disk utilities (df, lsblk)

**Commands:** `apt`, `git`, `mount`, `umount`, `df`, `lsblk`, `export`, `unset`, `env`

---

### 10. Diagnostics Layer
**Location:** `ai_os/diagnostics/`

**Purpose:** System health monitoring and diagnostics.

**Components:**
- **System Check** (`system_check.py`): Layer verification
- **Dependency Checker** (`dependency_checker.py`): Import validation
- **Resource Monitor** (`resource_monitor.py`): CPU/memory tracking
- **Diagnostics Master** (`diagnostics_master.py`): Unified interface

**Features:**
- Comprehensive system diagnostics
- Layer health checks
- Dependency verification
- Real-time resource monitoring
- Historical resource tracking

**Commands:** `syscheck`, `depcheck`, `resources`, `reshistory`

---

## Data Flow Examples

### Example 1: User Login Flow
```
1. User enters: login root password123
2. CLI Shell → Command Parser
3. Command Parser → Security Layer (cmd_login)
4. Security Layer → Auth Manager (authenticate)
5. Auth Manager → Hashing Manager (verify_password)
6. Auth Manager creates Session Token
7. Security Layer stores current_user and current_token
8. Response: "Login successful. Welcome, root!"
```

### Example 2: File Encryption Flow
```
1. User enters: encrypt secret.txt
2. CLI Shell → Security Layer (cmd_encrypt)
3. Security Layer → Encryption Manager (encrypt_file)
4. Encryption Manager reads file via VFS Layer
5. Encryption Manager encrypts data with Fernet
6. Encrypted data written back via VFS Layer
7. Response: "File encrypted: secret.txt.encrypted"
```

### Example 3: Memory Allocation Flow
```
1. Process requests memory
2. Process Layer → Memory Layer (allocate)
3. Memory Manager → Virtual Memory (allocate)
4. Virtual Memory finds free pages
5. If insufficient: swap out inactive pages
6. Pages allocated to process
7. Memory Monitor logs allocation
8. Return allocated page IDs
```

### Example 4: Network Ping Flow
```
1. User enters: ping google.com
2. CLI Shell → Network Layer (cmd_ping)
3. Network Layer → Network Tools (ping)
4. Network Tools resolves hostname via socket
5. Network Tools executes system ping or socket test
6. Results parsed and formatted
7. Network Monitor logs connection attempt
8. Response: Ping statistics displayed
```

---

## Inter-Layer Communication

### Event Bus Pattern
Layers communicate via the Event Bus for loose coupling:

```python
# Layer A publishes event
event_bus.publish('memory_low', {'threshold': 90, 'current': 95})

# Layer B subscribes to event
event_bus.subscribe('memory_low', callback_function)
```

### Direct API Calls
For performance-critical operations, layers expose direct APIs:

```python
# CLI Shell directly calls Memory Layer
memory_layer.allocate(process_id=123, size_mb=64)
```

---

## Configuration System

### Configuration Files
- `ai_os_config.json`: Main system configuration
- `system_config.json`: System-specific settings
- `users.json`: User database
- `repo_registry.json`: Package repository

### Configuration Hierarchy
```
1. Default values (hardcoded)
2. System config file
3. User config file
4. Runtime overrides
```

---

## Security Model

### Authentication
- Password-based with PBKDF2 hashing
- Session tokens with expiration
- Failed attempt tracking and lockout

### Authorization
- Role-based access control
- Resource-level permissions (rwxda)
- Admin override capability

### Encryption
- AES encryption via Fernet
- Key derivation from passwords
- Secure key storage

---

## Error Handling

### Error Levels
1. **CRITICAL**: System failure, requires restart
2. **ERROR**: Operation failed, user action needed
3. **WARNING**: Potential issue, operation continues
4. **INFO**: Informational message

### Error Flow
```
Error Occurs → Error Handler → Logger → User Notification
                             ↓
                    Event Bus (error event)
```

---

## Performance Considerations

### Memory Management
- Page-based allocation reduces fragmentation
- Lazy swapping minimizes disk I/O
- Monitoring runs in separate thread

### Network Operations
- Asynchronous socket operations
- Connection pooling
- Timeout management

### File System
- Cached metadata for fast lookups
- Lazy loading of file contents
- Efficient path resolution

---

## Extension Points

### Adding New Commands
```python
def cmd_mycommand(self, args):
    """My custom command"""
    # Implementation
    return "Result"

# Register in layer's get_commands()
'mycommand': {
    'function': self.cmd_mycommand,
    'description': 'My custom command',
    'usage': 'mycommand <args>'
}
```

### Adding New Layers
1. Create layer directory under `ai_os/`
2. Implement layer master class
3. Define `get_commands()` method
4. Register with Core Layer
5. Initialize in main OS startup

---

## Testing Strategy

### Unit Tests
- Test individual layer components
- Mock dependencies
- Cover edge cases

### Integration Tests
- Test layer interactions
- End-to-end command flows
- Error propagation

### Manual Tests
- User workflow scenarios
- Performance under load
- Security validation

---

## Future Enhancements

### Planned Features
- GUI interface
- Network file systems
- Advanced scheduling algorithms
- Plugin system for extensions
- Remote access capabilities
- Container support
- Distributed processing

---

## Troubleshooting

### Common Issues

**Issue:** Import errors on startup
**Solution:** Run `syscheck` to verify all layers

**Issue:** Memory allocation failures
**Solution:** Run `memstat` and `flushmem` to free memory

**Issue:** Authentication failures
**Solution:** Check `users.json` exists and is valid

**Issue:** Network commands fail
**Solution:** Verify network connectivity and firewall settings

---

## References

- [Commands Reference](COMMANDS.md)
- [Configuration Guide](CONFIGURATION.md)
- [Testing Guide](TESTING.md)

---

*AI OS v1.0 - Architecture Documentation*

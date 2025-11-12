# ✅ Layers 5 & 6 Complete: Process Management + User Authentication

**Layers 5 & 6** have been fully implemented with process scheduling, user authentication, and multi-user support!

## 📦 What Was Built

### **Layer 5: Process Management**

#### **Core Components**

1. **Process** (`process.py`)
   - Process lifecycle management (ready, running, suspended, terminated)
   - PID tracking and ownership
   - Priority levels (1-10)
   - CPU time tracking
   - Thread-based execution
   - Output capture

2. **Scheduler** (`scheduler.py`)
   - **FIFO** (First-In-First-Out) scheduling
   - **Round-Robin** scheduling with time quantum
   - Process queues (ready, running, waiting, terminated)
   - Concurrent process management
   - Statistics tracking

3. **ProcessManager** (`process_manager.py`)
   - Process registration and control
   - CLI commands: `run`, `ps`, `kill`, `suspend`, `resume`, `top`
   - Permission-based process control
   - Process cleanup and statistics

4. **ProcessLayer** (`process_master.py`)
   - Integration with Core, Device, VFS, and I/O layers
   - Event-driven architecture
   - Unified process management interface

### **Layer 6: User Management & Authentication**

#### **Core Components**

1. **User** (`user.py`)
   - User accounts with roles (root, admin, user, guest)
   - **SHA-256 password hashing**
   - Permission system
   - Account status (active, locked)
   - Login tracking

2. **UserManager** (`user_manager.py`)
   - User account management
   - Authentication
   - Password management
   - User persistence (JSON storage)
   - Permission enforcement

3. **SessionManager** (`session_manager.py`)
   - Login/logout functionality
   - Session tracking with unique IDs
   - Activity monitoring
   - Session timeout support
   - Multi-session support

4. **UserLayer** (`user_master.py`)
   - Integration with all OS layers
   - CLI commands: `login`, `logout`, `whoami`, `adduser`, `deluser`, `passwd`, `listusers`
   - Sudo functionality
   - Home directory creation

## 🎯 Key Features

### **Process Management**

✅ **Process Lifecycle**
- Create, start, suspend, resume, terminate
- Automatic PID assignment
- Process ownership by user
- Background and foreground execution

✅ **Scheduling Algorithms**
- FIFO (First-In-First-Out)
- Round-Robin with configurable time quantum
- Priority-based scheduling
- Concurrent process execution

✅ **Process Control**
- `run(name, function, ...)` - Execute a process
- `ps([owner], [show_all])` - List processes
- `kill(pid, [owner])` - Terminate process
- `suspend(pid)` / `resume(pid)` - Pause/resume
- `top([limit])` - Show top processes by CPU
- `cleanup_terminated()` - Remove finished processes

✅ **Statistics & Monitoring**
- CPU time tracking
- Process state monitoring
- Runtime statistics
- Scheduler performance metrics

### **User Authentication**

✅ **User Accounts**
- Default users: root, admin, guest
- Custom user creation
- Role-based access (root, admin, user, guest)
- Password hashing (SHA-256)

✅ **Authentication**
- Secure login/logout
- Session management
- Password verification
- Account locking

✅ **Permissions**
- Granular permission system
- Role-based defaults
- Wildcard permissions
- Permission checking

✅ **User Commands**
- `login(username, password)` - Authenticate user
- `logout()` - End session
- `whoami()` - Get current user
- `adduser(username, password, role)` - Create user
- `deluser(username)` - Delete user
- `passwd([username], new_password)` - Change password
- `listusers()` - List all users
- `sudo(function, ...)` - Execute with elevated privileges

## 📁 File Structure

```
ai_os/
├── processes/                 # Layer 5
│   ├── __init__.py
│   ├── process.py             # Process class
│   ├── scheduler.py           # FIFO/Round-Robin scheduler
│   ├── process_manager.py     # Process management
│   └── process_master.py      # Process layer integration
│
├── users/                     # Layer 6
│   ├── __init__.py
│   ├── user.py                # User class
│   ├── user_manager.py        # User account management
│   ├── session_manager.py     # Session tracking
│   └── user_master.py         # User layer integration
│
├── tests/manual_tests/
│   ├── test_processes.py      # Process layer tests
│   └── test_users.py          # User layer tests
│
└── example_layers_5_6.py      # Comprehensive demo
```

## 🚀 Quick Start

### 1. Run Tests

```bash
# Test Process Management
python tests\manual_tests\test_processes.py

# Test User Authentication
python tests\manual_tests\test_users.py
```

### 2. Run Demo

```bash
python example_layers_5_6.py
```

### 3. Basic Usage

```python
from core import AIOSCore
from processes import ProcessLayer
from users import UserLayer, UserRole

# Initialize
core = AIOSCore()
processes = ProcessLayer(core, algorithm="fifo")
users = UserLayer(core)

# Login
session = users.login("root", "root")
print(f"Logged in as: {users.whoami()}")

# Create user
users.adduser("alice", "password123", UserRole.USER)

# Run a process
def my_task():
    print("Task running!")
    return "Done"

proc = processes.run("MyTask", my_task, owner=users.whoami())

# List processes
for p in processes.ps():
    print(f"PID {p['pid']}: {p['name']} ({p['state']})")

# Cleanup
processes.shutdown()
users.shutdown()
core.shutdown()
```

## 💡 Usage Examples

### Example 1: Process Management

```python
# Run foreground process
proc = processes.run("Task1", my_function, args=(arg1, arg2))

# Run background process
proc = processes.run("Task2", my_function, background=True)

# List processes
for p in processes.ps():
    print(f"PID {p['pid']}: {p['name']}")

# Control processes
processes.suspend(proc.pid)
processes.resume(proc.pid)
processes.kill(proc.pid)

# Get statistics
stats = processes.get_statistics()
print(f"Total: {stats['total_processes']}")
```

### Example 2: User Authentication

```python
# Login
session = users.login("admin", "admin")

# Check current user
username = users.whoami()

# Create user
users.adduser("bob", "bob123", UserRole.USER)

# Change password
users.passwd("bob", "newpassword")

# Check permissions
if users.has_permission("user.create"):
    print("Can create users")

# Switch user
users.switch_user("bob", "newpassword")

# Logout
users.logout()
```

### Example 3: Integrated Workflow

```python
# Initialize all layers
core = AIOSCore()
vfs = VirtualFileSystem(core)
processes = ProcessLayer(core)
users = UserLayer(core, vfs_layer=vfs)

# Login
users.login("alice", "password")

# Create workspace
vfs.mkdir("/home/alice/projects")
vfs.write("/home/alice/projects/data.txt", "Important data")

# Run file processing as process
def process_file(vfs, path):
    content = vfs.read(path)
    print(f"Processing: {len(content)} bytes")
    return "Processed"

proc = processes.run(
    "FileProcessor",
    process_file,
    args=(vfs, "/home/alice/projects/data.txt"),
    owner=users.whoami(),
    background=True
)

# Monitor process
print(f"Process {proc.pid} running...")
proc.wait()
print(f"Process completed: {proc.result}")
```

## 🔐 Security Features

### **Password Security**
- SHA-256 hashing
- No plaintext storage
- Secure password verification

### **Permission System**
- Role-based access control
- Granular permissions
- Wildcard support
- Permission inheritance

### **Process Isolation**
- Process ownership
- User-based process control
- Permission checks on kill/suspend/resume

### **Session Management**
- Unique session IDs
- Activity tracking
- Session timeout support
- Secure logout

## 📊 Default Users

| Username | Password | Role  | Permissions |
|----------|----------|-------|-------------|
| root     | root     | ROOT  | All (*) |
| admin    | admin    | ADMIN | User management, process control, file access |
| guest    | guest    | GUEST | Read public files only |

## 🎮 Process States

- **READY**: Process created, waiting to start
- **RUNNING**: Process actively executing
- **SUSPENDED**: Process paused
- **WAITING**: Process waiting for resource
- **TERMINATED**: Process finished

## 🔄 Integration with Other Layers

### **Core Layer (Layer 1)**
- Event bus for process/user events
- System registry for layer registration
- Configuration management

### **Device Layer (Layer 2)**
- Process can access device information
- Console device for process output

### **I/O Layer (Layer 3)**
- Formatted process output
- User interaction

### **VFS Layer (Layer 4)**
- Processes can read/write files
- User home directories
- File permissions based on user

## 📈 Performance

- **Process Scheduling**: Efficient FIFO and Round-Robin algorithms
- **Concurrent Execution**: Thread-based process execution
- **Session Management**: Fast session lookup with dictionary storage
- **User Authentication**: Quick SHA-256 hashing

## 🧪 Test Coverage

All tests passing:
- ✅ Process creation and execution
- ✅ Process control (kill, suspend, resume)
- ✅ Process listing and statistics
- ✅ FIFO and Round-Robin scheduling
- ✅ User creation and deletion
- ✅ Authentication (valid/invalid)
- ✅ Session management
- ✅ Permission system
- ✅ Password changes
- ✅ Multi-user scenarios

## 🎯 CLI Commands Summary

### Process Commands
```python
processes.run(name, function, ...)  # Run process
processes.ps([owner])               # List processes
processes.kill(pid)                 # Terminate process
processes.suspend(pid)              # Suspend process
processes.resume(pid)               # Resume process
processes.top([limit])              # Top processes
processes.cleanup_terminated()      # Clean up
processes.get_statistics()          # Get stats
```

### User Commands
```python
users.login(username, password)     # Login
users.logout()                      # Logout
users.whoami()                      # Current user
users.adduser(username, password)   # Create user
users.deluser(username)             # Delete user
users.passwd([username], password)  # Change password
users.listusers()                   # List users
users.sudo(function, ...)           # Elevated execution
```

## 🔮 Next Steps

With Layers 5 & 6 complete, you can now build:

1. **Layer 7: Shell/CLI** - Command-line interface interpreter
2. **Layer 8: AI Integration** - AI model integration
3. **Layer 9: API Layer** - REST/WebSocket APIs
4. **Layer 10: Web Layer** - Frontend interface

## 🐛 Troubleshooting

**Issue**: Processes not starting
- **Solution**: Check scheduler is running: `processes.scheduler.running`

**Issue**: Permission denied
- **Solution**: Login as root or admin for elevated operations

**Issue**: User not found
- **Solution**: Check user exists with `users.listusers()`

**Issue**: Session expired
- **Solution**: Login again with `users.login(username, password)`

---

**Layers 5 & 6 are production-ready!** 🚀

The OS now supports:
- ✅ Multi-process execution with scheduling
- ✅ Multi-user authentication and sessions
- ✅ Permission-based access control
- ✅ Integrated workflow with VFS
- ✅ Complete CLI command set

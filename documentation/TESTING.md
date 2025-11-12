# AI OS v1.0 Testing Guide

## Overview

This guide provides comprehensive testing procedures for the AI OS v1.0.

---

## Quick Start

### Run All Tests
```bash
cd ai_os
python tests/test_all_layers.py
```

### Run Example Demonstration
```bash
python example_v1_complete.py
```

### Run System Diagnostics
```bash
python -m ai_os.cli_shell
> syscheck
```

---

## Test Categories

### 1. Unit Tests

Test individual layer components in isolation.

#### Memory Layer Tests
```python
python -c "
from ai_os.memory_layer import MemoryLayer
mem = MemoryLayer(total_memory_mb=128)
mem.initialize()
print('✓ Memory layer initialized')
print(mem.cmd_memstat())
mem.shutdown()
"
```

#### Network Layer Tests
```python
python -c "
from ai_os.network_layer import NetworkLayer
net = NetworkLayer()
net.initialize()
print('✓ Network layer initialized')
print(net.cmd_netinfo())
net.shutdown()
"
```

#### Security Layer Tests
```python
python -c "
from ai_os.security_layer import SecurityLayer
sec = SecurityLayer()
sec.initialize()
print('✓ Security layer initialized')
sec.auth.create_user('test', 'pass')
token = sec.auth.authenticate('test', 'pass')
print(f'✓ Authentication: {\"Success\" if token else \"Failed\"}')
sec.shutdown()
"
```

#### Diagnostics Layer Tests
```python
python -c "
from ai_os.diagnostics import DiagnosticsLayer
diag = DiagnosticsLayer()
diag.initialize()
print('✓ Diagnostics layer initialized')
summary = diag.system_check.run_all_checks()
print(f'✓ System check: {summary[\"overall_status\"]}')
diag.shutdown()
"
```

---

### 2. Integration Tests

Test layer interactions and command execution.

#### Test OS Master Initialization
```bash
python -c "
from ai_os.os_master import AIOSMaster
os = AIOSMaster()
success = os.initialize()
print(f'OS Initialization: {\"✓ Success\" if success else \"✗ Failed\"}')
print(f'Layers: {len(os.layers)}')
print(f'Commands: {len(os.command_registry)}')
os.shutdown()
"
```

#### Test Command Execution
```bash
python -c "
from ai_os.os_master import AIOSMaster
os = AIOSMaster()
os.initialize()

# Test multiple commands
commands = ['memstat', 'netinfo', 'syscheck']
for cmd in commands:
    result = os.execute_command(cmd)
    print(f'{cmd}: {\"✓\" if result else \"✗\"}')

os.shutdown()
"
```

---

### 3. Manual Testing Procedures

#### Complete Workflow Test

**Objective:** Test full user workflow from login to logout.

**Steps:**

1. **Start System**
   ```bash
   python example_v1_complete.py
   ```

2. **Verify Initialization**
   - All layers should initialize without errors
   - Check for ✓ marks next to each layer

3. **Test Memory Commands**
   ```
   > memstat
   > procmem 1001
   > memhistory
   ```
   - Verify statistics are displayed
   - Check memory allocation works

4. **Test Network Commands**
   ```
   > netinfo
   > ifconfig
   > ping google.com
   > hostname
   ```
   - Verify network information is correct
   - Ping should work (or show appropriate error)

5. **Test Security Commands**
   ```
   > adduser testuser testpass
   > users
   > login testuser testpass
   > whoami
   > genkey
   > hash "test" sha256
   > logout
   ```
   - User creation should succeed
   - Login/logout should work
   - Encryption key should be generated

6. **Test Diagnostics**
   ```
   > syscheck
   > resources
   > depcheck
   ```
   - System check should show OK status
   - Resources should display current usage

---

### 4. Performance Tests

#### Memory Performance
```python
python -c "
import time
from ai_os.memory_layer import MemoryLayer

mem = MemoryLayer(total_memory_mb=512)
mem.initialize()

# Test allocation speed
start = time.time()
for i in range(100):
    mem.allocate(i, 1)  # 1MB each
elapsed = time.time() - start

print(f'100 allocations: {elapsed:.3f}s')
print(f'Avg per allocation: {elapsed/100*1000:.2f}ms')

mem.shutdown()
"
```

#### Network Performance
```python
python -c "
import time
from ai_os.network_layer import NetworkLayer

net = NetworkLayer()
net.initialize()

# Test ping performance
start = time.time()
result = net.network_tools.ping('8.8.8.8', count=10)
elapsed = time.time() - start

print(f'10 pings: {elapsed:.3f}s')
if result.get('avg_rtt'):
    print(f'Avg RTT: {result[\"avg_rtt\"]:.2f}ms')

net.shutdown()
"
```

---

### 5. Stress Tests

#### Memory Stress Test
```python
python -c "
from ai_os.memory_layer import MemoryLayer

mem = MemoryLayer(total_memory_mb=256)
mem.initialize()

# Allocate until full
process_id = 1
allocated = 0
while mem.allocate(process_id, 16):
    allocated += 16
    process_id += 1
    if process_id > 100:
        break

print(f'Allocated {allocated}MB across {process_id-1} processes')
stats = mem.get_stats()
print(f'Memory usage: {stats[\"used_percent\"]:.1f}%')

mem.shutdown()
"
```

#### Concurrent Operations Test
```python
python -c "
import threading
from ai_os.os_master import AIOSMaster

os = AIOSMaster()
os.initialize()

def worker(cmd):
    for _ in range(10):
        os.execute_command(cmd)

# Run multiple commands concurrently
threads = []
for cmd in ['memstat', 'netinfo', 'resources']:
    t = threading.Thread(target=worker, args=(cmd,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print('✓ Concurrent operations completed')
os.shutdown()
"
```

---

## Test Checklist

### Pre-Release Testing

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Manual workflow test completes
- [ ] System diagnostics show OK
- [ ] No memory leaks detected
- [ ] All commands execute without errors
- [ ] Documentation is accurate
- [ ] Example scripts run successfully

### Layer-Specific Tests

#### Memory Layer
- [ ] Memory allocation works
- [ ] Memory deallocation works
- [ ] Memory statistics accurate
- [ ] Swapping functions correctly
- [ ] Memory monitoring active
- [ ] Commands execute properly

#### Network Layer
- [ ] Network interfaces detected
- [ ] Ping works (or fails gracefully)
- [ ] Hostname resolution works
- [ ] Connection monitoring works
- [ ] Statistics are accurate
- [ ] Commands execute properly

#### Security Layer
- [ ] User creation works
- [ ] Authentication works
- [ ] Password hashing secure
- [ ] Encryption/decryption works
- [ ] Session management works
- [ ] Access control works
- [ ] Commands execute properly

#### Diagnostics Layer
- [ ] System check runs
- [ ] Dependency check works
- [ ] Resource monitoring works
- [ ] Reports are accurate
- [ ] Commands execute properly

---

## Common Test Scenarios

### Scenario 1: New User Setup
```
1. adduser john password123
2. login john password123
3. whoami → should show "john"
4. memstat → should show memory stats
5. logout
```

### Scenario 2: Security Audit
```
1. login admin adminpass
2. users → list all users
3. sessions → show active sessions
4. syscheck → run diagnostics
5. resources → check resource usage
6. logout
```

### Scenario 3: System Monitoring
```
1. resources → initial state
2. memstat → memory before
3. [perform operations]
4. resources → after operations
5. memstat → memory after
6. memhistory → allocation history
```

### Scenario 4: Network Testing
```
1. netinfo → system info
2. ifconfig → interfaces
3. ping google.com → connectivity
4. ping 8.8.8.8 → DNS test
5. hostname → local hostname
6. netstats → statistics
```

---

## Troubleshooting Tests

### Test Fails: Import Error
**Solution:**
```bash
# Ensure you're in the correct directory
cd WebBasedOS-college

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Install dependencies
pip install -r ai_os/requirements.txt
```

### Test Fails: Layer Initialization
**Solution:**
```bash
# Run system check
python -c "
from ai_os.diagnostics import DiagnosticsLayer
diag = DiagnosticsLayer()
diag.initialize()
print(diag.cmd_syscheck())
"
```

### Test Fails: Permission Error
**Solution:**
```bash
# Check file permissions
ls -la ai_os/

# Ensure write access for user database
chmod 644 users.json
```

---

## Automated Testing

### Continuous Integration Script
```bash
#!/bin/bash
# test_ci.sh

echo "Running AI OS v1.0 Test Suite"
echo "=============================="

# Run unit tests
echo "Running unit tests..."
python ai_os/tests/test_all_layers.py

# Run example
echo "Running example demonstration..."
python ai_os/example_v1_complete.py

# Run system check
echo "Running system diagnostics..."
python -c "
from ai_os.os_master import AIOSMaster
os = AIOSMaster()
os.initialize()
print(os.execute_command('syscheck'))
os.shutdown()
"

echo "=============================="
echo "Test suite complete"
```

---

## Performance Benchmarks

### Expected Performance

| Operation | Expected Time | Acceptable Range |
|-----------|--------------|------------------|
| Layer Init | < 1s | 0.5s - 2s |
| Memory Alloc | < 10ms | 1ms - 50ms |
| Memory Free | < 5ms | 1ms - 20ms |
| Ping (local) | < 50ms | 10ms - 200ms |
| Hash (SHA256) | < 1ms | 0.1ms - 10ms |
| Encrypt (1MB) | < 100ms | 50ms - 500ms |
| System Check | < 5s | 2s - 10s |

---

## Test Reports

### Generate Test Report
```bash
python ai_os/tests/test_all_layers.py > test_report.txt 2>&1
```

### View Test Summary
```bash
tail -20 test_report.txt
```

---

## Best Practices

1. **Run tests before commits**
2. **Test on clean environment**
3. **Verify all dependencies installed**
4. **Check for resource leaks**
5. **Test error handling**
6. **Validate edge cases**
7. **Document test failures**
8. **Keep tests updated**

---

## Contact

For test failures or issues:
- Check documentation/ARCHITECTURE.md
- Review AI_OS_V1.0_COMPLETION_REPORT.md
- Run `syscheck` for diagnostics

---

*AI OS v1.0 - Testing Guide*

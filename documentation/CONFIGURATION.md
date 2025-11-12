# AI OS v1.0 Configuration Guide

## Overview

This guide explains how to configure the AI OS for different use cases.

---

## Configuration Files

### Main Configuration
**File:** `ai_os_config.json`

```json
{
  "system": {
    "name": "AI OS",
    "version": "1.0.0"
  },
  "memory": {
    "total_mb": 512,
    "page_size_kb": 4,
    "enable_monitoring": true,
    "swap_enabled": true
  },
  "network": {
    "enable_monitoring": true,
    "default_timeout": 5,
    "ping_count": 4
  },
  "security": {
    "user_db_path": "users.json",
    "session_timeout": 3600,
    "max_failed_attempts": 5,
    "password_min_length": 8
  },
  "filesystem": {
    "root_path": "./vfs_storage",
    "max_file_size_mb": 100
  },
  "diagnostics": {
    "enable_monitoring": true,
    "check_interval": 300,
    "log_level": "INFO"
  }
}
```

---

## Layer Configuration

### 1. Memory Layer Configuration

```python
from ai_os.memory_layer import MemoryLayer

# Default configuration
memory = MemoryLayer(
    total_memory_mb=512,      # Total virtual memory
    page_size_kb=4,           # Page size in KB
    enable_monitoring=True    # Enable real-time monitoring
)
```

**Parameters:**
- `total_memory_mb`: Total virtual memory (default: 512MB)
- `page_size_kb`: Memory page size (default: 4KB)
- `enable_monitoring`: Enable memory monitoring (default: True)

**Recommended Settings:**

| Use Case | total_memory_mb | page_size_kb | monitoring |
|----------|----------------|--------------|------------|
| Development | 256 | 4 | True |
| Production | 1024 | 4 | True |
| Testing | 128 | 4 | False |
| High Performance | 2048 | 8 | True |

---

### 2. Network Layer Configuration

```python
from ai_os.network_layer import NetworkLayer

# Default configuration
network = NetworkLayer(
    enable_monitoring=True    # Enable connection monitoring
)
```

**Parameters:**
- `enable_monitoring`: Enable network monitoring (default: True)

**Environment Variables:**
```bash
# Set default ping timeout
export AIOS_PING_TIMEOUT=5

# Set default ping count
export AIOS_PING_COUNT=4
```

---

### 3. Security Layer Configuration

```python
from ai_os.security_layer import SecurityLayer

# Default configuration
security = SecurityLayer(
    user_db_path='users.json'  # Path to user database
)
```

**Parameters:**
- `user_db_path`: Path to user database file

**User Database Format:**
```json
{
  "root": {
    "password_hash": "...",
    "salt": "...",
    "created": "2025-01-01T00:00:00",
    "last_login": "2025-01-01T12:00:00"
  }
}
```

**Security Settings:**
```python
# Configure in code
security.auth.max_failed_attempts = 5
security.auth.session_timeout = 3600  # 1 hour
```

---

### 4. Diagnostics Layer Configuration

```python
from ai_os.diagnostics import DiagnosticsLayer

# Default configuration
diagnostics = DiagnosticsLayer()
```

**Monitoring Configuration:**
```python
# Set monitoring interval
diagnostics.resource_monitor.interval = 5  # seconds

# Set alert threshold
diagnostics.memory_monitor.set_alert_threshold(80.0)  # 80%
```

---

## OS Master Configuration

### Basic Configuration

```python
from ai_os.os_master import AIOSMaster

config = {
    'memory': {
        'total_mb': 512,
        'page_size_kb': 4,
        'enable_monitoring': True
    },
    'network': {
        'enable_monitoring': True
    },
    'security': {
        'user_db_path': 'users.json',
        'session_timeout': 3600
    },
    'diagnostics': {
        'enable_monitoring': True
    }
}

os_master = AIOSMaster(config=config)
os_master.initialize()
```

---

## Environment-Specific Configurations

### Development Environment

```json
{
  "memory": {
    "total_mb": 256,
    "enable_monitoring": true
  },
  "security": {
    "user_db_path": "dev_users.json",
    "session_timeout": 7200
  },
  "diagnostics": {
    "enable_monitoring": true,
    "log_level": "DEBUG"
  }
}
```

### Production Environment

```json
{
  "memory": {
    "total_mb": 1024,
    "enable_monitoring": true
  },
  "security": {
    "user_db_path": "/var/lib/aios/users.json",
    "session_timeout": 1800,
    "max_failed_attempts": 3
  },
  "diagnostics": {
    "enable_monitoring": true,
    "log_level": "WARNING"
  }
}
```

### Testing Environment

```json
{
  "memory": {
    "total_mb": 128,
    "enable_monitoring": false
  },
  "security": {
    "user_db_path": "test_users.json",
    "session_timeout": 300
  },
  "diagnostics": {
    "enable_monitoring": false,
    "log_level": "ERROR"
  }
}
```

---

## Command-Line Configuration

### Using Environment Variables

```bash
# Set memory size
export AIOS_MEMORY_MB=512

# Set user database path
export AIOS_USER_DB=/path/to/users.json

# Set log level
export AIOS_LOG_LEVEL=DEBUG

# Run AI OS
python -m ai_os.cli_shell
```

### Using Configuration File

```bash
# Specify config file
python -m ai_os.cli_shell --config my_config.json

# Or set environment variable
export AIOS_CONFIG=/path/to/config.json
python -m ai_os.cli_shell
```

---

## Advanced Configuration

### Custom Memory Allocation Strategy

```python
from ai_os.memory_layer import MemoryLayer

memory = MemoryLayer(total_memory_mb=512)
memory.initialize()

# Configure swap behavior
memory.memory_manager.virtual_memory.swap_enabled = True

# Set custom page size (must be done before initialization)
# memory.memory_manager.virtual_memory.page_size = 8192  # 8KB
```

### Custom Network Adapters

```python
from ai_os.network_layer import NetworkLayer, NetworkAdapter

network = NetworkLayer()
network.initialize()

# Add custom adapter
custom_adapter = NetworkAdapter("wlan0", "wifi")
custom_adapter.status = "up"
custom_adapter.ip_address = "192.168.1.100"
network.network_interface.adapters["wlan0"] = custom_adapter
```

### Custom Security Policies

```python
from ai_os.security_layer import SecurityLayer, Permission

security = SecurityLayer()
security.initialize()

# Add admin user
security.access_control.add_admin("root")

# Set default permissions
security.access_control.default_permissions = {
    Permission.READ
}

# Configure password policy
security.auth.max_failed_attempts = 3
```

---

## Logging Configuration

### Enable Detailed Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aios.log'),
        logging.StreamHandler()
    ]
)
```

### Layer-Specific Logging

```python
# Memory layer logging
memory_logger = logging.getLogger('ai_os.memory_layer')
memory_logger.setLevel(logging.INFO)

# Network layer logging
network_logger = logging.getLogger('ai_os.network_layer')
network_logger.setLevel(logging.DEBUG)
```

---

## Performance Tuning

### Memory Performance

```python
# Increase memory for better performance
memory = MemoryLayer(total_memory_mb=2048)

# Larger page size for large allocations
memory = MemoryLayer(page_size_kb=8)

# Disable monitoring for maximum speed
memory = MemoryLayer(enable_monitoring=False)
```

### Network Performance

```python
# Reduce monitoring overhead
network = NetworkLayer(enable_monitoring=False)

# Adjust timeouts
network.network_tools.default_timeout = 3
```

### Diagnostics Performance

```python
# Reduce check frequency
diagnostics.resource_monitor.interval = 10  # seconds

# Limit history size
diagnostics.resource_monitor.max_history = 500
```

---

## Security Hardening

### Strong Password Policy

```python
# Increase minimum password length
security.auth.min_password_length = 12

# Reduce max failed attempts
security.auth.max_failed_attempts = 3

# Shorter session timeout
security.auth.session_timeout = 1800  # 30 minutes
```

### Encryption Configuration

```python
# Use stronger key derivation
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

# Increase iterations (in encryption.py)
# kdf = PBKDF2(iterations=200000)  # Instead of 100000
```

### Access Control

```python
# Restrict default permissions
security.access_control.default_permissions = set()  # No default access

# Require explicit permission grants
security.access_control.grant_permission('/data', 'user', Permission.READ)
```

---

## Troubleshooting Configuration

### Common Issues

**Issue:** Memory allocation failures
**Solution:**
```python
# Increase memory size
memory = MemoryLayer(total_memory_mb=1024)
```

**Issue:** Network timeouts
**Solution:**
```python
# Increase timeout
network.network_tools.default_timeout = 10
```

**Issue:** Authentication failures
**Solution:**
```bash
# Check user database exists
ls -la users.json

# Verify permissions
chmod 644 users.json
```

---

## Configuration Best Practices

1. **Use configuration files** for environment-specific settings
2. **Store sensitive data** (passwords, keys) securely
3. **Enable monitoring** in production for diagnostics
4. **Set appropriate timeouts** based on network conditions
5. **Regular backups** of user database
6. **Log rotation** for long-running systems
7. **Resource limits** appropriate for hardware
8. **Security policies** matching requirements

---

## Configuration Templates

### Minimal Configuration
```json
{
  "memory": {"total_mb": 128},
  "security": {"user_db_path": "users.json"}
}
```

### Standard Configuration
```json
{
  "memory": {
    "total_mb": 512,
    "enable_monitoring": true
  },
  "network": {
    "enable_monitoring": true
  },
  "security": {
    "user_db_path": "users.json",
    "session_timeout": 3600
  },
  "diagnostics": {
    "enable_monitoring": true
  }
}
```

### High-Performance Configuration
```json
{
  "memory": {
    "total_mb": 2048,
    "page_size_kb": 8,
    "enable_monitoring": false
  },
  "network": {
    "enable_monitoring": false
  },
  "security": {
    "user_db_path": "users.json",
    "session_timeout": 7200
  },
  "diagnostics": {
    "enable_monitoring": false
  }
}
```

---

## Validation

### Validate Configuration

```python
from ai_os.os_master import AIOSMaster

def validate_config(config):
    """Validate configuration"""
    required_keys = ['memory', 'security']
    
    for key in required_keys:
        if key not in config:
            print(f"Missing required key: {key}")
            return False
    
    # Validate memory
    if config['memory']['total_mb'] < 64:
        print("Memory too small (minimum 64MB)")
        return False
    
    return True

# Test configuration
config = {...}
if validate_config(config):
    os_master = AIOSMaster(config=config)
    os_master.initialize()
```

---

*AI OS v1.0 - Configuration Guide*

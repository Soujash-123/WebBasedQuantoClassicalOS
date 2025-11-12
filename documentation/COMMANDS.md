# AI OS Command Reference v1.0

Complete command reference for the AI OS CLI.

## Table of Contents
- [Memory Management](#memory-management)
- [Network Commands](#network-commands)
- [Security Commands](#security-commands)
- [File System Commands](#file-system-commands)
- [Process Management](#process-management)
- [System Simulation](#system-simulation)
- [Diagnostics](#diagnostics)
- [General Commands](#general-commands)

---

## Memory Management

### `memstat`
Display memory statistics including total, used, and free memory.

**Usage:** `memstat`

**Example:**
```
> memstat
============================================================
MEMORY STATISTICS
============================================================
Total Memory:     512.00 MB
Used Memory:      128.50 MB (25.1%)
Free Memory:      383.50 MB
...
```

### `memdump`
Dump complete memory state to a JSON file for debugging.

**Usage:** `memdump [output_file]`

**Example:**
```
> memdump memory_state.json
Memory dump saved to: memory_state.json
```

### `flushmem`
Flush inactive memory pages to free up resources.

**Usage:** `flushmem [inactive_seconds]`

**Default:** 300 seconds (5 minutes)

**Example:**
```
> flushmem 600
Flushed 15 inactive memory pages (inactive > 600s)
```

### `procmem`
Show memory usage for a specific process.

**Usage:** `procmem <process_id>`

**Example:**
```
> procmem 1234
Process 1234 Memory Usage:
  Allocated Pages: 8
  Memory: 32.00 MB (32768.00 KB)
```

### `memhistory`
Show memory allocation history.

**Usage:** `memhistory [limit]`

**Default:** 20 entries

**Example:**
```
> memhistory 10
```

### `memmonitor`
Show memory monitoring report with usage trends.

**Usage:** `memmonitor`

---

## Network Commands

### `ping`
Ping a host to check connectivity.

**Usage:** `ping <host> [count] [timeout]`

**Defaults:** count=4, timeout=5

**Example:**
```
> ping google.com 4 5
PING google.com (142.250.185.46)
4 packets transmitted, 4 received, 0.0% packet loss
rtt min/avg/max = 12.45/15.32/18.21 ms
```

### `netstat`
Show active network connections.

**Usage:** `netstat`

**Example:**
```
> netstat
====================================================================================================
Protocol   Local Address             Remote Address            State           Bytes TX/RX
====================================================================================================
TCP        192.168.1.100:8080        192.168.1.50:54321       ESTABLISHED     1024/2048
```

### `ifconfig` / `ipconfig`
Show network interface configuration.

**Usage:** `ifconfig` or `ipconfig`

**Example:**
```
> ifconfig
============================================================
NETWORK INTERFACES
============================================================

eth0: <UP>
  Type: ethernet
  IP Address: 192.168.1.100
  TX: 0 bytes (0 packets)
  RX: 0 bytes (0 packets)
```

### `hostname`
Display system hostname.

**Usage:** `hostname`

**Example:**
```
> hostname
my-computer
```

### `netinfo`
Show comprehensive network information.

**Usage:** `netinfo`

### `ports`
Show listening ports.

**Usage:** `ports`

### `netstats`
Show network statistics.

**Usage:** `netstats`

### `checkport`
Check if a specific port is open on a host.

**Usage:** `checkport <host> <port>`

**Example:**
```
> checkport google.com 443
Port 443 (HTTPS) on google.com: OPEN
```

---

## Security Commands

### `login`
Login to the system.

**Usage:** `login <username> <password>`

**Example:**
```
> login root mypassword
Login successful. Welcome, root!
```

### `logout`
Logout from the system.

**Usage:** `logout`

### `whoami`
Show current logged-in user.

**Usage:** `whoami`

**Example:**
```
> whoami
root
```

### `adduser`
Create a new user account.

**Usage:** `adduser <username> <password>`

**Example:**
```
> adduser john secretpass
User 'john' created successfully
```

### `deluser`
Delete a user account.

**Usage:** `deluser <username>`

**Example:**
```
> deluser john
User 'john' deleted
```

### `passwd`
Change your password.

**Usage:** `passwd <old_password> <new_password>`

**Example:**
```
> passwd oldpass newpass
Password changed successfully
```

### `users`
List all users.

**Usage:** `users`

### `sessions`
Show active user sessions.

**Usage:** `sessions`

### `encrypt`
Encrypt a file.

**Usage:** `encrypt <file> [output_file]`

**Example:**
```
> encrypt secret.txt secret.txt.encrypted
File encrypted: secret.txt.encrypted
```

### `decrypt`
Decrypt a file.

**Usage:** `decrypt <file> [output_file]`

**Example:**
```
> decrypt secret.txt.encrypted secret.txt
File decrypted: secret.txt
```

### `genkey`
Generate an encryption key.

**Usage:** `genkey`

### `hash`
Hash a string using specified algorithm.

**Usage:** `hash <string> [algorithm]`

**Algorithms:** sha256 (default), sha512, md5

**Example:**
```
> hash "hello world" sha256
SHA256: b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
```

### `hashfile`
Hash a file.

**Usage:** `hashfile <file> [algorithm]`

**Example:**
```
> hashfile document.pdf sha256
SHA256 (document.pdf): a1b2c3d4...
```

### `chmod`
Change file/resource permissions.

**Usage:** `chmod <resource> <user> <permissions>`

**Permissions:** r (read), w (write), x (execute), d (delete), a (admin)

**Example:**
```
> chmod /data/file.txt john rwx
Permissions updated for /data/file.txt
```

### `chown`
Change owner of a resource.

**Usage:** `chown <resource> <user>`

**Example:**
```
> chown /data/file.txt john
Owner of /data/file.txt changed to john
```

### `getacl`
Get Access Control List for a resource.

**Usage:** `getacl <resource>`

---

## Diagnostics

### `syscheck`
Run comprehensive system diagnostics.

**Usage:** `syscheck`

**Example:**
```
> syscheck
================================================================================
SYSTEM DIAGNOSTIC REPORT
================================================================================
Overall Status: OK
Total Checks: 11
  ✓ OK: 10
  ⚠ Warnings: 1
  ✗ Errors: 0
...
```

### `depcheck`
Check inter-layer dependencies.

**Usage:** `depcheck`

### `resources`
Show current resource usage (CPU, memory, processes).

**Usage:** `resources`

**Example:**
```
> resources
============================================================
RESOURCE STATISTICS
============================================================
CPU Usage: 15.3%
Memory Usage: 45.2% (3621 MB / 8192 MB)
Process Count: 127
Disk Usage: 62.1%
```

### `reshistory`
Show resource usage history.

**Usage:** `reshistory [limit]`

**Default:** 10 entries

---

## System Simulation

### APT Package Management

#### `apt update`
Update package repository.

**Usage:** `apt update`

#### `apt install`
Install a package.

**Usage:** `apt install <package>`

**Example:**
```
> apt install textutils
Installing textutils...
Package installed successfully
```

#### `apt remove`
Remove a package.

**Usage:** `apt remove <package>`

#### `apt list`
List installed packages.

**Usage:** `apt list`

#### `apt upgrade`
Upgrade all packages.

**Usage:** `apt upgrade`

### Git Commands

#### `git clone`
Clone a repository.

**Usage:** `git clone <url>`

#### `git pull`
Pull latest changes.

**Usage:** `git pull`

#### `git status`
Show repository status.

**Usage:** `git status`

#### `git log`
Show commit history.

**Usage:** `git log`

### Mount Commands

#### `mount`
Mount a device.

**Usage:** `mount <device> <mount_point>`

**Example:**
```
> mount usb0 /mnt/usb
Device usb0 mounted at /mnt/usb
```

#### `umount`
Unmount a device.

**Usage:** `umount <mount_point>`

#### `df`
Show disk usage.

**Usage:** `df`

#### `lsblk`
List block devices.

**Usage:** `lsblk`

### Environment Variables

#### `export`
Set an environment variable.

**Usage:** `export <name>=<value>`

**Example:**
```
> export PATH=/usr/bin:/usr/local/bin
```

#### `unset`
Unset an environment variable.

**Usage:** `unset <name>`

#### `env`
Show all environment variables.

**Usage:** `env`

---

## General Commands

### `help`
Show help information.

**Usage:** `help [command]`

### `clear`
Clear the screen.

**Usage:** `clear`

### `exit`
Exit the shell.

**Usage:** `exit`

### `history`
Show command history.

**Usage:** `history`

### `alias`
Create command alias.

**Usage:** `alias <name>=<command>`

**Example:**
```
> alias ll=ls -la
```

---

## File System Commands

### `ls`
List directory contents.

**Usage:** `ls [path]`

### `cd`
Change directory.

**Usage:** `cd <path>`

### `pwd`
Print working directory.

**Usage:** `pwd`

### `mkdir`
Create directory.

**Usage:** `mkdir <path>`

### `rm`
Remove file or directory.

**Usage:** `rm <path>`

### `cp`
Copy file or directory.

**Usage:** `cp <source> <destination>`

### `mv`
Move or rename file/directory.

**Usage:** `mv <source> <destination>`

### `cat`
Display file contents.

**Usage:** `cat <file>`

### `touch`
Create empty file or update timestamp.

**Usage:** `touch <file>`

### `grep`
Search for pattern in files.

**Usage:** `grep <pattern> <file>`

### `head`
Show first lines of file.

**Usage:** `head <file> [lines]`

### `tail`
Show last lines of file.

**Usage:** `tail <file> [lines]`

### `echo`
Print text to output.

**Usage:** `echo <text>`

---

## Process Management

### `ps`
List running processes.

**Usage:** `ps [aux]`

### `run`
Start a new process.

**Usage:** `run <command>`

### `kill`
Terminate a process.

**Usage:** `kill <pid>`

### `killall`
Terminate all processes matching name.

**Usage:** `killall <name>`

---

## Tips and Tricks

1. **Command History**: Use up/down arrows to navigate command history
2. **Tab Completion**: Press Tab to auto-complete commands and paths
3. **Background Jobs**: Add `&` at the end of a command to run it in background
4. **Piping**: Use `|` to pipe output between commands
5. **Redirection**: Use `>` to redirect output to file

---

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Misuse of command
- `126`: Command cannot execute
- `127`: Command not found
- `130`: Terminated by Ctrl+C

---

*AI OS v1.0 - Complete Command Reference*

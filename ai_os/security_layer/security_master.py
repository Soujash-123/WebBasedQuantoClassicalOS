"""
Security Layer Master
Unified interface for the security layer.
"""

import os
from typing import Optional
from .encryption import EncryptionManager
from .hashing import HashingManager
from .access_control import AccessControl, Permission
from .auth_manager import AuthenticationManager


class SecurityLayer:
    """Master controller for security layer"""
    
    def __init__(self, user_db_path: Optional[str] = None):
        self.encryption = EncryptionManager()
        self.hashing = HashingManager()
        self.access_control = AccessControl()
        self.auth = AuthenticationManager(user_db_path)
        self.initialized = False
        self.current_user = None
        self.current_token = None
        
        # Generate default encryption key
        default_key = self.encryption.generate_key()[0]
        self.encryption.set_default_key(default_key)
    
    def initialize(self):
        """Initialize security layer"""
        if self.initialized:
            return
        
        self.initialized = True
        print("[Security Layer] Initialized")
    
    def shutdown(self):
        """Shutdown security layer"""
        if not self.initialized:
            return
        
        # Cleanup expired sessions
        self.auth.cleanup_expired_sessions()
        
        self.initialized = False
        print("[Security Layer] Shutdown complete")
    
    # Authentication Commands
    
    def cmd_login(self, args: list = None) -> str:
        """Login user"""
        if not args or len(args) < 2:
            return "Usage: login <username> <password>"
        
        username = args[0]
        password = args[1]
        
        token = self.auth.authenticate(username, password)
        
        if token:
            self.current_user = username
            self.current_token = token
            return f"Login successful. Welcome, {username}!"
        else:
            return "Login failed. Invalid credentials or account locked."
    
    def cmd_logout(self, args: list = None) -> str:
        """Logout current user"""
        if not self.current_token:
            return "No active session"
        
        if self.auth.logout(self.current_token):
            user = self.current_user
            self.current_user = None
            self.current_token = None
            return f"Logged out {user}"
        else:
            return "Logout failed"
    
    def cmd_whoami(self, args: list = None) -> str:
        """Show current user"""
        if self.current_user:
            return self.current_user
        else:
            return "Not logged in"
    
    def cmd_adduser(self, args: list = None) -> str:
        """Add a new user"""
        if not args or len(args) < 2:
            return "Usage: adduser <username> <password>"
        
        username = args[0]
        password = args[1]
        
        if self.auth.create_user(username, password):
            return f"User '{username}' created successfully"
        else:
            return f"Failed to create user '{username}' (may already exist)"
    
    def cmd_deluser(self, args: list = None) -> str:
        """Delete a user"""
        if not args:
            return "Usage: deluser <username>"
        
        username = args[0]
        
        if self.auth.delete_user(username):
            return f"User '{username}' deleted"
        else:
            return f"Failed to delete user '{username}'"
    
    def cmd_passwd(self, args: list = None) -> str:
        """Change password"""
        if not self.current_user:
            return "Must be logged in to change password"
        
        if not args or len(args) < 2:
            return "Usage: passwd <old_password> <new_password>"
        
        old_password = args[0]
        new_password = args[1]
        
        if self.auth.change_password(self.current_user, old_password, new_password):
            return "Password changed successfully"
        else:
            return "Failed to change password (incorrect old password)"
    
    def cmd_users(self, args: list = None) -> str:
        """List all users"""
        users = self.auth.list_users()
        
        if not users:
            return "No users found"
        
        lines = ["Users:", "-" * 40]
        for user in users:
            marker = " (current)" if user == self.current_user else ""
            lines.append(f"  {user}{marker}")
        
        return "\n".join(lines)
    
    def cmd_sessions(self, args: list = None) -> str:
        """Show active sessions"""
        sessions = self.auth.get_active_sessions()
        
        if not sessions:
            return "No active sessions"
        
        lines = ["Active Sessions:", "=" * 60]
        
        for session in sessions:
            lines.append(f"User: {session['username']}")
            lines.append(f"  Created: {session['created']}")
            lines.append(f"  Expires: {session['expires']}")
            lines.append(f"  Last Activity: {session['last_activity']}")
            lines.append("")
        
        return "\n".join(lines)
    
    # Encryption Commands
    
    def cmd_encrypt(self, args: list = None) -> str:
        """Encrypt a file"""
        if not args:
            return "Usage: encrypt <file> [output_file]"
        
        input_file = args[0]
        output_file = args[1] if len(args) > 1 else None
        
        try:
            result = self.encryption.encrypt_file(input_file, output_file)
            return f"File encrypted: {result}"
        except Exception as e:
            return f"Encryption failed: {e}"
    
    def cmd_decrypt(self, args: list = None) -> str:
        """Decrypt a file"""
        if not args:
            return "Usage: decrypt <file> [output_file]"
        
        input_file = args[0]
        output_file = args[1] if len(args) > 1 else None
        
        try:
            result = self.encryption.decrypt_file(input_file, output_file)
            return f"File decrypted: {result}"
        except Exception as e:
            return f"Decryption failed: {e}"
    
    def cmd_genkey(self, args: list = None) -> str:
        """Generate encryption key"""
        key, _ = self.encryption.generate_key()
        key_str = self.encryption.key_to_string(key)
        return f"Generated key:\n{key_str}\n\nStore this key securely!"
    
    # Hashing Commands
    
    def cmd_hash(self, args: list = None) -> str:
        """Hash a string"""
        if not args:
            return "Usage: hash <string> [algorithm]"
        
        data = args[0]
        algorithm = args[1] if len(args) > 1 else 'sha256'
        
        if algorithm == 'sha256':
            result = self.hashing.hash_sha256(data)
        elif algorithm == 'sha512':
            result = self.hashing.hash_sha512(data)
        elif algorithm == 'md5':
            result = self.hashing.hash_md5(data)
        else:
            return f"Unsupported algorithm: {algorithm}"
        
        return f"{algorithm.upper()}: {result}"
    
    def cmd_hashfile(self, args: list = None) -> str:
        """Hash a file"""
        if not args:
            return "Usage: hashfile <file> [algorithm]"
        
        file_path = args[0]
        algorithm = args[1] if len(args) > 1 else 'sha256'
        
        try:
            result = self.hashing.hash_file(file_path, algorithm)
            return f"{algorithm.upper()} ({file_path}): {result}"
        except Exception as e:
            return f"Hashing failed: {e}"
    
    # Access Control Commands
    
    def cmd_chmod(self, args: list = None) -> str:
        """Change permissions"""
        if not args or len(args) < 3:
            return "Usage: chmod <resource> <user> <permissions>"
        
        resource = args[0]
        user = args[1]
        perm_str = args[2]
        
        permissions = self.access_control.parse_permissions(perm_str)
        self.access_control.grant_permissions(resource, user, permissions)
        
        return f"Permissions updated for {resource}"
    
    def cmd_chown(self, args: list = None) -> str:
        """Change owner"""
        if not args or len(args) < 2:
            return "Usage: chown <resource> <user>"
        
        resource = args[0]
        user = args[1]
        
        self.access_control.set_owner(resource, user)
        return f"Owner of {resource} changed to {user}"
    
    def cmd_getacl(self, args: list = None) -> str:
        """Get ACL for resource"""
        if not args:
            return "Usage: getacl <resource>"
        
        resource = args[0]
        return self.access_control.format_acl(resource)
    
    # API Methods
    
    def check_permission(self, resource: str, permission: Permission) -> bool:
        """Check if current user has permission"""
        if not self.current_user:
            return False
        
        return self.access_control.check_permission(resource, self.current_user, permission)
    
    def get_commands(self) -> dict:
        """Get available security commands"""
        return {
            'login': {
                'function': self.cmd_login,
                'description': 'Login to the system',
                'usage': 'login <username> <password>'
            },
            'logout': {
                'function': self.cmd_logout,
                'description': 'Logout from the system',
                'usage': 'logout'
            },
            'whoami': {
                'function': self.cmd_whoami,
                'description': 'Show current user',
                'usage': 'whoami'
            },
            'adduser': {
                'function': self.cmd_adduser,
                'description': 'Add a new user',
                'usage': 'adduser <username> <password>'
            },
            'deluser': {
                'function': self.cmd_deluser,
                'description': 'Delete a user',
                'usage': 'deluser <username>'
            },
            'passwd': {
                'function': self.cmd_passwd,
                'description': 'Change password',
                'usage': 'passwd <old_password> <new_password>'
            },
            'users': {
                'function': self.cmd_users,
                'description': 'List all users',
                'usage': 'users'
            },
            'sessions': {
                'function': self.cmd_sessions,
                'description': 'Show active sessions',
                'usage': 'sessions'
            },
            'encrypt': {
                'function': self.cmd_encrypt,
                'description': 'Encrypt a file',
                'usage': 'encrypt <file> [output_file]'
            },
            'decrypt': {
                'function': self.cmd_decrypt,
                'description': 'Decrypt a file',
                'usage': 'decrypt <file> [output_file]'
            },
            'genkey': {
                'function': self.cmd_genkey,
                'description': 'Generate encryption key',
                'usage': 'genkey'
            },
            'hash': {
                'function': self.cmd_hash,
                'description': 'Hash a string',
                'usage': 'hash <string> [algorithm]'
            },
            'hashfile': {
                'function': self.cmd_hashfile,
                'description': 'Hash a file',
                'usage': 'hashfile <file> [algorithm]'
            },
            'chmod': {
                'function': self.cmd_chmod,
                'description': 'Change permissions',
                'usage': 'chmod <resource> <user> <permissions>'
            },
            'chown': {
                'function': self.cmd_chown,
                'description': 'Change owner',
                'usage': 'chown <resource> <user>'
            },
            'getacl': {
                'function': self.cmd_getacl,
                'description': 'Get ACL for resource',
                'usage': 'getacl <resource>'
            }
        }

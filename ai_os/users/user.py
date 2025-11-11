"""
User Class
Represents a user account with authentication and permissions.
"""

import hashlib
import time
from enum import Enum
from typing import Dict, List, Any, Optional


class UserRole(Enum):
    """User role types."""
    ROOT = "root"           # Superuser with all permissions
    ADMIN = "admin"         # Administrative user
    USER = "user"           # Standard user
    GUEST = "guest"         # Limited guest user


class User:
    """Represents a user account in the OS."""
    
    def __init__(
        self,
        username: str,
        password: str,
        role: UserRole = UserRole.USER,
        home_directory: Optional[str] = None
    ):
        """
        Initialize a user account.
        
        Args:
            username: Username (unique identifier)
            password: Plain text password (will be hashed)
            role: User role
            home_directory: Home directory path
        """
        self.username = username
        self.role = role
        self.home_directory = home_directory or f"/home/{username}"
        
        # Password (hashed)
        self.password_hash = self._hash_password(password)
        
        # Metadata
        self.created_at = time.time()
        self.last_login: Optional[float] = None
        self.login_count = 0
        
        # Permissions (extensible)
        self.permissions: List[str] = self._get_default_permissions()
        
        # User info
        self.full_name: Optional[str] = None
        self.email: Optional[str] = None
        
        # Status
        self.is_active = True
        self.is_locked = False
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def _get_default_permissions(self) -> List[str]:
        """Get default permissions based on role."""
        if self.role == UserRole.ROOT:
            return ["*"]  # All permissions
        elif self.role == UserRole.ADMIN:
            return [
                "user.create", "user.delete", "user.modify",
                "process.kill_any", "file.read_any", "file.write_any",
                "system.config"
            ]
        elif self.role == UserRole.USER:
            return [
                "file.read_own", "file.write_own",
                "process.create", "process.kill_own"
            ]
        elif self.role == UserRole.GUEST:
            return ["file.read_public"]
        
        return []
    
    def check_password(self, password: str) -> bool:
        """
        Verify a password.
        
        Args:
            password: Plain text password to check
            
        Returns:
            True if password matches
        """
        if self.is_locked:
            return False
        
        return self._hash_password(password) == self.password_hash
    
    def set_password(self, new_password: str) -> None:
        """
        Change user password.
        
        Args:
            new_password: New plain text password
        """
        self.password_hash = self._hash_password(new_password)
        print(f"[User] Password changed for {self.username}")
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            permission: Permission string (e.g., "file.write")
            
        Returns:
            True if user has permission
        """
        if not self.is_active or self.is_locked:
            return False
        
        # Root has all permissions
        if "*" in self.permissions:
            return True
        
        # Check exact match
        if permission in self.permissions:
            return True
        
        # Check wildcard permissions (e.g., "file.*")
        permission_parts = permission.split('.')
        for perm in self.permissions:
            if perm.endswith('*'):
                perm_prefix = perm[:-1]
                if permission.startswith(perm_prefix):
                    return True
        
        return False
    
    def add_permission(self, permission: str) -> None:
        """Add a permission to the user."""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission: str) -> None:
        """Remove a permission from the user."""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def record_login(self) -> None:
        """Record a successful login."""
        self.last_login = time.time()
        self.login_count += 1
    
    def lock(self) -> None:
        """Lock the user account."""
        self.is_locked = True
        print(f"[User] Account locked: {self.username}")
    
    def unlock(self) -> None:
        """Unlock the user account."""
        self.is_locked = False
        print(f"[User] Account unlocked: {self.username}")
    
    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        print(f"[User] Account deactivated: {self.username}")
    
    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        print(f"[User] Account activated: {self.username}")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get user information.
        
        Returns:
            Dictionary with user details
        """
        return {
            'username': self.username,
            'role': self.role.value,
            'home_directory': self.home_directory,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'login_count': self.login_count,
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'permissions': self.permissions,
            'full_name': self.full_name,
            'email': self.email
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"User(username='{self.username}', role={self.role.value})"

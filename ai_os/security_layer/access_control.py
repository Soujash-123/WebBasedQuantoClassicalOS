"""
Access Control
Manages permissions and access control for files and commands.
"""

from typing import Dict, List, Optional, Set
from enum import Enum
from datetime import datetime


class Permission(Enum):
    """Permission types"""
    READ = "r"
    WRITE = "w"
    EXECUTE = "x"
    DELETE = "d"
    ADMIN = "a"


class AccessLevel(Enum):
    """Access levels"""
    OWNER = "owner"
    GROUP = "group"
    PUBLIC = "public"


class AccessControlEntry:
    """Represents an access control entry"""
    
    def __init__(self, resource: str, user: str, permissions: Set[Permission]):
        self.resource = resource
        self.user = user
        self.permissions = permissions
        self.created = datetime.now()
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if entry has a specific permission"""
        return permission in self.permissions or Permission.ADMIN in self.permissions
    
    def add_permission(self, permission: Permission):
        """Add a permission"""
        self.permissions.add(permission)
    
    def remove_permission(self, permission: Permission):
        """Remove a permission"""
        self.permissions.discard(permission)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'resource': self.resource,
            'user': self.user,
            'permissions': [p.value for p in self.permissions],
            'created': self.created.isoformat()
        }


class AccessControl:
    """Manages access control and permissions"""
    
    def __init__(self):
        self.acl: Dict[str, List[AccessControlEntry]] = {}  # resource -> [ACEs]
        self.default_permissions = {Permission.READ}
        self.admin_users = set()
    
    def add_admin(self, username: str):
        """Add an admin user"""
        self.admin_users.add(username)
    
    def remove_admin(self, username: str):
        """Remove an admin user"""
        self.admin_users.discard(username)
    
    def is_admin(self, username: str) -> bool:
        """Check if user is admin"""
        return username in self.admin_users
    
    def grant_permission(self, resource: str, user: str, permission: Permission):
        """Grant a permission to a user for a resource"""
        if resource not in self.acl:
            self.acl[resource] = []
        
        # Find existing ACE
        for ace in self.acl[resource]:
            if ace.user == user:
                ace.add_permission(permission)
                return
        
        # Create new ACE
        ace = AccessControlEntry(resource, user, {permission})
        self.acl[resource].append(ace)
    
    def revoke_permission(self, resource: str, user: str, permission: Permission):
        """Revoke a permission from a user for a resource"""
        if resource not in self.acl:
            return
        
        for ace in self.acl[resource]:
            if ace.user == user:
                ace.remove_permission(permission)
                break
    
    def grant_permissions(self, resource: str, user: str, permissions: Set[Permission]):
        """Grant multiple permissions"""
        for permission in permissions:
            self.grant_permission(resource, user, permission)
    
    def check_permission(self, resource: str, user: str, permission: Permission) -> bool:
        """Check if user has permission for resource"""
        # Admins have all permissions
        if self.is_admin(user):
            return True
        
        # Check ACL
        if resource in self.acl:
            for ace in self.acl[resource]:
                if ace.user == user:
                    return ace.has_permission(permission)
        
        # Check default permissions
        return permission in self.default_permissions
    
    def get_user_permissions(self, resource: str, user: str) -> Set[Permission]:
        """Get all permissions a user has for a resource"""
        if self.is_admin(user):
            return {Permission.READ, Permission.WRITE, Permission.EXECUTE, 
                   Permission.DELETE, Permission.ADMIN}
        
        if resource in self.acl:
            for ace in self.acl[resource]:
                if ace.user == user:
                    return ace.permissions.copy()
        
        return self.default_permissions.copy()
    
    def get_resource_acl(self, resource: str) -> List[AccessControlEntry]:
        """Get ACL for a resource"""
        return self.acl.get(resource, [])
    
    def remove_resource(self, resource: str):
        """Remove all ACL entries for a resource"""
        if resource in self.acl:
            del self.acl[resource]
    
    def set_owner(self, resource: str, user: str):
        """Set owner of a resource (grants all permissions)"""
        self.grant_permissions(resource, user, {
            Permission.READ, Permission.WRITE, 
            Permission.EXECUTE, Permission.DELETE
        })
    
    def format_permissions(self, permissions: Set[Permission]) -> str:
        """Format permissions as string (e.g., 'rwxd')"""
        perm_str = ""
        perm_str += "r" if Permission.READ in permissions else "-"
        perm_str += "w" if Permission.WRITE in permissions else "-"
        perm_str += "x" if Permission.EXECUTE in permissions else "-"
        perm_str += "d" if Permission.DELETE in permissions else "-"
        perm_str += "a" if Permission.ADMIN in permissions else "-"
        return perm_str
    
    def parse_permissions(self, perm_str: str) -> Set[Permission]:
        """Parse permission string to set"""
        permissions = set()
        if 'r' in perm_str:
            permissions.add(Permission.READ)
        if 'w' in perm_str:
            permissions.add(Permission.WRITE)
        if 'x' in perm_str:
            permissions.add(Permission.EXECUTE)
        if 'd' in perm_str:
            permissions.add(Permission.DELETE)
        if 'a' in perm_str:
            permissions.add(Permission.ADMIN)
        return permissions
    
    def format_acl(self, resource: str) -> str:
        """Format ACL for display"""
        if resource not in self.acl or not self.acl[resource]:
            return f"No ACL entries for: {resource}"
        
        lines = [f"ACL for: {resource}", "-" * 60]
        
        for ace in self.acl[resource]:
            perm_str = self.format_permissions(ace.permissions)
            lines.append(f"  {ace.user}: {perm_str}")
        
        return "\n".join(lines)

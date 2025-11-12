"""
User Manager
Manages user accounts and authentication.
"""

import json
import os
from typing import Optional, List, Dict, Any
from .user import User, UserRole


class UserManager:
    """Manages user accounts."""
    
    def __init__(self, users_file: str = "./users.json"):
        """
        Initialize user manager.
        
        Args:
            users_file: Path to users database file
        """
        self.users_file = users_file
        self.users: Dict[str, User] = {}
        
        # Load existing users or create default
        self._load_users()
        
        print("[UserManager] User Manager initialized")
    
    def _load_users(self) -> None:
        """Load users from file."""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                
                for username, user_data in data.items():
                    user = User(
                        username=username,
                        password="",  # Dummy, will be replaced
                        role=UserRole(user_data['role'])
                    )
                    # Restore saved data
                    user.password_hash = user_data['password_hash']
                    user.home_directory = user_data.get('home_directory', f"/home/{username}")
                    user.created_at = user_data.get('created_at', 0)
                    user.last_login = user_data.get('last_login')
                    user.login_count = user_data.get('login_count', 0)
                    user.permissions = user_data.get('permissions', [])
                    user.is_active = user_data.get('is_active', True)
                    user.is_locked = user_data.get('is_locked', False)
                    user.full_name = user_data.get('full_name')
                    user.email = user_data.get('email')
                    
                    self.users[username] = user
                
                print(f"[UserManager] Loaded {len(self.users)} user(s)")
            except Exception as e:
                print(f"[UserManager] Error loading users: {e}")
                self._create_default_users()
        else:
            self._create_default_users()
    
    def _create_default_users(self) -> None:
        """Create default system users."""
        # Create root user
        root = User("root", "root", UserRole.ROOT, "/root")
        self.users["root"] = root
        
        # Create default admin
        admin = User("admin", "admin", UserRole.ADMIN, "/home/admin")
        self.users["admin"] = admin
        
        # Create guest user
        guest = User("guest", "guest", UserRole.GUEST, "/home/guest")
        self.users["guest"] = guest
        
        self._save_users()
        print("[UserManager] Created default users (root, admin, guest)")
    
    def _save_users(self) -> None:
        """Save users to file."""
        try:
            data = {}
            for username, user in self.users.items():
                data[username] = {
                    'password_hash': user.password_hash,
                    'role': user.role.value,
                    'home_directory': user.home_directory,
                    'created_at': user.created_at,
                    'last_login': user.last_login,
                    'login_count': user.login_count,
                    'permissions': user.permissions,
                    'is_active': user.is_active,
                    'is_locked': user.is_locked,
                    'full_name': user.full_name,
                    'email': user.email
                }
            
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            print(f"[UserManager] Error saving users: {e}")
    
    def add_user(
        self,
        username: str,
        password: str,
        role: UserRole = UserRole.USER,
        requester: Optional[str] = None
    ) -> bool:
        """
        Add a new user.
        
        Args:
            username: Username
            password: Password
            role: User role
            requester: Username of person creating the user
            
        Returns:
            True if user created successfully
        """
        # Check permissions
        if requester:
            requester_user = self.get_user(requester)
            if not requester_user or not requester_user.has_permission("user.create"):
                print(f"[UserManager] Permission denied: {requester} cannot create users")
                return False
        
        # Check if user exists
        if username in self.users:
            print(f"[UserManager] User already exists: {username}")
            return False
        
        # Create user
        user = User(username, password, role)
        self.users[username] = user
        self._save_users()
        
        print(f"[UserManager] Created user: {username} ({role.value})")
        return True
    
    def delete_user(self, username: str, requester: Optional[str] = None) -> bool:
        """
        Delete a user.
        
        Args:
            username: Username to delete
            requester: Username of person deleting the user
            
        Returns:
            True if user deleted successfully
        """
        # Check permissions
        if requester:
            requester_user = self.get_user(requester)
            if not requester_user or not requester_user.has_permission("user.delete"):
                print(f"[UserManager] Permission denied")
                return False
        
        # Prevent deleting root
        if username == "root":
            print("[UserManager] Cannot delete root user")
            return False
        
        # Check if user exists
        if username not in self.users:
            print(f"[UserManager] User not found: {username}")
            return False
        
        # Delete user
        del self.users[username]
        self._save_users()
        
        print(f"[UserManager] Deleted user: {username}")
        return True
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User instance or None
        """
        return self.users.get(username)
    
    def list_users(self, requester: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all users.
        
        Args:
            requester: Username requesting the list
            
        Returns:
            List of user information dictionaries
        """
        result = []
        for user in self.users.values():
            info = user.get_info()
            # Hide sensitive info for non-admin users
            if requester and requester != "root":
                requester_user = self.get_user(requester)
                if not requester_user or not requester_user.has_permission("user.view_all"):
                    info.pop('permissions', None)
            
            result.append(info)
        
        return result
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User instance if authenticated, None otherwise
        """
        user = self.get_user(username)
        if not user:
            print(f"[UserManager] User not found: {username}")
            return None
        
        if not user.is_active:
            print(f"[UserManager] Account is inactive: {username}")
            return None
        
        if user.is_locked:
            print(f"[UserManager] Account is locked: {username}")
            return None
        
        if not user.check_password(password):
            print(f"[UserManager] Invalid password for: {username}")
            return None
        
        # Record login
        user.record_login()
        self._save_users()
        
        print(f"[UserManager] Authenticated: {username}")
        return user
    
    def change_password(
        self,
        username: str,
        new_password: str,
        requester: Optional[str] = None
    ) -> bool:
        """
        Change user password.
        
        Args:
            username: Username
            new_password: New password
            requester: Username requesting the change
            
        Returns:
            True if password changed successfully
        """
        user = self.get_user(username)
        if not user:
            print(f"[UserManager] User not found: {username}")
            return False
        
        # Check permissions (user can change own password, or admin can change any)
        if requester and requester != username:
            requester_user = self.get_user(requester)
            if not requester_user or not requester_user.has_permission("user.modify"):
                print(f"[UserManager] Permission denied")
                return False
        
        user.set_password(new_password)
        self._save_users()
        
        return True
    
    def lock_user(self, username: str, requester: Optional[str] = None) -> bool:
        """Lock a user account."""
        user = self.get_user(username)
        if not user:
            return False
        
        # Check permissions
        if requester:
            requester_user = self.get_user(requester)
            if not requester_user or not requester_user.has_permission("user.modify"):
                print(f"[UserManager] Permission denied")
                return False
        
        user.lock()
        self._save_users()
        return True
    
    def unlock_user(self, username: str, requester: Optional[str] = None) -> bool:
        """Unlock a user account."""
        user = self.get_user(username)
        if not user:
            return False
        
        # Check permissions
        if requester:
            requester_user = self.get_user(requester)
            if not requester_user or not requester_user.has_permission("user.modify"):
                print(f"[UserManager] Permission denied")
                return False
        
        user.unlock()
        self._save_users()
        return True
    
    def get_user_count(self) -> int:
        """Get total number of users."""
        return len(self.users)

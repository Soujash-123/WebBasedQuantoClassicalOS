"""
User Master
Integrates user management with other OS layers.
"""

from typing import Optional, List, Dict, Any
from .user import User, UserRole
from .user_manager import UserManager
from .session_manager import SessionManager, Session


class UserLayer:
    """
    Main interface for the User Management & Authentication Layer.
    Integrates with Core, Process, VFS, and I/O layers.
    """
    
    def __init__(
        self,
        core_system=None,
        process_layer=None,
        vfs_layer=None,
        io_layer=None,
        users_file: str = "./users.json"
    ):
        """
        Initialize the User Layer.
        
        Args:
            core_system: Reference to AIOSCore instance
            process_layer: Reference to ProcessLayer instance
            vfs_layer: Reference to VirtualFileSystem instance
            io_layer: Reference to IOLayer instance
            users_file: Path to users database file
        """
        print("=" * 60)
        print("Initializing User Management & Authentication Layer")
        print("=" * 60)
        
        self.core = core_system
        self.process_layer = process_layer
        self.vfs_layer = vfs_layer
        self.io_layer = io_layer
        
        # Initialize user manager
        self.user_manager = UserManager(users_file)
        
        # Initialize session manager
        self.session_manager = SessionManager(self.user_manager)
        
        # Register with core if available
        if self.core:
            self.core.system_registry.register_module("user_layer", self)
            self.event_bus = self.core.event_bus
            self._setup_event_handlers()
        else:
            self.event_bus = None
        
        print("=" * 60)
        print("User Management Layer initialized successfully")
        print("=" * 60)
    
    def _setup_event_handlers(self) -> None:
        """Setup event handlers for user events."""
        if not self.event_bus:
            return
        
        # Subscribe to system events
        self.event_bus.subscribe("system.shutdown", self._on_system_shutdown)
    
    def _on_system_shutdown(self, data: Any) -> None:
        """Handle system shutdown event."""
        print("[UserLayer] Received shutdown signal...")
        self.shutdown()
    
    # Authentication methods
    
    def login(self, username: str, password: str) -> Optional[Session]:
        """Login a user."""
        session = self.session_manager.login(username, password)
        
        # Create home directory if VFS available
        if session and self.vfs_layer:
            user = session.user
            try:
                # Check if home directory exists
                if not self.vfs_layer.vfs_manager.storage.path_exists(user.home_directory):
                    self.vfs_layer.mkdir(user.home_directory)
                    print(f"[UserLayer] Created home directory: {user.home_directory}")
            except Exception as e:
                print(f"[UserLayer] Error creating home directory: {e}")
        
        return session
    
    def logout(self, session_id: Optional[str] = None) -> bool:
        """Logout a user."""
        return self.session_manager.logout(session_id)
    
    def whoami(self) -> Optional[str]:
        """Get current username."""
        return self.session_manager.whoami()
    
    def switch_user(self, username: str, password: str) -> Optional[Session]:
        """Switch to a different user."""
        return self.session_manager.switch_user(username, password)
    
    # User management methods
    
    def adduser(
        self,
        username: str,
        password: str,
        role: UserRole = UserRole.USER
    ) -> bool:
        """Add a new user."""
        requester = self.whoami()
        success = self.user_manager.add_user(username, password, role, requester)
        
        # Create home directory if VFS available
        if success and self.vfs_layer:
            user = self.user_manager.get_user(username)
            if user:
                try:
                    self.vfs_layer.mkdir(user.home_directory)
                    print(f"[UserLayer] Created home directory: {user.home_directory}")
                except Exception as e:
                    print(f"[UserLayer] Error creating home directory: {e}")
        
        return success
    
    def deluser(self, username: str) -> bool:
        """Delete a user."""
        requester = self.whoami()
        return self.user_manager.delete_user(username, requester)
    
    def passwd(self, username: Optional[str] = None, new_password: str = "") -> bool:
        """
        Change password.
        
        Args:
            username: Username (None = current user)
            new_password: New password
            
        Returns:
            True if successful
        """
        if username is None:
            username = self.whoami()
            if not username:
                print("[UserLayer] Not logged in")
                return False
        
        requester = self.whoami()
        return self.user_manager.change_password(username, new_password, requester)
    
    def listusers(self) -> List[Dict[str, Any]]:
        """List all users."""
        requester = self.whoami()
        return self.user_manager.list_users(requester)
    
    def userinfo(self, username: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get user information.
        
        Args:
            username: Username (None = current user)
            
        Returns:
            User info dictionary or None
        """
        if username is None:
            username = self.whoami()
            if not username:
                return None
        
        user = self.user_manager.get_user(username)
        return user.get_info() if user else None
    
    # Session methods
    
    def sessions(self) -> List[Dict[str, Any]]:
        """List active sessions."""
        return self.session_manager.list_sessions()
    
    def get_current_user(self) -> Optional[User]:
        """Get current user object."""
        return self.session_manager.get_current_user()
    
    def has_permission(self, permission: str) -> bool:
        """Check if current user has a permission."""
        user = self.get_current_user()
        if not user:
            return False
        return user.has_permission(permission)
    
    # Sudo functionality
    
    def sudo(self, command_func, *args, **kwargs) -> Any:
        """
        Execute a command with elevated privileges.
        
        Args:
            command_func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result of command function
        """
        user = self.get_current_user()
        if not user:
            print("[UserLayer] Not logged in")
            return None
        
        if user.role not in [UserRole.ROOT, UserRole.ADMIN]:
            print("[UserLayer] Permission denied: sudo requires admin privileges")
            return None
        
        print(f"[UserLayer] Executing with elevated privileges: {user.username}")
        return command_func(*args, **kwargs)
    
    def help(self) -> None:
        """Display available user commands."""
        commands = {
            "Authentication": [
                "login(username, password) - Login a user",
                "logout([session_id]) - Logout current or specified session",
                "whoami() - Get current username",
                "switch_user(username, password) - Switch to different user"
            ],
            "User Management": [
                "adduser(username, password, [role]) - Create new user",
                "deluser(username) - Delete a user",
                "passwd([username], new_password) - Change password",
                "listusers() - List all users",
                "userinfo([username]) - Get user information"
            ],
            "Sessions": [
                "sessions() - List active sessions",
                "get_current_user() - Get current user object",
                "has_permission(permission) - Check permission"
            ],
            "Elevated Commands": [
                "sudo(function, *args, **kwargs) - Execute with admin privileges"
            ]
        }
        
        print("\n" + "=" * 60)
        print("User Management Layer - Available Commands")
        print("=" * 60)
        
        for category, cmds in commands.items():
            print(f"\n{category}:")
            for cmd in cmds:
                print(f"  {cmd}")
        
        print("\n" + "=" * 60)
        print("\nDefault Users:")
        print("  root/root   - Superuser (all permissions)")
        print("  admin/admin - Administrator")
        print("  guest/guest - Guest user (limited access)")
        print("=" * 60)
    
    def shutdown(self) -> None:
        """Shutdown the user layer."""
        print("\n" + "=" * 60)
        print("Shutting down User Management Layer")
        print("=" * 60)
        
        # Logout all users
        self.session_manager.logout_all()
        
        print("=" * 60)
        print("User Management Layer shut down successfully")
        print("=" * 60 + "\n")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
        return False

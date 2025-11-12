"""
Session Manager
Manages user login sessions and tracks active users.
"""

import time
import uuid
from typing import Optional, Dict, List, Any
from .user import User


class Session:
    """Represents a user session."""
    
    def __init__(self, user: User, session_id: Optional[str] = None):
        """
        Initialize a session.
        
        Args:
            user: User instance
            session_id: Optional session ID (generated if not provided)
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.user = user
        self.login_time = time.time()
        self.last_activity = time.time()
        self.is_active = True
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = time.time()
    
    def get_duration(self) -> float:
        """Get session duration in seconds."""
        return time.time() - self.login_time
    
    def get_idle_time(self) -> float:
        """Get idle time since last activity in seconds."""
        return time.time() - self.last_activity
    
    def get_info(self) -> Dict[str, Any]:
        """Get session information."""
        return {
            'session_id': self.session_id,
            'username': self.user.username,
            'role': self.user.role.value,
            'login_time': self.login_time,
            'last_activity': self.last_activity,
            'duration': self.get_duration(),
            'idle_time': self.get_idle_time(),
            'is_active': self.is_active
        }


class SessionManager:
    """Manages user sessions."""
    
    def __init__(self, user_manager, session_timeout: float = 3600):
        """
        Initialize session manager.
        
        Args:
            user_manager: UserManager instance
            session_timeout: Session timeout in seconds (default: 1 hour)
        """
        self.user_manager = user_manager
        self.session_timeout = session_timeout
        
        # Active sessions
        self.sessions: Dict[str, Session] = {}
        
        # Current session (for single-user mode)
        self.current_session: Optional[Session] = None
        
        print("[SessionManager] Session Manager initialized")
    
    def login(self, username: str, password: str) -> Optional[Session]:
        """
        Login a user and create a session.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Session instance if successful, None otherwise
        """
        # Authenticate user
        user = self.user_manager.authenticate(username, password)
        if not user:
            return None
        
        # Create session
        session = Session(user)
        self.sessions[session.session_id] = session
        self.current_session = session
        
        print(f"[SessionManager] User logged in: {username} (session: {session.session_id[:8]}...)")
        return session
    
    def logout(self, session_id: Optional[str] = None) -> bool:
        """
        Logout a user session.
        
        Args:
            session_id: Session ID (uses current session if None)
            
        Returns:
            True if logged out successfully
        """
        if session_id is None:
            if self.current_session:
                session_id = self.current_session.session_id
            else:
                print("[SessionManager] No active session")
                return False
        
        session = self.sessions.get(session_id)
        if not session:
            print(f"[SessionManager] Session not found")
            return False
        
        # Mark as inactive
        session.is_active = False
        
        # Remove from sessions
        del self.sessions[session_id]
        
        # Clear current session if it's this one
        if self.current_session and self.current_session.session_id == session_id:
            self.current_session = None
        
        print(f"[SessionManager] User logged out: {session.user.username}")
        return True
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session instance or None
        """
        return self.sessions.get(session_id)
    
    def get_current_session(self) -> Optional[Session]:
        """Get current active session."""
        return self.current_session
    
    def get_current_user(self) -> Optional[User]:
        """Get currently logged in user."""
        if self.current_session:
            return self.current_session.user
        return None
    
    def whoami(self) -> Optional[str]:
        """
        Get current username.
        
        Returns:
            Username or None if not logged in
        """
        user = self.get_current_user()
        return user.username if user else None
    
    def switch_user(self, username: str, password: str) -> Optional[Session]:
        """
        Switch to a different user (logout current, login new).
        
        Args:
            username: New username
            password: Password
            
        Returns:
            New session if successful
        """
        # Logout current session
        if self.current_session:
            self.logout()
        
        # Login new user
        return self.login(username, password)
    
    def list_sessions(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        List all sessions.
        
        Args:
            include_inactive: Include inactive sessions
            
        Returns:
            List of session information dictionaries
        """
        result = []
        for session in self.sessions.values():
            if not include_inactive and not session.is_active:
                continue
            result.append(session.get_info())
        
        return result
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions.
        
        Returns:
            Number of sessions removed
        """
        expired_ids = []
        
        for session_id, session in self.sessions.items():
            if session.get_idle_time() > self.session_timeout:
                expired_ids.append(session_id)
        
        for session_id in expired_ids:
            session = self.sessions[session_id]
            print(f"[SessionManager] Session expired: {session.user.username}")
            del self.sessions[session_id]
            
            # Clear current session if expired
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
        
        return len(expired_ids)
    
    def get_active_users(self) -> List[str]:
        """Get list of currently logged in usernames."""
        return [session.user.username for session in self.sessions.values() if session.is_active]
    
    def is_logged_in(self, username: str) -> bool:
        """Check if a user is currently logged in."""
        return username in self.get_active_users()
    
    def get_session_count(self) -> int:
        """Get number of active sessions."""
        return len([s for s in self.sessions.values() if s.is_active])
    
    def logout_all(self) -> int:
        """
        Logout all users.
        
        Returns:
            Number of sessions logged out
        """
        count = len(self.sessions)
        self.sessions.clear()
        self.current_session = None
        print(f"[SessionManager] Logged out {count} session(s)")
        return count

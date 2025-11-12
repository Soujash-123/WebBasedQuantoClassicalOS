"""
Authentication Manager
Handles user authentication and session management.
"""

import secrets
import json
import os
from typing import Optional, Dict
from datetime import datetime, timedelta
from .hashing import HashingManager


class Session:
    """Represents a user session"""
    
    def __init__(self, username: str, token: str, expires_in: int = 3600):
        self.username = username
        self.token = token
        self.created = datetime.now()
        self.expires = self.created + timedelta(seconds=expires_in)
        self.last_activity = self.created
    
    def is_valid(self) -> bool:
        """Check if session is still valid"""
        return datetime.now() < self.expires
    
    def refresh(self, extend_seconds: int = 3600):
        """Refresh session expiration"""
        self.last_activity = datetime.now()
        self.expires = self.last_activity + timedelta(seconds=extend_seconds)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'username': self.username,
            'token': self.token,
            'created': self.created.isoformat(),
            'expires': self.expires.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'valid': self.is_valid()
        }


class AuthenticationManager:
    """Manages user authentication"""
    
    def __init__(self, user_db_path: Optional[str] = None):
        self.hasher = HashingManager()
        self.sessions: Dict[str, Session] = {}  # token -> Session
        self.user_sessions: Dict[str, str] = {}  # username -> token
        self.user_db_path = user_db_path
        self.users = {}  # username -> {password_hash, salt, ...}
        self.failed_attempts = {}  # username -> count
        self.max_failed_attempts = 5
        
        if user_db_path and os.path.exists(user_db_path):
            self._load_users()
    
    def _load_users(self):
        """Load users from database"""
        try:
            with open(self.user_db_path, 'r') as f:
                self.users = json.load(f)
        except Exception as e:
            print(f"Error loading users: {e}")
    
    def _save_users(self):
        """Save users to database"""
        if not self.user_db_path:
            return
        
        try:
            os.makedirs(os.path.dirname(self.user_db_path), exist_ok=True)
            with open(self.user_db_path, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def create_user(self, username: str, password: str, **kwargs) -> bool:
        """Create a new user"""
        if username in self.users:
            return False
        
        # Hash password
        password_hash, salt = self.hasher.hash_password(password)
        
        self.users[username] = {
            'password_hash': password_hash,
            'salt': salt,
            'created': datetime.now().isoformat(),
            'last_login': None,
            **kwargs
        }
        
        self._save_users()
        return True
    
    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        if username not in self.users:
            return False
        
        # Logout user if logged in
        if username in self.user_sessions:
            token = self.user_sessions[username]
            self.logout(token)
        
        del self.users[username]
        self._save_users()
        return True
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        if username not in self.users:
            return False
        
        # Verify old password
        user = self.users[username]
        if not self.hasher.verify_password(old_password, user['password_hash'], user['salt']):
            return False
        
        # Hash new password
        password_hash, salt = self.hasher.hash_password(new_password)
        
        user['password_hash'] = password_hash
        user['salt'] = salt
        user['password_changed'] = datetime.now().isoformat()
        
        self._save_users()
        return True
    
    def reset_password(self, username: str, new_password: str) -> bool:
        """Reset user password (admin function)"""
        if username not in self.users:
            return False
        
        password_hash, salt = self.hasher.hash_password(new_password)
        
        user = self.users[username]
        user['password_hash'] = password_hash
        user['salt'] = salt
        user['password_reset'] = datetime.now().isoformat()
        
        self._save_users()
        return True
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate user and create session
        Returns session token if successful, None otherwise
        """
        # Check if user exists
        if username not in self.users:
            return None
        
        # Check failed attempts
        if self.failed_attempts.get(username, 0) >= self.max_failed_attempts:
            return None
        
        user = self.users[username]
        
        # Verify password
        if not self.hasher.verify_password(password, user['password_hash'], user['salt']):
            self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
            return None
        
        # Reset failed attempts
        self.failed_attempts[username] = 0
        
        # Create session
        token = self._generate_token()
        session = Session(username, token)
        
        # Store session
        self.sessions[token] = session
        self.user_sessions[username] = token
        
        # Update last login
        user['last_login'] = datetime.now().isoformat()
        self._save_users()
        
        return token
    
    def validate_session(self, token: str) -> Optional[str]:
        """
        Validate session token
        Returns username if valid, None otherwise
        """
        if token not in self.sessions:
            return None
        
        session = self.sessions[token]
        
        if not session.is_valid():
            # Clean up expired session
            self.logout(token)
            return None
        
        # Refresh session
        session.refresh()
        
        return session.username
    
    def logout(self, token: str) -> bool:
        """Logout user by token"""
        if token not in self.sessions:
            return False
        
        session = self.sessions[token]
        username = session.username
        
        # Remove session
        del self.sessions[token]
        if username in self.user_sessions and self.user_sessions[username] == token:
            del self.user_sessions[username]
        
        return True
    
    def get_session_info(self, token: str) -> Optional[dict]:
        """Get session information"""
        if token not in self.sessions:
            return None
        
        return self.sessions[token].to_dict()
    
    def get_active_sessions(self) -> list:
        """Get all active sessions"""
        return [s.to_dict() for s in self.sessions.values() if s.is_valid()]
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_tokens = [
            token for token, session in self.sessions.items()
            if not session.is_valid()
        ]
        
        for token in expired_tokens:
            self.logout(token)
        
        return len(expired_tokens)
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        return username in self.users
    
    def get_user_info(self, username: str) -> Optional[dict]:
        """Get user information (without sensitive data)"""
        if username not in self.users:
            return None
        
        user = self.users[username].copy()
        # Remove sensitive data
        user.pop('password_hash', None)
        user.pop('salt', None)
        
        return user
    
    def list_users(self) -> list:
        """List all usernames"""
        return list(self.users.keys())
    
    def _generate_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)

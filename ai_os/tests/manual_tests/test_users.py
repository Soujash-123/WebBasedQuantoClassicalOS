"""
Manual Test Suite for User Management & Authentication Layer
Tests user accounts, authentication, and sessions.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core import AIOSCore
from users import UserLayer, UserRole


def test_user_creation():
    """Test user creation and management."""
    print("\n" + "=" * 60)
    print("TEST: User Creation and Management")
    print("=" * 60)
    
    core = AIOSCore("test_user_config.json")
    users = UserLayer(core, users_file="test_users.json")
    
    # Login as root
    print("\n[TEST] Logging in as root...")
    session = users.login("root", "root")
    assert session is not None, "Root login failed"
    print(f"✓ Logged in as root")
    
    # Create a new user
    print("\n[TEST] Creating new user...")
    assert users.adduser("testuser", "testpass", UserRole.USER), "Failed to create user"
    print("✓ User created")
    
    # List users
    print("\n[TEST] Listing users...")
    user_list = users.listusers()
    assert len(user_list) >= 4, f"Expected at least 4 users, got {len(user_list)}"
    print(f"✓ Found {len(user_list)} user(s)")
    
    users.shutdown()
    core.shutdown()
    
    # Cleanup
    for f in ["test_user_config.json", "test_users.json"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("\n✓ User Creation tests PASSED")


def test_authentication():
    """Test user authentication."""
    print("\n" + "=" * 60)
    print("TEST: User Authentication")
    print("=" * 60)
    
    core = AIOSCore("test_auth_config.json")
    users = UserLayer(core, users_file="test_auth_users.json")
    
    # Test valid login
    print("\n[TEST] Testing valid login...")
    session = users.login("admin", "admin")
    assert session is not None, "Valid login failed"
    assert users.whoami() == "admin", "whoami() incorrect"
    print("✓ Valid login successful")
    
    # Test invalid password
    print("\n[TEST] Testing invalid password...")
    users.logout()
    session = users.login("admin", "wrongpassword")
    assert session is None, "Invalid login should fail"
    print("✓ Invalid password rejected")
    
    # Test non-existent user
    print("\n[TEST] Testing non-existent user...")
    session = users.login("nonexistent", "password")
    assert session is None, "Non-existent user should fail"
    print("✓ Non-existent user rejected")
    
    users.shutdown()
    core.shutdown()
    
    # Cleanup
    for f in ["test_auth_config.json", "test_auth_users.json"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("\n✓ Authentication tests PASSED")


def test_sessions():
    """Test session management."""
    print("\n" + "=" * 60)
    print("TEST: Session Management")
    print("=" * 60)
    
    core = AIOSCore("test_session_config.json")
    users = UserLayer(core, users_file="test_session_users.json")
    
    # Login
    print("\n[TEST] Creating session...")
    session = users.login("root", "root")
    assert session is not None, "Login failed"
    print(f"✓ Session created: {session.session_id[:8]}...")
    
    # Check whoami
    print("\n[TEST] Testing whoami...")
    username = users.whoami()
    assert username == "root", f"Expected 'root', got '{username}'"
    print(f"✓ Current user: {username}")
    
    # List sessions
    print("\n[TEST] Listing sessions...")
    sessions = users.sessions()
    assert len(sessions) >= 1, "No sessions found"
    print(f"✓ Found {len(sessions)} active session(s)")
    
    # Logout
    print("\n[TEST] Logging out...")
    assert users.logout(), "Logout failed"
    assert users.whoami() is None, "User still logged in after logout"
    print("✓ Logout successful")
    
    users.shutdown()
    core.shutdown()
    
    # Cleanup
    for f in ["test_session_config.json", "test_session_users.json"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("\n✓ Session Management tests PASSED")


def test_permissions():
    """Test user permissions."""
    print("\n" + "=" * 60)
    print("TEST: User Permissions")
    print("=" * 60)
    
    core = AIOSCore("test_perm_config.json")
    users = UserLayer(core, users_file="test_perm_users.json")
    
    # Login as root
    print("\n[TEST] Testing root permissions...")
    users.login("root", "root")
    assert users.has_permission("anything"), "Root should have all permissions"
    print("✓ Root has all permissions")
    
    # Login as guest
    print("\n[TEST] Testing guest permissions...")
    users.switch_user("guest", "guest")
    assert not users.has_permission("user.create"), "Guest should not create users"
    assert users.has_permission("file.read_public"), "Guest should read public files"
    print("✓ Guest permissions correct")
    
    # Login as admin
    print("\n[TEST] Testing admin permissions...")
    users.switch_user("admin", "admin")
    assert users.has_permission("user.create"), "Admin should create users"
    print("✓ Admin permissions correct")
    
    users.shutdown()
    core.shutdown()
    
    # Cleanup
    for f in ["test_perm_config.json", "test_perm_users.json"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("\n✓ Permissions tests PASSED")


def test_password_change():
    """Test password change functionality."""
    print("\n" + "=" * 60)
    print("TEST: Password Change")
    print("=" * 60)
    
    core = AIOSCore("test_passwd_config.json")
    users = UserLayer(core, users_file="test_passwd_users.json")
    
    # Login as root and create user
    users.login("root", "root")
    users.adduser("changetest", "oldpass", UserRole.USER)
    
    # Change password
    print("\n[TEST] Changing password...")
    assert users.passwd("changetest", "newpass"), "Password change failed"
    print("✓ Password changed")
    
    # Test old password fails
    print("\n[TEST] Testing old password...")
    users.logout()
    session = users.login("changetest", "oldpass")
    assert session is None, "Old password should not work"
    print("✓ Old password rejected")
    
    # Test new password works
    print("\n[TEST] Testing new password...")
    session = users.login("changetest", "newpass")
    assert session is not None, "New password should work"
    print("✓ New password accepted")
    
    users.shutdown()
    core.shutdown()
    
    # Cleanup
    for f in ["test_passwd_config.json", "test_passwd_users.json"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("\n✓ Password Change tests PASSED")


def test_user_deletion():
    """Test user deletion."""
    print("\n" + "=" * 60)
    print("TEST: User Deletion")
    print("=" * 60)
    
    core = AIOSCore("test_del_config.json")
    users = UserLayer(core, users_file="test_del_users.json")
    
    # Login as root
    users.login("root", "root")
    
    # Create and delete user
    print("\n[TEST] Creating user...")
    users.adduser("deletetest", "pass", UserRole.USER)
    
    print("\n[TEST] Deleting user...")
    assert users.deluser("deletetest"), "User deletion failed"
    print("✓ User deleted")
    
    # Verify user is gone
    print("\n[TEST] Verifying deletion...")
    user_list = users.listusers()
    usernames = [u['username'] for u in user_list]
    assert "deletetest" not in usernames, "User still exists after deletion"
    print("✓ User successfully removed")
    
    # Test cannot delete root
    print("\n[TEST] Testing root protection...")
    assert not users.deluser("root"), "Should not be able to delete root"
    print("✓ Root user protected")
    
    users.shutdown()
    core.shutdown()
    
    # Cleanup
    for f in ["test_del_config.json", "test_del_users.json"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("\n✓ User Deletion tests PASSED")


def run_all_tests():
    """Run all user tests."""
    print("\n" + "#" * 60)
    print("# USER MANAGEMENT LAYER - MANUAL TEST SUITE")
    print("#" * 60)
    
    try:
        test_user_creation()
        test_authentication()
        test_sessions()
        test_permissions()
        test_password_change()
        test_user_deletion()
        
        print("\n" + "#" * 60)
        print("# ALL USER TESTS PASSED ✓")
        print("#" * 60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        print("\n" + "#" * 60)
        print("# TESTS FAILED ✗")
        print("#" * 60 + "\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()

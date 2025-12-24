"""
Quick test script to verify DuckDB authentication system works.
"""

import sys
sys.path.insert(0, '/Users/ashwin/Desktop/pca_agent copy')

from src.services.user_service import UserService, PasswordValidator
from src.database.duckdb_auth import get_auth_manager

def test_duckdb_auth():
    """Test DuckDB authentication system."""
    print("=" * 60)
    print("Testing DuckDB Authentication System")
    print("=" * 60)
    
    # Initialize service
    user_service = UserService()
    print("✓ UserService initialized")
    
    # Test password validation
    is_valid, error = PasswordValidator.validate("weak")
    assert not is_valid, "Weak password should fail"
    print("✓ Password validation works")
    
    # Create test user
    try:
        user = user_service.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123!"
        )
        print(f"✓ User created: {user['email']}")
    except ValueError as e:
        if "already exists" in str(e):
            print(f"✓ User already exists (expected if running multiple times)")
            user = user_service.get_user_by_email("test@example.com")
        else:
            raise
    
    # Test authentication
    auth_user = user_service.authenticate_user("testuser", "TestPass123!")
    assert auth_user is not None, "Authentication should succeed"
    print(f"✓ Authentication successful: {auth_user['email']}")
    
    # Test wrong password
    auth_fail = user_service.authenticate_user("testuser", "WrongPassword")
    assert auth_fail is None, "Authentication should fail with wrong password"
    print("✓ Wrong password correctly rejected")
    
    # Test get user by email
    user_by_email = user_service.get_user_by_email("test@example.com")
    assert user_by_email is not None, "Should find user by email"
    print(f"✓ Get user by email works: {user_by_email['username']}")
    
    # Test list users
    users = user_service.list_users()
    assert len(users) > 0, "Should have at least one user"
    print(f"✓ List users works: {len(users)} users found")
    
    print("\n" + "=" * 60)
    print("✅ All DuckDB authentication tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_duckdb_auth()

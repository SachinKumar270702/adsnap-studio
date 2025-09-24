#!/usr/bin/env python3
"""
Test script for AdSnap Studio login functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.auth import AuthManager

def test_auth_system():
    """Test the authentication system"""
    print("🧪 Testing AdSnap Studio Authentication System")
    print("=" * 50)
    
    # Initialize auth manager
    auth = AuthManager("data/test_users.json")
    
    # Test user creation
    print("\n1. Testing user creation...")
    success, message = auth.create_user(
        username="testuser",
        email="test@adsnap.studio", 
        password="testpass123",
        full_name="Test User"
    )
    print(f"   Result: {message}")
    
    # Test authentication
    print("\n2. Testing authentication...")
    success, message = auth.authenticate("testuser", "testpass123")
    print(f"   Result: {message}")
    
    # Test wrong password
    print("\n3. Testing wrong password...")
    success, message = auth.authenticate("testuser", "wrongpass")
    print(f"   Result: {message}")
    
    # Test user info retrieval
    print("\n4. Testing user info retrieval...")
    user_info = auth.get_user_info("testuser")
    print(f"   User info: {user_info.get('full_name', 'N/A')} ({user_info.get('email', 'N/A')})")
    
    # Test password change
    print("\n5. Testing password change...")
    success, message = auth.change_password("testuser", "testpass123", "newpass456")
    print(f"   Result: {message}")
    
    # Test authentication with new password
    print("\n6. Testing authentication with new password...")
    success, message = auth.authenticate("testuser", "newpass456")
    print(f"   Result: {message}")
    
    print("\n✅ Authentication system test completed!")

if __name__ == "__main__":
    test_auth_system()
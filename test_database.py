#!/usr/bin/env python3
"""
Test script for AdSnap Studio database functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.database import DatabaseManager, ActivityTracker
import hashlib

def test_database_system():
    """Test the database system"""
    print("🧪 Testing AdSnap Studio Database System")
    print("=" * 50)
    
    # Initialize database
    db = DatabaseManager("data/test_adsnap.db")
    tracker = ActivityTracker(db)
    
    # Test user creation
    print("\n1. Testing user creation...")
    password_hash = hashlib.sha256("testpass123".encode()).hexdigest()
    success, message = db.create_user(
        username="testuser",
        email="test@adsnap.studio", 
        password_hash=password_hash,
        full_name="Test User",
        user_uuid="test-uuid-123"
    )
    print(f"   Result: {message}")
    
    # Test authentication
    print("\n2. Testing authentication...")
    success, message, user_info = db.authenticate_user("testuser", password_hash)
    print(f"   Result: {message}")
    if success:
        print(f"   User ID: {user_info['id']}")
        user_id = user_info['id']
    
    # Test activity logging
    print("\n3. Testing activity logging...")
    tracker.track_login(user_id)
    tracker.track_image_generation(user_id, "A beautiful sunset", {"style": "realistic"})
    tracker.track_image_editing(user_id, "shadow", {"intensity": 50})
    print("   Activities logged successfully")
    
    # Test activity retrieval
    print("\n4. Testing activity retrieval...")
    activities = db.get_user_activities(user_id, limit=5)
    print(f"   Found {len(activities)} activities:")
    for activity in activities:
        print(f"     - {activity['description']} ({activity['type']})")
    
    # Test statistics
    print("\n5. Testing statistics...")
    stats = db.get_user_statistics(user_id)
    print(f"   Images generated: {stats['images_generated']}")
    print(f"   Images edited: {stats['images_edited']}")
    print(f"   Projects: {stats['projects']}")
    
    # Test image saving
    print("\n6. Testing image saving...")
    db.save_generated_image(
        user_id, 
        "https://example.com/image.jpg", 
        "generated",
        "Test prompt",
        {"style": "realistic", "size": "1024x1024"}
    )
    print("   Image saved successfully")
    
    # Test image retrieval
    print("\n7. Testing image retrieval...")
    images = db.get_user_images(user_id, limit=5)
    print(f"   Found {len(images)} images:")
    for image in images:
        print(f"     - {image['type']}: {image['prompt'][:30]}...")
    
    print("\n✅ Database system test completed!")

if __name__ == "__main__":
    test_database_system()
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import streamlit as st

class DatabaseManager:
    def __init__(self, db_path="data/adsnap_studio.db"):
        self.db_path = db_path
        self.ensure_data_directory()
        self.init_database()
    
    def ensure_data_directory(self):
        """Ensure the data directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    user_id TEXT UNIQUE,
                    profile_image TEXT,
                    preferences TEXT -- JSON string for user preferences
                )
            ''')
            
            # Activity logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    activity_type TEXT NOT NULL,
                    activity_description TEXT NOT NULL,
                    details TEXT, -- JSON string for additional details
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Projects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    project_name TEXT NOT NULL,
                    project_description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    project_data TEXT, -- JSON string for project configuration
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Generated images table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generated_images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    project_id INTEGER,
                    image_url TEXT,
                    image_type TEXT, -- 'generated', 'edited', 'lifestyle', etc.
                    prompt TEXT,
                    settings TEXT, -- JSON string for generation settings
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_size INTEGER,
                    dimensions TEXT, -- "width x height"
                    is_favorite BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''')
            
            # User sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_id TEXT UNIQUE,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    logout_time TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # User statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    total_images_generated INTEGER DEFAULT 0,
                    total_images_edited INTEGER DEFAULT 0,
                    total_projects INTEGER DEFAULT 0,
                    total_login_time INTEGER DEFAULT 0, -- in minutes
                    favorite_feature TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
    
    def create_user(self, username: str, email: str, password_hash: str, 
                   full_name: str = "", user_uuid: str = "") -> Tuple[bool, str]:
        """Create a new user."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, full_name, user_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, email, password_hash, full_name, user_uuid))
                
                user_id = cursor.lastrowid
                
                # Initialize user statistics
                cursor.execute('''
                    INSERT INTO user_statistics (user_id)
                    VALUES (?)
                ''', (user_id,))
                
                conn.commit()
                return True, "User created successfully"
                
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return False, "Username already exists"
            elif "email" in str(e):
                return False, "Email already registered"
            else:
                return False, "User creation failed"
        except Exception as e:
            return False, f"Database error: {str(e)}"
    
    def authenticate_user(self, username: str, password_hash: str) -> Tuple[bool, str, Optional[Dict]]:
        """Authenticate user and return user info."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, email, full_name, is_active, user_id
                    FROM users 
                    WHERE username = ? AND password_hash = ?
                ''', (username, password_hash))
                
                user = cursor.fetchone()
                
                if not user:
                    return False, "Invalid username or password", None
                
                if not user[4]:  # is_active
                    return False, "Account is deactivated", None
                
                # Update last login
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (user[0],))
                
                conn.commit()
                
                user_info = {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'full_name': user[3],
                    'user_id': user[5]
                }
                
                return True, "Login successful", user_info
                
        except Exception as e:
            return False, f"Database error: {str(e)}", None
    
    def log_activity(self, user_id: int, activity_type: str, description: str, 
                    details: Dict = None, session_id: str = None):
        """Log user activity."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                details_json = json.dumps(details) if details else None
                
                cursor.execute('''
                    INSERT INTO activity_logs 
                    (user_id, activity_type, activity_description, details, session_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, activity_type, description, details_json, session_id))
                
                conn.commit()
                
        except Exception as e:
            print(f"Error logging activity: {e}")
    
    def get_user_activities(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's recent activities."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT activity_type, activity_description, details, timestamp
                    FROM activity_logs 
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, limit))
                
                activities = []
                for row in cursor.fetchall():
                    activity = {
                        'type': row[0],
                        'description': row[1],
                        'details': json.loads(row[2]) if row[2] else {},
                        'timestamp': row[3]
                    }
                    activities.append(activity)
                
                return activities
                
        except Exception as e:
            print(f"Error fetching activities: {e}")
            return []
    
    def get_user_statistics(self, user_id: int) -> Dict:
        """Get user statistics."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT total_images_generated, total_images_edited, 
                           total_projects, total_login_time, favorite_feature
                    FROM user_statistics 
                    WHERE user_id = ?
                ''', (user_id,))
                
                stats = cursor.fetchone()
                
                if stats:
                    return {
                        'images_generated': stats[0],
                        'images_edited': stats[1],
                        'projects': stats[2],
                        'login_time': stats[3],
                        'favorite_feature': stats[4] or 'Image Generation'
                    }
                else:
                    return {
                        'images_generated': 0,
                        'images_edited': 0,
                        'projects': 0,
                        'login_time': 0,
                        'favorite_feature': 'Image Generation'
                    }
                    
        except Exception as e:
            print(f"Error fetching statistics: {e}")
            return {
                'images_generated': 0,
                'images_edited': 0,
                'projects': 0,
                'login_time': 0,
                'favorite_feature': 'Image Generation'
            }
    
    def update_user_statistics(self, user_id: int, stat_type: str, increment: int = 1):
        """Update user statistics."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if stat_type == 'images_generated':
                    cursor.execute('''
                        UPDATE user_statistics 
                        SET total_images_generated = total_images_generated + ?,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (increment, user_id))
                elif stat_type == 'images_edited':
                    cursor.execute('''
                        UPDATE user_statistics 
                        SET total_images_edited = total_images_edited + ?,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (increment, user_id))
                elif stat_type == 'projects':
                    cursor.execute('''
                        UPDATE user_statistics 
                        SET total_projects = total_projects + ?,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (increment, user_id))
                
                conn.commit()
                
        except Exception as e:
            print(f"Error updating statistics: {e}")
    
    def save_generated_image(self, user_id: int, image_url: str, image_type: str,
                           prompt: str = "", settings: Dict = None, project_id: int = None):
        """Save generated image information."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                settings_json = json.dumps(settings) if settings else None
                
                cursor.execute('''
                    INSERT INTO generated_images 
                    (user_id, project_id, image_url, image_type, prompt, settings)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, project_id, image_url, image_type, prompt, settings_json))
                
                conn.commit()
                
                # Update statistics
                if image_type in ['generated', 'hd_generation']:
                    self.update_user_statistics(user_id, 'images_generated')
                else:
                    self.update_user_statistics(user_id, 'images_edited')
                
        except Exception as e:
            print(f"Error saving image: {e}")
    
    def get_user_images(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get user's recent images."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT image_url, image_type, prompt, created_at, is_favorite
                    FROM generated_images 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (user_id, limit))
                
                images = []
                for row in cursor.fetchall():
                    image = {
                        'url': row[0],
                        'type': row[1],
                        'prompt': row[2],
                        'created_at': row[3],
                        'is_favorite': bool(row[4])
                    }
                    images.append(image)
                
                return images
                
        except Exception as e:
            print(f"Error fetching images: {e}")
            return []
    
    def create_project(self, user_id: int, project_name: str, description: str = "") -> int:
        """Create a new project."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO projects (user_id, project_name, project_description)
                    VALUES (?, ?, ?)
                ''', (user_id, project_name, description))
                
                project_id = cursor.lastrowid
                conn.commit()
                
                # Update statistics
                self.update_user_statistics(user_id, 'projects')
                
                return project_id
                
        except Exception as e:
            print(f"Error creating project: {e}")
            return 0
    
    def get_user_projects(self, user_id: int) -> List[Dict]:
        """Get user's projects."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, project_name, project_description, created_at, updated_at
                    FROM projects 
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY updated_at DESC
                ''', (user_id,))
                
                projects = []
                for row in cursor.fetchall():
                    project = {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'created_at': row[3],
                        'updated_at': row[4]
                    }
                    projects.append(project)
                
                return projects
                
        except Exception as e:
            print(f"Error fetching projects: {e}")
            return []

# Activity tracking helper functions
class ActivityTracker:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def track_login(self, user_id: int):
        """Track user login."""
        self.db.log_activity(
            user_id, 
            "authentication", 
            "User logged in",
            {"action": "login", "timestamp": datetime.now().isoformat()}
        )
    
    def track_image_generation(self, user_id: int, prompt: str, settings: Dict):
        """Track image generation."""
        self.db.log_activity(
            user_id,
            "image_generation",
            f"Generated image with prompt: '{prompt[:50]}...'",
            {"prompt": prompt, "settings": settings}
        )
    
    def track_image_editing(self, user_id: int, edit_type: str, details: Dict):
        """Track image editing."""
        self.db.log_activity(
            user_id,
            "image_editing",
            f"Applied {edit_type} to image",
            {"edit_type": edit_type, "details": details}
        )
    
    def track_project_creation(self, user_id: int, project_name: str):
        """Track project creation."""
        self.db.log_activity(
            user_id,
            "project_management",
            f"Created new project: {project_name}",
            {"project_name": project_name}
        )
    
    def track_feature_usage(self, user_id: int, feature_name: str, details: Dict = None):
        """Track feature usage."""
        self.db.log_activity(
            user_id,
            "feature_usage",
            f"Used {feature_name} feature",
            {"feature": feature_name, "details": details or {}}
        )

# Initialize database manager
@st.cache_resource
def get_database_manager():
    """Get cached database manager instance."""
    return DatabaseManager()

@st.cache_resource
def get_activity_tracker():
    """Get cached activity tracker instance."""
    db_manager = get_database_manager()
    return ActivityTracker(db_manager)
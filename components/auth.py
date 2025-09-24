import streamlit as st
import hashlib
import json
import os
from datetime import datetime, timedelta
import uuid
from components.database import get_database_manager, get_activity_tracker

class AuthManager:
    def __init__(self, users_file="data/users.json"):
        self.users_file = users_file
        self.ensure_data_directory()
        self.load_users()
    
    def ensure_data_directory(self):
        """Ensure the data directory exists."""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
    
    def load_users(self):
        """Load users from JSON file."""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.users = {}
        else:
            self.users = {}
    
    def save_users(self):
        """Save users to JSON file."""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def hash_password(self, password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, email, password, full_name=""):
        """Create a new user account."""
        if username in self.users:
            return False, "Username already exists"
        
        if any(user.get('email') == email for user in self.users.values()):
            return False, "Email already registered"
        
        user_data = {
            'email': email,
            'password': self.hash_password(password),
            'full_name': full_name,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'is_active': True,
            'user_id': str(uuid.uuid4())
        }
        
        self.users[username] = user_data
        self.save_users()
        return True, "Account created successfully"
    
    def authenticate(self, username, password):
        """Authenticate user credentials."""
        if username not in self.users:
            return False, "Invalid username or password"
        
        user = self.users[username]
        if not user.get('is_active', True):
            return False, "Account is deactivated"
        
        if user['password'] == self.hash_password(password):
            # Update last login
            self.users[username]['last_login'] = datetime.now().isoformat()
            self.save_users()
            return True, "Login successful"
        
        return False, "Invalid username or password"
    
    def get_user_info(self, username):
        """Get user information."""
        return self.users.get(username, {})
    
    def update_user_profile(self, username, **kwargs):
        """Update user profile information."""
        if username in self.users:
            for key, value in kwargs.items():
                if key != 'password':  # Don't allow direct password updates
                    self.users[username][key] = value
            self.save_users()
            return True
        return False
    
    def change_password(self, username, old_password, new_password):
        """Change user password."""
        if username not in self.users:
            return False, "User not found"
        
        if self.users[username]['password'] != self.hash_password(old_password):
            return False, "Current password is incorrect"
        
        self.users[username]['password'] = self.hash_password(new_password)
        self.save_users()
        return True, "Password changed successfully"

def init_session_state():
    """Initialize authentication session state."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = get_database_manager()
    if 'activity_tracker' not in st.session_state:
        st.session_state.activity_tracker = get_activity_tracker()

def logout():
    """Logout user and clear session."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_info = {}
    st.rerun()

def require_auth():
    """Decorator to require authentication for pages."""
    if not st.session_state.get('authenticated', False):
        show_login_page()
        return False
    return True

def show_login_page():
    """Display the login/signup page."""
    init_session_state()
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        color: white;
        border: 2px solid rgba(255,255,255,0.2);
    }
    .auth-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #FFFFFF !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.8);
        background: none !important;
        -webkit-text-fill-color: #FFFFFF !important;
        text-decoration: none !important;
        font-family: 'Arial', sans-serif;
        letter-spacing: 2px;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        border: none;
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .auth-tabs {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown('''
        <div style="background: rgba(0,0,0,0.5); padding: 1.5rem; border-radius: 15px; 
                    margin-bottom: 1rem; border: 3px solid #FFD700; 
                    box-shadow: 0 0 20px rgba(255,215,0,0.3);">
            <h1 class="auth-title">🎨 AdSnap Studio</h1>
            <p style="text-align: center; color: #FFD700; font-size: 1.1rem; 
                      margin: 0; font-weight: 500;">AI-Powered Image Generation & Editing</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Login/Signup tabs
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            st.markdown('<div class="auth-tabs">', unsafe_allow_html=True)
            with st.form("login_form"):
                st.subheader("Welcome Back!")
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    login_btn = st.form_submit_button("🚀 Login", use_container_width=True)
                with col_b:
                    demo_btn = st.form_submit_button("🎭 Demo Mode", use_container_width=True)
                
                if login_btn:
                    if username and password:
                        # Try database authentication first
                        password_hash = hashlib.sha256(password.encode()).hexdigest()
                        success, message, user_info = st.session_state.db_manager.authenticate_user(username, password_hash)
                        
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.session_state.user_info = user_info
                            
                            # Track login activity
                            st.session_state.activity_tracker.track_login(user_info['id'])
                            
                            st.success(f"Welcome back, {username}! 🎉")
                            st.rerun()
                        else:
                            # Fallback to file-based authentication for existing users
                            success, message = st.session_state.auth_manager.authenticate(username, password)
                            if success:
                                st.session_state.authenticated = True
                                st.session_state.username = username
                                st.session_state.user_info = st.session_state.auth_manager.get_user_info(username)
                                st.success(f"Welcome back, {username}! 🎉")
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.warning("Please fill in all fields")
                
                if demo_btn:
                    st.session_state.authenticated = True
                    st.session_state.username = "demo_user"
                    st.session_state.user_info = {
                        'full_name': 'Demo User',
                        'email': 'demo@adsnap.studio',
                        'created_at': datetime.now().isoformat()
                    }
                    st.success("Welcome to Demo Mode! 🎭")
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="auth-tabs">', unsafe_allow_html=True)
            with st.form("signup_form"):
                st.subheader("Join AdSnap Studio!")
                full_name = st.text_input("Full Name", placeholder="Your full name")
                email = st.text_input("Email", placeholder="your.email@example.com")
                new_username = st.text_input("Username", placeholder="Choose a username")
                new_password = st.text_input("Password", type="password", placeholder="Create a strong password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                signup_btn = st.form_submit_button("🌟 Create Account", use_container_width=True)
                
                if signup_btn:
                    if all([full_name, email, new_username, new_password, confirm_password]):
                        if new_password != confirm_password:
                            st.error("Passwords don't match!")
                        elif len(new_password) < 6:
                            st.error("Password must be at least 6 characters long")
                        else:
                            # Create user in database
                            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
                            user_uuid = str(uuid.uuid4())
                            
                            success, message = st.session_state.db_manager.create_user(
                                new_username, email, password_hash, full_name, user_uuid
                            )
                            
                            if success:
                                st.success("Account created successfully! Please login.")
                                st.balloons()
                            else:
                                st.error(message)
                    else:
                        st.warning("Please fill in all fields")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; color: #666;'>🎨 Generate & modify images with AI-powered tools</p>",
            unsafe_allow_html=True
        )

def show_user_profile():
    """Display user profile in sidebar."""
    if st.session_state.get('authenticated'):
        with st.sidebar:
            st.markdown("---")
            user_info = st.session_state.get('user_info', {})
            
            # User info display
            st.markdown(f"**👤 {user_info.get('full_name', st.session_state.username)}**")
            st.markdown(f"📧 {user_info.get('email', 'N/A')}")
            
            if user_info.get('last_login'):
                last_login = datetime.fromisoformat(user_info['last_login'])
                st.markdown(f"🕒 Last login: {last_login.strftime('%Y-%m-%d %H:%M')}")
            
            # Profile actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⚙️ Profile", use_container_width=True):
                    st.session_state.show_profile_modal = True
            with col2:
                if st.button("🚪 Logout", use_container_width=True):
                    logout()
            
            # Profile modal
            if st.session_state.get('show_profile_modal', False):
                show_profile_modal()

def show_profile_modal():
    """Show profile editing modal."""
    st.markdown("### 👤 User Profile")
    
    user_info = st.session_state.get('user_info', {})
    
    with st.form("profile_form"):
        new_full_name = st.text_input("Full Name", value=user_info.get('full_name', ''))
        new_email = st.text_input("Email", value=user_info.get('email', ''))
        
        st.markdown("**Change Password**")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save Changes"):
                # Update profile
                if new_full_name or new_email:
                    st.session_state.auth_manager.update_user_profile(
                        st.session_state.username,
                        full_name=new_full_name,
                        email=new_email
                    )
                    st.session_state.user_info.update({
                        'full_name': new_full_name,
                        'email': new_email
                    })
                
                # Change password if provided
                if current_password and new_password:
                    if new_password != confirm_new_password:
                        st.error("New passwords don't match!")
                    else:
                        success, message = st.session_state.auth_manager.change_password(
                            st.session_state.username, current_password, new_password
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                
                if not (current_password and new_password):
                    st.success("Profile updated successfully!")
                
                st.session_state.show_profile_modal = False
                st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.session_state.show_profile_modal = False
                st.rerun()
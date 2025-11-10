import streamlit as st
import hashlib
import json
import os
from datetime import datetime, timedelta
import uuid

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
    
    def authenticate(self, username_or_email, password):
        """Authenticate user credentials using username or email."""
        # First try to find user by username
        found_username = None
        
        if username_or_email in self.users:
            found_username = username_or_email
        else:
            # Try to find by email
            for uname, user_data in self.users.items():
                if user_data.get('email') == username_or_email:
                    found_username = uname
                    break
        
        if not found_username:
            return False, "Invalid username/email or password"
        
        user = self.users[found_username]
        if not user.get('is_active', True):
            return False, "Account is deactivated"
        
        if user['password'] == self.hash_password(password):
            # Update last login
            self.users[found_username]['last_login'] = datetime.now().isoformat()
            self.save_users()
            return True, "Login successful", found_username
        
        return False, "Invalid username/email or password"
    
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
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    
    # Check for persistent authentication
    if 'authenticated' not in st.session_state:
        # Try to restore authentication from query params (simple persistence)
        query_params = st.query_params
        if 'auth_token' in query_params and 'username' in query_params:
            username = query_params['username']
            auth_token = query_params['auth_token']
            
            # Simple token validation (in production, use proper JWT or similar)
            expected_token = hashlib.sha256(f"{username}_adsnap_session".encode()).hexdigest()[:16]
            
            if auth_token == expected_token and (username in st.session_state.auth_manager.users or username == "demo_user"):
                st.session_state.authenticated = True
                st.session_state.username = username
                
                if username == "demo_user":
                    st.session_state.user_info = {
                        'full_name': 'Demo User',
                        'email': 'demo@adsnap.studio',
                        'created_at': datetime.now().isoformat()
                    }
                else:
                    st.session_state.user_info = st.session_state.auth_manager.get_user_info(username)
            else:
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.user_info = {}
        else:
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_info = {}

def logout():
    """Logout user and clear session."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_info = {}
    
    # Clear persistent authentication
    st.query_params.clear()
    
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
    
    # Check if there's a reset token in URL
    query_params = st.query_params
    if 'reset_token' in query_params:
        show_password_reset_form(query_params['reset_token'])
        return
    
    # Check if showing password reset page
    if st.session_state.get('show_password_reset', False):
        show_password_reset_page()
        return
    
    # Custom CSS for better styling with animated background
    st.markdown("""
    <style>
    /* Hide Streamlit header, toolbar and menu */
    header[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    
    .stApp > header {
        display: none !important;
    }
    
    div[data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    #MainMenu {
        visibility: hidden !important;
        display: none !important;
    }
    
    footer {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* Remove top padding from main container */
    .main .block-container {
        padding-top: 2rem !important;
    }
    
    /* Ensure full viewport height */
    .stApp {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating particles effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
        animation: float 20s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    .auth-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 2.5rem;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.3);
        color: #333;
        position: relative;
        z-index: 1;
        animation: slideUp 0.6s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .auth-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 2px;
        animation: titlePulse 2s ease-in-out infinite;
        text-transform: uppercase;
    }
    
    @keyframes titlePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    .subtitle-text {
        text-align: center;
        color: #667eea;
        font-size: 1rem;
        margin: 0;
        font-weight: 500;
        animation: fadeIn 1s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
        color: white;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .auth-tabs {
        background: rgba(102, 126, 234, 0.05);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid rgba(102, 126, 234, 0.2);
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        color: #667eea;
        font-weight: 600;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.2);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
    
    /* Form styling */
    .stForm {
        background: transparent;
    }
    
    /* Decorative elements */
    .auth-container::before {
        content: '✨';
        position: absolute;
        top: -20px;
        right: -20px;
        font-size: 3rem;
        animation: rotate 4s linear infinite;
    }
    
    .auth-container::after {
        content: '🎨';
        position: absolute;
        bottom: -20px;
        left: -20px;
        font-size: 3rem;
        animation: bounce 2s ease-in-out infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown('''
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 0.5rem; animation: bounce 2s ease-in-out infinite;">
                🎨
            </div>
            <h1 class="auth-title">AdSnap Studio</h1>
            <p class="subtitle-text">AI-Powered Image Generation & Editing</p>
            <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 1rem; font-size: 1.5rem;">
                <span style="animation: bounce 2s ease-in-out infinite; animation-delay: 0.1s;">✨</span>
                <span style="animation: bounce 2s ease-in-out infinite; animation-delay: 0.2s;">🚀</span>
                <span style="animation: bounce 2s ease-in-out infinite; animation-delay: 0.3s;">💫</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Login/Signup tabs
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            st.markdown('<div class="auth-tabs">', unsafe_allow_html=True)
            with st.form("login_form"):
                st.markdown("""
                <div style="text-align: center; margin-bottom: 1rem;">
                    <h3 style="color: #667eea; margin-bottom: 0.5rem;">👋 Welcome Back!</h3>
                    <p style="color: #999; font-size: 0.9rem;">Ready to create something amazing?</p>
                </div>
                """, unsafe_allow_html=True)
                username = st.text_input("Username or Email", placeholder="Enter your username or email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    login_btn = st.form_submit_button("🚀 Login", use_container_width=True)
                with col_b:
                    demo_btn = st.form_submit_button("🎭 Demo Mode", use_container_width=True)
                
                # Forgot password link
                forgot_password_btn = st.form_submit_button("🔑 Forgot Password?", use_container_width=True)
                
                if login_btn:
                    if username and password:
                        result = st.session_state.auth_manager.authenticate(username, password)
                        
                        # Handle both old (2 values) and new (3 values) return format
                        if len(result) == 3:
                            success, message, actual_username = result
                        else:
                            success, message = result
                            actual_username = username
                        
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.username = actual_username
                            st.session_state.user_info = st.session_state.auth_manager.get_user_info(actual_username)
                            
                            # Set persistent authentication using query params
                            auth_token = hashlib.sha256(f"{actual_username}_adsnap_session".encode()).hexdigest()[:16]
                            st.query_params.update({
                                'auth_token': auth_token,
                                'username': actual_username
                            })
                            
                            st.success(f"Welcome back, {actual_username}! 🎉")
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
                    
                    # Set persistent authentication for demo mode
                    auth_token = hashlib.sha256("demo_user_adsnap_session".encode()).hexdigest()[:16]
                    st.query_params.update({
                        'auth_token': auth_token,
                        'username': 'demo_user'
                    })
                    
                    st.success("Welcome to Demo Mode! 🎭")
                    st.rerun()
                
                if forgot_password_btn:
                    st.session_state.show_password_reset = True
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="auth-tabs">', unsafe_allow_html=True)
            with st.form("signup_form"):
                st.markdown("""
                <div style="text-align: center; margin-bottom: 1rem;">
                    <h3 style="color: #667eea; margin-bottom: 0.5rem;">🌟 Join AdSnap Studio!</h3>
                    <p style="color: #999; font-size: 0.9rem;">Start your creative journey today</p>
                </div>
                """, unsafe_allow_html=True)
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
                            # Create user using AuthManager
                            success, message = st.session_state.auth_manager.create_user(
                                new_username, email, new_password, full_name
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
        st.markdown("""
        <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 2px solid rgba(102, 126, 234, 0.1);">
            <p style='text-align: center; color: #667eea; font-weight: 500; margin-bottom: 0.5rem;'>
                ✨ Generate & modify images with AI-powered tools ✨
            </p>
            <div style="text-align: center; font-size: 0.9rem; color: #999;">
                <span style="margin: 0 0.5rem;">🎨 Create</span>
                <span style="margin: 0 0.5rem;">✂️ Edit</span>
                <span style="margin: 0 0.5rem;">🚀 Transform</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

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

def show_password_reset_page():
    """Display password reset request page."""
    from components.email_service import EmailService
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 4rem; margin-bottom: 0.5rem;">🔐</div>
        <h1 style="color: #667eea;">Reset Your Password</h1>
        <p style="color: #888;">Enter your email to receive a password reset link</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("password_reset_form"):
            email = st.text_input("Email Address", placeholder="your.email@example.com")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit_btn = st.form_submit_button("📧 Send Reset Link", use_container_width=True, type="primary")
            with col_b:
                back_btn = st.form_submit_button("← Back to Login", use_container_width=True)
            
            if submit_btn:
                if email:
                    # Check if email exists
                    auth_manager = st.session_state.auth_manager
                    user_found = False
                    
                    for username, user_data in auth_manager.users.items():
                        if user_data.get('email') == email:
                            user_found = True
                            break
                    
                    if user_found:
                        # Generate reset token
                        email_service = EmailService()
                        token = email_service.generate_reset_token(email)
                        
                        # Create reset link
                        base_url = st.query_params.get('base_url', 'http://localhost:8501')
                        reset_link = f"{base_url}/?reset_token={token}"
                        
                        # Send email
                        success, message = email_service.send_password_reset_email(email, reset_link)
                        
                        if success:
                            st.success("✅ Password reset link sent! Check your email.")
                            st.info("📧 The link will expire in 1 hour.")
                        else:
                            st.error(f"❌ {message}")
                            st.info("💡 Note: Email service requires SMTP configuration in environment variables.")
                    else:
                        # Don't reveal if email exists for security
                        st.success("✅ If that email exists, a reset link has been sent!")
                else:
                    st.warning("Please enter your email address")
            
            if back_btn:
                st.session_state.show_password_reset = False
                st.rerun()

def show_password_reset_form(reset_token):
    """Display form to set new password after clicking reset link."""
    from components.email_service import EmailService
    
    email_service = EmailService()
    valid, email, message = email_service.verify_reset_token(reset_token)
    
    if not valid:
        st.error(f"❌ {message}")
        st.info("Please request a new password reset link.")
        if st.button("← Back to Login"):
            st.query_params.clear()
            st.rerun()
        return
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 4rem; margin-bottom: 0.5rem;">🔑</div>
        <h1 style="color: #667eea;">Set New Password</h1>
        <p style="color: #888;">Create a strong password for your account</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("new_password_form"):
            st.info(f"📧 Resetting password for: {email}")
            
            new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm new password")
            
            submit_btn = st.form_submit_button("🔐 Reset Password", use_container_width=True, type="primary")
            
            if submit_btn:
                if new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("❌ Passwords don't match!")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters long")
                    else:
                        # Find user by email and update password
                        auth_manager = st.session_state.auth_manager
                        
                        for username, user_data in auth_manager.users.items():
                            if user_data.get('email') == email:
                                # Update password
                                auth_manager.users[username]['password'] = auth_manager.hash_password(new_password)
                                auth_manager.save_users()
                                
                                # Mark token as used
                                email_service.mark_token_used(reset_token)
                                
                                st.success("✅ Password reset successfully!")
                                st.balloons()
                                st.info("You can now login with your new password.")
                                
                                # Clear reset token from URL
                                st.query_params.clear()
                                
                                if st.button("🚀 Go to Login"):
                                    st.rerun()
                                break
                else:
                    st.warning("Please fill in all fields")

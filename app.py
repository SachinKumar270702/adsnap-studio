# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from services import (
    lifestyle_shot_by_image,
    lifestyle_shot_by_text,
    add_shadow,
    create_packshot,
    enhance_prompt,
    generative_fill,
    generate_hd_image,
    erase_foreground
)
from PIL import Image, ImageFilter
import io
import requests
import json
import time
import base64
from streamlit_drawable_canvas import st_canvas
import numpy as np
from services.erase_foreground import erase_foreground

# Import our custom components
from components.auth import init_session_state, require_auth, show_login_page, show_user_profile, logout
from components.interactive_ui import (
    add_custom_css, show_animated_header, show_feature_card, 
    show_progress_bar, show_metric_cards, show_loading_spinner,
    create_image_gallery, enhanced_file_uploader, show_generation_status,
    create_interactive_sidebar, show_welcome_dashboard
)
from components.dashboard import show_dashboard, show_feature_tour
from components.activity_dashboard import track_current_activity

# Configure Streamlit page
st.set_page_config(
    page_title="AdSnap Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit default elements
hide_streamlit_style = """
<style>
    header[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    #MainMenu {
        visibility: hidden !important;
    }
    
    footer {
        visibility: hidden !important;
    }
    
    .main .block-container {
        padding-top: 1rem !important;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Load environment variables
print("Loading environment variables...")
load_dotenv(verbose=True)

# Debug: Print environment variable status
api_key = os.getenv("BRIA_API_KEY")
print(f"API Key present: {bool(api_key)}")
print(f"API Key value: {api_key if api_key else 'Not found'}")
print(f"Current working directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")

def initialize_session_state():
    """Initialize session state variables."""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv('BRIA_API_KEY')
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []  # List to store multiple generated images
    if 'current_image' not in st.session_state:
        st.session_state.current_image = None
    if 'pending_urls' not in st.session_state:
        st.session_state.pending_urls = []
    if 'edited_image' not in st.session_state:
        st.session_state.edited_image = None  # Single image (backward compatibility)
    if 'original_prompt' not in st.session_state:
        st.session_state.original_prompt = ""
    if 'enhanced_prompt' not in st.session_state:
        st.session_state.enhanced_prompt = None

def download_image(url):
    """Download image from URL and return as bytes."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.error(f"Error downloading image: {str(e)}")
        return None

def main():
    # Initialize authentication
    init_session_state()
    
    # Add custom CSS
    add_custom_css()
    
    # Check if user is authenticated
    if not require_auth():
        return
    
    # Show user profile in sidebar
    show_user_profile()
    
    # Create interactive sidebar
    create_interactive_sidebar()
    
    # Initialize app session state
    initialize_session_state()
    
    # Show welcome dashboard for first-time users
    if not st.session_state.get('has_used_app', False):
        show_welcome_dashboard()
        if st.button("🚀 Get Started", type="primary", use_container_width=True):
            st.session_state.has_used_app = True
            st.rerun()
        return
    
    # Professional & Elegant Styling
    st.markdown("""
    <style>
    /* Global Styling */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Navigation Buttons */
    .stButton > button {
        background: transparent !important;
        border: none !important;
        color: rgba(255,255,255,0.95) !important;
        font-weight: 600 !important;
        padding: 14px 28px !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-size: 0.95rem !important;
        white-space: nowrap !important;
        letter-spacing: 0.3px !important;
    }
    .stButton > button:hover {
        background: rgba(255,255,255,0.25) !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15) !important;
    }
    
    /* Primary Buttons - Enhanced Blue Theme */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 800 !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5) !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .stButton > button[kind="primary"]::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent) !important;
        transition: left 0.5s !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 10px 35px rgba(102, 126, 234, 0.7) !important;
        border-color: white !important;
    }
    .stButton > button[kind="primary"]:hover::before {
        left: 100% !important;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(0,0,0,0.12);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 12px !important;
        border: 2px solid rgba(102, 126, 234, 0.2) !important;
        padding: 12px 16px !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* File Uploader */
    .stFileUploader {
        background: white;
        border-radius: 16px;
        padding: 25px;
        border: 2px dashed rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    .stFileUploader:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.02);
    }
    
    /* Sliders */
    .stSlider > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Info/Warning/Error Boxes */
    .stAlert {
        border-radius: 12px !important;
        padding: 16px 20px !important;
        margin: 15px 0 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(102, 126, 234, 0.05) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
    }
    
    /* Markdown Headers - Enhanced Gradient Theme */
    h1, h2, h3, h4 {
        background: linear-gradient(135deg, #667eea 0%, #ffd700 50%, #764ba2 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
        filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3)) !important;
    }
    
    /* Enhanced text colors */
    p, span, div {
        color: #2d3748;
    }
    
    /* Feature card text enhancement */
    .feature-card h3 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }
    
    /* Spacing */
    .block-container {
        padding: 2rem 3rem !important;
        max-width: 1400px !important;
    }
    
    /* ========== MOBILE RESPONSIVE STYLES ========== */
    @media only screen and (max-width: 768px) {
        /* Hide sidebar on mobile */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Expand main content to full width */
        .main .block-container {
            max-width: 100% !important;
            padding: 0.5rem !important;
        }
        
        /* Reduce padding on mobile */
        .block-container {
            padding: 0.5rem !important;
        }
        
        /* Smaller buttons on mobile */
        .stButton > button {
            padding: 10px 16px !important;
            font-size: 0.85rem !important;
        }
        
        /* Stack columns vertically */
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
            max-width: 100% !important;
        }
        
        /* Smaller headers */
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.3rem !important; }
        h4 { font-size: 1.1rem !important; }
        
        /* Adjust feature cards */
        .feature-card {
            padding: 15px;
            margin: 10px 0;
        }
        
        /* Smaller input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            font-size: 0.9rem !important;
            padding: 10px 12px !important;
        }
        
        /* File uploader */
        .stFileUploader {
            padding: 15px;
        }
    }
    
    @media only screen and (max-width: 480px) {
        /* Extra small devices */
        .block-container {
            padding: 0.5rem !important;
        }
        
        .stButton > button {
            padding: 8px 12px !important;
            font-size: 0.8rem !important;
        }
        
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Centered Header with Logo and Features
    st.markdown("""
    <style>
    .header-container {
        text-align: center;
        padding: 50px 0 20px 0;
        margin: -80px -100px 0 -100px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .logo-title-wrapper {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 25px;
        margin-bottom: 15px;
    }
    .logo-emoji {
        font-size: 4rem;
        line-height: 1;
        display: block;
        filter: drop-shadow(0 8px 16px rgba(0,0,0,0.3));
    }
    .main-title {
        margin: 0;
        font-size: 3.5rem;
        font-weight: 900;
        letter-spacing: 5px;
        font-family: 'Segoe UI', 'Arial Black', sans-serif;
        line-height: 1;
        background: linear-gradient(135deg, #ffffff 0%, #ffd700 50%, #ffffff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 0 20px rgba(255, 215, 0, 0.6)) drop-shadow(3px 3px 6px rgba(0,0,0,0.4));
        animation: shimmer 3s ease-in-out infinite;
        background-size: 200% auto;
    }
    
    @keyframes shimmer {
        0%, 100% { background-position: 0% center; }
        50% { background-position: 100% center; }
    }
    
    .subtitle {
        margin: 12px 0 0 0;
        background: linear-gradient(90deg, #ffd700 0%, #ffffff 50%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 4px;
        text-transform: uppercase;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
    }
    
    /* Mobile Responsive Header */
    @media only screen and (max-width: 768px) {
        .header-container {
            padding: 30px 10px 15px 10px;
            margin: -80px -20px 0 -20px;
        }
        .logo-title-wrapper {
            flex-direction: column;
            gap: 15px;
        }
        .logo-emoji {
            font-size: 3rem;
        }
        .main-title {
            font-size: 2rem;
            letter-spacing: 2px;
        }
        .subtitle {
            font-size: 0.75rem;
            letter-spacing: 1.5px;
        }
    }
    
    @media only screen and (max-width: 480px) {
        .header-container {
            padding: 20px 5px 10px 5px;
            margin: -80px -10px 0 -10px;
        }
        .logo-emoji {
            font-size: 2.5rem;
        }
        .main-title {
            font-size: 1.5rem;
            letter-spacing: 1px;
        }
        .subtitle {
            font-size: 0.65rem;
            letter-spacing: 1px;
        }
    }
    </style>
    <div class="header-container">
        <div class="logo-title-wrapper">
            <div style="background: transparent; padding: 0; display: flex; align-items: center; justify-content: center;">
                <span class="logo-emoji">🎨</span>
            </div>
            <div>
                <h1 class="main-title">ADSNAP STUDIO</h1>
                <p class="subtitle">AI-Powered Image Generation & Editing</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mobile Hamburger Menu
    st.markdown("""
    <style>
    /* Desktop Navigation - Hide on mobile */
    .desktop-nav {
        display: block;
        margin: 30px 0 40px 0;
    }
    
    /* Hamburger Menu Button */
    .hamburger-btn {
        display: none;
        position: fixed;
        top: 15px;
        left: 15px;
        z-index: 10001;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        width: 50px;
        height: 50px;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5);
        transition: all 0.3s ease;
    }
    
    .hamburger-btn:active {
        transform: scale(0.95);
    }
    
    .hamburger-icon {
        display: flex;
        flex-direction: column;
        gap: 5px;
        align-items: center;
        justify-content: center;
        height: 100%;
    }
    
    .hamburger-icon span {
        display: block;
        width: 25px;
        height: 3px;
        background: white;
        border-radius: 2px;
        transition: all 0.3s ease;
    }
    
    /* Mobile Slide-out Menu */
    .mobile-menu {
        display: none;
        position: fixed;
        top: 0;
        left: -100%;
        width: 280px;
        height: 100vh;
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        box-shadow: 4px 0 20px rgba(0,0,0,0.3);
        z-index: 10000;
        transition: left 0.3s ease;
        overflow-y: auto;
    }
    
    .mobile-menu.active {
        left: 0;
    }
    
    .mobile-menu-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 9999;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .mobile-menu-overlay.active {
        opacity: 1;
    }
    
    .mobile-menu-header {
        padding: 20px;
        border-bottom: 2px solid rgba(255,255,255,0.2);
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .mobile-menu-logo {
        font-size: 2.5rem;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
    }
    
    .mobile-menu-title {
        background: linear-gradient(135deg, #ffd700 0%, #ffffff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.3rem;
        font-weight: 900;
        letter-spacing: 2px;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
    }
    
    .mobile-menu-items {
        padding: 10px 0;
    }
    
    .mobile-menu-item {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 18px 25px;
        color: rgba(255,255,255,0.95);
        text-decoration: none;
        transition: all 0.3s ease;
        border-left: 4px solid transparent;
        position: relative;
    }
    
    .mobile-menu-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 0;
        background: linear-gradient(90deg, rgba(255,215,0,0.2) 0%, transparent 100%);
        transition: width 0.3s ease;
    }
    
    .mobile-menu-item:hover {
        background: rgba(255,255,255,0.15);
        border-left-color: #ffd700;
        color: #ffd700;
    }
    
    .mobile-menu-item:hover::before {
        width: 100%;
    }
    
    .mobile-menu-item.active {
        background: linear-gradient(90deg, rgba(255,215,0,0.25) 0%, rgba(255,255,255,0.15) 100%);
        border-left-color: #ffd700;
        color: #ffd700;
        font-weight: 800;
        text-shadow: 0 0 10px rgba(255,215,0,0.5);
    }
    
    .mobile-menu-item-icon {
        font-size: 1.8rem;
        line-height: 1;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
    }
    
    .mobile-menu-item-label {
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0.8px;
    }
    
    .mobile-menu-footer {
        padding: 20px;
        border-top: 2px solid rgba(255,215,0,0.3);
        margin-top: auto;
    }
    
    .mobile-menu-footer-text {
        background: linear-gradient(90deg, #ffd700 0%, #ffffff 50%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 0.85rem;
        text-align: center;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    @media only screen and (max-width: 768px) {
        .desktop-nav {
            display: none !important;
        }
        
        .hamburger-btn {
            display: block !important;
        }
        
        .mobile-menu {
            display: block !important;
        }
        
        .mobile-menu-overlay {
            display: block !important;
        }
        
        /* Adjust header for mobile with hamburger menu */
        .header-container {
            margin: -80px -20px 20px -20px !important;
            padding: 25px 10px 15px 70px !important;
        }
        
        /* Hide floating auth buttons on mobile */
        [style*="position: fixed"][style*="top: 20px"] {
            display: none !important;
        }
    }
    
    @media only screen and (max-width: 480px) {
        .header-container {
            padding: 20px 5px 10px 65px !important;
        }
        
        .hamburger-btn {
            width: 45px;
            height: 45px;
        }
        
        .mobile-menu {
            width: 260px;
        }
    }
    </style>
    <div class='desktop-nav'>
    """, unsafe_allow_html=True)
    
    # Navigation columns
    nav_cols = st.columns([0.5, 1, 1, 1, 1, 1, 1, 0.5])
    
    # Skip first spacer column
    menu_items = [
        ("🏠 Dashboard", 0),
        ("🎨 Generate", 1),
        ("✨ Editor", 2),
        ("🖼️ Lifestyle", 3),
        ("🎨 Fill", 4),
        ("✂️ Erase", 5)
    ]
    
    for idx, (name, page) in enumerate(menu_items):
        with nav_cols[idx + 1]:  # Skip first spacer
            is_active = st.session_state.get('current_page', 0) == page
            
            if is_active:
                if st.button(name, key=f"nav_{idx}", use_container_width=True, type="primary"):
                    st.session_state.current_page = page
                    st.query_params.update({'page': str(page)})
                    st.rerun()
            else:
                if st.button(name, key=f"nav_{idx}", use_container_width=True):
                    st.session_state.current_page = page
                    st.query_params.update({'page': str(page)})
                    st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Mobile Hamburger Menu
    current_page = st.session_state.get('current_page', 0)
    mobile_menu_items = [
        ("🏠", "Dashboard", 0),
        ("🎨", "Generate", 1),
        ("✨", "Editor", 2),
        ("🖼️", "Lifestyle", 3),
        ("🎨", "Fill", 4),
        ("✂️", "Erase", 5)
    ]
    
    # Create hamburger menu HTML
    mobile_menu_html = '''
    <button class="hamburger-btn" onclick="toggleMobileMenu()">
        <div class="hamburger-icon">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </button>
    
    <div class="mobile-menu-overlay" onclick="toggleMobileMenu()"></div>
    
    <div class="mobile-menu">
        <div class="mobile-menu-header">
            <div class="mobile-menu-logo">🎨</div>
            <div class="mobile-menu-title">ADSNAP</div>
        </div>
        <div class="mobile-menu-items">
    '''
    
    for icon, label, page_num in mobile_menu_items:
        active_class = "active" if current_page == page_num else ""
        mobile_menu_html += f'''
        <a href="?page={page_num}" class="mobile-menu-item {active_class}">
            <div class="mobile-menu-item-icon">{icon}</div>
            <div class="mobile-menu-item-label">{label}</div>
        </a>
        '''
    
    mobile_menu_html += '''
        </div>
        <div class="mobile-menu-footer">
            <div class="mobile-menu-footer-text">AI-Powered Image Generation</div>
        </div>
    </div>
    
    <script>
    function toggleMobileMenu() {
        const menu = document.querySelector('.mobile-menu');
        const overlay = document.querySelector('.mobile-menu-overlay');
        menu.classList.toggle('active');
        overlay.classList.toggle('active');
    }
    </script>
    '''
    
    st.markdown(mobile_menu_html, unsafe_allow_html=True)
    
    # Auth buttons in top-right corner (floating)
    st.markdown("""
    <div style="position: fixed; top: 20px; right: 30px; z-index: 1000; display: flex; gap: 10px;">
    </div>
    """, unsafe_allow_html=True)
    
    # Create a container for auth buttons
    # Auth buttons in top-right (floating)
    auth_container = st.container()
    with auth_container:
        col_spacer, col_auth = st.columns([8, 2])
        with col_auth:
            user_info = st.session_state.get('user_info', {})
            username = st.session_state.get('username', 'User')
            is_demo = username == 'demo_user'
            
            if is_demo:
                auth_cols = st.columns(2)
                with auth_cols[0]:
                    if st.button("🔑", key="float_login", help="Login", use_container_width=True):
                        logout()
                with auth_cols[1]:
                    if st.button("✨", key="float_signup", help="Sign Up", use_container_width=True, type="primary"):
                        logout()
            else:
                if st.button(f"👤 {username[:8]}", key="float_profile", use_container_width=True):
                    st.session_state.show_profile_menu = not st.session_state.get('show_profile_menu', False)
    
    st.markdown("---")
    
    
    # Sidebar for API key and additional settings
    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input("API Key:", value=st.session_state.api_key if st.session_state.api_key else "", type="password")
        if api_key:
            st.session_state.api_key = api_key
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        if st.session_state.get('user_info'):
            st.metric("Account Type", "Premium" if st.session_state.get('username') != 'demo_user' else "Demo")
            st.metric("Images Generated", st.session_state.get('images_generated', 0))
        
        st.markdown("---")
        st.markdown("### 🔗 Quick Links")
        st.markdown("- [📖 Documentation](https://github.com)")
        st.markdown("- [💡 Tutorials](https://github.com)")
        st.markdown("- [🐛 Report Bug](https://github.com)")
        st.markdown("- [⭐ Rate Us](https://github.com)")

    # Main navigation (hidden, controlled by menu bar)
    tab_names = [
        "🏠 Dashboard",
        "🎨 Generate Image",
        "✨ Image Editor",
        "🖼️ Lifestyle Shot",
        "🎨 Generative Fill",
        "🎨 Erase Elements"
    ]
    
    # Handle quick actions from dashboard - use session state for navigation
    if 'current_page' not in st.session_state:
        # Try to restore current page from query params
        query_params = st.query_params
        if 'page' in query_params:
            try:
                st.session_state.current_page = int(query_params['page'])
            except (ValueError, TypeError):
                st.session_state.current_page = 0
        else:
            st.session_state.current_page = 0
    
    # Check if a quick action was triggered
    if st.session_state.get('active_tab') is not None:
        st.session_state.current_page = st.session_state.active_tab
        # Update query params to persist current page
        current_params = dict(st.query_params)
        current_params['page'] = str(st.session_state.active_tab)
        st.query_params.update(current_params)
        st.session_state.active_tab = None  # Reset after use
    
    # Display content based on selected page
    if st.session_state.current_page == 0:  # Dashboard
        if st.session_state.get('tour_completed', True):
            show_dashboard()
        else:
            show_feature_tour()
    
    elif st.session_state.current_page == 1:  # Generate Images
        st.header("Generate Images")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            # Prompt input
            prompt = st.text_area("Enter your prompt", 
                                value="",
                                height=100,
                                key="prompt_input")
            
            # Enhanced prompt display
            if st.session_state.get('enhanced_prompt'):
                st.markdown("**Enhanced Prompt:**")
                st.markdown(f"*{st.session_state.enhanced_prompt}*")
            
            # Enhance Prompt button
            if st.button("✨ Enhance Prompt", key="enhance_button"):
                if not prompt:
                    st.warning("Please enter a prompt to enhance.")
                else:
                    with st.spinner("Enhancing prompt..."):
                        try:
                            result = enhance_prompt(st.session_state.api_key, prompt)
                            if result:
                                st.session_state.enhanced_prompt = result
                                st.success("Prompt enhanced!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error enhancing prompt: {str(e)}")
        
        with col2:
            num_images = st.slider("Number of images", 1, 4, 1)
            aspect_ratio = st.selectbox("Aspect ratio", ["1:1", "16:9", "9:16", "4:3", "3:4"])
            enhance_img = st.checkbox("Enhance image quality", value=True)
            
            # Style options
            st.subheader("Style Options")
            style = st.selectbox("Image Style", [
                "Realistic", "Artistic", "Cartoon", "Sketch", 
                "Watercolor", "Oil Painting", "Digital Art"
            ])
        
        # Generate button
        if st.button("🎨 Generate Images", type="primary"):
            if not st.session_state.api_key:
                st.error("Please enter your API key in the sidebar.")
                return
            
            # Track activity
            track_current_activity(
                "image_generation", 
                f"Generated image with prompt: '{prompt[:50]}...'",
                {
                    "prompt": prompt,
                    "num_images": num_images,
                    "aspect_ratio": aspect_ratio,
                    "style": style,
                    "enhance_image": enhance_img
                }
            )
                
            with st.spinner("🎨 Generating your masterpiece..."):
                try:
                    result = generate_hd_image(
                        prompt=st.session_state.enhanced_prompt or prompt,
                        api_key=st.session_state.api_key,
                        num_results=num_images,
                        aspect_ratio=aspect_ratio if aspect_ratio is not None else "1:1",
                        sync=True,
                        enhance_image=enhance_img,
                        medium="art" if style != "Realistic" else "photography",
                        prompt_enhancement=False,
                        content_moderation=True
                    )
                    
                    if result:
                        if isinstance(result, dict):
                            # Store multiple images in a list
                            generated_images = []
                            
                            # Bria API returns results in 'result' array when sync=True
                            # Format: {"result": [{"urls": ["url1"]}, {"urls": ["url2"]}]}
                            if "result" in result and isinstance(result["result"], list):
                                for item in result["result"]:
                                    if isinstance(item, dict) and "urls" in item:
                                        # Each result item has 'urls' array - take the first URL from each
                                        if isinstance(item["urls"], list) and len(item["urls"]) > 0:
                                            generated_images.append(item["urls"][0])
                                        elif isinstance(item["urls"], str):
                                            generated_images.append(item["urls"])
                            
                            # Fallback: check for other possible formats
                            elif "result_url" in result:
                                generated_images.append(result["result_url"])
                            elif "result_urls" in result:
                                if isinstance(result["result_urls"], list):
                                    generated_images = result["result_urls"]
                                else:
                                    generated_images.append(result["result_urls"])
                            elif "url" in result:
                                generated_images.append(result["url"])
                            
                            if generated_images:
                                st.session_state.generated_images = generated_images
                                st.session_state.edited_image = None  # Clear single image
                                st.success(f"✨ {len(generated_images)} image(s) generated successfully!")
                                st.rerun()  # Force rerun to display images
                            else:
                                st.error("❌ No images found in API response.")
                        else:
                            st.error("❌ Invalid API response format.")
                            
                except Exception as e:
                    st.error(f"Error generating images: {str(e)}")
        
        # Display generated images if available
        if st.session_state.get('generated_images') and len(st.session_state.generated_images) > 0:
            st.markdown("### 🖼️ Generated Images")
            
            # Display images in a collage based on count
            num_imgs = len(st.session_state.generated_images)
            
            if num_imgs == 1:
                # Single image - full width
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.image(st.session_state.generated_images[0], caption="Generated Image 1", use_column_width=True)
                with col2:
                    image_data = download_image(st.session_state.generated_images[0])
                    if image_data:
                        st.download_button(
                            "⬇️ Download",
                            image_data,
                            "generated_image_1.png",
                            "image/png",
                            use_container_width=True
                        )
            
            elif num_imgs == 2:
                # Two images side by side
                cols = st.columns(2)
                for idx, img_url in enumerate(st.session_state.generated_images):
                    with cols[idx]:
                        st.image(img_url, caption=f"Generated Image {idx + 1}", use_column_width=True)
                        image_data = download_image(img_url)
                        if image_data:
                            st.download_button(
                                f"⬇️ Download {idx + 1}",
                                image_data,
                                f"generated_image_{idx + 1}.png",
                                "image/png",
                                use_container_width=True,
                                key=f"download_{idx}"
                            )
            
            elif num_imgs == 3:
                # Three images - 2 on top, 1 on bottom
                cols_top = st.columns(2)
                for idx in range(2):
                    with cols_top[idx]:
                        st.image(st.session_state.generated_images[idx], caption=f"Generated Image {idx + 1}", use_column_width=True)
                        image_data = download_image(st.session_state.generated_images[idx])
                        if image_data:
                            st.download_button(
                                f"⬇️ Download {idx + 1}",
                                image_data,
                                f"generated_image_{idx + 1}.png",
                                "image/png",
                                use_container_width=True,
                                key=f"download_{idx}"
                            )
                
                # Bottom image centered
                col_left, col_center, col_right = st.columns([1, 2, 1])
                with col_center:
                    st.image(st.session_state.generated_images[2], caption="Generated Image 3", use_column_width=True)
                    image_data = download_image(st.session_state.generated_images[2])
                    if image_data:
                        st.download_button(
                            "⬇️ Download 3",
                            image_data,
                            "generated_image_3.png",
                            "image/png",
                            use_container_width=True,
                            key="download_2"
                        )
            
            else:  # 4 images
                # Four images in 2x2 grid
                cols_top = st.columns(2)
                for idx in range(2):
                    with cols_top[idx]:
                        st.image(st.session_state.generated_images[idx], caption=f"Generated Image {idx + 1}", use_column_width=True)
                        image_data = download_image(st.session_state.generated_images[idx])
                        if image_data:
                            st.download_button(
                                f"⬇️ Download {idx + 1}",
                                image_data,
                                f"generated_image_{idx + 1}.png",
                                "image/png",
                                use_container_width=True,
                                key=f"download_{idx}"
                            )
                
                cols_bottom = st.columns(2)
                for idx in range(2, 4):
                    with cols_bottom[idx - 2]:
                        st.image(st.session_state.generated_images[idx], caption=f"Generated Image {idx + 1}", use_column_width=True)
                        image_data = download_image(st.session_state.generated_images[idx])
                        if image_data:
                            st.download_button(
                                f"⬇️ Download {idx + 1}",
                                image_data,
                                f"generated_image_{idx + 1}.png",
                                "image/png",
                                use_container_width=True,
                                key=f"download_{idx}"
                            )
            
            # Clear all images button
            st.markdown("---")
            if st.button("🗑️ Clear All Images", use_container_width=False):
                st.session_state.generated_images = []
                st.session_state.edited_image = None
                st.rerun()
        
        # Fallback for old single image format (backward compatibility)
        elif st.session_state.get('edited_image'):
            st.markdown("### 🖼️ Generated Image")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.image(st.session_state.edited_image, caption="Generated Image", use_column_width=True)
            
            with col2:
                # Download button
                image_data = download_image(st.session_state.edited_image)
                if image_data:
                    st.download_button(
                        "⬇️ Download Image",
                        image_data,
                        "generated_image.png",
                        "image/png",
                        use_container_width=True
                    )
                
                # Clear image button
                if st.button("🗑️ Clear Image", use_container_width=True):
                    st.session_state.edited_image = None
                    st.rerun()
    
    elif st.session_state.current_page == 2:  # Image Editor - All-in-One
        st.markdown("### ✨ Image Editor")
        st.markdown("Upload an image and apply any editing feature")
        
        # Upload image
        uploaded_file = st.file_uploader(
            "📤 Upload Image to Edit",
            type=["png", "jpg", "jpeg"],
            key="unified_editor_upload"
        )
        
        if uploaded_file:
            # Store uploaded image in session state
            if 'editor_image' not in st.session_state or st.session_state.get('editor_image_name') != uploaded_file.name:
                st.session_state.editor_image = uploaded_file.getvalue()
                st.session_state.editor_image_name = uploaded_file.name
                st.session_state.editor_result = None
            
            # Display original image
            st.markdown("---")
            col_img, col_tools = st.columns([2, 1])
            
            with col_img:
                st.markdown("#### 🖼️ Your Image")
                img = Image.open(io.BytesIO(st.session_state.editor_image))
                st.image(img, use_column_width=True)
                
                # Show result if available
                if st.session_state.get('editor_result'):
                    st.markdown("#### ✨ Result")
                    st.image(st.session_state.editor_result, use_column_width=True)
                    
                    # Download result
                    result_data = download_image(st.session_state.editor_result)
                    if result_data:
                        st.download_button(
                            "⬇️ Download Result",
                            result_data,
                            "edited_image.png",
                            "image/png",
                            use_container_width=True
                        )
            
            with col_tools:
                st.markdown("#### 🛠️ Editing Tools")
                
                edit_feature = st.selectbox(
                    "Choose Feature",
                    [
                        "🎯 Create Packshot",
                        "🌟 Add Shadow",
                        "🎨 Generative Fill",
                        "🗑️ Erase Foreground",
                        "✂️ Remove Background"
                    ]
                )
                
                st.markdown("---")
                
                # Feature-specific options
                if edit_feature == "🎯 Create Packshot":
                    st.markdown("**Packshot Settings**")
                    bg_color = st.color_picker("Background Color", "#FFFFFF")
                    force_rmbg = st.checkbox("Force Background Removal", False)
                    
                    if st.button("🎯 Create Packshot", type="primary", use_container_width=True):
                        if not st.session_state.api_key:
                            st.error("Please enter your API key")
                        else:
                            with st.spinner("Creating packshot..."):
                                try:
                                    result = create_packshot(
                                        st.session_state.api_key,
                                        st.session_state.editor_image,
                                        background_color=bg_color,
                                        force_rmbg=force_rmbg
                                    )
                                    if result and "result_url" in result:
                                        st.session_state.editor_result = result["result_url"]
                                        st.success("✨ Packshot created!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                
                elif edit_feature == "🌟 Add Shadow":
                    st.markdown("**Shadow Settings**")
                    shadow_type = st.selectbox("Shadow Type", ["Natural", "Drop"])
                    shadow_intensity = st.slider("Intensity", 0, 100, 60)
                    bg_color = st.color_picker("Background Color", "#FFFFFF", key="shadow_bg")
                    
                    if st.button("🌟 Add Shadow", type="primary", use_container_width=True):
                        if not st.session_state.api_key:
                            st.error("Please enter your API key")
                        else:
                            with st.spinner("Adding shadow..."):
                                try:
                                    result = add_shadow(
                                        api_key=st.session_state.api_key,
                                        image_data=st.session_state.editor_image,
                                        shadow_type=shadow_type.lower(),
                                        background_color=bg_color,
                                        shadow_intensity=shadow_intensity
                                    )
                                    if result and "result_url" in result:
                                        st.session_state.editor_result = result["result_url"]
                                        st.success("✨ Shadow added!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                
                elif edit_feature == "🎨 Generative Fill":
                    st.markdown("**Generative Fill**")
                    st.info("Upload a mask image below")
                    
                    mask_file = st.file_uploader(
                        "Mask (white = fill)",
                        type=["png", "jpg", "jpeg"],
                        key="editor_mask"
                    )
                    
                    fill_prompt = st.text_area(
                        "Describe fill content",
                        placeholder="e.g., 'blue sky', 'grass'",
                        height=80
                    )
                    
                    if mask_file and st.button("🎨 Generate Fill", type="primary", use_container_width=True):
                        if not st.session_state.api_key:
                            st.error("Please enter your API key")
                        elif not fill_prompt:
                            st.warning("Please enter a prompt")
                        else:
                            with st.spinner("Generating fill..."):
                                try:
                                    result = generative_fill(
                                        api_key=st.session_state.api_key,
                                        image_data=st.session_state.editor_image,
                                        mask_data=mask_file.getvalue(),
                                        prompt=fill_prompt,
                                        sync=True
                                    )
                                    if result and "result_url" in result:
                                        st.session_state.editor_result = result["result_url"]
                                        st.success("✨ Fill generated!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                
                elif edit_feature == "🗑️ Erase Foreground":
                    st.markdown("**Erase Foreground**")
                    st.info("Automatically removes foreground objects")
                    
                    if st.button("🗑️ Erase Foreground", type="primary", use_container_width=True):
                        if not st.session_state.api_key:
                            st.error("Please enter your API key")
                        else:
                            with st.spinner("Erasing foreground..."):
                                try:
                                    result = erase_foreground(
                                        api_key=st.session_state.api_key,
                                        image_data=st.session_state.editor_image
                                    )
                                    if result and "result_url" in result:
                                        st.session_state.editor_result = result["result_url"]
                                        st.success("✨ Foreground erased!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                
                elif edit_feature == "✂️ Remove Background":
                    st.markdown("**Remove Background**")
                    st.info("Creates transparent background")
                    
                    if st.button("✂️ Remove Background", type="primary", use_container_width=True):
                        st.info("This feature uses the packshot API with transparent background")
                        if not st.session_state.api_key:
                            st.error("Please enter your API key")
                        else:
                            with st.spinner("Removing background..."):
                                try:
                                    result = create_packshot(
                                        st.session_state.api_key,
                                        st.session_state.editor_image,
                                        background_color="transparent",
                                        force_rmbg=True
                                    )
                                    if result and "result_url" in result:
                                        st.session_state.editor_result = result["result_url"]
                                        st.success("✨ Background removed!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                
                # Clear result button
                if st.session_state.get('editor_result'):
                    st.markdown("---")
                    if st.button("🔄 Clear Result", use_container_width=True):
                        st.session_state.editor_result = None
                        st.rerun()
        
        else:
            st.info("👆 Upload an image to start editing")
            
            # Show feature preview cards
            st.markdown("### Available Features")
            cols = st.columns(3)
            
            with cols[0]:
                st.markdown("""
                **🎯 Create Packshot**
                - Professional product photos
                - Custom backgrounds
                - Auto background removal
                """)
            
            with cols[1]:
                st.markdown("""
                **🌟 Add Shadow**
                - Natural shadows
                - Drop shadows
                - Adjustable intensity
                """)
            
            with cols[2]:
                st.markdown("""
                **🎨 Generative Fill**
                - Fill masked areas
                - AI-powered content
                - Custom prompts
                """)
            
            cols2 = st.columns(2)
            with cols2[0]:
                st.markdown("""
                **🗑️ Erase Foreground**
                - Auto object removal
                - Background generation
                """)
            
            with cols2[1]:
                st.markdown("""
                **✂️ Remove Background**
                - Transparent background
                - Clean cutouts
                """)
    
    elif st.session_state.current_page == 3:  # Lifestyle Shot
        st.markdown("### 📸 Lifestyle Shot")
        st.markdown("Transform your product images into professional lifestyle shots")
        
        uploaded_file = enhanced_file_uploader(
            "Upload Product Image", 
            ["png", "jpg", "jpeg"], 
            "Drag and drop your product image here, or click to browse",
            "product_upload"
        )
        
        if uploaded_file:
            # Track file upload activity
            track_current_activity(
                "feature_usage",
                "Uploaded product image",
                {
                    "file_name": uploaded_file.name,
                    "file_size": uploaded_file.size,
                    "file_type": uploaded_file.type
                }
            )
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(uploaded_file, caption="Original Image", use_column_width=True)
                
                # Product editing options
                edit_option = st.selectbox("Select Edit Option", [
                    "Create Packshot",
                    "Add Shadow",
                    "Lifestyle Shot"
                ])
                
                if edit_option == "Create Packshot":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        bg_color = st.color_picker("Background Color", "#FFFFFF")
                        sku = st.text_input("SKU (optional)", "")
                    with col_b:
                        force_rmbg = st.checkbox("Force Background Removal", False)
                        content_moderation = st.checkbox("Enable Content Moderation", False)
                    
                    if st.button("🎯 Create Packshot", type="primary"):
                        # Track activity
                        track_current_activity(
                            "image_editing",
                            "Created packshot",
                            {
                                "edit_type": "packshot",
                                "background_color": bg_color,
                                "force_rmbg": force_rmbg
                            }
                        )
                        
                        with st.spinner("Creating professional packshot..."):
                            try:
                                result = create_packshot(
                                    st.session_state.api_key,
                                    uploaded_file.getvalue(),
                                    background_color=bg_color,
                                    sku=sku if sku else None,
                                    force_rmbg=force_rmbg,
                                    content_moderation=content_moderation
                                )
                                
                                if result and "result_url" in result:
                                    st.success("✨ Packshot created successfully!")
                                    st.session_state.edited_image = result["result_url"]
                                else:
                                    st.error("No result URL in the API response. Please try again.")
                            except Exception as e:
                                st.error(f"Error creating packshot: {str(e)}")
                
                elif edit_option == "Add Shadow":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        shadow_type = st.selectbox("Shadow Type", ["Natural", "Drop"])
                        bg_color = st.color_picker("Background Color", "#FFFFFF")
                        shadow_color = st.color_picker("Shadow Color", "#000000")
                    with col_b:
                        shadow_intensity = st.slider("Shadow Intensity", 0, 100, 60)
                        force_rmbg = st.checkbox("Force Background Removal", False)
                        content_moderation = st.checkbox("Enable Content Moderation", False)
                    
                    if st.button("🌟 Add Shadow", type="primary"):
                        # Track activity
                        track_current_activity(
                            "image_editing",
                            "Added shadow effect",
                            {
                                "edit_type": "shadow",
                                "shadow_type": shadow_type,
                                "shadow_intensity": shadow_intensity
                            }
                        )
                        
                        with st.spinner("Adding shadow effect..."):
                            try:
                                result = add_shadow(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    shadow_type=shadow_type.lower(),
                                    background_color=bg_color,
                                    shadow_color=shadow_color,
                                    shadow_intensity=shadow_intensity,
                                    force_rmbg=force_rmbg,
                                    content_moderation=content_moderation
                                )
                                
                                if result and "result_url" in result:
                                    st.success("✨ Shadow added successfully!")
                                    st.session_state.edited_image = result["result_url"]
                                else:
                                    st.error("No result URL in the API response. Please try again.")
                            except Exception as e:
                                st.error(f"Error adding shadow: {str(e)}")
            
            with col2:
                if st.session_state.edited_image:
                    st.image(st.session_state.edited_image, caption="Edited Image", use_column_width=True)
                    image_data = download_image(st.session_state.edited_image)
                    if image_data:
                        st.download_button(
                            "⬇️ Download Result",
                            image_data,
                            "edited_product.png",
                            "image/png"
                        )
    
    elif st.session_state.current_page == 4:  # Generative Fill
        st.markdown("### 🎨 Generative Fill")
        st.markdown("Upload an image, create a mask, and fill areas with AI-generated content")
        
        # Upload image
        uploaded_file = st.file_uploader(
            "📤 Upload Image to Edit",
            type=["png", "jpg", "jpeg"],
            key="generative_fill_image"
        )
        
        if uploaded_file:
            # Store image in session state
            if 'gf_uploaded_image' not in st.session_state or st.session_state.get('gf_image_name') != uploaded_file.name:
                st.session_state.gf_uploaded_image = uploaded_file.getvalue()
                st.session_state.gf_image_name = uploaded_file.name
                st.session_state.generative_fill_result = None
            # Open and display the image
            img = Image.open(io.BytesIO(st.session_state.gf_uploaded_image))
            
            st.markdown("---")
            
            # Three-column layout
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown("#### 🖼️ Original Image")
                st.image(img, use_column_width=True)
                
                # Download button for creating mask externally
                st.download_button(
                    "⬇️ Download Image (to create mask)",
                    st.session_state.gf_uploaded_image,
                    f"original_{st.session_state.gf_image_name}",
                    "image/png",
                    help="Download to create a mask in Paint/Photoshop"
                )
            
            with col2:
                st.markdown("#### 🎭 Create Mask")
                
                # Mask creation method
                mask_method = st.radio(
                    "Choose method:",
                    ["✏️ Draw on Page", "📤 Upload Mask"],
                    horizontal=True,
                    key="gf_mask_method"
                )
                
                if mask_method == "✏️ Draw on Page":
                    st.info("💡 Click on the image below to draw. Each click adds a brush stroke at that position.")
                    
                    # Initialize mask in session state
                    if 'gf_mask_image' not in st.session_state or st.session_state.get('gf_current_image') != st.session_state.gf_image_name:
                        # Create blank mask (black background)
                        st.session_state.gf_mask_image = Image.new('L', img.size, 0)  # Grayscale, black
                        st.session_state.gf_current_image = st.session_state.gf_image_name
                    
                    from PIL import ImageDraw
                    
                    # Drawing tools
                    st.markdown("**🎨 Drawing Tools**")
                    tool_cols = st.columns(4)
                    with tool_cols[0]:
                        brush_size = st.slider("Brush Size", 10, 150, 50, step=10, key="gf_brush_size")
                    with tool_cols[1]:
                        draw_color = st.radio("Draw", ["⚪ White (Fill)", "⚫ Black (Keep)"], key="gf_draw_color", horizontal=True)
                    with tool_cols[2]:
                        if st.button("🗑️ Clear Mask", use_container_width=True, key="gf_clear_mask"):
                            st.session_state.gf_mask_image = Image.new('L', img.size, 0)
                            st.rerun()
                    with tool_cols[3]:
                        if st.button("⚡ Fill All", use_container_width=True, key="gf_fill_all"):
                            color = 255 if "White" in draw_color else 0
                            st.session_state.gf_mask_image = Image.new('L', img.size, color)
                            st.rerun()
                    
                    st.markdown("---")
                    st.markdown("**🖱️ Click on Image to Draw**")
                    
                    # Try to use streamlit-image-coordinates for click-based drawing
                    try:
                        from streamlit_image_coordinates import streamlit_image_coordinates
                        
                        # Create composite image showing mask overlay
                        mask_rgb = st.session_state.gf_mask_image.convert('RGB')
                        # Create semi-transparent overlay
                        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
                        mask_overlay = Image.new('RGBA', img.size, (255, 255, 255, 128))
                        
                        # Apply mask as overlay
                        for x in range(img.width):
                            for y in range(img.height):
                                if st.session_state.gf_mask_image.getpixel((x, y)) > 128:
                                    overlay.putpixel((x, y), (255, 255, 255, 128))
                        
                        # Composite image
                        display_img = img.convert('RGBA')
                        display_img = Image.alpha_composite(display_img, overlay)
                        
                        # Get click coordinates
                        value = streamlit_image_coordinates(display_img, key="gf_image_click")
                        
                        if value is not None and value.get("x") is not None:
                            # Draw on mask at clicked position
                            draw = ImageDraw.Draw(st.session_state.gf_mask_image)
                            color = 255 if "White" in draw_color else 0
                            x, y = value["x"], value["y"]
                            
                            # Draw circle (brush stroke)
                            draw.ellipse(
                                [x - brush_size//2, y - brush_size//2,
                                 x + brush_size//2, y + brush_size//2],
                                fill=color
                            )
                            st.rerun()
                    
                    except ImportError:
                        # Fallback if streamlit-image-coordinates not available
                        st.warning("⚠️ Interactive drawing requires 'streamlit-image-coordinates' package. Using alternative method.")
                        
                        # Show image with current mask overlay
                        mask_rgb = st.session_state.gf_mask_image.convert('RGB')
                        blended = Image.blend(img.convert('RGB'), mask_rgb, alpha=0.4)
                        st.image(blended, caption="Current Mask (White = Fill, Black = Keep)", use_column_width=True)
                        
                        # Manual coordinate input
                        st.markdown("**Manual Drawing:**")
                        coord_cols = st.columns(3)
                        with coord_cols[0]:
                            click_x = st.number_input("X Position", 0, img.width-1, img.width//2, key="gf_manual_x")
                        with coord_cols[1]:
                            click_y = st.number_input("Y Position", 0, img.height-1, img.height//2, key="gf_manual_y")
                        with coord_cols[2]:
                            if st.button("🖌️ Draw Here", key="gf_manual_draw", use_container_width=True):
                                draw = ImageDraw.Draw(st.session_state.gf_mask_image)
                                color = 255 if "White" in draw_color else 0
                                draw.ellipse(
                                    [click_x - brush_size//2, click_y - brush_size//2,
                                     click_x + brush_size//2, click_y + brush_size//2],
                                    fill=color
                                )
                                st.rerun()
                    
                    # Show pure mask
                    with st.expander("🔍 View Pure Mask"):
                        st.image(st.session_state.gf_mask_image, caption="Pure Mask", use_column_width=True)
                    
                    # Convert mask to file for API
                    mask_buffer = io.BytesIO()
                    st.session_state.gf_mask_image.save(mask_buffer, format='PNG')
                    mask_file = mask_buffer.getvalue()
                    
                else:  # Upload Mask
                    st.info("💡 Upload a mask: **white areas** = fill with AI, **black areas** = keep original")
                    
                    mask_file_upload = st.file_uploader(
                        "Upload Mask Image",
                        type=["png", "jpg", "jpeg"],
                        key="generative_fill_mask_upload",
                        help="White = areas to fill, Black = areas to keep"
                    )
                    
                    if mask_file_upload:
                        mask_img = Image.open(mask_file_upload)
                        st.image(mask_img, caption="Your Mask", use_column_width=True)
                        mask_file = mask_file_upload.getvalue()
                    else:
                        st.markdown("""
                        **How to create a mask:**
                        1. Download the image from left
                        2. Open in Paint/Photoshop/GIMP
                        3. Paint WHITE where you want AI to fill
                        4. Keep BLACK where you want original
                        5. Save and upload here
                        """)
                        mask_file = None
            
            with col3:
                st.markdown("#### ⚙️ Settings")
                
                prompt = st.text_area(
                    "What to fill",
                    placeholder="e.g., 'blue sky', 'grass', 'ocean'",
                    height=100,
                    key="gf_prompt"
                )
                
                sync_mode = st.checkbox("Wait for result", value=True, key="gf_sync")
                
                st.markdown("---")
            
            # Show result below
            if st.session_state.get('generative_fill_result'):
                st.markdown("---")
                st.markdown("### ✨ Result")
                
                result_cols = st.columns([2, 2, 1])
                with result_cols[0]:
                    st.image(img, caption="Original", use_column_width=True)
                with result_cols[1]:
                    st.image(st.session_state.generative_fill_result, caption="Generated", use_column_width=True)
                with result_cols[2]:
                    # Download button
                    result_data = download_image(st.session_state.generative_fill_result)
                    if result_data:
                        st.download_button(
                            "⬇️ Download Result",
                            result_data,
                            "generative_fill_result.png",
                            "image/png",
                            use_container_width=True
                        )
                    
                    if st.button("🔄 New Edit", use_container_width=True):
                        st.session_state.generative_fill_result = None
                        st.rerun()
            
            # Generate button
            st.markdown("---")
            
            # Check if we have a mask (either drawn or uploaded)
            has_mask = False
            mask_data = None
            
            if mask_method == "✏️ Draw on Page":
                if 'gf_mask_image' in st.session_state:
                    has_mask = True
                    mask_data = mask_file
            else:  # Upload method
                if mask_file is not None:
                    has_mask = True
                    mask_data = mask_file
            
            if has_mask and mask_data:
                if st.button("🎨 Generate Fill", type="primary", use_container_width=True, key="gf_generate"):
                    if not prompt:
                        st.warning("⚠️ Please enter a prompt describing what to fill")
                    elif not st.session_state.api_key:
                        st.error("❌ Please enter your API key in the sidebar")
                    else:
                        with st.spinner("🎨 Generating fill content..."):
                            try:
                                result = generative_fill(
                                    api_key=st.session_state.api_key,
                                    image_data=st.session_state.gf_uploaded_image,
                                    mask_data=mask_data,
                                    prompt=prompt,
                                    num_results=1,
                                    sync=sync_mode
                                )
                                
                                if result and "result_url" in result:
                                    st.session_state.generative_fill_result = result["result_url"]
                                    st.success("✨ Generative fill completed!")
                                    st.rerun()
                                elif result and "result" in result and isinstance(result["result"], list):
                                    if len(result["result"]) > 0 and "urls" in result["result"][0]:
                                        st.session_state.generative_fill_result = result["result"][0]["urls"][0]
                                        st.success("✨ Generative fill completed!")
                                        st.rerun()
                                else:
                                    st.error("❌ No result URL in API response")
                                    with st.expander("🔍 Debug: API Response"):
                                        st.json(result)
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
            else:
                if mask_method == "✏️ Draw on Page":
                    st.info("👆 **Step 1:** Draw white areas on the mask\n\n**Step 2:** Enter a prompt\n\n**Step 3:** Click 'Generate Fill'")
                else:
                    st.info("👆 **Step 1:** Upload a mask image above\n\n**Step 2:** Enter a prompt\n\n**Step 3:** Click 'Generate Fill'")
        
        else:
            st.info("👆 Upload an image to start")
            
            # Show example
            st.markdown("### 📖 How it Works")
            cols = st.columns(3)
            with cols[0]:
                st.markdown("**1️⃣ Upload Image**\nUpload the image you want to edit")
            with cols[1]:
                st.markdown("**2️⃣ Create Mask**\nDraw or upload a mask (white = fill area)")
            with cols[2]:
                st.markdown("**3️⃣ Generate**\nDescribe what to fill and generate!")
    
    elif st.session_state.current_page == 5:  # Erase Elements
        st.markdown("### ✂️ Erase Elements")
        st.markdown("Mark areas to erase with arrows, then remove them with AI")
        
        # Method selection
        erase_method = st.radio(
            "Choose erase method:",
            ["🤖 Automatic (AI detects foreground)", "✏️ Manual (Draw mask to erase)"],
            horizontal=True
        )
        
        if erase_method == "🤖 Automatic (AI detects foreground)":
            st.info("💡 This feature automatically detects and removes foreground objects, generating the background behind them.")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                uploaded_file = st.file_uploader(
                    "Upload Image",
                    type=["png", "jpg", "jpeg"],
                    key="erase_image_auto"
                )
            
            with col2:
                st.markdown("#### ⚙️ Settings")
                content_mod = st.checkbox("Enable content moderation", value=True, key="erase_content_mod")
            
            if uploaded_file:
                st.markdown("---")
                st.markdown("### 🖼️ Preview")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    img = Image.open(uploaded_file)
                    st.image(img, caption="Original Image", use_column_width=True)
                
                with col_b:
                    if st.session_state.get('erase_result'):
                        st.image(st.session_state.erase_result, caption="Foreground Removed", use_column_width=True)
                        
                        # Download button
                        image_data = download_image(st.session_state.erase_result)
                        if image_data:
                            st.download_button(
                                "⬇️ Download Result",
                                image_data,
                                "erase_result.png",
                                "image/png",
                                use_container_width=True
                            )
                    else:
                        st.info("Result will appear here after processing")
                
                st.markdown("---")
                
                if st.button("🗑️ Remove Foreground Objects", type="primary", use_container_width=True):
                    if not st.session_state.api_key:
                        st.error("Please enter your API key in the sidebar")
                    else:
                        with st.spinner("🗑️ Removing foreground objects..."):
                            try:
                                result = erase_foreground(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    content_moderation=content_mod
                                )
                                
                                if result and "result_url" in result:
                                    st.session_state.erase_result = result["result_url"]
                                    st.success("✨ Foreground objects removed successfully!")
                                    st.rerun()
                                else:
                                    st.error("No result URL in API response")
                                    with st.expander("Debug: API Response"):
                                        st.json(result)
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            else:
                st.info("👆 Please upload an image to get started")
        
        else:  # Manual mask drawing with cursor
            st.info("💡 Click on the image below to draw. Each click adds a brush stroke to mark areas for removal.")
            
            uploaded_file = st.file_uploader(
                "Upload Image to Edit",
                type=["png", "jpg", "jpeg"],
                key="erase_image_manual"
            )
            
            if uploaded_file:
                # Store image in session state
                if 'erase_uploaded_image' not in st.session_state or st.session_state.get('erase_image_name') != uploaded_file.name:
                    st.session_state.erase_uploaded_image = uploaded_file.getvalue()
                    st.session_state.erase_image_name = uploaded_file.name
                    st.session_state.erase_manual_result = None
                
                # Open image
                img = Image.open(io.BytesIO(st.session_state.erase_uploaded_image))
                
                st.markdown("---")
                
                # Three-column layout
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown("#### 🖼️ Original Image")
                    st.image(img, use_column_width=True)
                
                with col2:
                    st.markdown("#### 🎭 Draw Mask")
                    st.info("💡 Click on image to draw. White = erase, Black = keep")
                    
                    # Initialize mask
                    if 'erase_mask_image' not in st.session_state or st.session_state.get('erase_current_image') != st.session_state.erase_image_name:
                        st.session_state.erase_mask_image = Image.new('L', img.size, 0)
                        st.session_state.erase_current_image = st.session_state.erase_image_name
                    
                    from PIL import ImageDraw
                    
                    # Drawing tools
                    tool_cols = st.columns(3)
                    with tool_cols[0]:
                        brush_size = st.slider("Brush Size", 10, 150, 50, step=10, key="erase_brush_size")
                    with tool_cols[1]:
                        draw_color = st.radio("Draw", ["⚪ White (Erase)", "⚫ Black (Keep)"], key="erase_draw_color", horizontal=True)
                    with tool_cols[2]:
                        if st.button("🗑️ Clear", use_container_width=True, key="erase_clear_mask"):
                            st.session_state.erase_mask_image = Image.new('L', img.size, 0)
                            st.rerun()
                    
                    # Try cursor-based drawing
                    try:
                        from streamlit_image_coordinates import streamlit_image_coordinates
                        
                        # Create overlay
                        mask_rgb = st.session_state.erase_mask_image.convert('RGB')
                        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
                        
                        for x in range(img.width):
                            for y in range(img.height):
                                if st.session_state.erase_mask_image.getpixel((x, y)) > 128:
                                    overlay.putpixel((x, y), (255, 0, 0, 128))  # Red overlay for erase areas
                        
                        display_img = img.convert('RGBA')
                        display_img = Image.alpha_composite(display_img, overlay)
                        
                        # Get click coordinates
                        value = streamlit_image_coordinates(display_img, key="erase_image_click")
                        
                        if value is not None and value.get("x") is not None:
                            draw = ImageDraw.Draw(st.session_state.erase_mask_image)
                            color = 255 if "White" in draw_color else 0
                            x, y = value["x"], value["y"]
                            
                            draw.ellipse(
                                [x - brush_size//2, y - brush_size//2,
                                 x + brush_size//2, y + brush_size//2],
                                fill=color
                            )
                            st.rerun()
                    
                    except ImportError:
                        # Fallback
                        mask_rgb = st.session_state.erase_mask_image.convert('RGB')
                        blended = Image.blend(img.convert('RGB'), mask_rgb, alpha=0.4)
                        st.image(blended, caption="Current Mask", use_column_width=True)
                        
                        st.markdown("**Manual Drawing:**")
                        coord_cols = st.columns(3)
                        with coord_cols[0]:
                            click_x = st.number_input("X", 0, img.width-1, img.width//2, key="erase_manual_x")
                        with coord_cols[1]:
                            click_y = st.number_input("Y", 0, img.height-1, img.height//2, key="erase_manual_y")
                        with coord_cols[2]:
                            if st.button("🖌️ Draw", key="erase_manual_draw", use_container_width=True):
                                draw = ImageDraw.Draw(st.session_state.erase_mask_image)
                                color = 255 if "White" in draw_color else 0
                                draw.ellipse(
                                    [click_x - brush_size//2, click_y - brush_size//2,
                                     click_x + brush_size//2, click_y + brush_size//2],
                                    fill=color
                                )
                                st.rerun()
                    
                    with st.expander("🔍 View Pure Mask"):
                        st.image(st.session_state.erase_mask_image, caption="Pure Mask", use_column_width=True)
                
                with col3:
                    st.markdown("#### ⚙️ Settings")
                    prompt = st.text_area(
                        "Fill with",
                        placeholder="e.g., 'grass', 'sky'",
                        height=80,
                        key="erase_prompt"
                    )
                    
                    sync_mode = st.checkbox("Wait for result", value=True, key="erase_sync")
                
                # Show result
                if st.session_state.get('erase_manual_result'):
                    st.markdown("---")
                    st.markdown("### ✨ Result")
                    
                    result_cols = st.columns([2, 2, 1])
                    with result_cols[0]:
                        st.image(img, caption="Original", use_column_width=True)
                    with result_cols[1]:
                        st.image(st.session_state.erase_manual_result, caption="Erased", use_column_width=True)
                    with result_cols[2]:
                        result_data = download_image(st.session_state.erase_manual_result)
                        if result_data:
                            st.download_button(
                                "⬇️ Download",
                                result_data,
                                "erase_result.png",
                                "image/png",
                                use_container_width=True
                            )
                        if st.button("🔄 New Edit", use_container_width=True):
                            st.session_state.erase_manual_result = None
                            st.rerun()
                
                # Generate button
                st.markdown("---")
                
                # Convert mask to bytes
                mask_buffer = io.BytesIO()
                st.session_state.erase_mask_image.save(mask_buffer, format='PNG')
                mask_data = mask_buffer.getvalue()
                
                if st.button("🗑️ Erase & Fill", type="primary", use_container_width=True, key="erase_generate"):
                    if not st.session_state.api_key:
                        st.error("❌ Please enter your API key")
                    else:
                        with st.spinner("🗑️ Erasing and filling..."):
                            try:
                                result = generative_fill(
                                    api_key=st.session_state.api_key,
                                    image_data=st.session_state.erase_uploaded_image,
                                    mask_data=mask_data,
                                    prompt=prompt if prompt else "natural background",
                                    num_results=1,
                                    sync=sync_mode
                                )
                                
                                if result and "result_url" in result:
                                    st.session_state.erase_manual_result = result["result_url"]
                                    st.success("✨ Area erased successfully!")
                                    st.rerun()
                                elif result and "result" in result and isinstance(result["result"], list):
                                    if len(result["result"]) > 0 and "urls" in result["result"][0]:
                                        st.session_state.erase_manual_result = result["result"][0]["urls"][0]
                                        st.success("✨ Area erased successfully!")
                                        st.rerun()
                                else:
                                    st.error("❌ No result in API response")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
            else:
                st.info("👆 Upload an image to start")
    


if __name__ == "__main__":
    main()
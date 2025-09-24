import streamlit as st
import time
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

def add_custom_css():
    """Add custom CSS for enhanced UI."""
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --accent-color: #FF6B6B;
        --success-color: #4ECDC4;
        --warning-color: #FFD93D;
        --error-color: #FF6B6B;
        --text-primary: #ffffff;
        --text-secondary: #e0e0e0;
    }
    
    /* Improve text visibility */
    .main .block-container {
        color: var(--text-primary) !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    p, div, span {
        color: var(--text-secondary) !important;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        border: none;
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, var(--secondary-color), var(--primary-color));
    }
    
    /* Primary button style */
    .primary-button > button {
        background: linear-gradient(45deg, var(--accent-color), var(--success-color)) !important;
        color: white !important;
        font-size: 1.1rem !important;
    }
    
    /* Success button style */
    .success-button > button {
        background: linear-gradient(45deg, #28a745, #20c997) !important;
        color: white !important;
    }
    
    /* Warning button style */
    .warning-button > button {
        background: linear-gradient(45deg, #ffc107, #fd7e14) !important;
        color: white !important;
    }
    
    /* Enhanced cards */
    .feature-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        border-color: var(--primary-color);
    }
    
    /* Progress bars */
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, var(--primary-color), var(--success-color));
        height: 8px;
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    /* Animated icons */
    .rotating-icon {
        animation: rotate 2s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .pulse-icon {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    /* Enhanced metrics */
    .metric-card {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Image gallery */
    .image-gallery {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .image-item {
        position: relative;
        border-radius: 10px;
        overflow: hidden;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .image-item:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    
    /* Loading animations */
    .loading-spinner {
        border: 4px solid rgba(255,255,255,0.3);
        border-radius: 50%;
        border-top: 4px solid var(--primary-color);
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Notification styles */
    .notification {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid;
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .notification.success {
        background: rgba(76, 205, 196, 0.1);
        border-color: var(--success-color);
        color: var(--success-color);
    }
    
    .notification.warning {
        background: rgba(255, 217, 61, 0.1);
        border-color: var(--warning-color);
        color: var(--warning-color);
    }
    
    .notification.error {
        background: rgba(255, 107, 107, 0.1);
        border-color: var(--error-color);
        color: var(--error-color);
    }
    
    /* Sidebar enhancements */
    .sidebar-section {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border-radius: 10px;
        padding: 0.5rem 1rem;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def show_animated_header(title, subtitle="", icon="🎨"):
    """Display an animated header with icon."""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        <div class="pulse-icon" style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
        <h1 style="color: #667eea !important; 
                   font-size: 3rem; margin-bottom: 0.5rem; 
                   text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                   font-weight: bold;">{title}</h1>
        {f'<p style="font-size: 1.2rem; color: #888; margin-top: 0; font-weight: 500;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def show_feature_card(title, description, icon, action_text="Learn More", key=None):
    """Display a feature card with hover effects."""
    card_html = f"""
    <div class="feature-card">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="font-size: 2rem; margin-right: 1rem;">{icon}</div>
            <h3 style="margin: 0; color: #333;">{title}</h3>
        </div>
        <p style="color: #666; margin-bottom: 1.5rem;">{description}</p>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    if key and st.button(action_text, key=key, use_container_width=True):
        return True
    return False

def show_progress_bar(progress, text="Processing...", show_percentage=True):
    """Display an animated progress bar."""
    progress_html = f"""
    <div class="progress-container">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: bold;">{text}</span>
            {f'<span>{int(progress * 100)}%</span>' if show_percentage else ''}
        </div>
        <div style="background: rgba(255,255,255,0.2); border-radius: 4px; height: 8px;">
            <div class="progress-bar" style="width: {progress * 100}%;"></div>
        </div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

def show_metric_cards(metrics):
    """Display metrics in attractive cards."""
    cols = st.columns(len(metrics))
    
    for i, (label, value, icon) in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

def show_loading_spinner(text="Loading..."):
    """Display a loading spinner with text."""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <div class="loading-spinner"></div>
        <p style="margin-top: 1rem; color: #666;">{text}</p>
    </div>
    """, unsafe_allow_html=True)

def show_notification(message, type="info", duration=3):
    """Display a notification with auto-dismiss."""
    type_class = type if type in ["success", "warning", "error"] else "info"
    
    notification_html = f"""
    <div class="notification {type_class}">
        <strong>{message}</strong>
    </div>
    """
    
    placeholder = st.empty()
    placeholder.markdown(notification_html, unsafe_allow_html=True)
    
    # Auto-dismiss after duration
    if duration > 0:
        time.sleep(duration)
        placeholder.empty()

def create_image_gallery(images, captions=None, max_cols=3):
    """Create an interactive image gallery."""
    if not images:
        return
    
    captions = captions or [f"Image {i+1}" for i in range(len(images))]
    
    # Calculate number of rows needed
    num_cols = min(len(images), max_cols)
    cols = st.columns(num_cols)
    
    for i, (image, caption) in enumerate(zip(images, captions)):
        col_idx = i % num_cols
        
        with cols[col_idx]:
            # Create a container for the image
            container = st.container()
            
            with container:
                if isinstance(image, str):  # URL
                    st.image(image, caption=caption, use_column_width=True)
                else:  # PIL Image or bytes
                    st.image(image, caption=caption, use_column_width=True)
                
                # Add download button
                if st.button(f"📥 Download", key=f"download_{i}"):
                    # Handle download logic here
                    st.success(f"Downloaded {caption}")

def enhanced_file_uploader(label, accepted_types=None, help_text=None, key=None):
    """Enhanced file uploader with drag-and-drop styling."""
    accepted_types = accepted_types or ["png", "jpg", "jpeg"]
    
    st.markdown(f"""
    <div style="border: 2px dashed #667eea; border-radius: 10px; padding: 2rem; 
                text-align: center; background: rgba(102, 126, 234, 0.05); margin: 1rem 0;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
        <h4 style="color: #667eea; margin-bottom: 0.5rem;">{label}</h4>
        {f'<p style="color: #666; font-size: 0.9rem;">{help_text}</p>' if help_text else ''}
    </div>
    """, unsafe_allow_html=True)
    
    return st.file_uploader(
        label,
        type=accepted_types,
        key=key,
        label_visibility="collapsed"
    )

def show_generation_status(status_text, is_processing=False):
    """Show generation status with animated elements."""
    if is_processing:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <div class="rotating-icon" style="font-size: 3rem; margin-bottom: 1rem;">🎨</div>
                <h3 style="color: #667eea;">{status_text}</h3>
                <div class="loading-spinner" style="margin: 1rem auto;"></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success(f"✨ {status_text}")

def create_interactive_sidebar():
    """Create an enhanced interactive sidebar."""
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        show_metric_cards([
            ("Images Generated", "42", "🎨"),
            ("Projects", "7", "📁"),
            ("Success Rate", "98%", "✅")
        ])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Recent activity
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🕒 Recent Activity")
        
        activities = [
            ("Generated lifestyle shot", "2 min ago", "🎨"),
            ("Created packshot", "15 min ago", "📦"),
            ("Enhanced image", "1 hour ago", "✨")
        ]
        
        for activity, time_ago, icon in activities:
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 0.5rem 0; 
                        border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span style="margin-right: 0.5rem;">{icon}</span>
                <div>
                    <div style="font-size: 0.9rem; font-weight: bold;">{activity}</div>
                    <div style="font-size: 0.8rem; color: #666;">{time_ago}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_welcome_dashboard():
    """Display a welcome dashboard for new users."""
    show_animated_header("Welcome to AdSnap Studio", "Generate & modify images with AI-powered tools", "🚀")
    
    # Feature overview
    st.markdown("### 🌟 What you can do:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if show_feature_card(
            "Generate Images", 
            "Create stunning visuals from text prompts using advanced AI",
            "🎨",
            "Start Creating",
            "feature_generate"
        ):
            st.session_state.active_tab = 0
    
    with col2:
        if show_feature_card(
            "Lifestyle Shots",
            "Transform product photos into lifestyle scenes",
            "📸",
            "Try Now",
            "feature_lifestyle"
        ):
            st.session_state.active_tab = 1
    
    with col3:
        if show_feature_card(
            "Image Editing",
            "Remove backgrounds, add shadows, and enhance your images",
            "✨",
            "Explore",
            "feature_editing"
        ):
            st.session_state.active_tab = 2
    
    # Quick start guide
    st.markdown("### 🚀 Quick Start Guide")
    
    steps = [
        ("Upload or generate an image", "Start with your product photo or create one from scratch"),
        ("Choose your enhancement", "Select from our AI-powered editing tools"),
        ("Customize settings", "Adjust parameters to match your vision"),
        ("Generate & download", "Get your enhanced images in seconds")
    ]
    
    for i, (step, description) in enumerate(steps, 1):
        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 1rem; margin: 0.5rem 0; 
                    background: rgba(102, 126, 234, 0.05); border-radius: 10px; 
                    border-left: 4px solid #667eea;">
            <div style="background: #667eea; color: white; border-radius: 50%; 
                        width: 30px; height: 30px; display: flex; align-items: center; 
                        justify-content: center; margin-right: 1rem; font-weight: bold;">{i}</div>
            <div>
                <div style="font-weight: bold; margin-bottom: 0.25rem;">{step}</div>
                <div style="color: #666; font-size: 0.9rem;">{description}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
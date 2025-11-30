import streamlit as st
import time
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import streamlit.components.v1 as components
import textwrap

def show_lottie_animation(url, height=300, key=None):
    """Embed a Lottie animation from a URL."""
    components.html(
        textwrap.dedent(f"""
        <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
        <div class="pulse-icon" style="font-size: 4rem; margin-bottom: 1.5rem;">{icon}</div>
        <h1 class="gradient-text" style="font-size: 3.5rem; margin-bottom: 1rem; font-weight: 800;">{title}</h1>
        {f'<p style="font-size: 1.25rem; color: var(--text-secondary); margin-top: 0; max-width: 600px; margin: 0 auto;">{subtitle}</p>' if subtitle else ''}
    </div>
    """), unsafe_allow_html=True)

def show_feature_card(title, description, icon, action_text="Learn More", key=None):
    """Display a feature card with hover effects."""
    card_html = textwrap.dedent(f"""
    <div class="feature-card animate-fade-in">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="font-size: 2rem; margin-right: 1rem; color: var(--primary-color);">{icon}</div>
            <h3 style="margin: 0; color: var(--text-color);">{title}</h3>
        </div>
        <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">{description}</p>
    </div>
    """)
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    st.markdown(textwrap.dedent(f"""
    <div class="glass-panel" style="padding: 1rem; border-radius: 0.75rem; margin-bottom: 1rem; border: 1px solid var(--card-border);">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.25rem; margin-right: 0.5rem; color: var(--secondary-color);"><i class="fas fa-folder"></i></span>
            <span style="font-weight: 600; color: var(--text-color);">Current Project</span>
        </div>
        <div style="font-size: 0.875rem; color: var(--text-secondary);">{st.session_state.get('current_project', 'Untitled Project')}</div>
    </div>
    """), unsafe_allow_html=True)
    
    if key and st.button(action_text, key=key, use_container_width=True):
        return True
    return False

def show_progress_bar(progress, text="Processing...", show_percentage=True):
    """Display an animated progress bar."""
    progress_html = textwrap.dedent(f"""
    <div class="progress-container animate-fade-in">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 600; color: var(--text-color);">{text}</span>
            {f'<span style="color: var(--text-secondary);">{int(progress * 100)}%</span>' if show_percentage else ''}
        </div>
        <div style="background: rgba(30, 41, 59, 0.5); border-radius: 4px; height: 8px; overflow: hidden;">
            <div class="progress-bar" style="width: {progress * 100}%;"></div>
        </div>
    </div>
    """)
    st.markdown(progress_html, unsafe_allow_html=True)

def show_metric_cards(metrics):
    """Display metrics in attractive cards."""
    cols = st.columns(len(metrics))
    
    for i, (label, value, icon) in enumerate(metrics):
        with cols[i]:
            st.markdown(textwrap.dedent(f"""
            <div class="metric-card animate-fade-in stagger-{i+1}">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """), unsafe_allow_html=True)

def show_loading_spinner(text="Loading..."):
    """Display a loading spinner with text."""
    st.markdown(textwrap.dedent(f"""
    <div style="text-align: center; padding: 2rem;" class="animate-fade-in">
        <div class="loading-spinner"></div>
        <p style="margin-top: 1rem; color: var(--text-secondary);">{text}</p>
    </div>
    """), unsafe_allow_html=True)

def show_notification(message, type="info", duration=3):
    """Display a notification with auto-dismiss."""
    type_class = type if type in ["success", "warning", "error"] else "info"
    
    notification_html = textwrap.dedent(f"""
    <div class="notification {type_class}">
        <strong style="color: var(--text-color);">{message}</strong>
    </div>
    """)
    
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
    
    st.markdown(textwrap.dedent(f"""
    <div style="border: 2px dashed var(--card-border); border-radius: 1rem; padding: 2rem; 
                text-align: center; background: var(--card-bg); margin: 1rem 0; transition: border-color 0.3s;" class="animate-fade-in">
        <div style="font-size: 3rem; margin-bottom: 1rem; color: var(--primary-color);"><i class="fas fa-cloud-upload-alt"></i></div>
        <h4 style="color: var(--text-color); margin-bottom: 0.5rem;">{label}</h4>
        {f'<p style="color: var(--text-secondary); font-size: 0.875rem;">{help_text}</p>' if help_text else ''}
    </div>
    """), unsafe_allow_html=True)
    
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
            st.markdown(textwrap.dedent(f"""
            <div style="text-align: center; padding: 2rem;" class="animate-fade-in">
                <div class="rotating-icon" style="font-size: 3rem; margin-bottom: 1rem; color: var(--secondary-color);"><i class="fas fa-paint-brush"></i></div>
                <h3 style="color: var(--text-color);">{status_text}</h3>
                <div class="loading-spinner" style="margin: 1rem auto;"></div>
            </div>
            """), unsafe_allow_html=True)
    else:
        st.success(f"✨ {status_text}")

def create_interactive_sidebar():
    """Create an enhanced interactive sidebar."""
    with st.sidebar:
        st.markdown('<div class="sidebar-section animate-fade-in">', unsafe_allow_html=True)
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        show_metric_cards([
            ("Images Generated", "42", "🎨"),
            ("Projects", "7", "📁"),
            ("Success Rate", "98%", "✅")
        ])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Recent activity
        st.markdown('<div class="sidebar-section animate-fade-in stagger-1">', unsafe_allow_html=True)
        st.markdown("### 🕒 Recent Activity")
        
        activities = [
            ("Generated lifestyle shot", "2 min ago", "🎨"),
            ("Created packshot", "15 min ago", "📦"),
            ("Enhanced image", "1 hour ago", "✨")
        ]
        
        for activity, time_ago, icon in activities:
            st.markdown(textwrap.dedent(f"""
            <div style="display: flex; align-items: center; padding: 0.75rem 0; 
                        border-bottom: 1px solid var(--card-border);">
                <span style="margin-right: 0.75rem; font-size: 1.25rem;">{icon}</span>
                <div>
                    <div style="font-size: 0.875rem; font-weight: 600; color: var(--text-color);">{activity}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">{time_ago}</div>
                </div>
            </div>
            """), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_welcome_dashboard():
    """Display a welcome dashboard for new users."""
    show_animated_header("Welcome to AdSnap Studio", "Generate & modify images with AI-powered tools", '<i class="fas fa-rocket"></i>')
    
    # Feature overview
    st.markdown("### 🌟 What you can do:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(textwrap.dedent("""
        <div class="feature-card animate-fade-in stagger-1" style="text-align: center;">
            <div style="font-size: 3rem; color: var(--primary-color); margin-bottom: 1rem;"><i class="fas fa-palette"></i></div>
            <h3 style="color: var(--text-color);">Generate Images</h3>
            <p style="color: var(--text-secondary);">Create stunning product images from text descriptions.</p>
        </div>
        """), unsafe_allow_html=True)
        if st.button("Start Generating", use_container_width=True, type="primary"):
            st.session_state.has_used_app = True
            st.session_state.active_tab = 1
            st.rerun()
            
    with col2:
        st.markdown(textwrap.dedent("""
        <div class="feature-card animate-fade-in stagger-2" style="text-align: center;">
            <div style="font-size: 3rem; color: var(--secondary-color); margin-bottom: 1rem;"><i class="fas fa-camera"></i></div>
            <h3 style="color: var(--text-color);">Lifestyle Shots</h3>
            <p style="color: var(--text-secondary);">Place your products in realistic lifestyle environments.</p>
        </div>
        """), unsafe_allow_html=True)
        if st.button("Create Lifestyle Shot", use_container_width=True):
            st.session_state.has_used_app = True
            st.session_state.active_tab = 2
            st.rerun()
            
    with col3:
        st.markdown(textwrap.dedent("""
        <div class="feature-card animate-fade-in stagger-3" style="text-align: center;">
            <div style="font-size: 3rem; color: var(--secondary-color); margin-bottom: 1rem;"><i class="fas fa-magic"></i></div>
            <h3 style="color: var(--text-color);">AI Editing</h3>
            <p style="color: var(--text-secondary);">Remove backgrounds, add shadows, and enhance quality.</p>
        </div>
        """), unsafe_allow_html=True)
        if st.button("Open Editor", use_container_width=True):
            st.session_state.has_used_app = True
            st.session_state.active_tab = 3
            st.rerun()
    
    # Quick start guide
    st.markdown("### 🚀 Quick Start Guide")
    
    steps = [
        ("Upload or generate an image", "Start with your product photo or create one from scratch"),
        ("Choose your enhancement", "Select from our AI-powered editing tools"),
        ("Customize settings", "Adjust parameters to match your vision"),
        ("Generate & download", "Get your enhanced images in seconds")
    ]
    
    for i, (step, description) in enumerate(steps, 1):
        st.markdown(textwrap.dedent(f"""
        <div style="display: flex; align-items: center; padding: 1.25rem; margin: 0.75rem 0; 
                    background: var(--card-bg); border-radius: 0.75rem; 
                    border: 1px solid var(--card-border); border-left: 4px solid var(--primary-color);" class="animate-fade-in stagger-{min(i, 3)}">
            <div style="background: var(--primary-color); color: white; border-radius: 50%; 
                        width: 32px; height: 32px; display: flex; align-items: center; 
                        justify-content: center; margin-right: 1.25rem; font-weight: bold;">{i}</div>
            <div>
                <div style="font-weight: 600; margin-bottom: 0.25rem; color: var(--text-color);">{step}</div>
                <div style="color: var(--text-secondary); font-size: 0.875rem;">{description}</div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    st.markdown(textwrap.dedent("""
    <div style="margin-top: 3rem; padding: 1.5rem; background: var(--card-bg); border-radius: 1rem; border: 1px solid var(--card-border);" class="animate-fade-in">
        <h4 style="color: var(--text-color); margin-bottom: 1rem;">System Status</h4>
        <div style="display: flex; gap: 2rem;">
            <div style="display: flex; align-items: center; color: var(--secondary-color);">
                <span style="margin-right: 0.5rem;"><i class="fas fa-check-circle"></i></span> API Connected
            </div>
            <div style="display: flex; align-items: center; color: var(--secondary-color);">
                <span style="margin-right: 0.5rem;"><i class="fas fa-box"></i></span> Models Loaded
            </div>
            <div style="display: flex; align-items: center; color: #f59e0b;">
                <span style="margin-right: 0.5rem;"><i class="fas fa-bolt"></i></span> GPU Ready
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)
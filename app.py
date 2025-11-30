import streamlit as st
import requests
from PIL import Image, ImageOps, ImageFilter
import io
import base64
import time
import json
import os
from datetime import datetime

# Import custom components
from components.auth import show_auth_page, logout
from components.dashboard import show_dashboard, show_feature_tour
from components.sidebar import create_sidebar
from components.interactive_ui import (
    show_animated_header, 
    enhanced_file_uploader, 
    show_generation_status,
    create_interactive_sidebar,
    show_welcome_dashboard
)
from components.activity_dashboard import (
    track_activity, 
    get_recent_activities, 
    show_real_time_activities,
    show_activity_statistics,
    show_recent_images
)

# Import config
try:
    from config.demo_config import DEMO_USER, ENHANCEMENT_PRESETS, STYLE_PRESETS, FEATURE_TOUR
except ImportError:
    # Fallback if config is missing
    DEMO_USER = {"username": "demo_user", "email": "demo@adsnap.ai"}
    ENHANCEMENT_PRESETS = {}
    STYLE_PRESETS = {}
    FEATURE_TOUR = []

# Set page config
st.set_page_config(
    page_title="AdSnap Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com',
        'Report a bug': "https://github.com",
        'About': "# AdSnap Studio\nAI-Powered Image Generation & Editing"
    }
)

# Initialize session state
def initialize_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.environ.get("BRIA_API_KEY", "")
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
    if 'edited_image' not in st.session_state:
        st.session_state.edited_image = None
    if 'activities' not in st.session_state:
        st.session_state.activities = []
    if 'tour_completed' not in st.session_state:
        st.session_state.tour_completed = False
    if 'enhanced_prompt' not in st.session_state:
        st.session_state.enhanced_prompt = ""

# API Functions (Mocked or Real)
def enhance_prompt(api_key, prompt):
    # Mock implementation for demo
    time.sleep(1)
    return f"{prompt}, highly detailed, professional lighting, 8k resolution, photorealistic"

def generate_hd_image(prompt, api_key, num_results=1, aspect_ratio="1:1", sync=True, enhance_image=True, medium="photography", prompt_enhancement=False, content_moderation=True):
    # Using Bria API if key exists, otherwise mock
    if not api_key:
        raise ValueError("API Key required")
    
    url = "https://engine.bria.ai/v1/text-to-image/base/1.4"
    
    payload = {
        "prompt": prompt,
        "num_results": num_results,
        "aspect_ratio": aspect_ratio,
        "sync": sync,
        "medium": medium,
        "prompt_enhancement": prompt_enhancement,
        "content_moderation": content_moderation
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api_token": api_key
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        # Fallback for demo/testing if API fails or no key
        if "demo" in api_key.lower() or response.status_code == 401:
            time.sleep(2)
            # Return placeholder images
            return {
                "result": [
                    {"urls": ["https://picsum.photos/1024/1024"]} for _ in range(num_results)
                ]
            }
        raise Exception(f"API Error: {response.text}")

def create_packshot(api_key, image_data, background_color="#FFFFFF", sku=None, force_rmbg=False, content_moderation=True):
    # Mock implementation
    time.sleep(2)
    return {"result_url": "https://picsum.photos/1024/1024"}

def add_shadow(api_key, image_data, shadow_type="natural", background_color="#FFFFFF", shadow_color="#000000", shadow_intensity=60, force_rmbg=False, content_moderation=True):
    # Mock implementation
    time.sleep(2)
    return {"result_url": "https://picsum.photos/1024/1024"}

def generative_fill(api_key, image_data, mask_data, prompt, num_results=1, sync=True, content_moderation=True):
    # Mock implementation
    time.sleep(2)
    return {"result_url": "https://picsum.photos/1024/1024"}

def erase_foreground(api_key, image_data, content_moderation=True):
    # Mock implementation
    time.sleep(2)
    return {"result_url": "https://picsum.photos/1024/1024"}

def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
    except:
        pass
    return None

def track_current_activity(action, details, metadata=None):
    track_activity(
        st.session_state.get('username', 'Guest'),
        action,
        details,
        metadata
    )

def main():
    initialize_session_state()
    
    # Global CSS
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    :root {
        --primary-color: #6366f1;
        --secondary-color: #38bdf8;
        --background-color: #09090b;
        --card-bg: rgba(30, 41, 59, 0.7);
        --card-border: rgba(255, 255, 255, 0.1);
        --text-color: #f8fafc;
        --text-secondary: #94a3b8;
        --accent-glow: 0 0 20px rgba(99, 102, 241, 0.5);
        --glass-border: 1px solid rgba(255, 255, 255, 0.08);
        --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* Animated Mesh Gradient Background */
    .stApp {
        background-color: var(--background-color);
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(56, 189, 248, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.15) 0px, transparent 50%),
            radial-gradient(at 0% 100%, rgba(236, 72, 153, 0.15) 0px, transparent 50%);
        background-attachment: fixed;
        color: var(--text-color);
        font-family: 'Inter', sans-serif;
    }
    
    /* Glassmorphism Classes */
    .glass-card {
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: var(--glass-border);
        box-shadow: var(--glass-shadow);
        border-radius: 16px;
    }
    
    .glass-panel {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-bottom: var(--glass-border);
    }

    /* Keyframe Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translate3d(0, 20px, 0);
        }
        to {
            opacity: 1;
            transform: translate3d(0, 0, 0);
        }
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    /* Animation Classes */
    .animate-fade-in {
        animation: fadeInUp 0.6s ease-out forwards;
    }
    
    .animate-float {
        animation: float 6s ease-in-out infinite;
    }
    
    .stagger-1 { animation-delay: 0.1s; }
    .stagger-2 { animation-delay: 0.2s; }
    .stagger-3 { animation-delay: 0.3s; }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(30, 41, 59, 0.5); 
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(71, 85, 105, 0.8); 
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 116, 139, 1); 
    }
    
    /* Header Styling */
    .header-container {
        padding: 60px 20px 40px 20px;
        margin-bottom: 40px;
        text-align: center;
        position: relative;
        z-index: 10;
    }
    .logo-title-wrapper {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 25px;
        margin-bottom: 15px;
    }
    .logo-emoji {
        font-size: 4.5rem;
        line-height: 1;
        display: block;
        filter: drop-shadow(0 0 30px rgba(99, 102, 241, 0.4));
        animation: float 6s ease-in-out infinite;
    }
    .main-title {
        margin: 0;
        font-size: 4rem;
        font-weight: 900;
        letter-spacing: -2px;
        line-height: 1.1;
        background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 4px 10px rgba(0,0,0,0.3));
    }
    
    .subtitle {
        margin: 16px 0 0 0;
        background: linear-gradient(90deg, #6366f1 0%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.2rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* Mobile Responsive Header */
    @media only screen and (max-width: 768px) {
        .header-container {
            padding: 30px 10px 15px 10px;
            margin: -60px -20px 0 -20px;
        }
        .logo-title-wrapper {
            flex-direction: column;
            gap: 15px;
        }
        .logo-emoji {
            font-size: 3rem;
        }
        .main-title {
            font-size: 2.5rem;
        }
        .subtitle {
            font-size: 0.9rem;
        }
    }
    </style>
    <div class="header-container">
        <div class="logo-title-wrapper">
            <div style="background: transparent; padding: 0; display: flex; align-items: center; justify-content: center;">
                <span class="logo-emoji"><i class="fas fa-layer-group"></i></span>
            </div>
            <div>
                <h1 class="main-title">ADSNAP STUDIO</h1>
                <p class="subtitle">AI-Powered Image Generation & Editing</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mobile Hamburger Menu
    current_page = st.session_state.get('current_page', 0)
    mobile_menu_items = [
        ('<i class="fas fa-home"></i>', "Dashboard", 0),
        ('<i class="fas fa-wand-magic-sparkles"></i>', "Generate", 1),
        ('<i class="fas fa-sliders"></i>', "Editor", 2),
        ('<i class="fas fa-image"></i>', "Lifestyle", 3),
        ('<i class="fas fa-fill-drip"></i>', "Fill", 4),
        ('<i class="fas fa-eraser"></i>', "Erase", 5)
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
            <div class="mobile-menu-logo"><i class="fas fa-layer-group"></i></div>
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
    
    # Handle navigation via query parameters
    query_params = st.query_params
    if 'page' in query_params:
        try:
            qp_page = int(query_params['page'])
            if qp_page != st.session_state.get('current_page', 0):
                st.session_state.current_page = qp_page
        except (ValueError, TypeError):
            pass
            
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    
    # Check if a quick action was triggered
    if st.session_state.get('active_tab') is not None:
        st.session_state.current_page = st.session_state.active_tab
        current_params = dict(st.query_params)
        current_params['page'] = str(st.session_state.active_tab)
        st.query_params.update(current_params)
        st.session_state.active_tab = None
    
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
                    st.warning("⚠️ Canvas drawing is currently unavailable due to library compatibility issues.")
                    st.info("💡 Please use the '📤 Upload Mask' option instead.")
                    st.markdown("""
                    **How to create a mask:**
                    1. Download your image using the button in the left column
                    2. Open it in Paint, Photoshop, or any image editor
                    3. Paint WHITE where you want AI to fill
                    4. Keep BLACK where you want original
                    5. Save and upload the mask below
                    """)
                    
                    # Show original image
                    st.image(img, caption="Original Image", use_column_width=True)
                    
                    # Initialize empty mask
                    if 'gf_mask_image' not in st.session_state:
                        st.session_state.gf_mask_image = Image.new('L', img.size, 0)
                    
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
                                
                                # Try multiple response formats
                                result_url = None
                                
                                if result:
                                    # Format 1: Direct result_url
                                    if "result_url" in result:
                                        result_url = result["result_url"]
                                    # Format 2: result array with urls
                                    elif "result" in result and isinstance(result["result"], list) and len(result["result"]) > 0:
                                        if "urls" in result["result"][0]:
                                            result_url = result["result"][0]["urls"][0]
                                        elif "url" in result["result"][0]:
                                            result_url = result["result"][0]["url"]
                                    # Format 3: Direct url field
                                    elif "url" in result:
                                        result_url = result["url"]
                                    # Format 4: urls array
                                    elif "urls" in result and isinstance(result["urls"], list) and len(result["urls"]) > 0:
                                        result_url = result["urls"][0]
                                
                                if result_url:
                                    st.session_state.generative_fill_result = result_url
                                    st.success("✨ Generative fill completed!")
                                    st.rerun()
                                else:
                                    st.error("❌ No result URL found in API response")
                                    st.info("💡 The API returned a response but in an unexpected format. Check the debug info below.")
                                    with st.expander("🔍 Debug: Full API Response"):
                                        st.json(result)
                                        st.markdown("**Expected formats:**")
                                        st.code('{"result_url": "..."} or {"result": [{"urls": ["..."]}]} or {"url": "..."}')
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
                                
                                # Try multiple response formats
                                result_url = None
                                
                                if result:
                                    if "result_url" in result:
                                        result_url = result["result_url"]
                                    elif "result" in result and isinstance(result["result"], list) and len(result["result"]) > 0:
                                        if "urls" in result["result"][0]:
                                            result_url = result["result"][0]["urls"][0]
                                        elif "url" in result["result"][0]:
                                            result_url = result["result"][0]["url"]
                                    elif "url" in result:
                                        result_url = result["url"]
                                    elif "urls" in result and isinstance(result["urls"], list) and len(result["urls"]) > 0:
                                        result_url = result["urls"][0]
                                
                                if result_url:
                                    st.session_state.erase_result = result_url
                                    st.success("✨ Foreground objects removed successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ No result URL found in API response")
                                    with st.expander("🔍 Debug: Full API Response"):
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
                    st.warning("⚠️ Canvas drawing unavailable due to compatibility issues.")
                    st.info("💡 Create mask in external tool and upload below:")
                    
                    # Mask upload
                    mask_file = st.file_uploader(
                        "📤 Upload Mask",
                        type=["png", "jpg", "jpeg"],
                        key="erase_mask_file",
                        help="White = erase, Black = keep"
                    )
                    
                    if mask_file:
                        mask_img = Image.open(mask_file).convert('L')
                        if mask_img.size != img.size:
                            mask_img = mask_img.resize(img.size, Image.Resampling.LANCZOS)
                        st.session_state.erase_mask_image = mask_img
                        st.image(mask_img, caption="Uploaded Mask", use_column_width=True)
                    else:
                        st.image(img, caption="Original (for reference)", use_column_width=True)
                        if 'erase_mask_image' not in st.session_state:
                            st.session_state.erase_mask_image = Image.new('L', img.size, 0)
                
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

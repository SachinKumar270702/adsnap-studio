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
        --primary-color: #4F46E5;
        --secondary-color: #10B981;
        --background-color: #0F172A;
        --card-bg: #1E293B;
        --text-color: #F8FAFC;
        --accent-glow: 0 0 20px rgba(79, 70, 229, 0.5);
    }
    
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1e293b; 
    }
    ::-webkit-scrollbar-thumb {
        background: #475569; 
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b; 
    }
    
    /* Header Styling */
    .header-container {
        padding: 40px 20px 20px 20px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0) 0%, rgba(15, 23, 42, 1) 100%);
        margin-bottom: 30px;
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

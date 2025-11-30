import streamlit as st
import requests
from PIL import Image, ImageOps, ImageFilter
import io
import base64
import time
import json
import os
import textwrap
from datetime import datetime

# Import custom components
from components.auth import show_login_page, logout
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

    # Import styles and header
    from components.styles import GLOBAL_CSS, HEADER_HTML
    
    # Apply global CSS
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    
    # Render header
    st.markdown(HEADER_HTML, unsafe_allow_html=True)

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
    
    # Import HTML templates
    from components.html_templates import get_mobile_menu_html

    # Create hamburger menu HTML
    mobile_menu_html = get_mobile_menu_html(current_page, mobile_menu_items)
    
    st.markdown(mobile_menu_html, unsafe_allow_html=True)
    
    # Auth buttons in top-right corner (floating)
    st.markdown(textwrap.dedent("""
    <div style="position: fixed; top: 20px; right: 30px; z-index: 1000; display: flex; gap: 10px;">
    </div>
    """), unsafe_allow_html=True)
    
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
        "📸 Lifestyle Shot",
        "🖌️ Generative Fill",
        "🧹 Erase Elements"
    ]
    
    # Handle page routing
    query_params = st.query_params
    if "page" in query_params:
        try:
            page_idx = int(query_params["page"])
            if 0 <= page_idx < len(tab_names):
                st.session_state.current_page = page_idx
        except:
            pass
            
    # Display current page
    if st.session_state.current_page == 0:
        show_dashboard()
        
    elif st.session_state.current_page == 1:
        # Generate Image Page
        show_animated_header("Generate Images", "Create stunning visuals with AI", '<i class="fas fa-wand-magic-sparkles"></i>')
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            prompt = st.text_area("Describe your image", height=150, placeholder="A futuristic city with flying cars...")
            
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                num_results = st.slider("Number of images", 1, 4, 1)
                aspect_ratio = st.selectbox("Aspect Ratio", ["1:1", "16:9", "9:16", "4:3", "3:4"])
            
            with col_opt2:
                medium = st.selectbox("Style", ["photography", "digital_art", "painting", "3d_render"])
                enhance = st.checkbox("Enhance Prompt", value=True)
            
            if st.button("Generate", type="primary", use_container_width=True):
                if not st.session_state.api_key:
                    st.error("Please enter your API key in the sidebar")
                else:
                    show_generation_status("Generating your masterpiece...", True)
                    try:
                        # Enhance prompt if selected
                        final_prompt = prompt
                        if enhance:
                            final_prompt = enhance_prompt(st.session_state.api_key, prompt)
                            st.info(f"Enhanced prompt: {final_prompt}")
                        
                        result = generate_hd_image(
                            final_prompt, 
                            st.session_state.api_key, 
                            num_results=num_results,
                            aspect_ratio=aspect_ratio,
                            medium=medium
                        )
                        
                        if result and "result" in result:
                            st.session_state.generated_images = result["result"]
                            track_current_activity("Generated Image", f"Prompt: {prompt[:30]}...")
                            show_generation_status("Generation complete!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col2:
            if st.session_state.generated_images:
                st.markdown("### Generated Results")
                for img_data in st.session_state.generated_images:
                    if "urls" in img_data:
                        for url in img_data["urls"]:
                            st.image(url, use_column_width=True)
                            st.download_button("Download", requests.get(url).content, "generated_image.png", "image/png")
            else:
                st.info("Your generated images will appear here")
                
    elif st.session_state.current_page == 2:
        # Image Editor Page
        show_animated_header("Image Editor", "Enhance and modify your images", '<i class="fas fa-sliders"></i>')
        
        uploaded_file = enhanced_file_uploader("Upload Image to Edit")
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Original Image", use_column_width=True)
            
            st.markdown("### Editing Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Remove Background", use_container_width=True):
                    # Call remove background API
                    pass
            
            with col2:
                if st.button("Add Shadow", use_container_width=True):
                    # Call add shadow API
                    pass
            
            with col3:
                if st.button("Upscale", use_container_width=True):
                    # Call upscale API
                    pass
                    
    elif st.session_state.current_page == 3:
        # Lifestyle Shot Page
        show_animated_header("Lifestyle Shot", "Place your product in any environment", '<i class="fas fa-image"></i>')
        st.info("Coming soon!")
        
    elif st.session_state.current_page == 4:
        # Generative Fill Page
        show_animated_header("Generative Fill", "Add or replace elements in your image", '<i class="fas fa-fill-drip"></i>')
        
        uploaded_file = enhanced_file_uploader("Upload Image")
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Original Image", use_column_width=True)
            
            prompt = st.text_input("What do you want to add/change?")
            
            if st.button("Generate Fill", type="primary"):
                # Call generative fill API
                pass
                
    elif st.session_state.current_page == 5:
        # Erase Elements Page
        show_animated_header("Erase Elements", "Remove unwanted objects from your image", '<i class="fas fa-eraser"></i>')
        
        # Initialize session state for erase tool
        if 'erase_mode' not in st.session_state:
            st.session_state.erase_mode = 'auto'  # 'auto' or 'manual'
            
        # Mode selector
        mode = st.radio("Select Mode", ["Auto Removal", "Manual Brush"], horizontal=True)
        
        if mode == "Auto Removal":
            uploaded_file = enhanced_file_uploader("Upload Image to Erase From", key="erase_upload_auto")
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Original Image", use_column_width=True)
                
                if st.button("Remove Foreground Object", type="primary"):
                    if not st.session_state.api_key:
                        st.error("Please enter your API key")
                    else:
                        with st.spinner("Removing object..."):
                            try:
                                # Content moderation check
                                content_mod = True
                                
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

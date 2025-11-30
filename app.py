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

# Import services
from services.hd_image_generation import generate_hd_image
from services.prompt_enhancement import enhance_prompt
from services.packshot import create_packshot
from services.shadow import add_shadow
from services.generative_fill import generative_fill
from services.erase_foreground import erase_foreground

# Import custom components
from components.auth import show_login_page, logout
from components.dashboard import show_dashboard, show_feature_tour
from components.sidebar import create_sidebar
from components.interactive_ui import (
    show_animated_header, 
    enhanced_file_uploader, 
    show_generation_status,
    create_interactive_sidebar,
    show_welcome_dashboard,
    show_navigation_dock
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

# API Functions imported from services


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
    # Initialize session state
    initialize_session_state()
    
    # Check authentication
    if not st.session_state.get('authenticated', False):
        show_login_page()
        return

    # Import styles and header
    from components.styles import apply_custom_css, HEADER_HTML
    
    # Apply global CSS
    apply_custom_css()
    
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
    # Display current page
    show_navigation_dock()
    
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
                            prompt=final_prompt, 
                            api_key=st.session_state.api_key, 
                            num_results=num_results,
                            aspect_ratio=aspect_ratio,
                            medium=medium,
                            enhance_image=True
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
        
        # Services imported globally

        
        uploaded_file = enhanced_file_uploader("Upload Image to Edit")
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Original Image", use_column_width=True)
            
            st.markdown("### Editing Options")
            
            # Tool Selection Buttons
            col_t1, col_t2, col_t3 = st.columns(3)
            
            with col_t1:
                if st.button("Remove Background", use_container_width=True):
                    st.session_state.editor_tool = "remove_bg"
            
            with col_t2:
                if st.button("Add Shadow", use_container_width=True):
                    st.session_state.editor_tool = "add_shadow"
            
            with col_t3:
                if st.button("Upscale", use_container_width=True):
                    st.session_state.editor_tool = "upscale"
            
            # Default tool if none selected
            if "editor_tool" not in st.session_state:
                st.session_state.editor_tool = "remove_bg"
            
            st.markdown("---")
            
            # Tool Interfaces
            if st.session_state.editor_tool == "remove_bg":
                st.markdown("#### ✂️ Remove Background")
                st.info("Remove the background from your image automatically.")
                
                if st.button("Process Image", type="primary", key="btn_process_rmbg"):
                    if not st.session_state.api_key:
                        st.error("Please enter your API key in the sidebar")
                    else:
                        with st.spinner("Removing background..."):
                            try:
                                result = create_packshot(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    background_color="transparent",
                                    force_rmbg=True
                                )
                                
                                if result and "result_url" in result:
                                    st.success("✨ Background removed!")
                                    st.image(result["result_url"], caption="Result", use_column_width=True)
                                    st.markdown(f"[Download Image]({result['result_url']})")
                                else:
                                    st.error("Failed to remove background")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

            elif st.session_state.editor_tool == "add_shadow":
                st.markdown("#### 🌑 Add Shadow")
                
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    shadow_type = st.selectbox("Shadow Type", ["regular", "float"])
                    intensity = st.slider("Intensity", 0, 100, 60)
                
                with col_s2:
                    shadow_color = st.color_picker("Shadow Color", "#000000")
                    bg_color = st.color_picker("Background Color", "#FFFFFF")
                
                if st.button("Apply Shadow", type="primary", key="btn_process_shadow"):
                    if not st.session_state.api_key:
                        st.error("Please enter your API key in the sidebar")
                    else:
                        with st.spinner("Adding shadow..."):
                            try:
                                result = add_shadow(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    shadow_type=shadow_type,
                                    shadow_intensity=intensity,
                                    shadow_color=shadow_color,
                                    background_color=bg_color,
                                    force_rmbg=True
                                )
                                
                                if result and "result_url" in result:
                                    st.success("✨ Shadow added!")
                                    st.image(result["result_url"], caption="Result", use_column_width=True)
                                    st.markdown(f"[Download Image]({result['result_url']})")
                                else:
                                    st.error("Failed to add shadow")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

            elif st.session_state.editor_tool == "upscale":
                st.markdown("#### 🔍 Upscale Image")
                st.info("Enhance image resolution and quality.")
                
                scale_factor = st.select_slider("Scale Factor", options=["2x", "4x"], value="2x")
                
                if st.button("Upscale Image", type="primary", key="btn_process_upscale"):
                    st.warning("Upscaling service is currently under maintenance. Please try again later.")
                    # Placeholder for future implementation
                    # result = upscale_image(...)
                    
    elif st.session_state.current_page == 3:
        # Lifestyle Shot Page
        show_animated_header("Lifestyle Shot", "Place your product in any environment", '<i class="fas fa-image"></i>')
        
        # Import service
        from services.lifestyle_shot import lifestyle_shot_by_text
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            uploaded_file = enhanced_file_uploader("Upload Product Image", key="lifestyle_upload")
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Product Image", use_column_width=True)
        
        with col2:
            if uploaded_file:
                scene_description = st.text_area("Describe the scene", height=100, 
                                               placeholder="A modern kitchen counter with sunlight streaming in...")
                
                col_opt1, col_opt2 = st.columns(2)
                with col_opt1:
                    placement = st.selectbox("Placement", ["original", "automatic", "manual_placement"])
                    num_results = st.slider("Number of images", 1, 4, 1)
                
                with col_opt2:
                    fast_mode = st.checkbox("Fast Mode", value=True)
                    sync_mode = st.checkbox("Sync Mode", value=True)
                
                if st.button("Generate Lifestyle Shot", type="primary", use_container_width=True):
                    if not st.session_state.api_key:
                        st.error("Please enter your API key in the sidebar")
                    else:
                        with st.spinner("Generating lifestyle shot..."):
                            try:
                                # Call API
                                result = lifestyle_shot_by_text(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    scene_description=scene_description,
                                    placement_type=placement,
                                    num_results=num_results,
                                    sync=sync_mode,
                                    fast=fast_mode
                                )
                                
                                # Handle response
                                if result and "result" in result:
                                    st.success("✨ Lifestyle shot generated successfully!")
                                    
                                    # Display results
                                    result_urls = []
                                    if isinstance(result["result"], list):
                                        for item in result["result"]:
                                            if isinstance(item, str): # URL string
                                                result_urls.append(item)
                                            elif isinstance(item, dict):
                                                if "url" in item:
                                                    result_urls.append(item["url"])
                                                elif "urls" in item and item["urls"]:
                                                    result_urls.extend(item["urls"])
                                    elif isinstance(result["result"], dict):
                                         if "url" in result["result"]:
                                             result_urls.append(result["result"]["url"])
                                    
                                    # Display images in grid
                                    if result_urls:
                                        cols = st.columns(min(len(result_urls), 2))
                                        for i, url in enumerate(result_urls):
                                            with cols[i % 2]:
                                                st.image(url, use_column_width=True)
                                                st.markdown(f"[Download Image]({url})")
                                    else:
                                        st.warning("No image URLs found in response")
                                        st.json(result)
                                        
                                else:
                                    st.error("Failed to generate image")
                                    st.json(result)
                                    
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            else:
                st.info("👆 Please upload a product image to get started")
                
                # Show demo example
                st.markdown("### Example")
                st.image("https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=1000&auto=format&fit=crop", 
                         caption="Product placed in a lifestyle setting", width=400)
        
    elif st.session_state.current_page == 4:
        # Generative Fill Page
        show_animated_header("Generative Fill", "Add or replace elements in your image", '<i class="fas fa-fill-drip"></i>')
        
        # Import service

        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            uploaded_file = enhanced_file_uploader("Upload Image", key="gen_fill_upload")
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Original Image", use_column_width=True)
        
        with col2:
            if uploaded_file:
                st.info("💡 You need a mask to define where to generate content.")
                mask_file = enhanced_file_uploader("Upload Mask (Black & White)", key="gen_fill_mask")
                
                if mask_file:
                    mask_image = Image.open(mask_file)
                    st.image(mask_image, caption="Mask", width=200)
                    
                    prompt = st.text_area("What do you want to generate?", 
                                        placeholder="A red rose, a vintage clock, etc.")
                    
                    if st.button("Generate Fill", type="primary", use_container_width=True):
                        if not st.session_state.api_key:
                            st.error("Please enter your API key in the sidebar")
                        else:
                            with st.spinner("Generating content..."):
                                try:
                                    # Call API
                                    result = generative_fill(
                                        api_key=st.session_state.api_key,
                                        image_data=uploaded_file.getvalue(),
                                        mask_data=mask_file.getvalue(),
                                        prompt=prompt,
                                        sync=True
                                    )
                                    
                                    # Handle response
                                    if result and "result" in result:
                                        st.success("✨ Content generated successfully!")
                                        
                                        # Display results
                                        result_urls = []
                                        if isinstance(result["result"], list):
                                            for item in result["result"]:
                                                if isinstance(item, str):
                                                    result_urls.append(item)
                                                elif isinstance(item, dict) and "url" in item:
                                                    result_urls.append(item["url"])
                                        elif isinstance(result["result"], dict) and "url" in result["result"]:
                                            result_urls.append(result["result"]["url"])
                                            
                                        if result_urls:
                                            for url in result_urls:
                                                st.image(url, use_column_width=True)
                                                st.markdown(f"[Download Image]({url})")
                                        else:
                                            st.json(result)
                                    else:
                                        st.error("Failed to generate content")
                                        st.json(result)
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                else:
                    st.warning("Please upload a mask image (white area = modify, black = keep)")
                
    elif st.session_state.current_page == 5:
        # Erase Elements Page
        show_animated_header("Erase Elements", "Remove unwanted objects from your image", '<i class="fas fa-eraser"></i>')
        
        # Import service

        
        # Initialize session state for erase tool
        if 'erase_mode' not in st.session_state:
            st.session_state.erase_mode = 'auto'  # 'auto' or 'manual'
            
        # Mode selector
        mode = st.radio("Select Mode", ["Auto Removal (Foreground)", "Manual Mask Upload"], horizontal=True)
        
        if mode == "Auto Removal (Foreground)":
            st.info("Automatically remove the main foreground object.")
            uploaded_file = enhanced_file_uploader("Upload Image", key="erase_upload_auto")
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Original Image", use_column_width=True)
                
                if st.button("Remove Foreground", type="primary"):
                    if not st.session_state.api_key:
                        st.error("Please enter your API key")
                    else:
                        with st.spinner("Removing object..."):
                            try:
                                result = erase_foreground(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    content_moderation=True
                                )
                                
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
                                
                                if result_url:
                                    st.success("✨ Foreground removed!")
                                    st.image(result_url, caption="Result", use_column_width=True)
                                    st.markdown(f"[Download Image]({result_url})")
                                else:
                                    st.error("Failed to remove object")
                                    st.json(result)
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                                
        else:  # Manual Mask Upload
            st.info("Upload a mask to specify exactly what to erase (White = erase, Black = keep).")
            
            col1, col2 = st.columns(2)
            
            with col1:
                uploaded_file = enhanced_file_uploader("1. Upload Image", key="erase_image_manual")
                if uploaded_file:
                    st.image(uploaded_file, caption="Original Image", use_column_width=True)
            
            with col2:
                mask_file = enhanced_file_uploader("2. Upload Mask", key="erase_mask_file")
                if mask_file:
                    st.image(mask_file, caption="Mask", width=200)
            
            if uploaded_file and mask_file:
                if st.button("Erase Selected Area", type="primary"):
                    if not st.session_state.api_key:
                        st.error("Please enter your API key")
                    else:
                        # For manual erase, we can use generative fill with empty prompt or specific erase endpoint if available.
                        # Since we don't have a specific 'erase by mask' service file visible (only erase_foreground),
                        # we'll use generative fill with a prompt like "background" or empty string to fill it in.
                        # Alternatively, check if generative_fill supports this.
                        # Let's use generative_fill with "remove object" prompt as a fallback.
                        from services.generative_fill import generative_fill
                        
                        with st.spinner("Erasing..."):
                            try:
                                result = generative_fill(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    mask_data=mask_file.getvalue(),
                                    prompt="remove object, clean background",
                                    sync=True
                                )
                                
                                if result and "result" in result:
                                    st.success("✨ Area erased!")
                                    
                                    # Display results
                                    result_urls = []
                                    if isinstance(result["result"], list):
                                        for item in result["result"]:
                                            if isinstance(item, str):
                                                result_urls.append(item)
                                            elif isinstance(item, dict) and "url" in item:
                                                result_urls.append(item["url"])
                                    elif isinstance(result["result"], dict) and "url" in result["result"]:
                                        result_urls.append(result["result"]["url"])
                                        
                                    if result_urls:
                                        for url in result_urls:
                                            st.image(url, use_column_width=True)
                                            st.markdown(f"[Download Image]({url})")
                                    else:
                                        st.json(result)
                                else:
                                    st.error("Failed to erase")
                                    st.json(result)
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
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

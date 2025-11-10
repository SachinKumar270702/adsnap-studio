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
from components.auth import init_session_state, require_auth, show_login_page, show_user_profile
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
    
    # Main app header
    show_animated_header("AdSnap Studio", "AI-Powered Image Generation & Editing Studio")
    
    # Sidebar for API key
    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input("Enter your API key:", value=st.session_state.api_key if st.session_state.api_key else "", type="password")
        if api_key:
            st.session_state.api_key = api_key

    # Main navigation
    tab_names = [
        "🏠 Dashboard",
        "🎨 Generate Image", 
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
    
    # Create navigation buttons
    nav_cols = st.columns(len(tab_names))
    
    for i, (col, tab_name) in enumerate(zip(nav_cols, tab_names)):
        with col:
            # Highlight active button
            button_type = "primary" if i == st.session_state.current_page else "secondary"
            if st.button(tab_name, key=f"nav_{i}", use_container_width=True, type=button_type):
                st.session_state.current_page = i
                # Update query params to persist current page
                current_params = dict(st.query_params)
                current_params['page'] = str(i)
                st.query_params.update(current_params)
                st.rerun()
    
    st.markdown("---")  # Separator line
    
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
    
    elif st.session_state.current_page == 2:  # Product Photography
        st.markdown("### 📸 Product Photography")
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
    
    elif st.session_state.current_page == 3:  # Generative Fill
        st.markdown("### 🎨 Generative Fill")
        st.markdown("Fill in missing parts of images with AI-powered content generation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📤 Upload Files")
            uploaded_file = st.file_uploader(
                "Upload Original Image",
                type=["png", "jpg", "jpeg"],
                key="generative_fill_image"
            )
            
            mask_file = st.file_uploader(
                "Upload Mask Image (white = fill area, black = keep)",
                type=["png", "jpg", "jpeg"],
                key="generative_fill_mask",
                help="Create a mask where white areas will be filled with AI-generated content"
            )
        
        with col2:
            st.markdown("#### ⚙️ Settings")
            prompt = st.text_area(
                "Describe what should fill the masked area", 
                placeholder="e.g., 'blue sky with clouds', 'green grass', 'modern furniture'",
                height=100
            )
            
            sync_mode = st.checkbox("Wait for result (sync mode)", value=True)
        
        if uploaded_file and mask_file:
            st.markdown("---")
            st.markdown("### 🖼️ Preview")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                img = Image.open(uploaded_file)
                st.image(img, caption="Original Image", use_column_width=True)
            
            with col_b:
                mask = Image.open(mask_file)
                st.image(mask, caption="Mask", use_column_width=True)
            
            with col_c:
                if st.session_state.get('generative_fill_result'):
                    st.image(st.session_state.generative_fill_result, caption="Result", use_column_width=True)
                    
                    # Download button
                    image_data = download_image(st.session_state.generative_fill_result)
                    if image_data:
                        st.download_button(
                            "⬇️ Download Result",
                            image_data,
                            "generative_fill_result.png",
                            "image/png",
                            use_container_width=True
                        )
                else:
                    st.info("Result will appear here")
            
            st.markdown("---")
            
            if st.button("🎨 Generate Fill", type="primary", use_container_width=True):
                if not prompt:
                    st.warning("Please enter a prompt describing what to fill")
                elif not st.session_state.api_key:
                    st.error("Please enter your API key in the sidebar")
                else:
                    with st.spinner("🎨 Generating fill content..."):
                        try:
                            result = generative_fill(
                                api_key=st.session_state.api_key,
                                image_data=uploaded_file.getvalue(),
                                mask_data=mask_file.getvalue(),
                                prompt=prompt,
                                sync=sync_mode
                            )
                            
                            if result and "result_url" in result:
                                st.session_state.generative_fill_result = result["result_url"]
                                st.success("✨ Generative fill completed!")
                                st.rerun()
                            else:
                                st.error("No result URL in API response")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        elif uploaded_file:
            st.info("👆 Please upload a mask image to continue")
        else:
            st.info("👆 Please upload both an image and a mask to get started")
    
    elif st.session_state.current_page == 4:  # Erase Elements
        st.markdown("### ✂️ Erase Elements")
        st.markdown("Automatically remove foreground objects from your images")
        
        st.info("💡 This feature automatically detects and removes foreground objects, generating the background behind them.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Upload Image",
                type=["png", "jpg", "jpeg"],
                key="erase_image"
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

if __name__ == "__main__":
    main()
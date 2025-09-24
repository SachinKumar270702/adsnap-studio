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
        st.session_state.generated_images = []
    if 'current_image' not in st.session_state:
        st.session_state.current_image = None
    if 'pending_urls' not in st.session_state:
        st.session_state.pending_urls = []
    if 'edited_image' not in st.session_state:
        st.session_state.edited_image = None
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
        st.session_state.current_page = 0
    
    # Check if a quick action was triggered
    if st.session_state.get('active_tab') is not None:
        st.session_state.current_page = st.session_state.active_tab
        st.session_state.active_tab = None  # Reset after use
    
    # Create navigation buttons
    nav_cols = st.columns(len(tab_names))
    
    for i, (col, tab_name) in enumerate(zip(nav_cols, tab_names)):
        with col:
            # Highlight active button
            button_type = "primary" if i == st.session_state.current_page else "secondary"
            if st.button(tab_name, key=f"nav_{i}", use_container_width=True, type=button_type):
                st.session_state.current_page = i
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
                            if "result_url" in result:
                                st.session_state.edited_image = result["result_url"]
                                
                                # Save to database
                                if st.session_state.get('user_info', {}).get('id'):
                                    db_manager = st.session_state.db_manager
                                    db_manager.save_generated_image(
                                        st.session_state.user_info['id'],
                                        result["result_url"],
                                        "generated",
                                        prompt,
                                        {
                                            "num_images": num_images,
                                            "aspect_ratio": aspect_ratio,
                                            "style": style,
                                            "enhance_image": enhance_img
                                        }
                                    )
                                
                                st.success("✨ Image generated successfully!")
                            elif "result_urls" in result:
                                st.session_state.edited_image = result["result_urls"][0]
                                st.success("✨ Image generated successfully!")
                            elif "result" in result and isinstance(result["result"], list):
                                for item in result["result"]:
                                    if isinstance(item, dict) and "urls" in item:
                                        st.session_state.edited_image = item["urls"][0]
                                        st.success("✨ Image generated successfully!")
                                        break
                        else:
                            st.error("No valid result format found in the API response.")
                            
                except Exception as e:
                    st.error(f"Error generating images: {str(e)}")
        
        # Display generated image if available
        if st.session_state.get('edited_image'):
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
        
        uploaded_file = enhanced_file_uploader(
            "Upload Image for Generative Fill",
            ["png", "jpg", "jpeg"],
            "Upload an image to fill missing areas with AI",
            "generative_fill_upload"
        )
        
        if uploaded_file:
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(uploaded_file, caption="Original Image", use_column_width=True)
                
                # Canvas for mask drawing
                st.markdown("**Draw the area to fill:**")
                canvas_result = st_canvas(
                    fill_color="rgba(255, 255, 255, 0.3)",
                    stroke_width=20,
                    stroke_color="white",
                    background_color="black",
                    background_image=Image.open(uploaded_file),
                    update_streamlit=True,
                    height=400,
                    drawing_mode="freedraw",
                    key="generative_fill_canvas",
                )
                
                prompt = st.text_area("Describe what should fill the selected area", 
                                    placeholder="e.g., 'blue sky with clouds', 'green grass', 'modern furniture'")
                
                if st.button("🎨 Generate Fill", type="primary") and prompt:
                    show_generation_status("Generating fill content...", True)
                    st.success("✨ Generative fill completed!")
            
            with col2:
                st.markdown("**Preview:**")
                if canvas_result.image_data is not None:
                    st.image(canvas_result.image_data, caption="Mask Preview", use_column_width=True)
    
    elif st.session_state.current_page == 4:  # Erase Elements
        st.markdown("### ✂️ Erase Elements")
        st.markdown("Remove unwanted objects from your images with precision")
        
        uploaded_file = enhanced_file_uploader(
            "Upload Image for Object Removal",
            ["png", "jpg", "jpeg"],
            "Upload an image to remove unwanted elements",
            "erase_upload"
        )
        
        if uploaded_file:
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(uploaded_file, caption="Original Image", use_column_width=True)
                
                # Canvas for selection
                st.markdown("**Select objects to remove:**")
                canvas_result = st_canvas(
                    fill_color="rgba(255, 0, 0, 0.3)",
                    stroke_width=15,
                    stroke_color="red",
                    background_color="transparent",
                    background_image=Image.open(uploaded_file),
                    update_streamlit=True,
                    height=400,
                    drawing_mode="freedraw",
                    key="erase_canvas",
                )
                
                erase_mode = st.selectbox("Erase Mode", ["Automatic", "Precise", "Smart Fill"])
                
                if st.button("🗑️ Remove Objects", type="primary"):
                    show_generation_status("Removing selected objects...", True)
                    st.success("✨ Objects removed successfully!")
            
            with col2:
                st.markdown("**Selection Preview:**")
                if canvas_result.image_data is not None:
                    st.image(canvas_result.image_data, caption="Selection Mask", use_column_width=True)

if __name__ == "__main__":
    main()
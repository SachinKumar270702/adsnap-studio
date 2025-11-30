import streamlit as st
import requests
from PIL import Image
import io
import base64
import time
import json
import os
import textwrap
from datetime import datetime
from streamlit_drawable_canvas import st_canvas
import numpy as np

# Import services
from services.hd_image_generation import generate_hd_image
from services.prompt_enhancement import enhance_prompt
from services.packshot import create_packshot
from services.shadow import add_shadow
from services.generative_fill import generative_fill
from services.erase_foreground import erase_foreground
from services.lifestyle_shot import lifestyle_shot_by_text

# Import custom components
from components.auth import show_login_page, logout
from components.styles import apply_custom_css
from components.html_templates import get_mobile_menu_html
from components.dashboard import show_dashboard
from components.interactive_ui import (
    show_lottie_animation, 
    add_custom_css, 
    show_animated_header, 
    enhanced_file_uploader, 
    show_generation_status,
    create_interactive_sidebar,
    show_welcome_dashboard,
    show_navigation_dock
)
from components.activity_dashboard import track_activity
from components.dashboard import get_user_stats
from config.demo_config import (
    SAMPLE_PROMPTS, 
    ENHANCEMENT_PRESETS, 
    FEATURE_TOUR,
    UI_THEMES,
    TIPS_AND_TRICKS
)

# Set page config
st.set_page_config(
    page_title="AdSnap Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
def initialize_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv("BRIA_API_KEY", "")
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
    if 'user_credits' not in st.session_state:
        st.session_state.user_credits = 100
    if 'theme' not in st.session_state:
        st.session_state.theme = "Midnight Aurora"

def main():
    initialize_session_state()
    
    # Apply global styles
    apply_custom_css()
    
    # Check authentication
    if not st.session_state.authenticated:
        show_login_page()
        return

    # Sidebar
    with st.sidebar:
        st.title("AdSnap Studio")
        
        # API Key Input
        api_key_input = st.text_input(
            "API Key", 
            value=st.session_state.api_key, 
            type="password",
            help="Enter your Bria AI API Key"
        )
        if api_key_input != st.session_state.api_key:
            st.session_state.api_key = api_key_input
            st.rerun()
            
        st.divider()
        
        # Navigation
        st.markdown("### Navigation")
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.current_page = 0
            st.rerun()
            
        if st.button("📸 Create Packshots", use_container_width=True):
            st.session_state.current_page = 1
            st.rerun()
            
        if st.button("🎨 Image Editor", use_container_width=True):
            st.session_state.current_page = 2
            st.rerun()
            
        if st.button("🖼️ Lifestyle Shot", use_container_width=True):
            st.session_state.current_page = 3
            st.rerun()
            
        if st.button("✨ Generative Fill", use_container_width=True):
            st.session_state.current_page = 4
            st.rerun()
            
        if st.button("🧹 Erase Elements", use_container_width=True):
            st.session_state.current_page = 5
            st.rerun()
            
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

    # Display current page
    show_navigation_dock()
    
    if st.session_state.current_page == 0:
        show_dashboard()
        
    elif st.session_state.current_page == 1:
        # Create Packshots Page
        show_animated_header("Create Packshots", "Generate high-quality product images", '<i class="fas fa-camera"></i>')
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            prompt = st.text_area("Describe your product image", height=150, 
                                placeholder="A futuristic sneaker floating in neon space...")
            
            enhance_option = st.checkbox("✨ Enhance Prompt", value=True)
            
            if st.button("Generate Image", type="primary", use_container_width=True):
                if not st.session_state.api_key:
                    st.error("Please enter your API key in the sidebar")
                else:
                    with st.spinner("Generating magic..."):
                        try:
                            final_prompt = prompt
                            if enhance_option:
                                with st.status("Enhancing prompt...") as status:
                                    enhanced = enhance_prompt(st.session_state.api_key, prompt)
                                    if enhanced:
                                        final_prompt = enhanced
                                        status.update(label="Prompt enhanced!", state="complete")
                                    else:
                                        status.update(label="Using original prompt", state="complete")
                            
                            # Call API
                            result = generate_hd_image(
                                api_key=st.session_state.api_key,
                                prompt=final_prompt,
                                num_results=1,
                                sync=True
                            )
                            
                            # Handle response
                            if result and "result" in result:
                                st.success("✨ Image generated successfully!")
                                
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
                            
        with col2:
            st.info("💡 Tips for better results:")
            st.markdown("""
            * Be specific about lighting (e.g., "studio lighting", "natural light")
            * Mention the angle (e.g., "front view", "isometric view")
            * Describe the background (e.g., "clean white background", "wooden table")
            """)
            
    elif st.session_state.current_page == 2:
        # Image Editor Page
        show_animated_header("Image Editor", "Edit and enhance your images", '<i class="fas fa-edit"></i>')
        
        # Tool selection
        if 'editor_tool' not in st.session_state:
            st.session_state.editor_tool = "remove_bg"
            
        col_tools = st.columns(3)
        with col_tools[0]:
            if st.button("Remove Background", type="primary" if st.session_state.editor_tool == "remove_bg" else "secondary", use_container_width=True):
                st.session_state.editor_tool = "remove_bg"
                st.rerun()
        with col_tools[1]:
            if st.button("Add Shadow", type="primary" if st.session_state.editor_tool == "add_shadow" else "secondary", use_container_width=True):
                st.session_state.editor_tool = "add_shadow"
                st.rerun()
        with col_tools[2]:
            if st.button("Upscale", type="primary" if st.session_state.editor_tool == "upscale" else "secondary", use_container_width=True):
                st.session_state.editor_tool = "upscale"
                st.rerun()
                
        st.divider()
        
        if st.session_state.editor_tool == "remove_bg":
            st.subheader("Remove Background")
            uploaded_file = enhanced_file_uploader("Upload Image", key="remove_bg_upload")
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Original Image", width=300)
                
                if st.button("Remove Background", type="primary"):
                    if not st.session_state.api_key:
                        st.error("Please enter your API key")
                    else:
                        with st.spinner("Removing background..."):
                            try:
                                result = create_packshot(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    bg_color=None # Transparent
                                )
                                
                                if result and "result_url" in result:
                                    st.success("✨ Background removed!")
                                    st.image(result["result_url"], caption="Result", width=300)
                                    st.markdown(f"[Download Image]({result['result_url']})")
                                else:
                                    st.error("Failed to remove background")
                                    st.json(result)
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                                
        elif st.session_state.editor_tool == "add_shadow":
            st.subheader("Add Shadow")
            uploaded_file = enhanced_file_uploader("Upload Image (Transparent Background)", key="shadow_upload")
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Original Image", width=300)
                
                if st.button("Add Shadow", type="primary"):
                    if not st.session_state.api_key:
                        st.error("Please enter your API key")
                    else:
                        with st.spinner("Adding shadow..."):
                            try:
                                result = add_shadow(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue()
                                )
                                
                                if result and "result_url" in result:
                                    st.success("✨ Shadow added!")
                                    st.image(result["result_url"], caption="Result", width=300)
                                    st.markdown(f"[Download Image]({result['result_url']})")
                                else:
                                    st.error("Failed to add shadow")
                                    st.json(result)
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                                
        elif st.session_state.editor_tool == "upscale":
            st.subheader("Upscale Image")
            st.info("🚧 This service is currently under maintenance. Please check back later.")

    elif st.session_state.current_page == 3:
        # Lifestyle Shot Page
        show_animated_header("Lifestyle Shot", "Place your product in any environment", '<i class="fas fa-image"></i>')
        
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
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            uploaded_file = enhanced_file_uploader("Upload Image", key="gen_fill_upload")
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Original Image", use_column_width=True)
        
        with col2:
            if uploaded_file:
                st.info("🖌️ Draw on the image to define where to generate content.")
                
                # Canvas for drawing mask
                # Resize image for canvas if too large, to fit in column
                img_width, img_height = image.size
                canvas_width = 400
                canvas_height = int(img_height * (canvas_width / img_width))
                
                canvas_result = st_canvas(
                    fill_color="rgba(255, 255, 255, 1.0)",  # White mask
                    stroke_width=20,
                    stroke_color="rgba(255, 255, 255, 1.0)",
                    background_image=image,
                    update_streamlit=True,
                    height=canvas_height,
                    width=canvas_width,
                    drawing_mode="freedraw",
                    key="gen_fill_canvas",
                )
                
                prompt = st.text_area("What do you want to generate?", 
                                    placeholder="A red rose, a vintage clock, etc.")
                
                if st.button("Generate Fill", type="primary", use_container_width=True):
                    if not st.session_state.api_key:
                        st.error("Please enter your API key in the sidebar")
                    elif canvas_result.image_data is None:
                        st.warning("Please draw a mask on the image first.")
                    else:
                        with st.spinner("Generating content..."):
                            try:
                                # Convert canvas data (RGBA numpy array) to mask bytes
                                # We need a black background with white drawing for the mask
                                mask_data = canvas_result.image_data
                                mask_img = Image.fromarray(mask_data.astype('uint8'), 'RGBA')
                                
                                # Create final mask: black background, white drawing
                                final_mask = Image.new("RGB", mask_img.size, (0, 0, 0))
                                final_mask.paste(mask_img, (0, 0), mask_img)
                                # Convert to grayscale as expected by many APIs, or keep RGB if Bria accepts it.
                                # Bria usually expects black/white.
                                final_mask = final_mask.convert("L")
                                
                                # Resize mask back to original image size if needed, 
                                # but better to send original image resized to canvas size or vice versa.
                                # For simplicity, let's resize mask to original image size
                                final_mask = final_mask.resize(image.size)
                                
                                buf = io.BytesIO()
                                final_mask.save(buf, format="PNG")
                                mask_bytes = buf.getvalue()
                                
                                # Call API
                                result = generative_fill(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    mask_data=mask_bytes,
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
                st.info("Please upload an image first")
                
    elif st.session_state.current_page == 5:
        # Erase Elements Page
        show_animated_header("Erase Elements", "Remove unwanted objects from your image", '<i class="fas fa-eraser"></i>')
        
        # Initialize session state for erase tool
        if 'erase_mode' not in st.session_state:
            st.session_state.erase_mode = 'auto'  # 'auto' or 'manual'
            
        # Mode selector
        mode = st.radio("Select Mode", ["Auto Removal (Foreground)", "Manual Mask (Draw)"], horizontal=True)
        
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
                                
        else:  # Manual Mask Upload (Now Canvas)
            st.info("Draw over the object you want to erase.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                uploaded_file = enhanced_file_uploader("Upload Image", key="erase_image_manual")
                if uploaded_file:
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Original Image", use_column_width=True)
            
            with col2:
                if uploaded_file:
                    # Canvas for drawing mask
                    img_width, img_height = image.size
                    canvas_width = 400
                    canvas_height = int(img_height * (canvas_width / img_width))
                    
                    canvas_result = st_canvas(
                        fill_color="rgba(255, 255, 255, 1.0)",
                        stroke_width=20,
                        stroke_color="rgba(255, 255, 255, 1.0)",
                        background_image=image,
                        update_streamlit=True,
                        height=canvas_height,
                        width=canvas_width,
                        drawing_mode="freedraw",
                        key="erase_canvas",
                    )
            
            if uploaded_file:
                if st.button("Erase Selected Area", type="primary"):
                    if not st.session_state.api_key:
                        st.error("Please enter your API key")
                    elif canvas_result.image_data is None:
                        st.warning("Please draw on the image to select an area.")
                    else:
                        with st.spinner("Erasing..."):
                            try:
                                # Convert canvas data to mask bytes
                                mask_data = canvas_result.image_data
                                mask_img = Image.fromarray(mask_data.astype('uint8'), 'RGBA')
                                final_mask = Image.new("RGB", mask_img.size, (0, 0, 0))
                                final_mask.paste(mask_img, (0, 0), mask_img)
                                final_mask = final_mask.convert("L")
                                final_mask = final_mask.resize(image.size)
                                
                                buf = io.BytesIO()
                                final_mask.save(buf, format="PNG")
                                mask_bytes = buf.getvalue()
                                
                                result = generative_fill(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    mask_data=mask_bytes,
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
                                    st.error("Failed to erase area")
                                    st.json(result)
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            else:
                st.info("👆 Upload an image to start")


if __name__ == "__main__":
    main()

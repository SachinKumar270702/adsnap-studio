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

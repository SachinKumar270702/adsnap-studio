import streamlit as st

def get_config():
    """Get configuration from sidebar."""
    config = {
        "create_packshot": False,
        "add_shadow": False,
        "lifestyle_shot": False,
        "background_color": "#FFFFFF",
        "shadow_type": "natural",
        "scene_description": "",
        "num_results": 1,
        "aspect_ratio": "1:1",
        "sync": True
    }
    
    st.sidebar.markdown("### <i class='fas fa-cog'></i> Configuration", unsafe_allow_html=True)
    
    # Image Generation Settings
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown("#### <i class='fas fa-image'></i> Image Generation", unsafe_allow_html=True)
    config["num_results"] = st.sidebar.slider("Number of Results", 1, 4, 1)
    config["aspect_ratio"] = st.sidebar.selectbox(
        "Aspect Ratio",
        ["1:1", "16:9", "9:16", "4:3", "3:4"]
    )
    config["sync"] = st.sidebar.checkbox("Wait for Results", True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Packshot Settings
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown("#### <i class='fas fa-box-open'></i> Packshot", unsafe_allow_html=True)
    config["create_packshot"] = st.sidebar.checkbox(
        "Create Packshot",
        help="Create a professional product packshot"
    )
    if config["create_packshot"]:
        config["background_color"] = st.sidebar.color_picker(
            "Background Color",
            "#FFFFFF"
        )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Shadow Settings
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown("#### <i class='fas fa-cloud-sun'></i> Shadow", unsafe_allow_html=True)
    config["add_shadow"] = st.sidebar.checkbox(
        "Add Shadow",
        help="Add shadow to the product image"
    )
    if config["add_shadow"]:
        config["shadow_type"] = st.sidebar.selectbox(
            "Shadow Type",
            ["Natural", "Drop"]
        ).lower()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Lifestyle Shot Settings
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown("#### <i class='fas fa-camera-retro'></i> Lifestyle Shot", unsafe_allow_html=True)
    config["lifestyle_shot"] = st.sidebar.checkbox(
        "Create Lifestyle Shot",
        help="Generate lifestyle context for the product"
    )
    if config["lifestyle_shot"]:
        config["scene_description"] = st.sidebar.text_area(
            "Scene Description",
            help="Describe the environment for the lifestyle shot"
        )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    return config 
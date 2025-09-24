import streamlit as st
from datetime import datetime, timedelta
import random
from config.demo_config import SAMPLE_PROMPTS, ENHANCEMENT_PRESETS, FEATURE_TOUR, TIPS_AND_TRICKS
from components.activity_dashboard import show_real_time_activities, show_activity_statistics, show_recent_images

def show_dashboard():
    """Display the main dashboard with user stats and quick actions."""
    
    # Welcome message
    user_name = st.session_state.get('user_info', {}).get('full_name', st.session_state.get('username', 'User'))
    current_hour = datetime.now().hour
    
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h2 style="margin: 0; font-size: 2rem;">{greeting}, {user_name}! 👋</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Ready to create some amazing ads today?</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Real-time statistics from database
    show_activity_statistics()
    
    # Quick actions section
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎨 Generate New Image", use_container_width=True, type="primary"):
            st.session_state.active_tab = 1  # Generate Image tab
            st.session_state.quick_action = "generate"
            st.success("🚀 Navigating to Image Generation...")
            st.rerun()
    
    with col2:
        if st.button("📸 Create Lifestyle Shot", use_container_width=True):
            st.session_state.active_tab = 2  # Lifestyle Shot tab
            st.session_state.quick_action = "lifestyle"
            st.success("🚀 Navigating to Lifestyle Shot...")
            st.rerun()
    
    with col3:
        if st.button("✨ Enhance Image", use_container_width=True):
            st.session_state.active_tab = 3  # Generative Fill tab (for image enhancement)
            st.session_state.quick_action = "enhance"
            st.success("🚀 Navigating to Image Enhancement...")
            st.rerun()
    
    # Recent activity and tips
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_real_time_activities()
    
    with col2:
        show_daily_tip()
        
    # Recent images gallery
    show_recent_images()

def show_stat_card(title, value, icon, color):
    """Display a statistics card."""
    st.markdown(f"""
    <div style="background: {color}; color: white; padding: 1.5rem; border-radius: 10px; 
                text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.25rem;">{value}</div>
        <div style="font-size: 0.9rem; opacity: 0.9;">{title}</div>
    </div>
    """, unsafe_allow_html=True)

def get_user_stats():
    """Get user statistics (simulated for demo)."""
    # In a real app, this would query a database
    base_stats = {
        'images_generated': random.randint(15, 150),
        'projects': random.randint(3, 25),
        'success_rate': random.randint(85, 99),
        'time_saved': random.randint(5, 50)
    }
    
    # Store in session state to maintain consistency
    if 'user_stats' not in st.session_state:
        st.session_state.user_stats = base_stats
    
    return st.session_state.user_stats

def show_recent_activity():
    """Display recent user activity."""
    st.markdown("### 📊 Recent Activity")
    
    activities = [
        ("Generated product image", "2 minutes ago", "🎨", "success"),
        ("Created lifestyle shot", "15 minutes ago", "📸", "info"),
        ("Enhanced image quality", "1 hour ago", "✨", "success"),
        ("Removed background", "2 hours ago", "✂️", "info"),
        ("Added shadow effect", "Yesterday", "🌟", "success")
    ]
    
    for activity, time_ago, icon, status in activities:
        status_color = "#4ECDC4" if status == "success" else "#667eea"
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 0.75rem; margin: 0.5rem 0; 
                    background: rgba(255,255,255,0.05); border-radius: 8px; 
                    border-left: 3px solid {status_color};">
            <span style="font-size: 1.5rem; margin-right: 1rem;">{icon}</span>
            <div style="flex: 1;">
                <div style="font-weight: 500; margin-bottom: 0.25rem;">{activity}</div>
                <div style="font-size: 0.85rem; color: #666;">{time_ago}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_daily_tip():
    """Display a daily tip."""
    st.markdown("### 💡 Daily Tip")
    
    # Get a consistent tip for the day
    day_of_year = datetime.now().timetuple().tm_yday
    tip = TIPS_AND_TRICKS[day_of_year % len(TIPS_AND_TRICKS)]
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #FFD93D, #FF6B6B); 
                padding: 1.5rem; border-radius: 10px; color: white;">
        <div style="font-size: 1.1rem; font-weight: 500; margin-bottom: 0.5rem;">Tip of the Day</div>
        <div style="font-size: 0.95rem; line-height: 1.4;">{tip}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick prompt suggestions
    st.markdown("### 🎯 Quick Prompts")
    
    if st.button("🎲 Get Random Prompt", use_container_width=True):
        prompt = random.choice(SAMPLE_PROMPTS)
        st.session_state.suggested_prompt = prompt
        st.success(f"Try this: {prompt}")
    
    if st.session_state.get('suggested_prompt'):
        if st.button("🚀 Use This Prompt", use_container_width=True, type="primary"):
            st.session_state.active_tab = 0
            st.session_state.quick_prompt = st.session_state.suggested_prompt
            st.rerun()

def show_feature_tour():
    """Display an interactive feature tour."""
    st.markdown("### 🗺️ Feature Tour")
    st.markdown("New to AdSnap Studio? Take a quick tour of our features!")
    
    if 'tour_step' not in st.session_state:
        st.session_state.tour_step = 0
    
    if st.session_state.tour_step < len(FEATURE_TOUR):
        feature = FEATURE_TOUR[st.session_state.tour_step]
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); 
                    padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(102, 126, 234, 0.3);">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <span style="font-size: 2rem; margin-right: 1rem;">{feature['icon']}</span>
                <h4 style="margin: 0; color: #667eea;">Step {st.session_state.tour_step + 1}: {feature['title']}</h4>
            </div>
            <p style="margin-bottom: 1rem; color: #666;">{feature['description']}</p>
            <div style="background: rgba(102, 126, 234, 0.1); padding: 0.75rem; border-radius: 5px; 
                        font-style: italic; color: #667eea;">
                💡 {feature['demo_action']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("⏮️ Previous", disabled=st.session_state.tour_step == 0):
                st.session_state.tour_step -= 1
                st.rerun()
        
        with col2:
            if st.button("⏭️ Next", disabled=st.session_state.tour_step == len(FEATURE_TOUR) - 1):
                st.session_state.tour_step += 1
                st.rerun()
        
        with col3:
            if st.button("✅ Finish Tour"):
                st.session_state.tour_completed = True
                st.session_state.tour_step = 0
                st.success("Tour completed! You're ready to create amazing ads! 🎉")
                st.rerun()
    
    else:
        st.success("🎉 Tour completed! You're all set to create amazing ads!")
        if st.button("🔄 Restart Tour"):
            st.session_state.tour_step = 0
            st.rerun()

def show_project_gallery():
    """Display user's project gallery."""
    st.markdown("### 🖼️ Your Projects")
    
    # Simulate project data
    projects = [
        {"name": "Summer Campaign", "images": 8, "created": "2 days ago", "status": "completed"},
        {"name": "Product Launch", "images": 12, "created": "1 week ago", "status": "in_progress"},
        {"name": "Holiday Ads", "images": 6, "created": "2 weeks ago", "status": "completed"},
    ]
    
    for project in projects:
        status_color = "#4ECDC4" if project["status"] == "completed" else "#FFD93D"
        status_text = "Completed" if project["status"] == "completed" else "In Progress"
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; 
                    padding: 1rem; margin: 0.5rem 0; background: rgba(255,255,255,0.05); 
                    border-radius: 8px; border-left: 3px solid {status_color};">
            <div>
                <div style="font-weight: 500; margin-bottom: 0.25rem;">{project['name']}</div>
                <div style="font-size: 0.85rem; color: #666;">{project['images']} images • {project['created']}</div>
            </div>
            <div style="background: {status_color}; color: white; padding: 0.25rem 0.75rem; 
                        border-radius: 15px; font-size: 0.8rem;">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)
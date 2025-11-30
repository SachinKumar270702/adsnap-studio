import streamlit as st
from datetime import datetime, timedelta
import random
import textwrap
from config.demo_config import SAMPLE_PROMPTS, ENHANCEMENT_PRESETS, FEATURE_TOUR, TIPS_AND_TRICKS
from components.activity_dashboard import show_real_time_activities, show_activity_statistics, show_recent_images
from components.interactive_ui import show_lottie_animation

def show_dashboard():
    """Display the main dashboard with user stats and quick actions."""
    
    # Welcome message with Lottie
    user_name = st.session_state.get('user_info', {}).get('full_name', st.session_state.get('username', 'User'))
    current_hour = datetime.now().hour
    
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(textwrap.dedent(f"""
        <div class="glass-card animate-fade-in" style="padding: 2.5rem; height: 100%; display: flex; flex-direction: column; justify-content: center; background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(56, 189, 248, 0.2) 100%); border: 1px solid rgba(255, 255, 255, 0.1);">
            <h2 style="margin: 0; font-size: 2.5rem; background: linear-gradient(90deg, #fff, #cbd5e1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"><i class="fas fa-hand-sparkles" style="color: #fbbf24;"></i> {greeting}, {user_name}!</h2>
            <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 1.1rem;">Ready to create some amazing ads today?</p>
        </div>
        <div style="font-size: 2rem; margin-bottom: 0.5rem; color: {color};">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
    </div>
    """), unsafe_allow_html=True)

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
    st.markdown("### <i class='fas fa-chart-line'></i> Recent Activity", unsafe_allow_html=True)
    
    activities = [
        ("Generated product image", "2 minutes ago", '<i class="fas fa-palette"></i>', "success"),
        ("Created lifestyle shot", "15 minutes ago", '<i class="fas fa-camera"></i>', "info"),
        ("Enhanced image quality", "1 hour ago", '<i class="fas fa-magic"></i>', "success"),
        ("Removed background", "2 hours ago", '<i class="fas fa-scissors"></i>', "info"),
        ("Added shadow effect", "Yesterday", '<i class="fas fa-star"></i>', "success")
    ]
    
    for i, (activity, time_ago, icon, status) in enumerate(activities):
        status_color = "var(--secondary-color)" if status == "info" else "var(--primary-color)"
        
        st.markdown(textwrap.dedent(f"""
        <div class="glass-panel animate-fade-in stagger-{min(i+1, 3)}" style="display: flex; align-items: center; padding: 1rem; margin: 0.75rem 0; 
                    border-radius: 0.75rem; border-left: 3px solid {status_color};">
            <span style="font-size: 1.5rem; margin-right: 1rem; color: {status_color};">{icon}</span>
            <div style="flex: 1;">
                <div style="font-weight: 600; margin-bottom: 0.25rem; color: var(--text-color);">{activity}</div>
                <div style="font-size: 0.85rem; color: var(--text-secondary);">{time_ago}</div>
            </div>
        </div>
        """), unsafe_allow_html=True)

def show_daily_tip():
    """Display a daily tip."""
    st.markdown("### <i class='fas fa-lightbulb'></i> Daily Tip", unsafe_allow_html=True)
    
    # Get a consistent tip for the day
    day_of_year = datetime.now().timetuple().tm_yday
    tip = TIPS_AND_TRICKS[day_of_year % len(TIPS_AND_TRICKS)]
    
    st.markdown(textwrap.dedent(f"""
    <div class="glass-card animate-fade-in" style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(239, 68, 68, 0.1)); 
                padding: 1.5rem; border: 1px solid rgba(245, 158, 11, 0.2);">
        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem; color: #f59e0b;"><i class="fas fa-lightbulb"></i> Tip of the Day</div>
        <div style="font-size: 0.95rem; line-height: 1.5; opacity: 0.95; color: var(--text-color);">{tip}</div>
    </div>
    """), unsafe_allow_html=True)
    
    # Quick prompt suggestions
    st.markdown("### <i class='fas fa-bullseye'></i> Quick Prompts", unsafe_allow_html=True)
    
    if st.button("Get Random Prompt", use_container_width=True, key="dash_tip_random_prompt"):
        prompt = random.choice(SAMPLE_PROMPTS)
        st.session_state.suggested_prompt = prompt
        st.success(f"Try this: {prompt}")
    
    if st.session_state.get('suggested_prompt'):
        if st.button("Use This Prompt", use_container_width=True, type="primary", key="dash_tip_use_prompt"):
            st.session_state.active_tab = 0
            st.session_state.quick_prompt = st.session_state.suggested_prompt
            st.rerun()

def show_feature_tour():
    """Display an interactive feature tour."""
    st.markdown("### <i class='fas fa-map-signs'></i> Feature Tour", unsafe_allow_html=True)
    st.markdown("New to AdSnap Studio? Take a quick tour of our features!")
    
    if 'tour_step' not in st.session_state:
        st.session_state.tour_step = 0
    
    if st.session_state.tour_step < len(FEATURE_TOUR):
        feature = FEATURE_TOUR[st.session_state.tour_step]
        
        st.markdown(textwrap.dedent(f"""
        <div class="feature-card animate-fade-in">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <span style="font-size: 2rem; margin-right: 1rem; color: var(--primary-color);">{feature['icon']}</span>
                <h4 style="margin: 0; color: var(--text-color);">Step {st.session_state.tour_step + 1}: {feature['title']}</h4>
            </div>
            <p style="margin-bottom: 1rem; color: var(--text-secondary);">{feature['description']}</p>
            <div style="background: rgba(99, 102, 241, 0.1); padding: 0.75rem; border-radius: 0.5rem; 
                        font-style: italic; color: var(--primary-color); border: 1px solid rgba(99, 102, 241, 0.2);">
                <i class="fas fa-lightbulb"></i> {feature['demo_action']}
            </div>
        </div>
        """), unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("Previous", disabled=st.session_state.tour_step == 0, key="tour_btn_prev"):
                st.session_state.tour_step -= 1
                st.rerun()
        
        with col2:
            if st.button("Next", disabled=st.session_state.tour_step == len(FEATURE_TOUR) - 1, key="tour_btn_next"):
                st.session_state.tour_step += 1
                st.rerun()
        
        with col3:
            if st.button("Finish Tour", key="tour_btn_finish"):
                st.session_state.tour_completed = True
                st.session_state.tour_step = 0
                st.success("Tour completed! You're ready to create amazing ads! 🎉")
                st.rerun()
    
    else:
        st.success("🎉 Tour completed! You're all set to create amazing ads!")
        if st.button("Restart Tour", key="tour_btn_restart"):
            st.session_state.tour_step = 0
            st.rerun()

def show_project_gallery():
    """Display user's project gallery."""
    st.markdown("### <i class='fas fa-images'></i> Your Projects", unsafe_allow_html=True)
    
    # Simulate project data
    projects = [
        {"name": "Summer Campaign", "images": 8, "created": "2 days ago", "status": "completed"},
        {"name": "Product Launch", "images": 12, "created": "1 week ago", "status": "in_progress"},
        {"name": "Holiday Ads", "images": 6, "created": "2 weeks ago", "status": "completed"},
    ]
    
    for i, project in enumerate(projects):
        status_color = "var(--primary-color)" if project["status"] == "completed" else "var(--secondary-color)"
        status_text = "Completed" if project["status"] == "completed" else "In Progress"
        
        st.markdown(textwrap.dedent(f"""
        <div class="glass-panel animate-fade-in stagger-{min(i+1, 3)}" style="display: flex; justify-content: space-between; align-items: center; 
                    padding: 1rem; margin: 0.75rem 0; border-radius: 0.75rem; border-left: 3px solid {status_color};">
            <div>
                <div style="font-weight: 600; margin-bottom: 0.25rem; color: var(--text-color);">{project['name']}</div>
                <div style="font-size: 0.85rem; color: var(--text-secondary);">{project['images']} images • {project['created']}</div>
            </div>
            <div style="background: {status_color}; color: white; padding: 0.25rem 0.75rem; 
                        border-radius: 9999px; font-size: 0.75rem; font-weight: 600;">{status_text}</div>
        </div>
        """), unsafe_allow_html=True)
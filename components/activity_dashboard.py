import streamlit as st
from datetime import datetime, timedelta
import random

def show_real_time_activities():
    """Display real-time user activities."""
    st.markdown("### <i class='fas fa-sync-alt'></i> Recent Activities", unsafe_allow_html=True)
    
    # Simulate recent activities
    activities = [
        ("Generated image", "2 minutes ago", '<i class="fas fa-palette"></i>'),
        ("Added shadow effect", "5 minutes ago", '<i class="fas fa-star"></i>'),
        ("Created lifestyle shot", "10 minutes ago", '<i class="fas fa-camera"></i>'),
        ("Enhanced image quality", "15 minutes ago", '<i class="fas fa-magic"></i>'),
        ("Removed background", "20 minutes ago", '<i class="fas fa-scissors"></i>')
    ]
    
    for activity, time_ago, icon in activities:
        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 0.5rem; margin: 0.25rem 0; 
                    background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
            <span style="font-size: 1.5rem; margin-right: 1rem;">{icon}</span>
            <div>
                <div style="font-weight: 500;">{activity}</div>
                <div style="font-size: 0.8rem; color: #666;">{time_ago}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_activity_statistics():
    """Display activity statistics."""
    st.markdown("### <i class='fas fa-chart-bar'></i> Usage Statistics", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Images Generated", "127", "+12")
    
    with col2:
        st.metric("Processing Time", "2.3s", "-0.5s")
    
    with col3:
        st.metric("Success Rate", "98.5%", "+1.2%")

def show_recent_images():
    """Display recent images."""
    st.markdown("### <i class='fas fa-images'></i> Recent Images", unsafe_allow_html=True)
    st.info("Recent images will appear here after you start generating or editing images.")

def track_current_activity(activity_type: str, description: str, details: dict = None):
    """Track current user activity (simplified version)."""
    # For now, just store in session state for demo purposes
    if 'user_activities' not in st.session_state:
        st.session_state.user_activities = []
    
    activity = {
        'type': activity_type,
        'description': description,
        'details': details or {},
        'timestamp': datetime.now().isoformat()
    }
    
    st.session_state.user_activities.insert(0, activity)
    # Keep only last 50 activities
    st.session_state.user_activities = st.session_state.user_activities[:50]
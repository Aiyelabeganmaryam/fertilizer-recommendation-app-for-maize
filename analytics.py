# Analytics and Usage Tracking Enhancement
# Add this to the top of your advanced_fertilizer_app.py file

import streamlit as st
from datetime import datetime
import json
import os

# Initialize session state for analytics
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()
    st.session_state.page_views = 0
    st.session_state.user_type = None
    st.session_state.recommendations_generated = 0

# Simple analytics function
def track_usage(event_type, user_type=None, details=None):
    """Track user interactions for analytics"""
    try:
        analytics_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_type': user_type or st.session_state.get('user_type', 'unknown'),
            'session_duration': str(datetime.now() - st.session_state.session_start),
            'details': details
        }
        
        # In a production app, you'd send this to an analytics service
        # For now, we'll just increment session counters
        if event_type == 'page_view':
            st.session_state.page_views += 1
        elif event_type == 'recommendation_generated':
            st.session_state.recommendations_generated += 1
            
    except Exception as e:
        pass  # Don't break the app if analytics fail

# Add to your sidebar
def display_session_stats():
    """Display session statistics in sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 Session Stats")
        st.write(f"⏱️ Session time: {str(datetime.now() - st.session_state.session_start).split('.')[0]}")
        st.write(f"👀 Page views: {st.session_state.page_views}")
        st.write(f"🌾 Recommendations: {st.session_state.recommendations_generated}")
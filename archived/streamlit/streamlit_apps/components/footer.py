"""
Footer component
"""
import streamlit as st
from ..config import VERSION


def render_footer():
    """Render page footer"""
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption(f"🔮 PCA Agent v{VERSION}")
    
    with col2:
        st.caption("© 2025 All Rights Reserved")
    
    with col3:
        st.caption("Powered by AI & ML")

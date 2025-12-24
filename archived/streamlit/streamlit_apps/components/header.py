"""
Header component
"""
import streamlit as st


def render_header(title=None, subtitle=None):
    """
    Render page header
    
    Args:
        title: Page title
        subtitle: Page subtitle
    """
    if title:
        st.markdown(f'<h1 class="main-header">{title}</h1>', unsafe_allow_html=True)
    
    if subtitle:
        st.markdown(f"**{subtitle}**")
    
    st.markdown("---")

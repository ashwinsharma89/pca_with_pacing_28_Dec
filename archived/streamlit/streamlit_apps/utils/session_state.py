"""
Session state management utilities
"""
import streamlit as st
from ..config import SESSION_KEYS


def init_session_state():
    """Initialize session state with default values"""
    
    # Historical data
    if SESSION_KEYS['historical_data'] not in st.session_state:
        st.session_state[SESSION_KEYS['historical_data']] = None
    
    # Predictive models
    if SESSION_KEYS['predictor'] not in st.session_state:
        st.session_state[SESSION_KEYS['predictor']] = None
    
    if SESSION_KEYS['epi'] not in st.session_state:
        st.session_state[SESSION_KEYS['epi']] = None
    
    if SESSION_KEYS['optimizer'] not in st.session_state:
        st.session_state[SESSION_KEYS['optimizer']] = None
    
    # Current campaign
    if SESSION_KEYS['current_campaign'] not in st.session_state:
        st.session_state[SESSION_KEYS['current_campaign']] = None
    
    # Analysis results
    if SESSION_KEYS['analysis_results'] not in st.session_state:
        st.session_state[SESSION_KEYS['analysis_results']] = None
    
    # Uploaded files
    if SESSION_KEYS['uploaded_files'] not in st.session_state:
        st.session_state[SESSION_KEYS['uploaded_files']] = []


def get_session_value(key, default=None):
    """Get value from session state"""
    return st.session_state.get(key, default)


def set_session_value(key, value):
    """Set value in session state"""
    st.session_state[key] = value


def clear_session_state():
    """Clear all session state"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()


def has_historical_data():
    """Check if historical data is loaded"""
    return st.session_state.get(SESSION_KEYS['historical_data']) is not None


def has_predictor_model():
    """Check if predictor model is loaded"""
    return st.session_state.get(SESSION_KEYS['predictor']) is not None


def get_historical_data():
    """Get historical data from session state"""
    return st.session_state.get(SESSION_KEYS['historical_data'])


def set_historical_data(data):
    """Set historical data in session state"""
    st.session_state[SESSION_KEYS['historical_data']] = data


def get_predictor():
    """Get predictor model from session state"""
    return st.session_state.get(SESSION_KEYS['predictor'])


def set_predictor(predictor):
    """Set predictor model in session state"""
    st.session_state[SESSION_KEYS['predictor']] = predictor

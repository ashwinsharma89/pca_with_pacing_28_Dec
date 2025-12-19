"""
Utility functions for PCA Agent Streamlit applications
"""

from .styling import apply_custom_css, get_color_scheme
from .session_state import (
    init_session_state, 
    get_session_value, 
    set_session_value,
    has_historical_data,
    has_predictor_model,
    get_historical_data,
    set_historical_data,
    get_predictor,
    set_predictor,
    clear_session_state
)
from .data_loader import load_historical_data, load_model, save_model
from .helpers import format_currency, format_percentage, format_number

# Create alias for has_predictor
has_predictor = has_predictor_model

__all__ = [
    'apply_custom_css',
    'get_color_scheme',
    'init_session_state',
    'get_session_value',
    'set_session_value',
    'has_historical_data',
    'has_predictor_model',
    'has_predictor',
    'get_historical_data',
    'set_historical_data',
    'get_predictor',
    'set_predictor',
    'clear_session_state',
    'load_historical_data',
    'load_model',
    'save_model',
    'format_currency',
    'format_percentage',
    'format_number'
]

"""
Styling utilities for PCA Agent Streamlit applications
"""
import streamlit as st
from ..config import PRIMARY_COLOR, SECONDARY_COLOR, SUCCESS_COLOR, WARNING_COLOR, DANGER_COLOR


def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""
    
    css = f"""
    <style>
    /* Main theme colors */
    :root {{
        --primary-color: {PRIMARY_COLOR};
        --secondary-color: {SECONDARY_COLOR};
        --success-color: {SUCCESS_COLOR};
        --warning-color: {WARNING_COLOR};
        --danger-color: {DANGER_COLOR};
    }}
    
    /* Remove white background at top */
    .main {{
        background-color: #0e1117;
        padding-top: 0rem;
    }}
    
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 0rem;
        background-color: #0e1117;
    }}
    
    /* Streamlit header */
    header {{
        background-color: #0e1117 !important;
    }}
    
    .stApp {{
        background-color: #0e1117;
    }}
    
    /* Header styling */
    .main-header {{
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }}
    
    .sub-header {{
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }}
    
    /* Card styling */
    .metric-card {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }}
    
    .info-card {{
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid {PRIMARY_COLOR};
        margin-bottom: 1rem;
    }}
    
    .success-card {{
        background: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid {SUCCESS_COLOR};
        margin-bottom: 1rem;
    }}
    
    .warning-card {{
        background: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid {WARNING_COLOR};
        margin-bottom: 1rem;
    }}
    
    .danger-card {{
        background: #f8d7da;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid {DANGER_COLOR};
        margin-bottom: 1rem;
    }}
    
    /* Button styling */
    .stButton>button {{
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    
    /* Metric styling */
    .metric-container {{
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {PRIMARY_COLOR};
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }}
    
    /* Progress bar */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%);
    }}
    
    /* File uploader */
    .uploadedFile {{
        border-radius: 8px;
        border: 2px dashed {PRIMARY_COLOR};
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        font-weight: 600;
        background: #f8f9fa;
        border-radius: 8px;
    }}
    
    /* Table styling */
    .dataframe {{
        border-radius: 8px;
        overflow: hidden;
    }}
    
    /* Success message */
    .element-container .stSuccess {{
        background: {SUCCESS_COLOR};
        color: white;
        border-radius: 8px;
        padding: 1rem;
    }}
    
    /* Warning message */
    .element-container .stWarning {{
        background: {WARNING_COLOR};
        color: white;
        border-radius: 8px;
        padding: 1rem;
    }}
    
    /* Error message */
    .element-container .stError {{
        background: {DANGER_COLOR};
        color: white;
        border-radius: 8px;
        padding: 1rem;
    }}
    
    /* Info message */
    .element-container .stInfo {{
        background: {PRIMARY_COLOR};
        color: white;
        border-radius: 8px;
        padding: 1rem;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: #f1f1f1;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {PRIMARY_COLOR};
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {SECONDARY_COLOR};
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def get_color_scheme():
    """Get the color scheme dictionary"""
    return {
        'primary': PRIMARY_COLOR,
        'secondary': SECONDARY_COLOR,
        'success': SUCCESS_COLOR,
        'warning': WARNING_COLOR,
        'danger': DANGER_COLOR
    }


def create_metric_card(label, value, delta=None, delta_color="normal"):
    """Create a styled metric card"""
    
    delta_html = ""
    if delta:
        delta_class = "success" if delta_color == "normal" else "danger"
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'
    
    html = f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    
    return html


def create_info_box(title, content, box_type="info"):
    """Create a styled info box"""
    
    html = f"""
    <div class="{box_type}-card">
        <h4>{title}</h4>
        <p>{content}</p>
    </div>
    """
    
    return html

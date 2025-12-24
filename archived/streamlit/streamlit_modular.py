"""
Modular Streamlit App - Main Entry Point.

This is the refactored version of streamlit_app.py with:
1. Modular component structure (< 500 lines per file)
2. Consolidated single app version
3. Clean code with proper logging (no debug prints)
4. Component-level caching strategy

Usage:
    streamlit run app_modular.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

import streamlit as st
import logging
import time
import re
import html
from datetime import datetime
from typing import Dict, Optional, Tuple, List, Any
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from loguru import logger

# Load environment variables BEFORE importing PCA Agent components
load_dotenv()

# Import all PCA Agent components
from src.analytics import MediaAnalyticsExpert
from src.evaluation.query_tracker import QueryTracker
from src.query_engine.nl_to_sql import NaturalLanguageQueryEngine
from src.visualization import SmartChartGenerator
from src.utils.data_loader import DataLoader, normalize_campaign_dataframe
from src.agents.channel_specialists import ChannelRouter
from src.agents.b2b_specialist_agent import B2BSpecialistAgent
from src.models.campaign import CampaignContext, BusinessModel, TargetAudienceLevel
from src.knowledge.benchmark_engine import DynamicBenchmarkEngine
from src.agents.enhanced_reasoning_agent import EnhancedReasoningAgent
from src.agents.enhanced_visualization_agent import EnhancedVisualizationAgent
from src.agents.visualization_filters import SmartFilterEngine
from src.streamlit_integration import get_streamlit_db_manager
from src.agents.filter_presets import FilterPresets
from streamlit_components.smart_filters import InteractiveFilterPanel, QuickFilterBar, FilterPresetsUI
from streamlit_components.data_loader import DataLoaderComponent, load_cached_dataframe
from streamlit_components.analysis_runner import AnalysisRunnerComponent, AnalysisHistoryComponent
from streamlit_components.caching_strategy import CacheManager
from src.utils.data_validator import validate_and_clean_data

# Load environment variables
load_dotenv()

# ============================================
# NUMBER FORMATTING UTILITIES
# ============================================
def format_number(value: float, format_type: str = 'number') -> str:
    """
    Format numbers for display in summaries and UI.
    
    Args:
        value: The numeric value to format
        format_type: 'currency' for $, 'percent' for %, 'number' for K/M formatting
    
    Returns:
        Formatted string
    """
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    
    if format_type == 'currency':
        if abs(value) >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        elif abs(value) >= 1_000:
            return f"${value/1_000:.1f}K"
        else:
            return f"${value:.2f}"
    
    elif format_type == 'percent':
        return f"{value:.2f}%"
    
    else:  # number
        if abs(value) >= 1_000_000:
            return f"{value/1_000_000:.2f}M"
        elif abs(value) >= 1_000:
            return f"{value/1_000:.1f}K"
        else:
            return f"{value:.2f}"

def format_summary_text(text: str) -> str:
    """
    Format summary text to fix number formatting issues from LLM output.
    
    Uses the production-grade TextCleaningPipeline for comprehensive fixes:
    - Numbers merged with words (4.45Mgenerated -> 4.45M generated)
    - Missing spaces after punctuation (word.Another -> word. Another)
    - Concatenated words (resultinginanoverall -> resulting in an overall)
    - CamelCase splitting (TheOverall -> The Overall)
    - Number-word boundaries (CPA of5.47 -> CPA of 5.47)
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    
    try:
        # Use the new summary formatter (post-processing)
        from src.utils.summary_formatter import _format_text
        return _format_text(text)
    except ImportError:
        # Fallback if module not available
        logger.warning("summary_formatter not available, using basic cleanup")
        # Basic cleanup
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
        text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
        text = re.sub(r'\.([A-Za-z])', r'. \1', text)
        text = re.sub(r',([A-Za-z])', r', \1', text)
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()
    except Exception as e:
        logger.warning(f"Error formatting summary text: {e}")
        return text

def create_dual_axis_chart(
    df: pd.DataFrame,
    x_col: str,
    primary_metric: str,
    secondary_metric: str,
    title: str = "Dual Axis Analysis",
    primary_color: str = "#667eea",
    secondary_color: str = "#f093fb"
) -> go.Figure:
    """
    Create a dual-axis chart with primary metric as bars and secondary as line.
    
    Args:
        df: DataFrame with the data
        x_col: Column to use for x-axis (e.g., 'Platform', 'Date')
        primary_metric: Primary metric for bar chart (left y-axis)
        secondary_metric: Secondary metric for line chart (right y-axis)
        title: Chart title
        primary_color: Color for primary metric bars
        secondary_color: Color for secondary metric line
    
    Returns:
        Plotly figure with dual axes
    """
    # Aggregate data by x_col
    agg_df = df.groupby(x_col).agg({
        primary_metric: 'sum',
        secondary_metric: 'sum'
    }).reset_index()
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Primary metric as bars
    fig.add_trace(
        go.Bar(
            x=agg_df[x_col],
            y=agg_df[primary_metric],
            name=primary_metric,
            marker_color=primary_color,
            yaxis='y'
        )
    )
    
    # Secondary metric as line
    fig.add_trace(
        go.Scatter(
            x=agg_df[x_col],
            y=agg_df[secondary_metric],
            name=secondary_metric,
            mode='lines+markers',
            line=dict(color=secondary_color, width=3),
            marker=dict(size=10),
            yaxis='y2'
        )
    )
    
    # Update layout for dual axes
    fig.update_layout(
        title=title,
        xaxis=dict(title=x_col),
        yaxis=dict(
            title=dict(text=primary_metric, font=dict(color=primary_color)),
            tickfont=dict(color=primary_color),
            side='left'
        ),
        yaxis2=dict(
            title=dict(text=secondary_metric, font=dict(color=secondary_color)),
            tickfont=dict(color=secondary_color),
            overlaying='y',
            side='right'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        hovermode='x unified',
        template='plotly_dark'
    )
    
    return fig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Constants
CACHE_DIR = ".pca_cache"
LAST_CSV_PATH = os.path.join(CACHE_DIR, "last_campaign_data.csv")
os.makedirs(CACHE_DIR, exist_ok=True)
SAMPLE_DATA_PATH = Path(__file__).parent / "data" / "historical_campaigns_sample.csv"

REQUIRED_COLUMNS = ["Campaign_Name", "Platform", "Spend"]
RECOMMENDED_COLUMNS = ["Conversions", "Revenue", "Date", "Placement"]

# Page configuration
st.set_page_config(
    page_title="PCA Agent - Auto Analysis + Q&A",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function for API keys
def get_api_key(secret_key: str, env_var: str) -> Optional[str]:
    """Return API key from Streamlit secrets, falling back to environment vars."""
    try:
        api_keys = st.secrets["api_keys"]
        value = api_keys.get(secret_key)
        if value:
            return value
    except Exception:
        pass
    return os.getenv(env_var)

# Enterprise CSS Styling
st.markdown("""
<style>
    /* ENTERPRISE DESIGN SYSTEM - PCA AGENT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .insight-card {
        background: rgba(102, 126, 234, 0.1);
        padding: 1.5rem;
        border-left: 4px solid #667eea;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        color: inherit;
    }
    
    .insight-card:empty {
        display: none;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables with all features."""
    defaults = {
        "df": None,
        "df_loaded_from_cache": False,
        "analysis_complete": False,
        "analysis_data": None,
        "analysis_history": [],
        "current_page": "home",
        "query_tracker": QueryTracker(),
        "nl_engine": None,
        "chart_generator": None,
        "channel_router": None,
        "benchmark_engine": None,
        "reasoning_agent": None,
        "viz_agent": None,
        "filter_engine": None,
        "analytics_expert": None,
        "b2b_specialist": None,
        "chat_history": [],
        "active_filters": {},
        "selected_campaigns": [],
        "comparison_mode": False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

@st.cache_resource
def initialize_agents():
    """Initialize all AI agents and engines."""
    try:
        analytics_expert = MediaAnalyticsExpert()
        channel_router = ChannelRouter()
        benchmark_engine = DynamicBenchmarkEngine()
        reasoning_agent = EnhancedReasoningAgent()
        viz_agent = EnhancedVisualizationAgent()
        filter_engine = SmartFilterEngine()
        chart_generator = SmartChartGenerator()
        b2b_specialist = B2BSpecialistAgent()
        
        return {
            "analytics_expert": analytics_expert,
            "channel_router": channel_router,
            "benchmark_engine": benchmark_engine,
            "reasoning_agent": reasoning_agent,
            "viz_agent": viz_agent,
            "filter_engine": filter_engine,
            "chart_generator": chart_generator,
            "b2b_specialist": b2b_specialist
        }
    except Exception as e:
        logger.error(f"Error initializing agents: {e}")
        return None


def render_sidebar():
    """Render sidebar navigation and controls."""
    with st.sidebar:
        st.title("📊 PCA Agent")
        st.caption("Performance Campaign Analytics")
        
        st.divider()
        
        # Navigation
        st.subheader("Navigation")
        
        st.info(
            """
            🔬 **Need Diagnostics?**
            Run `streamlit run streamlit_modular_v1.py --server.port 8503`
            to access the dedicated diagnostics experience.
            """
        )

        page = st.radio(
            "Select Page",
            options=["Home", "Analysis", "In-Depth Analysis", "Visualizations", "Q&A", "Settings"],
            key="nav_radio"
        )
        
        st.session_state.current_page = page.lower()
        
        st.divider()
        
        # Data status
        st.subheader("Data Status")
        
        if st.session_state.df is not None:
            st.success(f"✅ Data loaded: {len(st.session_state.df)} rows")
            
            if st.button("🗑️ Clear Data"):
                st.session_state.df = None
                st.session_state.analysis_complete = False
                st.session_state.analysis_data = None
                st.rerun()
        else:
            st.info("No data loaded")
        
        st.divider()
        
        # Analysis history
        if st.session_state.get('analysis_history'):
            AnalysisHistoryComponent.render_history()
        
        st.divider()
        
        # Cache management
        CacheManager.render_cache_controls()


def render_home_page():
    """Render home page."""
    st.markdown('<div class="main-header">🏠 Welcome to PCA Agent</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Performance Campaign Analytics Agent
    
    A modular, production-ready application for campaign performance analysis.
    
    **Features:**
    - 📁 Multi-source data loading (CSV, Excel, S3, Azure, GCS)
    - 🤖 AI-powered auto-analysis
    - 💬 Natural language Q&A
    - 📊 Interactive visualizations
    - 🗄️ Smart caching for performance
    
    **Get Started:**
    1. Upload or connect your data using the section below
    2. Go to **Analysis** to run AI-powered insights
    3. Use **Q&A** to ask questions about your data
    """)
    
    st.markdown("### 📁 Upload or Connect Your Data")
    render_data_upload_section(show_header=False)
    
    st.divider()
    
    # Quick stats
    if st.session_state.df is not None:
        st.subheader("📈 Quick Stats")
        
        df = st.session_state.df
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        
        with col2:
            st.metric("Columns", len(df.columns))
        
        with col3:
            if 'Spend' in df.columns:
                st.metric("Total Spend", f"${df['Spend'].sum():,.2f}")
        
        with col4:
            if 'Clicks' in df.columns:
                st.metric("Total Clicks", f"{df['Clicks'].sum():,}")


def render_data_upload_section(show_header: bool = True):
    """Render data upload section with optional header."""
    if show_header:
        st.markdown('<div class="main-header">📁 Data Upload</div>', unsafe_allow_html=True)
    
    # Try to load cached data first
    if st.session_state.df is None and not st.session_state.df_loaded_from_cache:
        cached_df = load_cached_dataframe()
        if cached_df is not None:
            st.session_state.df = cached_df
            st.session_state.df_loaded_from_cache = True
            st.success("✅ Loaded cached data from previous session")
    
    # File uploader
    df = DataLoaderComponent.render_file_uploader()
    
    # Validate and clean uploaded data
    if df is not None and st.session_state.df is None:
        with st.spinner("🔍 Validating and cleaning data..."):
            try:
                cleaned_df, validation_report = validate_and_clean_data(df)
                st.session_state.df = cleaned_df
                st.session_state.validation_report = validation_report
                
                # Show validation summary
                st.success(f"✅ Data validated! {validation_report['summary']['cleaned_rows']} rows, {validation_report['summary']['total_columns']} columns")
                
                # Show conversion summary
                if validation_report['conversions']:
                    with st.expander("🔄 Data Conversions Applied", expanded=True):
                        for col, conversion in validation_report['conversions'].items():
                            if col == 'Column Mappings':
                                st.markdown(f"### 📋 {conversion}")
                            else:
                                st.markdown(f"- **{col}**: {conversion}")
                
                # Show warnings if any
                if validation_report['warnings']:
                    with st.expander("⚠️ Warnings", expanded=False):
                        for warning in validation_report['warnings']:
                            st.warning(warning)
                            
            except Exception as e:
                st.error(f"❌ Validation error: {str(e)}")
                logger.error(f"Data validation error: {e}", exc_info=True)
    
    # Sample data button
    if st.session_state.df is None:
        DataLoaderComponent.render_sample_data_button()
    
    # Database Connection Options
    st.divider()
    st.markdown("### 🗄️ Database Connections")
    
    db_type = st.selectbox(
        "Select Database Type",
        [
            "None (Use File Upload)",
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "Amazon Redshift",
            "Snowflake",
            "Google BigQuery",
            "Azure SQL Database",
            "Azure Synapse",
            "Databricks",
            "Oracle",
            "SQL Server",
            "ClickHouse",
            "DuckDB"
        ],
        key="db_type_selector"
    )
    
    if db_type != "None (Use File Upload)":
        st.markdown(f"#### 🔌 {db_type} Connection")
        
        col1, col2 = st.columns(2)
        
        with col1:
            db_host = st.text_input("Host/Server", placeholder="localhost or server.database.com", key="db_host")
            db_port = st.text_input("Port", placeholder="5432", key="db_port")
            db_name = st.text_input("Database Name", placeholder="my_database", key="db_name")
        
        with col2:
            db_user = st.text_input("Username", placeholder="admin", key="db_user")
            db_password = st.text_input("Password", type="password", key="db_password")
            
            if db_type == "Snowflake":
                db_warehouse = st.text_input("Warehouse", placeholder="COMPUTE_WH", key="db_warehouse")
                db_schema = st.text_input("Schema", placeholder="PUBLIC", key="db_schema")
            elif db_type == "Google BigQuery":
                db_project = st.text_input("Project ID", placeholder="my-gcp-project", key="db_project")
                st.file_uploader("Service Account JSON", type=['json'], key="gcp_credentials")
            elif db_type == "Databricks":
                db_token = st.text_input("Access Token", type="password", key="db_token")
                db_http_path = st.text_input("HTTP Path", placeholder="/sql/1.0/warehouses/xxx", key="db_http_path")
            elif db_type in ["Azure SQL Database", "Azure Synapse"]:
                db_driver = st.selectbox("Driver", ["ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"], key="db_driver")
        
        # Query input
        st.markdown("#### 📝 SQL Query")
        db_query = st.text_area(
            "Enter your SQL query",
            placeholder="SELECT * FROM campaigns WHERE date >= '2024-01-01'",
            height=100,
            key="db_query"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔗 Connect & Load", type="primary", key="db_connect"):
                if not all([db_host, db_name, db_user]):
                    st.error("Please fill in all required connection fields")
                else:
                    with st.spinner(f"Connecting to {db_type}..."):
                        # Note: Actual connection logic would go here
                        # This is a placeholder showing the UI
                        st.info(f"🔄 Database connection feature for {db_type} is configured. Connection string would be built with provided credentials.")
                        st.warning("⚠️ Note: Full database connectivity requires additional driver installation. Contact your administrator to enable this feature.")
        
        with col2:
            if st.button("🧪 Test Connection", key="db_test"):
                st.info("Testing connection...")
    
    # Cloud storage options
    st.divider()
    DataLoaderComponent.render_cloud_storage_options()
    
    # Show data preview
    if st.session_state.df is not None:
        st.divider()
        st.subheader("📋 Data Preview")
        
        # Show first few rows
        st.dataframe(
            st.session_state.df.head(10),
            use_container_width=True,
            height=300
        )
        
        # Show column info
        with st.expander("ℹ️ Column Information"):
            col_info = st.session_state.df.dtypes.to_frame('Type')
            col_info['Non-Null Count'] = st.session_state.df.count()
            col_info['Null Count'] = st.session_state.df.isnull().sum()
            st.dataframe(col_info, use_container_width=True)


def render_data_upload_page():
    """Backward-compatible page wrapper that now delegates to home workflow."""
    render_data_upload_section(show_header=True)
    st.info("Data upload now lives on the Home page alongside quick stats and analysis entry points.")


def render_analysis_page():
    """Render AI analysis page with configurable RAG support."""
    st.markdown('<div class="main-header">🤖 AI Analysis</div>', unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload data first")
        return
    
    # Analysis configuration
    st.subheader("⚙️ Analysis Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        use_rag_summary = st.checkbox(
            "🧠 Use RAG-Enhanced Summaries",
            value=True,
            help="Use RAG (Retrieval-Augmented Generation) for more accurate and context-aware summaries"
        )
        
        include_benchmarks = st.checkbox(
            "🎯 Include Industry Benchmarks",
            value=True,
            help="Compare your performance against industry standards"
        )
    
    with col2:
        analysis_depth = st.select_slider(
            "🔍 Analysis Depth",
            options=["Quick", "Standard", "Deep"],
            value="Standard"
        )
        
        include_recommendations = st.checkbox(
            "💡 Generate Recommendations",
            value=True
        )
    
    config = {
        'use_rag_summary': use_rag_summary,
        'include_benchmarks': include_benchmarks,
        'analysis_depth': analysis_depth,
        'include_recommendations': include_recommendations
    }
    
    st.divider()
    
    # Run analysis button
    if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
        with st.spinner("🔍 Analyzing your campaign data..."):
            try:
                if st.session_state.analytics_expert is None:
                    st.session_state.analytics_expert = MediaAnalyticsExpert()
                
                analytics = st.session_state.analytics_expert
                
                if use_rag_summary:
                    st.info("🧠 Using RAG-Enhanced Analysis...")
                
                results = analytics.analyze_all(
                    st.session_state.df,
                    use_parallel=True
                )
                
                if use_rag_summary and results:
                    try:
                        rag_summary = analytics._generate_executive_summary_with_rag(
                            results.get('metrics', {}),
                            results.get('insights', []),
                            results.get('recommendations', [])
                        )
                        if rag_summary:
                            results['executive_summary'] = rag_summary
                            st.success("✅ RAG-enhanced summary generated!")
                    except Exception as e:
                        logger.warning(f"RAG summary generation failed, using standard: {e}")
                        st.warning("⚠️ Using standard summary (RAG unavailable)")
                
                if results:
                    st.session_state.analysis_data = results
                    st.session_state.analysis_complete = True
                    AnalysisHistoryComponent.save_to_history(results)
                    st.success("✅ Analysis complete!")
                    st.rerun()
                else:
                    st.error("❌ Analysis failed. Please try again.")
                    
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                logger.error(f"Analysis error: {e}", exc_info=True)
    
    if st.session_state.analysis_complete and st.session_state.analysis_data:
        st.divider()
        display_rag_analysis_results(st.session_state.analysis_data)


def display_rag_analysis_results(results: Dict[str, Any]):
    """Display RAG-enhanced analysis results."""
    
    # Executive Summary Section
    st.markdown("### 📊 Executive Summary")
    
    if 'executive_summary' in results:
        summary = results['executive_summary']
        
        # Check if RAG summary is available
        if isinstance(summary, dict) and 'brief' in summary:
            # RAG-enhanced summary - apply formatting
            brief_text = format_summary_text(summary['brief'])
            if brief_text and brief_text.strip():
                st.markdown("**🧠 RAG-Enhanced Brief Summary**")
                st.markdown(brief_text)
            
            with st.expander("📝 View Detailed Summary"):
                detailed_text = format_summary_text(summary.get('detailed', 'No detailed summary available'))
                st.markdown(detailed_text)
            
            # Show RAG metadata
            if 'rag_metadata' in summary:
                with st.expander("🔍 RAG Metadata"):
                    meta = summary['rag_metadata']
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Tokens Used", f"{meta.get('tokens_input', 0) + meta.get('tokens_output', 0):,}")
                    with col2:
                        st.metric("Model", meta.get('model', 'Unknown'))
                    with col3:
                        st.metric("Latency", f"{meta.get('latency', 0):.2f}s")
        elif isinstance(summary, dict) and ('summary_brief' in summary or 'summary_detailed' in summary):
            # Alternative RAG format - apply formatting
            brief_text = format_summary_text(summary.get('summary_brief', summary.get('brief', '')))
            if brief_text and brief_text.strip():
                st.markdown("**🧠 RAG-Enhanced Summary**")
                st.markdown(brief_text)
            
            if 'summary_detailed' in summary or 'detailed' in summary:
                with st.expander("📝 View Detailed Summary"):
                    detailed_text = format_summary_text(summary.get('summary_detailed', summary.get('detailed', '')))
                    st.markdown(detailed_text)
        else:
            # Standard summary - apply formatting
            text = summary if isinstance(summary, str) else str(summary)
            formatted_text = format_summary_text(text)
            if formatted_text and formatted_text.strip():
                st.markdown(formatted_text)
    
    st.divider()
    
    # Key Metrics
    if 'metrics' in results:
        st.markdown("### 📊 Key Metrics")
        metrics = results['metrics']
        
        # Extract and display key metrics in a clean format
        st.markdown("#### Overview")
        
        # Get overall KPIs if available
        overall_kpis = metrics.get('overall_kpis', {})
        if overall_kpis:
            def format_metric_value(value, prefix='', suffix=''):
                """Format metric values with M/K suffixes."""
                if value >= 1_000_000:
                    return f"{prefix}{value/1_000_000:.2f}M{suffix}"
                elif value >= 1_000:
                    return f"{prefix}{value/1_000:.1f}K{suffix}"
                else:
                    return f"{prefix}{value:,.0f}{suffix}"
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_spend = overall_kpis.get('Total_Spend', metrics.get('total_spend', 0))
                st.metric("Total Spend", format_metric_value(total_spend, '$'))
            
            with col2:
                total_conversions = overall_kpis.get('Total_Conversions', metrics.get('total_conversions', 0))
                st.metric("Total Conversions", format_metric_value(total_conversions))
            
            with col3:
                overall_ctr = overall_kpis.get('Overall_CTR', metrics.get('avg_ctr', 0))
                st.metric("Overall CTR", f"{overall_ctr:.2f}%")
            
            with col4:
                overall_cpa = overall_kpis.get('Overall_CPA', metrics.get('avg_cpa', 0))
                st.metric("Overall CPA", f"${overall_cpa:.2f}")
            
            # Second row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_clicks = overall_kpis.get('Total_Clicks', metrics.get('total_clicks', 0))
                st.metric("Total Clicks", format_metric_value(total_clicks))
            
            with col2:
                total_impressions = overall_kpis.get('Total_Impressions', metrics.get('total_impressions', 0))
                st.metric("Total Impressions", format_metric_value(total_impressions))
            
            with col3:
                overall_cpc = overall_kpis.get('Overall_CPC', metrics.get('avg_cpc', 0))
                st.metric("Overall CPC", f"${overall_cpc:.2f}")
            
            with col4:
                conversion_rate = overall_kpis.get('Overall_Conversion_Rate', metrics.get('avg_conversion_rate', 0))
                st.metric("Conversion Rate", f"{conversion_rate:.2f}%")
        
        # Platform breakdown
        if 'by_platform' in metrics:
            st.markdown("#### By Platform")
            platform_data = metrics['by_platform']
            
            if isinstance(platform_data, dict) and platform_data:
                for platform, data in platform_data.items():
                    with st.expander(f"📊 {platform}"):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Spend", f"${data.get('Spend', 0):,.2f}")
                        with col2:
                            st.metric("Conversions", f"{data.get('Conversions', 0):,.0f}")
                        with col3:
                            st.metric("CTR", f"{data.get('CTR', 0):.2f}%")
                        with col4:
                            st.metric("CPA", f"${data.get('CPA', 0):.2f}")
        
        # Monthly trends
        if 'monthly_trends' in metrics:
            st.markdown("#### Monthly Trends")
            monthly_data = metrics['monthly_trends']
            
            if isinstance(monthly_data, dict) and monthly_data:
                # Convert to DataFrame for better display
                import pandas as pd
                
                trend_df = pd.DataFrame.from_dict(monthly_data, orient='index')
                if not trend_df.empty:
                    # Format the index (Period objects) to strings
                    trend_df.index = [str(idx) for idx in trend_df.index]
                    
                    # Display as chart
                    st.line_chart(trend_df[['Spend', 'Conversions']])
                    
                    # Display as table
                    with st.expander("📋 View Monthly Data Table"):
                        st.dataframe(trend_df.style.format({
                            'Spend': '${:,.2f}',
                            'Conversions': '{:,.0f}',
                            'ROAS': '{:.2f}'
                        }))
    
    st.divider()
    
    # Insights
    if 'insights' in results:
        st.markdown("### 💡 Key Insights")
        for insight in results['insights']:
            st.markdown(f"<div class='insight-card'>{insight}</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Recommendations
    if 'recommendations' in results:
        st.markdown("### 🎯 Recommendations")
        for i, rec in enumerate(results['recommendations'], 1):
            st.markdown(f"**{i}.** {rec}")
    
    # Benchmarks
    if 'benchmarks' in results:
        st.divider()
        st.markdown("### 📈 Industry Benchmarks")
        benchmarks = results['benchmarks']
        
        if isinstance(benchmarks, dict) and benchmarks:
            for metric, data in benchmarks.items():
                with st.expander(f"📊 {metric.replace('_', ' ').title()}"):
                    if isinstance(data, dict):
                        col1, col2, col3 = st.columns(3)
                        
                        your_value = data.get('your_value', 0)
                        benchmark = data.get('benchmark', 0)
                        
                        # Calculate difference
                        if isinstance(your_value, (int, float)) and isinstance(benchmark, (int, float)) and benchmark != 0:
                            diff_pct = ((your_value - benchmark) / benchmark) * 100
                            
                            with col1:
                                st.metric("Your Performance", f"{your_value:.2f}")
                            with col2:
                                st.metric("Industry Average", f"{benchmark:.2f}")
                            with col3:
                                st.metric("Difference", f"{diff_pct:+.1f}%", delta=f"{diff_pct:.1f}%")
                        else:
                            with col1:
                                st.metric("Your Performance", str(your_value))
                            with col2:
                                st.metric("Industry Average", str(benchmark))


def render_qa_page():
    """Render Q&A page with full NL to SQL integration."""
    st.markdown('<div class="main-header">💬 Q&A</div>', unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload data first")
        return
    
    # Initialize NL engine if not already done
    if st.session_state.nl_engine is None:
        try:
            api_key = os.getenv('OPENAI_API_KEY', '')
            st.session_state.nl_engine = NaturalLanguageQueryEngine(api_key)
            # Load data into the engine
            st.session_state.nl_engine.load_data(st.session_state.df)
            logger.info("NL to SQL engine initialized")
        except Exception as e:
            st.error(f"Error initializing NL engine: {e}")
            return
    
    # Quick examples
    st.markdown("""
    ### 💡 Example Questions
    Ask anything about your campaign data in natural language!
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Total spend by platform"):
            st.session_state.current_question = "What is the total spend by platform?"
    
    with col2:
        if st.button("🎯 Best performing campaigns"):
            st.session_state.current_question = "Which campaigns have the highest CTR?"
    
    with col3:
        if st.button("📈 Performance trends"):
            st.session_state.current_question = "Show me performance trends over time"
    
    st.divider()
    
    # Question input
    question = st.text_area(
        "Your question:",
        value=st.session_state.get('current_question', ''),
        placeholder="e.g., What is the average CPC by channel? Show me campaigns with ROAS > 3",
        height=100
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        ask_button = st.button("🔍 Query", type="primary", use_container_width=True, key="query_btn")
    with col2:
        if st.button("🗑️ Clear History", use_container_width=False):
            st.session_state.chat_history = []
            st.rerun()
    
    if ask_button and question:
        with st.spinner("🤔 Analyzing your question..."):
            try:
                # Query the NL engine using ask() method
                result = st.session_state.nl_engine.ask(question)
                
                # Track query using start_query method
                query_id = st.session_state.query_tracker.start_query(
                    original_query=question,
                    interpretations=[{"sql": result.get('sql_query', ''), "success": result.get('success', False)}]
                )
                # Update with execution results
                results_df = result.get('results')
                result_count = len(results_df) if results_df is not None and hasattr(results_df, '__len__') else 0
                st.session_state.query_tracker.update_query(
                    query_id=query_id,
                    generated_sql=result.get('sql_query', ''),
                    result_count=result_count
                )
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'question': question,
                    'result': result,
                    'timestamp': datetime.now()
                })
                
                # Display result
                if result.get('success'):
                    st.success("✅ Query executed successfully!")
                    
                    # Show SQL query (key is 'sql_query' not 'sql')
                    with st.expander("🔍 Generated SQL", expanded=True):
                        sql_query = result.get('sql_query', '')
                        if sql_query:
                            st.code(sql_query, language='sql')
                        else:
                            st.info("No SQL query generated")
                    
                    # Show results (key is 'results' not 'data')
                    results_df = result.get('results')
                    if results_df is not None and not results_df.empty:
                        st.subheader("📊 Results")
                        
                        # Display as dataframe
                        st.dataframe(results_df, use_container_width=True)
                        
                        # Auto-generate visualization if applicable
                        if st.session_state.chart_generator:
                            try:
                                chart = st.session_state.chart_generator.generate_chart(
                                    results_df,
                                    question
                                )
                                if chart:
                                    st.plotly_chart(chart, use_container_width=True)
                            except Exception as e:
                                logger.error(f"Chart generation error: {e}")
                    else:
                        st.info("Query returned no results")
                    
                    # Show answer/insights (key is 'answer')
                    answer = result.get('answer')
                    if answer:
                        st.subheader("💡 AI Analysis")
                        st.markdown(answer)
                else:
                    st.error(f"❌ Query failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Q&A error: {e}", exc_info=True)
    
    # Display chat history
    if st.session_state.chat_history:
        st.divider()
        st.subheader("📜 Chat History")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):
            chat_result = chat.get('result', {})
            with st.expander(f"Q: {chat['question'][:100]}...", expanded=(i==0)):
                st.markdown(f"**Asked:** {chat['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                if chat_result.get('success'):
                    # Show SQL
                    sql = chat_result.get('sql_query', '')
                    if sql:
                        st.code(sql, language='sql')
                    # Show results
                    results = chat_result.get('results')
                    if results is not None and not results.empty:
                        st.dataframe(results, use_container_width=True)
                else:
                    st.error(chat_result.get('error', 'Query failed'))


def render_deep_dive_page():
    """Render in-depth analysis page with smart filters and custom chart builders."""
    st.markdown('<div class="main-header">🔍 In-Depth Analysis</div>', unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload data first")
        return
    
    df = st.session_state.df
    
    # ========================================
    # SECTION 1: CUSTOM CHART BUILDER (MOVED TO TOP, ALWAYS OPEN)
    # ========================================
    st.markdown("### 🎨 Custom Chart Builder")
    st.markdown("*Build custom visualizations with your data*")
    
    col1, col2, col3 = st.columns(3)
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    with col1:
        custom_chart_type = st.selectbox(
            "Chart Type",
            ["Bar Chart", "Line Chart", "Scatter Plot", "Area Chart", "Pie Chart", "Heatmap", "Box Plot"],
            key="custom_chart_type"
        )
    
    with col2:
        if custom_chart_type in ["Bar Chart", "Line Chart", "Area Chart"]:
            x_axis = st.selectbox("X-Axis", categorical_cols + (['Date'] if 'Date' in df.columns else []), key="custom_x")
        elif custom_chart_type == "Scatter Plot":
            x_axis = st.selectbox("X-Axis (Numeric)", numeric_cols, key="custom_x")
        elif custom_chart_type == "Pie Chart":
            x_axis = st.selectbox("Category", categorical_cols, key="custom_x")
        else:
            x_axis = st.selectbox("X-Axis", categorical_cols, key="custom_x")
    
    with col3:
        y_axis = st.selectbox("Y-Axis (Metric)", numeric_cols, key="custom_y")
    
    # Additional options
    col1, col2 = st.columns(2)
    with col1:
        color_by = st.selectbox("Color By (Optional)", ["None"] + categorical_cols, key="custom_color")
    with col2:
        aggregation = st.selectbox("Aggregation", ["Sum", "Mean", "Count", "Max", "Min"], key="custom_agg")
    
    if st.button("📊 Generate Custom Chart", key="generate_custom"):
        try:
            # Prepare data based on aggregation
            agg_map = {"Sum": "sum", "Mean": "mean", "Count": "count", "Max": "max", "Min": "min"}
            
            if custom_chart_type == "Bar Chart":
                chart_data = df.groupby(x_axis)[y_axis].agg(agg_map[aggregation]).reset_index()
                if color_by != "None":
                    chart_data = df.groupby([x_axis, color_by])[y_axis].agg(agg_map[aggregation]).reset_index()
                    fig = px.bar(chart_data, x=x_axis, y=y_axis, color=color_by, title=f"{y_axis} by {x_axis}")
                else:
                    fig = px.bar(chart_data, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
            
            elif custom_chart_type == "Line Chart":
                chart_data = df.groupby(x_axis)[y_axis].agg(agg_map[aggregation]).reset_index()
                fig = px.line(chart_data, x=x_axis, y=y_axis, title=f"{y_axis} Trend")
            
            elif custom_chart_type == "Scatter Plot":
                fig = px.scatter(df, x=x_axis, y=y_axis, 
                                color=color_by if color_by != "None" else None,
                                title=f"{y_axis} vs {x_axis}")
            
            elif custom_chart_type == "Area Chart":
                chart_data = df.groupby(x_axis)[y_axis].agg(agg_map[aggregation]).reset_index()
                fig = px.area(chart_data, x=x_axis, y=y_axis, title=f"{y_axis} Area")
            
            elif custom_chart_type == "Pie Chart":
                chart_data = df.groupby(x_axis)[y_axis].agg(agg_map[aggregation]).reset_index()
                fig = px.pie(chart_data, values=y_axis, names=x_axis, title=f"{y_axis} Distribution")
            
            elif custom_chart_type == "Box Plot":
                fig = px.box(df, x=x_axis, y=y_axis, 
                            color=color_by if color_by != "None" else None,
                            title=f"{y_axis} Distribution by {x_axis}")
            
            elif custom_chart_type == "Heatmap":
                pivot_data = df.pivot_table(values=y_axis, index=x_axis, 
                                            columns=color_by if color_by != "None" else None,
                                            aggfunc=agg_map[aggregation])
                fig = px.imshow(pivot_data, title=f"{y_axis} Heatmap", aspect="auto")
            
            fig.update_layout(
                template='plotly_dark',
                height=500,
                margin=dict(l=80, r=40, t=60, b=60),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.3)',
                    showline=True,
                    linewidth=2,
                    linecolor='rgba(255,255,255,0.3)',
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.3)',
                    showline=True,
                    linewidth=2,
                    linecolor='rgba(255,255,255,0.3)',
                    tickfont=dict(size=12),
                    showticklabels=True
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating chart: {str(e)[:200]}")
    
    st.divider()
    
    # ========================================
    # SECTION 2: CUSTOM CHART BUILDER-2 (NEW - KPIs ON X-AXIS)
    # ========================================
    st.markdown("### 🎨 Custom Chart Builder-2")
    st.markdown("*Compare multiple KPIs side-by-side*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Select multiple KPIs for X-axis
        kpi_options = [col for col in numeric_cols if col in ['Spend', 'Clicks', 'Conversions', 'Impressions', 'Revenue', 'CPA', 'CPC', 'CTR', 'ROAS']]
        selected_kpis = st.multiselect(
            "Select KPIs to Compare",
            kpi_options,
            default=kpi_options[:3] if len(kpi_options) >= 3 else kpi_options,
            key="kpi_multiselect"
        )
    
    with col2:
        # Select dimension for grouping
        dimension_options = ['Platform']
        if 'Campaign_Name' in df.columns:
            dimension_options.append('Campaign')
        if 'Placement' in df.columns:
            dimension_options.append('Placement')
        if 'Audience' in df.columns or 'Audience_Segment' in df.columns:
            dimension_options.append('Audience')
        
        compare_dimension = st.selectbox("Group By", dimension_options, key="compare_dimension")
    
    col1, col2 = st.columns(2)
    with col1:
        chart_type_2 = st.selectbox("Chart Type", ["Grouped Bar", "Line", "Radar"], key="chart_type_2")
    with col2:
        normalize_data = st.checkbox("Normalize Data (0-100 scale)", value=False, key="normalize_kpi")
    
    if st.button("📊 Generate KPI Comparison", key="generate_kpi_comparison"):
        if selected_kpis and compare_dimension:
            try:
                # Map dimension to actual column
                dim_map = {
                    'Platform': 'Platform',
                    'Campaign': 'Campaign_Name',
                    'Placement': 'Placement',
                    'Audience': 'Audience' if 'Audience' in df.columns else 'Audience_Segment'
                }
                actual_dim = dim_map.get(compare_dimension, 'Platform')
                
                if actual_dim in df.columns:
                    # Aggregate data
                    agg_data = df.groupby(actual_dim)[selected_kpis].sum().reset_index()
                    
                    # Helper function to format axis based on value range
                    def get_axis_format(values):
                        """Determine appropriate axis format based on value range."""
                        max_val = values.max()
                        min_val = values.min()
                        range_val = max_val - min_val
                        
                        if max_val >= 1_000_000:
                            return {'suffix': 'M', 'divisor': 1_000_000, 'decimals': 2}
                        elif max_val >= 1_000:
                            return {'suffix': 'K', 'divisor': 1_000, 'decimals': 1}
                        elif max_val >= 100:
                            return {'suffix': '', 'divisor': 1, 'decimals': 0}
                        elif max_val >= 1:
                            return {'suffix': '', 'divisor': 1, 'decimals': 1}
                        else:
                            return {'suffix': '', 'divisor': 1, 'decimals': 2}
                    
                    # Normalize if requested
                    if normalize_data:
                        for kpi in selected_kpis:
                            max_val = agg_data[kpi].max()
                            if max_val > 0:
                                agg_data[f"{kpi}_norm"] = (agg_data[kpi] / max_val) * 100
                        kpi_cols = [f"{kpi}_norm" for kpi in selected_kpis]
                        y_axis_format = {'suffix': '%', 'divisor': 1, 'decimals': 1}
                    else:
                        kpi_cols = selected_kpis
                        # Determine format based on all selected KPIs
                        all_values = pd.concat([agg_data[kpi] for kpi in selected_kpis])
                        y_axis_format = get_axis_format(all_values)
                    
                    # Melt data for plotting
                    melted_data = agg_data.melt(
                        id_vars=[actual_dim],
                        value_vars=kpi_cols,
                        var_name='KPI',
                        value_name='Value'
                    )
                    
                    # Create custom hover template with proper formatting
                    if normalize_data:
                        hover_template = '<b>%{x}</b><br>%{fullData.name}<br>Value: %{y:.1f}%<extra></extra>'
                    else:
                        divisor = y_axis_format['divisor']
                        suffix = y_axis_format['suffix']
                        decimals = y_axis_format['decimals']
                        hover_template = f'<b>%{{x}}</b><br>%{{fullData.name}}<br>Value: %{{y:,.{decimals}f}}{suffix}<extra></extra>'
                    
                    if chart_type_2 == "Grouped Bar":
                        fig = px.bar(
                            melted_data,
                            x='KPI',
                            y='Value',
                            color=actual_dim,
                            barmode='group',
                            title=f"KPI Comparison by {compare_dimension}"
                        )
                        fig.update_traces(hovertemplate=hover_template)
                        
                    elif chart_type_2 == "Line":
                        fig = px.line(
                            melted_data,
                            x='KPI',
                            y='Value',
                            color=actual_dim,
                            markers=True,
                            title=f"KPI Comparison by {compare_dimension}"
                        )
                        fig.update_traces(hovertemplate=hover_template)
                        
                    elif chart_type_2 == "Radar":
                        fig = go.Figure()
                        for dim_val in agg_data[actual_dim].unique():
                            dim_data = melted_data[melted_data[actual_dim] == dim_val]
                            fig.add_trace(go.Scatterpolar(
                                r=dim_data['Value'].tolist(),
                                theta=dim_data['KPI'].tolist(),
                                fill='toself',
                                name=str(dim_val)
                            ))
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True)),
                            title=f"KPI Radar: {compare_dimension}"
                        )
                    
                    # Apply adaptive Y-axis formatting with custom tick text
                    if chart_type_2 in ["Grouped Bar", "Line"]:
                        if normalize_data:
                            y_title = "Normalized Value (%)"
                        else:
                            divisor = y_axis_format['divisor']
                            suffix = y_axis_format['suffix']
                            y_title = f"Value ({suffix})" if suffix else "Value"
                        
                        fig.update_layout(
                            yaxis=dict(
                                title=dict(text=y_title, font=dict(size=14)),
                                showgrid=True,
                                gridcolor='rgba(128,128,128,0.3)',
                                showticklabels=True,
                                tickmode='linear',
                                tick0=0,
                                dtick='auto',
                                tickfont=dict(size=12),
                                showline=True,
                                linewidth=2,
                                linecolor='rgba(255,255,255,0.3)'
                            ),
                            xaxis=dict(
                                title=dict(text="KPI", font=dict(size=14)),
                                showgrid=True,
                                gridcolor='rgba(128,128,128,0.3)',
                                tickfont=dict(size=12),
                                showline=True,
                                linewidth=2,
                                linecolor='rgba(255,255,255,0.3)'
                            )
                        )
                    
                    fig.update_layout(
                        template='plotly_dark',
                        height=500,
                        showlegend=True,
                        margin=dict(l=80, r=40, t=60, b=60)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show summary statistics
                    st.markdown("**Summary Statistics:**")
                    summary_data = agg_data[selected_kpis].describe().T
                    summary_data['total'] = agg_data[selected_kpis].sum()
                    
                    # Format based on scale
                    formatted_summary = summary_data.copy()
                    for kpi in selected_kpis:
                        kpi_format = get_axis_format(agg_data[kpi])
                        divisor = kpi_format['divisor']
                        suffix = kpi_format['suffix']
                        decimals = kpi_format['decimals']
                        
                        for col in formatted_summary.columns:
                            if col in formatted_summary.index:
                                continue
                            val = formatted_summary.loc[kpi, col]
                            if divisor > 1:
                                formatted_summary.loc[kpi, col] = f"{val/divisor:,.{decimals}f}{suffix}"
                            else:
                                formatted_summary.loc[kpi, col] = f"{val:,.{decimals}f}"
                    
                    st.dataframe(formatted_summary, use_container_width=True)
                    
                else:
                    st.warning(f"Column {actual_dim} not found in data")
            except Exception as e:
                st.error(f"Error creating KPI comparison: {str(e)[:200]}")
        else:
            st.warning("Please select at least one KPI and a dimension")
    
    st.divider()
    
    # ========================================
    # SECTION 3: SMART FILTERS (MOVED DOWN)
    # ========================================
    st.markdown("### 🎯 Smart Filters")
    
    # Initialize filter engine if needed
    if st.session_state.filter_engine is None and st.session_state.get('analytics_expert'):
        try:
            st.session_state.filter_engine = SmartFilterEngine()
        except:
            pass
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Platform filter
        platforms = ['All'] + sorted(df['Platform'].dropna().unique().tolist()) if 'Platform' in df.columns else ['All']
        selected_platform = st.selectbox("📱 Platform", platforms)
    
    with col2:
        # Date range filter
        if 'Date' in df.columns:
            try:
                min_date = pd.to_datetime(df['Date'], format='mixed', dayfirst=True).min()
                max_date = pd.to_datetime(df['Date'], format='mixed', dayfirst=True).max()
                date_range = st.date_input(
                    "📅 Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
            except Exception as e:
                st.warning(f"⚠️ Date parsing issue: {str(e)[:100]}")
                date_range = None
        else:
            date_range = None
    
    with col3:
        # Metric filter
        metric_options = ['Spend', 'Clicks', 'Conversions', 'Impressions', 'Revenue']
        available_metrics = [m for m in metric_options if m in df.columns]
        if available_metrics:
            selected_metric = st.selectbox("📊 Primary Metric", available_metrics)
        else:
            selected_metric = None
    
    # Secondary metric for dual-axis charts
    col1, col2, col3 = st.columns(3)
    with col1:
        secondary_options = [m for m in available_metrics if m != selected_metric] if available_metrics else []
        if secondary_options:
            secondary_metric = st.selectbox("📈 Secondary Metric", secondary_options, key="secondary_metric")
        else:
            secondary_metric = None
    
    with col2:
        # Analysis type selector
        analysis_types = [
            "Spend-Conversion Analysis",
            "Marketing Funnel",
            "Platform Comparison",
            "Weekly Trends",
            "Monthly Trends"
        ]
        selected_analysis = st.selectbox("🔍 Analysis Type", analysis_types)
    
    with col3:
        # Group by selector
        group_options = ['Platform']
        if 'Campaign_Name' in df.columns:
            group_options.append('Campaign')
        if 'Placement' in df.columns:
            group_options.append('Placement')
        if 'Ad_Type' in df.columns or 'AdType' in df.columns:
            group_options.append('Ad Type')
        if 'Creative' in df.columns:
            group_options.append('Creative')
        if 'Audience' in df.columns or 'Audience_Segment' in df.columns:
            group_options.append('Audience')
        if 'Geo' in df.columns or 'Geography' in df.columns or 'Country' in df.columns:
            group_options.append('Geo')
        if 'Device' in df.columns:
            group_options.append('Device')
        if 'Age' in df.columns or 'Age_Group' in df.columns:
            group_options.append('Age')
        
        group_by = st.selectbox("📊 Group By", group_options)
    
    # Advanced filters
    with st.expander("🔧 Advanced Filters"):
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Spend' in df.columns:
                min_spend = float(df['Spend'].min())
                max_spend = float(df['Spend'].max())
                spend_range = st.slider(
                    "Spend Range",
                    min_value=min_spend,
                    max_value=max_spend,
                    value=(min_spend, max_spend)
                )
            else:
                spend_range = None
        
        with col2:
            if 'Conversions' in df.columns:
                min_conv = float(df['Conversions'].min())
                max_conv = float(df['Conversions'].max())
                conv_range = st.slider(
                    "Conversions Range",
                    min_value=min_conv,
                    max_value=max_conv,
                    value=(min_conv, max_conv)
                )
            else:
                conv_range = None
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_platform != 'All' and 'Platform' in df.columns:
        filtered_df = filtered_df[filtered_df['Platform'] == selected_platform]
    
    if date_range and 'Date' in df.columns:
        if len(date_range) == 2:
            try:
                filtered_df['Date_parsed'] = pd.to_datetime(filtered_df['Date'], format='mixed', dayfirst=True)
                filtered_df = filtered_df[
                    (filtered_df['Date_parsed'] >= pd.to_datetime(date_range[0])) &
                    (filtered_df['Date_parsed'] <= pd.to_datetime(date_range[1]))
                ]
                filtered_df = filtered_df.drop('Date_parsed', axis=1)
            except Exception as e:
                st.warning(f"⚠️ Date filtering failed: {str(e)[:100]}")
    
    if spend_range and 'Spend' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['Spend'] >= spend_range[0]) &
            (filtered_df['Spend'] <= spend_range[1])
        ]
    
    if conv_range and 'Conversions' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['Conversions'] >= conv_range[0]) &
            (filtered_df['Conversions'] <= conv_range[1])
        ]
    
    st.divider()
    
    # ========================================
    # SECTION 4: FILTERED RESULTS & ANALYSIS
    # ========================================
    st.markdown(f"### 📊 Filtered Results ({len(filtered_df)} rows)")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'Spend' in filtered_df.columns:
            spend_val = filtered_df['Spend'].sum()
            st.metric("Total Spend", format_number(spend_val, 'currency'))
    
    with col2:
        if 'Conversions' in filtered_df.columns:
            conv_val = filtered_df['Conversions'].sum()
            st.metric("Total Conversions", format_number(conv_val, 'number'))
    
    with col3:
        if 'Clicks' in filtered_df.columns:
            clicks_val = filtered_df['Clicks'].sum()
            st.metric("Total Clicks", format_number(clicks_val, 'number'))
    
    with col4:
        if 'Impressions' in filtered_df.columns:
            imp_val = filtered_df['Impressions'].sum()
            st.metric("Total Impressions", format_number(imp_val, 'number'))
    
    st.divider()
    
    # Dual-Axis Visualizations
    if selected_metric and selected_metric in filtered_df.columns:
        if secondary_metric:
            chart_title = f"{selected_metric}-{secondary_metric} Analysis"
        else:
            chart_title = f"{selected_metric} Analysis"
        
        st.markdown(f"### 📈 {chart_title}")
        
        # Map group_by to actual column
        group_col_map = {
            'Platform': 'Platform',
            'Campaign': 'Campaign_Name',
            'Placement': 'Placement',
            'Ad Type': 'Ad_Type' if 'Ad_Type' in filtered_df.columns else 'AdType',
            'Creative': 'Creative',
            'Audience': 'Audience' if 'Audience' in filtered_df.columns else 'Audience_Segment',
            'Geo': 'Geo' if 'Geo' in filtered_df.columns else ('Geography' if 'Geography' in filtered_df.columns else 'Country'),
            'Device': 'Device',
            'Age': 'Age' if 'Age' in filtered_df.columns else 'Age_Group'
        }
        
        actual_group_col = group_col_map.get(group_by, 'Platform')
        
        # Create dual-axis chart
        if secondary_metric and secondary_metric in filtered_df.columns and actual_group_col in filtered_df.columns:
            try:
                fig = create_dual_axis_chart(
                    filtered_df,
                    x_col=actual_group_col,
                    primary_metric=selected_metric,
                    secondary_metric=secondary_metric,
                    title=f"{selected_metric} vs {secondary_metric} by {group_by}"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create dual-axis chart: {e}")
                if actual_group_col in filtered_df.columns:
                    chart_data = filtered_df.groupby(actual_group_col)[selected_metric].sum().reset_index()
                    st.bar_chart(chart_data.set_index(actual_group_col))
        else:
            # Single metric chart
            if actual_group_col in filtered_df.columns:
                chart_data = filtered_df.groupby(actual_group_col)[selected_metric].sum().reset_index()
                fig = px.bar(
                    chart_data,
                    x=actual_group_col,
                    y=selected_metric,
                    title=f"{selected_metric} by {group_by}",
                    color=actual_group_col
                )
                fig.update_layout(template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True)
        
        # ========================================
        # TIME SERIES - WEEKLY LINE CHART (IMPROVED)
        # ========================================
        if 'Date' in filtered_df.columns and secondary_metric:
            st.markdown("#### 📅 Weekly Time Series Analysis")
            try:
                # Parse dates
                filtered_df['Date_parsed'] = pd.to_datetime(filtered_df['Date'], format='mixed', dayfirst=True)
                
                # Aggregate by week
                weekly_data = filtered_df.set_index('Date_parsed').resample('W')[
                    [selected_metric, secondary_metric]
                ].sum().reset_index()
                
                # Create line chart with dual axis
                fig = go.Figure()
                
                # Primary metric (left axis)
                fig.add_trace(go.Scatter(
                    x=weekly_data['Date_parsed'],
                    y=weekly_data[selected_metric],
                    name=selected_metric,
                    mode='lines+markers',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8)
                ))
                
                # Secondary metric (right axis)
                fig.add_trace(go.Scatter(
                    x=weekly_data['Date_parsed'],
                    y=weekly_data[secondary_metric],
                    name=secondary_metric,
                    mode='lines+markers',
                    line=dict(color='#f093fb', width=3),
                    marker=dict(size=8),
                    yaxis='y2'
                ))
                
                # Update layout with dual axes
                fig.update_layout(
                    title=f"Weekly Trend: {selected_metric} vs {secondary_metric}",
                    xaxis=dict(title='Week'),
                    yaxis=dict(title=selected_metric, side='left'),
                    yaxis2=dict(title=secondary_metric, side='right', overlaying='y'),
                    template='plotly_dark',
                    hovermode='x unified',
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create weekly time series: {e}")
        
        # Marketing Funnel
        if selected_analysis == "Marketing Funnel":
            st.markdown("#### 🔄 Marketing Funnel")
            funnel_metrics = ['Impressions', 'Clicks', 'Conversions']
            available_funnel = [m for m in funnel_metrics if m in filtered_df.columns]
            
            if len(available_funnel) >= 2:
                funnel_data = pd.DataFrame({
                    'Stage': available_funnel,
                    'Value': [filtered_df[m].sum() for m in available_funnel]
                })
                
                fig = go.Figure(go.Funnel(
                    y=funnel_data['Stage'],
                    x=funnel_data['Value'],
                    textinfo="value+percent initial",
                    marker=dict(color=['#667eea', '#764ba2', '#f093fb'])
                ))
                fig.update_layout(title="Marketing Funnel", template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True)
    
    # ========================================
    # SECTION 5: SPEND-CLICK ANALYSIS BY MULTIPLE DIMENSIONS (NEW)
    # ========================================
    st.divider()
    st.markdown("### 💰 Spend-Click Analysis by Dimension")
    
    # Detect available dimensions
    dimension_map = {}
    
    # Platform (always available)
    if 'Platform' in filtered_df.columns:
        dimension_map['Platform'] = 'Platform'
    
    # Funnel Stage
    funnel_cols = ['Funnel_Stage', 'Stage', 'Funnel', 'Marketing_Funnel']
    for col in funnel_cols:
        if col in filtered_df.columns:
            dimension_map['Funnel Stage'] = col
            break
    
    # Source/Channel
    source_cols = ['Source', 'Channel', 'Traffic_Source', 'Medium', 'utm_source', 'utm_medium']
    for col in source_cols:
        if col in filtered_df.columns:
            dimension_map['Source/Channel'] = col
            break
    
    # Audience Type
    audience_cols = ['Audience', 'Audience_Type', 'Audience_Segment', 'Segment', 'Target_Audience']
    for col in audience_cols:
        if col in filtered_df.columns:
            dimension_map['Audience Type'] = col
            break
    
    # Demographics
    demo_cols = ['Age', 'Age_Group', 'Age_Range', 'Gender', 'Location', 'Geography', 'Geo', 'Country', 'Region']
    for col in demo_cols:
        if col in filtered_df.columns:
            dimension_map['Demographics'] = col
            break
    
    # Campaign Type
    campaign_type_cols = ['Campaign_Type', 'CampaignType', 'Type', 'Objective', 'Campaign_Objective']
    for col in campaign_type_cols:
        if col in filtered_df.columns:
            dimension_map['Campaign Type'] = col
            break
    
    if dimension_map:
        selected_dimension = st.selectbox(
            "Select Dimension for Analysis",
            list(dimension_map.keys()),
            key="spend_click_dimension"
        )
        
        if selected_dimension and 'Spend' in filtered_df.columns and 'Clicks' in filtered_df.columns:
            actual_col = dimension_map[selected_dimension]
            
            try:
                # Aggregate by dimension
                analysis_data = filtered_df.groupby(actual_col).agg({
                    'Spend': 'sum',
                    'Clicks': 'sum'
                }).reset_index()
                
                # Create scatter plot
                fig = px.scatter(
                    analysis_data,
                    x='Spend',
                    y='Clicks',
                    text=actual_col,
                    title=f"Spend vs Clicks by {selected_dimension}",
                    size='Clicks',
                    color=actual_col,
                    hover_data={actual_col: True, 'Spend': ':,.0f', 'Clicks': ':,.0f'}
                )
                
                fig.update_traces(textposition='top center', textfont_size=10)
                fig.update_layout(
                    template='plotly_dark',
                    xaxis=dict(
                        title=dict(text="Total Spend ($)", font=dict(size=14)),
                        showgrid=True,
                        gridcolor='rgba(128,128,128,0.3)',
                        showticklabels=True,
                        tickformat='$,.0f',
                        tickmode='linear',
                        tick0=0,
                        dtick='auto',
                        tickfont=dict(size=12),
                        showline=True,
                        linewidth=2,
                        linecolor='rgba(255,255,255,0.3)'
                    ),
                    yaxis=dict(
                        title=dict(text="Total Clicks", font=dict(size=14)),
                        showgrid=True,
                        gridcolor='rgba(128,128,128,0.3)',
                        showticklabels=True,
                        tickformat=',',
                        tickmode='linear',
                        tick0=0,
                        dtick='auto',
                        tickfont=dict(size=12),
                        showline=True,
                        linewidth=2,
                        linecolor='rgba(255,255,255,0.3)'
                    ),
                    showlegend=True,
                    height=500,
                    margin=dict(l=80, r=40, t=60, b=60)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show data table
                st.markdown(f"**{selected_dimension} Performance:**")
                analysis_data['CPC'] = analysis_data['Spend'] / analysis_data['Clicks']
                analysis_data = analysis_data.sort_values('Spend', ascending=False)
                st.dataframe(
                    analysis_data.style.format({
                        'Spend': '${:,.2f}',
                        'Clicks': '{:,.0f}',
                        'CPC': '${:.2f}'
                    }),
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error creating spend-click analysis: {str(e)[:200]}")
    else:
        st.info("No additional dimensions found for spend-click analysis. Available: Platform only.")
    
    # Data table
    st.divider()
    with st.expander("📋 View Filtered Data"):
        st.dataframe(filtered_df, use_container_width=True, height=400)
    
    # Export options
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Export to CSV", key="deep_dive_export"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="filtered_data.csv",
                mime="text/csv"
            )


def render_diagnostics_page():
    """Render Smart Performance Diagnostics page."""
    st.markdown('<div class="main-header">🔬 Smart Performance Diagnostics</div>', unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload data first")
        return
    
    df = st.session_state.df
    
    # Render diagnostics component
    DiagnosticsComponent.render(df)


def render_visualizations_page():
    """Render interactive visualizations page."""
    st.markdown('<div class="main-header">📈 Smart Visualizations</div>', unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload data first")
        return
    
    df = st.session_state.df
    
    # Visualization type selector FIRST
    st.markdown("### 🎨 Visualization Type")
    
    viz_type = st.selectbox(
        "Select visualization",
        [
            "Performance Overview",
            "Trend Analysis",
            "Platform Comparison",
            "Funnel Analysis",
            "Correlation Matrix",
            "Custom Chart"
        ]
    )
    
    st.divider()
    
    # Smart Filters - Enhanced with more options
    with st.expander("🎯 Smart Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            platforms = ['All'] + sorted(df['Platform'].dropna().unique().tolist()) if 'Platform' in df.columns else ['All']
            viz_platform = st.selectbox("📱 Platform", platforms, key="viz_platform")
        
        with col2:
            if 'Campaign_Name' in df.columns:
                campaigns = ['All'] + sorted(df['Campaign_Name'].dropna().unique().tolist())[:20]
                viz_campaign = st.selectbox("📋 Campaign", campaigns, key="viz_campaign")
            else:
                viz_campaign = 'All'
        
        with col3:
            if 'Date' in df.columns:
                try:
                    df_dates = pd.to_datetime(df['Date'], format='mixed', dayfirst=True, errors='coerce')
                    min_date = df_dates.min()
                    max_date = df_dates.max()
                    if pd.notna(min_date) and pd.notna(max_date):
                        viz_date_range = st.date_input(
                            "📅 Date Range",
                            value=(min_date, max_date),
                            min_value=min_date,
                            max_value=max_date,
                            key="viz_date_range"
                        )
                    else:
                        viz_date_range = None
                except Exception:
                    viz_date_range = None
            else:
                viz_date_range = None
        
        # Additional filter row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Audience filter
            if 'Audience' in df.columns or 'Audience_Segment' in df.columns:
                audience_col = 'Audience' if 'Audience' in df.columns else 'Audience_Segment'
                audiences = ['All'] + sorted(df[audience_col].dropna().unique().tolist())[:15]
                viz_audience = st.selectbox("👥 Audience", audiences, key="viz_audience")
            else:
                viz_audience = 'All'
        
        with col2:
            # Device filter
            if 'Device' in df.columns:
                devices = ['All'] + sorted(df['Device'].dropna().unique().tolist())
                viz_device = st.selectbox("📱 Device", devices, key="viz_device")
            else:
                viz_device = 'All'
        
        with col3:
            # Placement filter
            if 'Placement' in df.columns:
                placements = ['All'] + sorted(df['Placement'].dropna().unique().tolist())[:15]
                viz_placement = st.selectbox("📍 Placement", placements, key="viz_placement")
            else:
                viz_placement = 'All'
        
        # Metric range filters
        col1, col2 = st.columns(2)
        with col1:
            if 'Spend' in df.columns:
                min_spend = float(df['Spend'].min())
                max_spend = float(df['Spend'].max())
                viz_spend_range = st.slider(
                    "💰 Spend Range",
                    min_value=min_spend,
                    max_value=max_spend,
                    value=(min_spend, max_spend),
                    key="viz_spend_range"
                )
            else:
                viz_spend_range = None
        
        with col2:
            if 'Clicks' in df.columns:
                min_clicks = float(df['Clicks'].min())
                max_clicks = float(df['Clicks'].max())
                viz_clicks_range = st.slider(
                    "🖱️ Clicks Range",
                    min_value=min_clicks,
                    max_value=max_clicks,
                    value=(min_clicks, max_clicks),
                    key="viz_clicks_range"
                )
            else:
                viz_clicks_range = None
    
    # Apply filters
    filtered_df = df.copy()
    if viz_platform != 'All' and 'Platform' in df.columns:
        filtered_df = filtered_df[filtered_df['Platform'] == viz_platform]
    if viz_campaign != 'All' and 'Campaign_Name' in df.columns:
        filtered_df = filtered_df[filtered_df['Campaign_Name'] == viz_campaign]
    if viz_date_range and 'Date' in df.columns and len(viz_date_range) == 2:
        try:
            filtered_df['_date_parsed'] = pd.to_datetime(filtered_df['Date'], format='mixed', dayfirst=True, errors='coerce')
            filtered_df = filtered_df[
                (filtered_df['_date_parsed'] >= pd.to_datetime(viz_date_range[0])) &
                (filtered_df['_date_parsed'] <= pd.to_datetime(viz_date_range[1]))
            ]
            filtered_df = filtered_df.drop('_date_parsed', axis=1)
        except Exception:
            pass
    
    # Apply additional filters
    if viz_audience != 'All':
        audience_col = 'Audience' if 'Audience' in df.columns else 'Audience_Segment'
        if audience_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[audience_col] == viz_audience]
    
    if viz_device != 'All' and 'Device' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Device'] == viz_device]
    
    if viz_placement != 'All' and 'Placement' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Placement'] == viz_placement]
    
    if viz_spend_range and 'Spend' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['Spend'] >= viz_spend_range[0]) &
            (filtered_df['Spend'] <= viz_spend_range[1])
        ]
    
    if viz_clicks_range and 'Clicks' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['Clicks'] >= viz_clicks_range[0]) &
            (filtered_df['Clicks'] <= viz_clicks_range[1])
        ]
    
    st.caption(f"📊 Showing {len(filtered_df):,} of {len(df):,} records")
    
    # Use filtered_df for all visualizations
    df = filtered_df
    
    if viz_type == "Performance Overview":
        st.markdown("### 📊 Performance Overview")
        
        # Key metrics cards
        col1, col2, col3, col4 = st.columns(4)
        
        metrics_to_show = [
            ('Spend', '$', '.2f'),
            ('Clicks', '', '.0f'),
            ('Conversions', '', '.0f'),
            ('Impressions', '', '.0f')
        ]
        
        def format_metric_value(value, prefix=''):
            """Format metric values with M/K suffixes."""
            if value >= 1_000_000:
                return f"{prefix}{value/1_000_000:.2f}M"
            elif value >= 1_000:
                return f"{prefix}{value/1_000:.1f}K"
            else:
                return f"{prefix}{value:,.0f}"
        
        for i, (metric, prefix, fmt) in enumerate(metrics_to_show):
            if metric in df.columns:
                with [col1, col2, col3, col4][i]:
                    value = df[metric].sum()
                    formatted_value = format_metric_value(value, prefix)
                    st.metric(f"Total {metric}", formatted_value)
        
        # Multi-metric chart
        if all(m in df.columns for m in ['Spend', 'Clicks', 'Conversions']):
            st.markdown("#### Multi-Metric Comparison")
            
            chart_data = df[['Spend', 'Clicks', 'Conversions']].sum().reset_index()
            chart_data.columns = ['Metric', 'Value']
            
            fig = px.bar(
                chart_data,
                x='Metric',
                y='Value',
                title='Key Metrics Summary',
                color='Metric'
            )
            fig.update_layout(
                template='plotly_dark',
                height=500,
                margin=dict(l=80, r=40, t=60, b=60),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.3)',
                    showline=True,
                    linewidth=2,
                    linecolor='rgba(255,255,255,0.3)',
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.3)',
                    showline=True,
                    linewidth=2,
                    linecolor='rgba(255,255,255,0.3)',
                    tickfont=dict(size=12),
                    showticklabels=True
                )
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "Trend Analysis":
        st.markdown("### 📈 Trend Analysis")
        
        if 'Date' in df.columns:
            # Metric selectors and aggregation options
            available_metrics = [col for col in ['Spend', 'Clicks', 'Conversions', 'Impressions', 'Revenue'] if col in df.columns]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                primary_metric = st.selectbox("Primary Metric", available_metrics, key="trend_primary")
            with col2:
                secondary_options = ["None"] + [m for m in available_metrics if m != primary_metric]
                secondary_metric = st.selectbox("Secondary Metric (Optional)", secondary_options, key="trend_secondary")
                if secondary_metric == "None":
                    secondary_metric = None
            with col3:
                # Time aggregation to reduce clutter
                time_agg = st.selectbox("Time Aggregation", ["Daily", "Weekly", "Monthly"], key="trend_agg")
            
            if primary_metric:
                try:
                    df_copy = df.copy()
                    df_copy['Date_parsed'] = pd.to_datetime(df_copy['Date'], format='mixed', dayfirst=True)
                    
                    # Apply time aggregation to reduce clutter
                    if time_agg == "Weekly":
                        df_copy['Date_agg'] = df_copy['Date_parsed'].dt.to_period('W').dt.start_time
                    elif time_agg == "Monthly":
                        df_copy['Date_agg'] = df_copy['Date_parsed'].dt.to_period('M').dt.start_time
                    else:
                        df_copy['Date_agg'] = df_copy['Date_parsed']
                    
                    # Aggregate data
                    agg_cols = [primary_metric]
                    if secondary_metric:
                        agg_cols.append(secondary_metric)
                    
                    trend_data = df_copy.groupby('Date_agg')[agg_cols].sum().reset_index()
                    trend_data = trend_data.sort_values('Date_agg')
                    
                    if secondary_metric:
                        # Clean dual-axis chart
                        fig = go.Figure()
                        
                        # Primary metric as area chart (cleaner than bars for time series)
                        fig.add_trace(go.Scatter(
                            x=trend_data['Date_agg'],
                            y=trend_data[primary_metric],
                            name=primary_metric,
                            fill='tozeroy',
                            fillcolor='rgba(102, 126, 234, 0.3)',
                            line=dict(color='#667eea', width=2),
                            yaxis='y'
                        ))
                        
                        # Secondary metric as line
                        fig.add_trace(go.Scatter(
                            x=trend_data['Date_agg'],
                            y=trend_data[secondary_metric],
                            name=secondary_metric,
                            mode='lines+markers',
                            line=dict(color='#f093fb', width=3),
                            marker=dict(size=6),
                            yaxis='y2'
                        ))
                        
                        fig.update_layout(
                            title=f'{primary_metric} vs {secondary_metric} ({time_agg})',
                            xaxis=dict(title='Date', tickformat='%b %d'),
                            yaxis=dict(title=dict(text=primary_metric, font=dict(color='#667eea')), side='left'),
                            yaxis2=dict(title=dict(text=secondary_metric, font=dict(color='#f093fb')), overlaying='y', side='right'),
                            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                            hovermode='x unified',
                            template='plotly_dark'
                        )
                    else:
                        # Single metric area chart
                        fig = px.area(
                            trend_data,
                            x='Date_agg',
                            y=primary_metric,
                            title=f'{primary_metric} Over Time ({time_agg})'
                        )
                        fig.update_layout(template='plotly_dark', xaxis_tickformat='%b %d')
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show summary stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(f"Total {primary_metric}", format_number(trend_data[primary_metric].sum(), 'number'))
                    with col2:
                        st.metric(f"Avg {primary_metric}", format_number(trend_data[primary_metric].mean(), 'number'))
                    with col3:
                        # Trend direction
                        if len(trend_data) > 1:
                            first_half = trend_data[primary_metric].iloc[:len(trend_data)//2].mean()
                            second_half = trend_data[primary_metric].iloc[len(trend_data)//2:].mean()
                            change = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0
                            st.metric("Trend", f"{change:+.1f}%", delta=f"{'↑' if change > 0 else '↓'}")
                        
                except Exception as e:
                    st.error(f"Chart error: {str(e)[:100]}")
        else:
            st.info("Date column not found in data")
    
    elif viz_type == "Platform Comparison":
        st.markdown("### 📱 Platform Comparison (Dual Axis)")
        
        if 'Platform' in df.columns:
            # Dual metric selectors
            available_metrics = [col for col in ['Spend', 'Clicks', 'Conversions', 'Impressions', 'Revenue'] if col in df.columns]
            
            col1, col2 = st.columns(2)
            with col1:
                primary_metric = st.selectbox("Primary Metric (Bars)", available_metrics, key="platform_primary")
            with col2:
                secondary_options = [m for m in available_metrics if m != primary_metric]
                secondary_metric = st.selectbox("Secondary Metric (Line)", secondary_options, key="platform_secondary") if secondary_options else None
            
            if primary_metric:
                if secondary_metric:
                    # Dual-axis chart
                    fig = create_dual_axis_chart(
                        df,
                        x_col='Platform',
                        primary_metric=primary_metric,
                        secondary_metric=secondary_metric,
                        title=f'{primary_metric} vs {secondary_metric} by Platform'
                    )
                else:
                    # Single metric bar chart
                    platform_data = df.groupby('Platform')[primary_metric].sum().reset_index()
                    platform_data = platform_data.sort_values(primary_metric, ascending=False)
                    fig = px.bar(
                        platform_data,
                        x='Platform',
                        y=primary_metric,
                        title=f'{primary_metric} by Platform',
                        color='Platform'
                    )
                    fig.update_layout(template='plotly_dark')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Pie chart for primary metric
                platform_data = df.groupby('Platform')[primary_metric].sum().reset_index()
                fig_pie = px.pie(
                    platform_data,
                    values=primary_metric,
                    names='Platform',
                    title=f'{primary_metric} Distribution'
                )
                fig_pie.update_layout(template='plotly_dark')
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Platform column not found in data")
    
    elif viz_type == "Funnel Analysis":
        st.markdown("### 🔽 Funnel Analysis")
        
        required_cols = ['Impressions', 'Clicks', 'Conversions']
        if all(col in df.columns for col in required_cols):
            # Calculate funnel metrics
            impressions = df['Impressions'].sum()
            clicks = df['Clicks'].sum()
            conversions = df['Conversions'].sum()
            
            funnel_data = pd.DataFrame({
                'Stage': ['Impressions', 'Clicks', 'Conversions'],
                'Count': [impressions, clicks, conversions],
                'Percentage': [100, (clicks/impressions)*100 if impressions > 0 else 0, (conversions/impressions)*100 if impressions > 0 else 0]
            })
            
            # Funnel chart
            fig = px.funnel(
                funnel_data,
                x='Count',
                y='Stage',
                title='Conversion Funnel'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Conversion rates
            col1, col2, col3 = st.columns(3)
            with col1:
                ctr = (clicks/impressions)*100 if impressions > 0 else 0
                st.metric("Click-Through Rate", f"{ctr:.2f}%")
            with col2:
                cvr = (conversions/clicks)*100 if clicks > 0 else 0
                st.metric("Conversion Rate", f"{cvr:.2f}%")
            with col3:
                overall_cvr = (conversions/impressions)*100 if impressions > 0 else 0
                st.metric("Overall Conversion", f"{overall_cvr:.2f}%")
        else:
            st.info("Required columns (Impressions, Clicks, Conversions) not found")
    
    elif viz_type == "Correlation Matrix":
        st.markdown("### 🔗 Correlation Matrix")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) >= 2:
            # Calculate correlation
            corr_matrix = df[numeric_cols].corr()
            
            # Heatmap
            fig = px.imshow(
                corr_matrix,
                title='Correlation Heatmap',
                color_continuous_scale='RdBu',
                aspect='auto'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Insights
            st.markdown("#### Key Correlations")
            
            # Find strongest correlations
            corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_pairs.append({
                        'Metric 1': corr_matrix.columns[i],
                        'Metric 2': corr_matrix.columns[j],
                        'Correlation': corr_matrix.iloc[i, j]
                    })
            
            corr_df = pd.DataFrame(corr_pairs)
            corr_df = corr_df.sort_values('Correlation', ascending=False, key=abs)
            
            st.dataframe(corr_df.head(10), use_container_width=True)
        else:
            st.info("Not enough numeric columns for correlation analysis")
    
    elif viz_type == "Custom Chart":
        st.markdown("### 🎨 Custom Chart Builder")
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart_type = st.selectbox(
                "Chart Type",
                ["Bar", "Line", "Scatter", "Box", "Histogram"]
            )
        
        with col2:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                y_axis = st.selectbox("Y-Axis", numeric_cols)
            else:
                y_axis = None
        
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            x_axis = st.selectbox("X-Axis", categorical_cols + ['Date'] if 'Date' in df.columns else categorical_cols)
        else:
            x_axis = None
        
        if x_axis and y_axis:
            if st.button("🚀 Generate Chart"):
                if chart_type == "Bar":
                    chart_data = df.groupby(x_axis)[y_axis].sum().reset_index()
                    fig = px.bar(chart_data, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
                elif chart_type == "Line":
                    chart_data = df.groupby(x_axis)[y_axis].sum().reset_index()
                    fig = px.line(chart_data, x=x_axis, y=y_axis, title=f"{y_axis} Trend")
                elif chart_type == "Scatter":
                    fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
                elif chart_type == "Box":
                    fig = px.box(df, x=x_axis, y=y_axis, title=f"{y_axis} Distribution by {x_axis}")
                elif chart_type == "Histogram":
                    fig = px.histogram(df, x=y_axis, title=f"{y_axis} Distribution")
                
                fig.update_layout(
                    template='plotly_dark',
                    height=500,
                    margin=dict(l=80, r=40, t=60, b=60),
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(128,128,128,0.3)',
                        showline=True,
                        linewidth=2,
                        linecolor='rgba(255,255,255,0.3)',
                        tickfont=dict(size=12)
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(128,128,128,0.3)',
                        showline=True,
                        linewidth=2,
                        linecolor='rgba(255,255,255,0.3)',
                        tickfont=dict(size=12),
                        showticklabels=True
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # ========================================
    # ADDITIONAL CUSTOM CHART BUILDER (NEW)
    # ========================================
    st.divider()
    st.markdown("### 🎨 Advanced Custom Chart Builder")
    st.markdown("*Create sophisticated visualizations with full control*")
    
    col1, col2, col3 = st.columns(3)
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    with col1:
        adv_chart_type = st.selectbox(
            "Chart Type",
            ["Bar Chart", "Line Chart", "Scatter Plot", "Area Chart", "Pie Chart", "Heatmap", "Box Plot", "Violin Plot"],
            key="adv_chart_type"
        )
    
    with col2:
        if adv_chart_type in ["Bar Chart", "Line Chart", "Area Chart", "Pie Chart"]:
            adv_x_axis = st.selectbox("X-Axis", categorical_cols + (['Date'] if 'Date' in df.columns else []), key="adv_x")
        elif adv_chart_type == "Scatter Plot":
            adv_x_axis = st.selectbox("X-Axis (Numeric)", numeric_cols, key="adv_x")
        else:
            adv_x_axis = st.selectbox("X-Axis", categorical_cols, key="adv_x")
    
    with col3:
        if adv_chart_type != "Pie Chart":
            adv_y_axis = st.selectbox("Y-Axis (Metric)", numeric_cols, key="adv_y")
        else:
            adv_y_axis = st.selectbox("Value (Metric)", numeric_cols, key="adv_y")
    
    # Additional options
    col1, col2, col3 = st.columns(3)
    with col1:
        adv_color_by = st.selectbox("Color By (Optional)", ["None"] + categorical_cols, key="adv_color")
    with col2:
        adv_aggregation = st.selectbox("Aggregation", ["Sum", "Mean", "Count", "Max", "Min", "Median"], key="adv_agg")
    with col3:
        adv_show_values = st.checkbox("Show Values on Chart", value=False, key="adv_show_values")
    
    if st.button("📊 Generate Advanced Chart", key="generate_adv"):
        try:
            # Prepare data based on aggregation
            agg_map = {"Sum": "sum", "Mean": "mean", "Count": "count", "Max": "max", "Min": "min", "Median": "median"}
            
            if adv_chart_type == "Bar Chart":
                chart_data = df.groupby(adv_x_axis)[adv_y_axis].agg(agg_map[adv_aggregation]).reset_index()
                if adv_color_by != "None":
                    chart_data = df.groupby([adv_x_axis, adv_color_by])[adv_y_axis].agg(agg_map[adv_aggregation]).reset_index()
                    fig = px.bar(chart_data, x=adv_x_axis, y=adv_y_axis, color=adv_color_by, 
                                title=f"{adv_y_axis} by {adv_x_axis}", text=adv_y_axis if adv_show_values else None)
                else:
                    fig = px.bar(chart_data, x=adv_x_axis, y=adv_y_axis, 
                                title=f"{adv_y_axis} by {adv_x_axis}", text=adv_y_axis if adv_show_values else None)
            
            elif adv_chart_type == "Line Chart":
                chart_data = df.groupby(adv_x_axis)[adv_y_axis].agg(agg_map[adv_aggregation]).reset_index()
                if adv_color_by != "None":
                    chart_data = df.groupby([adv_x_axis, adv_color_by])[adv_y_axis].agg(agg_map[adv_aggregation]).reset_index()
                    fig = px.line(chart_data, x=adv_x_axis, y=adv_y_axis, color=adv_color_by, 
                                 markers=True, title=f"{adv_y_axis} Trend")
                else:
                    fig = px.line(chart_data, x=adv_x_axis, y=adv_y_axis, markers=True, title=f"{adv_y_axis} Trend")
            
            elif adv_chart_type == "Scatter Plot":
                fig = px.scatter(df, x=adv_x_axis, y=adv_y_axis, 
                                color=adv_color_by if adv_color_by != "None" else None,
                                size=adv_y_axis if adv_show_values else None,
                                title=f"{adv_y_axis} vs {adv_x_axis}")
            
            elif adv_chart_type == "Area Chart":
                chart_data = df.groupby(adv_x_axis)[adv_y_axis].agg(agg_map[adv_aggregation]).reset_index()
                fig = px.area(chart_data, x=adv_x_axis, y=adv_y_axis, title=f"{adv_y_axis} Area")
            
            elif adv_chart_type == "Pie Chart":
                chart_data = df.groupby(adv_x_axis)[adv_y_axis].agg(agg_map[adv_aggregation]).reset_index()
                fig = px.pie(chart_data, values=adv_y_axis, names=adv_x_axis, 
                            title=f"{adv_y_axis} Distribution",
                            hole=0.3 if adv_show_values else 0)
            
            elif adv_chart_type == "Box Plot":
                fig = px.box(df, x=adv_x_axis, y=adv_y_axis, 
                            color=adv_color_by if adv_color_by != "None" else None,
                            title=f"{adv_y_axis} Distribution by {adv_x_axis}")
            
            elif adv_chart_type == "Violin Plot":
                fig = px.violin(df, x=adv_x_axis, y=adv_y_axis, 
                               color=adv_color_by if adv_color_by != "None" else None,
                               box=True, title=f"{adv_y_axis} Distribution by {adv_x_axis}")
            
            elif adv_chart_type == "Heatmap":
                if adv_color_by != "None":
                    pivot_data = df.pivot_table(values=adv_y_axis, index=adv_x_axis, 
                                                columns=adv_color_by,
                                                aggfunc=agg_map[adv_aggregation])
                    fig = px.imshow(pivot_data, title=f"{adv_y_axis} Heatmap", aspect="auto",
                                   labels=dict(x=adv_color_by, y=adv_x_axis, color=adv_y_axis))
                else:
                    st.warning("Please select a 'Color By' dimension for heatmap")
                    fig = None
            
            if fig:
                fig.update_layout(
                    template='plotly_dark',
                    height=500,
                    showlegend=True,
                    xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show summary statistics
                if adv_chart_type not in ["Pie Chart", "Heatmap"]:
                    st.markdown("**Summary Statistics:**")
                    summary = df.groupby(adv_x_axis)[adv_y_axis].agg(['count', 'sum', 'mean', 'min', 'max']).reset_index()
                    summary.columns = [adv_x_axis, 'Count', 'Total', 'Average', 'Min', 'Max']
                    st.dataframe(summary, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error creating chart: {str(e)[:200]}")

def render_settings_page():
    """Render settings page."""
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    st.subheader("Application Settings")
    
    # Privacy & Anonymization Settings
    st.markdown("### 🔒 Privacy & Data Anonymization")
    st.markdown("""
    Control how your data is protected before being sent to external LLM APIs (OpenAI, Gemini, Anthropic).
    Anonymization replaces sensitive values with tokens, then restores them in the response.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        anonymization_level = st.selectbox(
            "Anonymization Level",
            options=["None", "Light", "Moderate", "Strict"],
            index=2,  # Default to Moderate
            key="anonymization_level",
            help="""
            • **None**: No anonymization - all data sent as-is
            • **Light**: Campaign names, client names, brand names tokenized
            • **Moderate**: Light + geographic data, creative names, ad groups
            • **Strict**: All identifiable fields + audience segments, placements
            """
        )
    
    with col2:
        st.markdown("#### What's Protected")
        if anonymization_level == "None":
            st.warning("⚠️ No protection")
        elif anonymization_level == "Light":
            st.info("🔐 Campaign, Client, Brand names")
        elif anonymization_level == "Moderate":
            st.info("🔐 Names + Geo, Creative, Ad Groups")
        else:
            st.success("🔐 All identifiable fields")
    
    # Show example
    with st.expander("📋 See Anonymization Example"):
        st.markdown("**Before (sent to LLM):**")
        st.code("""
{
  "campaign_name": "Campaign_001",
  "client": "Client_001", 
  "geo": "Region_001",
  "spend": 45000,  // Numbers NOT anonymized
  "ctr": 2.5       // Metrics NOT anonymized
}
        """)
        st.markdown("**After (displayed to you):**")
        st.code("""
{
  "campaign_name": "Summer Sale 2024",
  "client": "Acme Corp",
  "geo": "United States",
  "spend": 45000,
  "ctr": 2.5
}
        """)
    
    st.divider()
    
    # Cache settings
    st.markdown("### 🗄️ Cache Settings")
    
    cache_enabled = st.checkbox("Enable caching", value=True)
    cache_ttl = st.slider("Cache TTL (minutes)", 5, 120, 60)
    
    st.divider()
    
    # LLM Settings
    st.markdown("### 🤖 LLM Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("OpenAI API Key", type="password", key="openai_key_setting", 
                     placeholder="sk-...", help="For GPT-4o-mini fallback")
    with col2:
        st.text_input("Google API Key", type="password", key="google_key_setting",
                     placeholder="AIza...", help="For Gemini 2.0 Flash")
    
    if st.button("💾 Save Settings", type="primary"):
        # Save anonymization level to environment
        import os
        level_map = {"None": "none", "Light": "light", "Moderate": "moderate", "Strict": "strict"}
        os.environ['ANONYMIZATION_LEVEL'] = level_map.get(anonymization_level, "moderate")
        st.success(f"✅ Settings saved! Anonymization level: {anonymization_level}")
    
    # Debug info
    with st.expander("🔧 Debug Information"):
        st.json({
            'session_state_keys': list(st.session_state.keys()),
            'cache_stats': CacheManager.get_cache_stats(),
            'anonymization_level': anonymization_level
        })


def main():
    """Main application entry point with full feature initialization."""
    # Initialize session state
    init_session_state()
    
    # Initialize all AI agents (cached)
    agents = initialize_agents()
    if agents:
        for key, agent in agents.items():
            if st.session_state.get(key) is None:
                st.session_state[key] = agent
    
    # Render sidebar
    render_sidebar()
    
    # Render current page
    page = st.session_state.current_page
    
    if page == "home":
        render_home_page()
    elif page == "analysis":
        render_analysis_page()
    elif page == "in-depth analysis":
        render_deep_dive_page()
    elif page == "visualizations":
        render_visualizations_page()
    elif page == "q&a":
        render_qa_page()
    elif page == "settings":
        render_settings_page()
    
    # Footer with version info
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("🚀 PCA Agent v2.0 - Enhanced Modular")
    with col2:
        st.caption("🤖 All AI Agents Active")
    with col3:
        st.caption("📊 Built with Streamlit")
    
    # Show active features
    with st.expander("✨ Active Features"):
        features = [
            "✅ MediaAnalyticsExpert",
            "✅ Channel Specialists (Google, Meta, LinkedIn, etc.)",
            "✅ Dynamic Benchmark Engine",
            "✅ Enhanced Reasoning Agent",
            "✅ Smart Visualization Agent",
            "✅ NL to SQL Query Engine",
            "✅ B2B Specialist Agent",
            "✅ Smart Filter Engine",
            "✅ Query Tracking & Evaluation"
        ]
        for feature in features:
            st.markdown(feature)


if __name__ == "__main__":
    logger.info("Starting PCA Agent (Modular)")
    main()

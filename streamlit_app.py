"""Unified PCA Agent Streamlit app with auto-analysis and Q&A."""
# At the top of streamlit_app_hitl.py
import sys
import os
import io
from pathlib import Path

# Add both current directory and parent to Python path for Streamlit Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

import streamlit as st

# DELETE OR COMMENT OUT THESE LINES (11-17):
# print("Project root:", project_root)
# print("Files in src/query_engine/:")
# query_engine_path = project_root / "src" / "query_engine"
# if query_engine_path.exists():
#     print(os.listdir(query_engine_path))
# else:
#     print("Directory doesn't exist!")

# Then your imports...
import time
import re
import html
from datetime import datetime
from typing import Dict, Optional, Tuple, List, Any

import numpy as np
import pandas as pd
import plotly.express as px
# REMOVE this duplicate streamlit import (line 25):
# import streamlit as st
from dotenv import load_dotenv
from loguru import logger

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
#from src.query_engine.smart_interpretation import SmartQueryInterpreter
#from src.orchestration.query_orchestrator import QueryOrchestrator

load_dotenv()


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

CACHE_DIR = ".pca_cache"
LAST_CSV_PATH = os.path.join(CACHE_DIR, "last_campaign_data.csv")
os.makedirs(CACHE_DIR, exist_ok=True)
SAMPLE_DATA_PATH = Path(__file__).parent / "data" / "historical_campaigns_sample.csv"

REQUIRED_COLUMNS = ["Campaign_Name", "Platform", "Spend"]
RECOMMENDED_COLUMNS = ["Conversions", "Revenue", "Date", "Placement"]

st.set_page_config(
    page_title="PCA Agent - Auto Analysis + Q&A",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
    /* ============================================
       ENTERPRISE DESIGN SYSTEM - PCA AGENT
       ============================================ */
    
    /* === TYPOGRAPHY === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    
    h1, h2, h3 {
        font-weight: 600;
        letter-spacing: -0.01em;
        color: #f1f5f9 !important;
    }
    
    /* IE11 fallback for text visibility */
    p, span, div, label {
        color: #e2e8f0 !important;
        opacity: 1 !important;
    }
    
    /* === LAYOUT & CONTAINERS === */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1400px;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.1);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.12);
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
        opacity: 1 !important;
    }
    
    /* IE11: Force text contrast */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        padding: 0.5rem 0;
    }
    
    /* === TABS === */
    [data-testid="stTabs"] {
        background: rgba(15, 23, 42, 0.4);
        border-radius: 16px;
        padding: 0.5rem;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
    }
    
    [data-testid="stTabs"] [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        color: #94a3b8;
        font-weight: 500;
        font-size: 0.95rem;
        border: none;
        transition: all 0.2s ease;
    }
    
    [data-testid="stTabs"] [data-baseweb="tab"]:hover {
        background: rgba(59, 130, 246, 0.1);
        color: #cbd5e1;
    }
    
    [data-testid="stTabs"] [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: #ffffff !important;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* === CARDS === */
    .metric-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
        backdrop-filter: blur(16px);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 48px rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    .insight-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        backdrop-filter: blur(16px);
        padding: 1.5rem;
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        margin-bottom: 1rem;
        color: #e2e8f0;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        max-height: 260px;
        overflow-y: auto;
        scrollbar-width: thin;
    }
    
    .insight-card:hover {
        transform: translateY(-2px);
        border-left-color: #8b5cf6;
    }

    .exec-summary {
        font-size: 1rem;
        line-height: 1.6;
        color: #e2e8f0 !important;
        margin-bottom: 0;
        white-space: pre-wrap;
        opacity: 1 !important;
    }
    
    /* IE11: Force all text elements to be visible */
    .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: #e2e8f0 !important;
        opacity: 1 !important;
    }
    
    .quick-nav-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .quick-nav-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.85rem 1rem;
        border-radius: 12px;
        background: rgba(59, 130, 246, 0.12);
        color: #e2e8f0;
        font-weight: 600;
        text-decoration: none;
        border: 1px solid rgba(148, 163, 184, 0.2);
        transition: all 0.2s ease;
    }
    
    .quick-nav-button:hover {
        background: rgba(59, 130, 246, 0.25);
        border-color: rgba(59, 130, 246, 0.6);
        color: #fff;
        background: linear-gradient(90deg, transparent 0%, rgba(59, 130, 246, 0.3) 50%, transparent 100%);
    }
    
    /* === BUTTONS === */
    .stButton > button {
        border-radius: 12px;
        font-weight: 500;
        font-size: 0.95rem;
        padding: 0.65rem 1.75rem;
        transition: all 0.2s ease;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
        filter: brightness(1.1);
    }
    
    .stButton > button:not([kind="primary"]) {
        background: rgba(30, 41, 59, 0.6);
        color: #cbd5e1;
        backdrop-filter: blur(8px);
    }
    
    .stButton > button:not([kind="primary"]):hover {
        background: rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.3);
        color: #e2e8f0;
    }
    
    /* === INPUTS & FORMS === */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        backdrop-filter: blur(8px);
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {
        border-color: rgba(59, 130, 246, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* === DATAFRAMES & TABLES === */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(16px);
    }
    
    /* === METRICS === */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #f1f5f9;
        letter-spacing: -0.02em;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 500;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    /* === EXPANDERS === */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.1);
        color: #e2e8f0;
        font-weight: 500;
        backdrop-filter: blur(8px);
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    /* === ALERTS & MESSAGES === */
    .stAlert {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        backdrop-filter: blur(16px);
        padding: 1rem 1.25rem;
    }
    
    .stSuccess {
        border-left-color: #10b981;
        background: rgba(16, 185, 129, 0.1);
    }
    
    .stWarning {
        border-left-color: #f59e0b;
        background: rgba(245, 158, 11, 0.1);
    }
    
    .stError {
        border-left-color: #ef4444;
        background: rgba(239, 68, 68, 0.1);
    }
    
    .stInfo {
        border-left-color: #3b82f6;
        background: rgba(59, 130, 246, 0.1);
    }
    
    /* === CHARTS === */
    .js-plotly-plot {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    /* === FILE UPLOADER === */
    [data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.6);
        border: 2px dashed rgba(148, 163, 184, 0.3);
        border-radius: 16px;
        padding: 2rem;
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(59, 130, 246, 0.5);
        background: rgba(59, 130, 246, 0.05);
    }
    
    /* === RADIO BUTTONS === */
    .stRadio > div {
        background: rgba(30, 41, 59, 0.4);
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(59, 130, 246, 0.5);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(59, 130, 246, 0.7);
    }
    
    /* === DOWNLOAD BUTTON === */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 500;
        padding: 0.65rem 1.5rem;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
    }
    
    /* === SPINNER === */
    .stSpinner > div {
        border-top-color: #3b82f6 !important;
    }
    
    /* === CODE BLOCKS === */
    .stCodeBlock {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    /* === RESPONSIVE DESIGN === */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .main-header {
            font-size: 2rem;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------
def init_state():
    defaults = {
        "analysis_complete": False,
        "analysis_data": None,
        "df": None,
        "df_loaded_from_cache": False,
        "query_tracker": QueryTracker(),
        "interpreter": None,
      #  "orchestrator": None,
        "current_query_id": None,
        "interpretations": None,
        "selected_interpretation": None,
        "query_engine": None,
        "session_id": str(datetime.now().timestamp()),
        "chart_generator": SmartChartGenerator(),
        "overview_charts": None,
        "last_result": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


init_state()


def load_cached_df_if_available():
    if st.session_state.get("df") is None and os.path.exists(LAST_CSV_PATH):
        try:
            df_cached = pd.read_csv(LAST_CSV_PATH)
            # Apply normalization to cached data too
            df_cached = normalize_campaign_dataframe(df_cached)
            st.session_state.df = df_cached
            st.session_state.df_loaded_from_cache = True
        except Exception:
            st.session_state.df_loaded_from_cache = False


load_cached_df_if_available()


# ---------------------------------------------------------------------------
# Database Integration Helper
# ---------------------------------------------------------------------------
@st.cache_resource
def get_db_manager():
    """Get cached database manager instance."""
    return get_streamlit_db_manager()


def save_to_database(df: pd.DataFrame) -> bool:
    """
    Save DataFrame to database.
    
    Args:
        df: DataFrame to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db_manager = get_db_manager()
        result = db_manager.import_dataframe(df)
        
        if result['success']:
            logger.info(f"✅ Saved {result['imported_count']} campaigns to database")
            return True
        else:
            logger.error(f"❌ Database save failed: {result['message']}")
            return False
    except Exception as e:
        logger.error(f"❌ Database save error: {e}")
        return False


def _get_column(df: pd.DataFrame, metric: str) -> Optional[str]:
    """Use shared column mappings from MediaAnalyticsExpert to find actual column name."""
    mappings = getattr(MediaAnalyticsExpert, "COLUMN_MAPPINGS", {})
    metric = metric.lower()
    if metric in mappings:
        for col_name in mappings[metric]:
            if col_name in df.columns:
                return col_name
    return None


def _strip_light_markup(text: str) -> str:
    """Remove italics/underline markers and fix ALL number-letter spacing issues."""
    if not isinstance(text, str):
        return text
    
    # PASS 1: Basic HTML cleanup
    text = text.replace('&nbsp;', ' ').replace('\xa0', ' ')
    text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    text = re.sub(r'<(i|em)>(.*?)</\1>', lambda m: f"**{m.group(2).strip()}**", text, flags=re.DOTALL)
    text = re.sub(r'</?(i|em)>', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    
    # PASS 2: Remove asterisks and underscores
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'_+', '', text)
    
    # PASS 3: Fix em-dash and en-dash spacing
    text = text.replace('—', ' - ')
    text = text.replace('–', ' - ')
    
    # PASS 4: SIMPLE RULE - Always space after any number or decimal
    # This catches ALL cases: 39.05CPA, 992campaigns, 4.45Macross, etc.
    for _ in range(5):
        # Space after decimal number followed by any letter
        text = re.sub(r'(\d+\.\d+)([A-Za-z])', r'\1 \2', text)
        # Space after integer followed by any letter
        text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
        # Space before number when preceded by letter
        text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)
    
    # PASS 5: Fix common concatenated patterns
    common_fixes = {
        'versusDIS': 'versus DIS',
        'versusSOC': 'versus SOC',
        'comparedto': 'compared to',
        'fromDIS': 'from DIS',
        'fromSOC': 'from SOC',
        'toSOC': 'to SOC',
        'toDIS': 'to DIS',
        'isconcerning': 'is concerning',
        'isnotably': 'is notably',
        'asit': 'as it',
        'wheretheCPA': 'where the CPA',
        'fromGoogleAds': 'from Google Ads',
        'toMetaAds': 'to Meta Ads',
        'tooptimize': 'to optimize',
        'whichcould': 'which could',
        'couldpotentially': 'could potentially',
        'andgenerate': 'and generate',
        'anadditional': 'an additional',
        'theoverall': 'the overall',
        'especiallyfor': 'especially for',
        'GoogleAds': 'Google Ads',
        'MetaAds': 'Meta Ads',
        'Thisreallocation': 'This reallocation',
        'wouldreduce': 'would reduce',
        'spendto': 'spend to',
        'potentiallygenerating': 'potentially generating',
        'additionalconversions': 'additional conversions',
        'basedoncurrent': 'based on current',
        'performanceratios': 'performance ratios',
        'costefficiency': 'cost efficiency',
        'percentCTR': 'percent CTR',
        'higherthan': 'higher than',
        'establishesitas': 'establishes it as',
        'yourprimary': 'your primary',
        'growthengine': 'growth engine',
        'withproven': 'with proven',
        'scalabilitypotential': 'scalability potential',
        'Youroverall': 'Your overall',
        'trafficacquisit': 'traffic acquisit',
        'spendwhileachieving': 'spend while achieving',
        'xbetter': 'x better',

        # Targeted fixes for remaining artifacts seen in SECTION 1
        'spendacross': 'spend across',
        'campaignsand': 'campaigns and',
        'Plat form': 'Platform',
        'plat forms': 'platforms',
        'Overallper formance': 'Overall performance',
        'per formance': 'performance',
        'per formanceshows': 'performance shows',
        
        # Fixes for concatenated words after numbers
        'CPAcombined': 'CPA combined',
        'CPCThe': 'CPC. The',
        'percentconversion': 'percent conversion',
        'ratereveals': 'rate reveals',
        'revealsahigh': 'reveals a high',
        'ahigh-intent': 'a high-intent',
        'audiencebut': 'audience but',
        'butinefficient': 'but inefficient',
        'inefficienttraffic': 'inefficient traffic',
        'trafficacquisition': 'traffic acquisition',
        'acquisitionat': 'acquisition at',
        'withexceptional': 'with exceptional',
        
        # New fixes based on latest screenshots
        'campaignson': 'campaigns on',
        'platformsgenerating': 'platforms generating',
        'conversionsat': 'conversions at',
        'CPAfrom': 'CPA from',
        'CPAwith': 'CPA with',
        'Mat': 'M at',
        'Kconversions': 'K conversions',
        'Mspend': 'M spend',
        'Mimpressions': 'M impressions',
        'Mclicks': 'M clicks',
        'conversionswhile': 'conversions while',
        'whileDIS': 'while DIS',
        'DISseverely': 'DIS severely',
        'severelyunderperforms': 'severely underperforms',
        'underperformsat': 'underperforms at',
        'performsat': 'performs at',
    }
    for wrong, correct in common_fixes.items():
        text = text.replace(wrong, correct)
    
    # PASS 6: Fix punctuation spacing
    text = re.sub(r'([.,;:!?])([A-Za-z0-9])', r'\1 \2', text)
    text = re.sub(r'(\))([A-Za-z])', r'\1 \2', text)
    
    # PASS 7: Fix camelCase (lowercase followed by uppercase)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # PASS 8: Fix uppercase abbreviations followed by lowercase (CPAat -> CPA at)
    text = re.sub(r'([A-Z]{2,})([a-z])', r'\1 \2', text)
    
    # PASS 9: Fix formatting issues with lines starting with numbers
    text = re.sub(r'^(\d+)\.([A-Z])', r'\1. \2', text, flags=re.MULTILINE)
    text = re.sub(r'\n(\d+)\.([A-Z])', r'\n\1. \2', text)
    
    # PASS 10: Final aggressive number-letter fix (run again to catch any remaining)
    for _ in range(3):
        text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
        text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)
    
    # PASS 11: Remove brackets from headers - [OVERALL SUMMARY] -> OVERALL SUMMARY:
    text = re.sub(r'\[OVERALL SUMMARY\]', 'OVERALL SUMMARY:', text)
    text = re.sub(r'\[CHANNEL SUMMARY\]', 'CHANNEL SUMMARY:', text)
    text = re.sub(r'\[KEY STRENGTH\]', 'KEY STRENGTH:', text)
    text = re.sub(r'\[PRIORITY ACTION\]', 'PRIORITY ACTION:', text)
    text = re.sub(r'\[BENCHMARK PERFORMANCE\]', 'BENCHMARK PERFORMANCE:', text)
    text = re.sub(r'\[CRITICAL GAP\]', 'CRITICAL GAP:', text)
    
    # PASS 11b: Remove "SECTION N:" from headers
    # "SECTION 1: Performance Overview" -> "Performance Overview"
    text = re.sub(r'###?\s*SECTION\s*\d+:\s*', '', text)
    text = re.sub(r'SECTION\s*\d+:\s*', '', text)
    
    # PASS 12: Clean up multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    
    return text


def _build_key_highlights(analysis: Dict[str, Any]) -> List[str]:
    """Generate deterministic key highlights from analysis payload."""
    highlights: List[str] = []
    metrics = analysis.get("metrics") or {}
    overview = metrics.get("overview") or {}
    by_platform = metrics.get("by_platform") or {}
    by_campaign = metrics.get("by_campaign") or {}

    total_spend = overview.get("total_spend")
    total_conv = overview.get("total_conversions")
    total_campaigns = overview.get("total_campaigns")
    total_platforms = overview.get("total_platforms")
    total_impr = overview.get("total_impressions")
    total_clicks = overview.get("total_clicks")

    if total_spend is not None:
        highlights.append(
            f"${total_spend:,.0f} in media spend delivered {total_conv:,.0f} conversions across {total_campaigns} campaigns on {total_platforms} platforms."
        )
    if overview:
        kpi_bits = []
        if overview.get("avg_roas"):
            kpi_bits.append(f"ROAS {overview['avg_roas']:.2f}x")
        if overview.get("avg_ctr"):
            kpi_bits.append(f"CTR {overview['avg_ctr']:.2f}%")
        if overview.get("avg_cpa"):
            kpi_bits.append(f"CPA ${overview['avg_cpa']:.2f}")
        if overview.get("avg_conversion_rate"):
            kpi_bits.append(f"Conv Rate {overview['avg_conversion_rate']:.2f}%")
        if kpi_bits:
            highlights.append("Key efficiency KPIs: " + ", ".join(kpi_bits))

    if by_platform:
        best_platform = max(
            by_platform.items(),
            key=lambda item: item[1].get('ROAS', 0),
        )
        platform_name, stats = best_platform
        highlights.append(
            f"{platform_name} leads with ROAS {stats.get('ROAS', 0):.2f}x and CTR {stats.get('CTR', 0):.2f}%."
        )

    if by_campaign:
        best_campaign = max(
            by_campaign.items(),
            key=lambda item: item[1].get('ROAS', 0),
        )
        camp_name, stats = best_campaign
        highlights.append(
            f"Top campaign '{camp_name}' is driving ROAS {stats.get('ROAS', 0):.2f}x on ${stats.get('Spend', 0):,.0f} spend."
        )

    insights = analysis.get("insights") or []
    for insight in insights[:1]:
        insight_text = insight.get("insight")
        if insight_text:
            highlights.append(insight_text)

    # Keep first four unique highlights
    deduped = []
    for point in highlights:
        if point and point not in deduped:
            deduped.append(point)
        if len(deduped) == 4:
            break
    return deduped


def _infer_monthly_agg(column_name: str) -> str:
    """Heuristically determine aggregation for monthly metrics."""
    lowered = column_name.lower()
    if any(keyword in lowered for keyword in ["rate", "roas", "ctr", "cpa", "cpc", "avg", "average"]):
        return "mean"
    return "sum"


def _resolve_dimension_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """Resolve dimension column with case-insensitive matching."""
    # First try exact match
    for col in candidates:
        if col in df.columns:
            return col
    
    # Then try case-insensitive match
    df_cols_lower = {col.lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate.lower() in df_cols_lower:
            return df_cols_lower[candidate.lower()]
    
    return None


MONTHLY_DIMENSION_CANDIDATES = [
    ("Platform", ["Platform"]),
    ("Age", ["Age", "Age_Group", "Age_Bucket", "Age_Range"]),
    ("Funnel", ["Funnel_Stage", "Funnel", "Stage", "Campaign_Type"]),
    ("Placement", ["Placement", "Inventory_Type"]),
    ("Creative", ["Creative", "Creative_Type", "Ad_Name"]),
    ("Ad Type", ["Ad_Type", "Format", "Ad_Format"]),
    ("Audience", ["Audience", "Audience_Type", "Segment"]),
    ("Region", ["Region", "Geo", "Country", "Location"]),
]


def _get_funnel_column(df: pd.DataFrame) -> Optional[str]:
    return _resolve_dimension_column(df, ["Funnel_Stage", "Funnel", "Stage", "Campaign_Type"])


def validate_campaign_dataframe(df: pd.DataFrame) -> Dict[str, list]:
    """Validate essential columns and data quality for enterprise ingestion."""
    report = {
        "missing_required": [col for col in REQUIRED_COLUMNS if col not in df.columns],
        "missing_recommended": [col for col in RECOMMENDED_COLUMNS if col not in df.columns],
        "alerts": [],
    }

    if "Spend" in df.columns and (df["Spend"].fillna(0) < 0).any():
        report["alerts"].append("Detected negative values in Spend column")
    if "Conversions" in df.columns and (df["Conversions"].fillna(0) < 0).any():
        report["alerts"].append("Conversions column contains negative values")
    if df.duplicated().any():
        report["alerts"].append("Duplicate rows detected")

    return report


def _process_campaign_dataframe(df: pd.DataFrame, metadata: Dict) -> Tuple[pd.DataFrame, Dict, Dict]:
    """Normalize, validate, and log metadata for a campaign dataframe."""
    df = normalize_campaign_dataframe(df)
    metadata.update({"rows": len(df), "columns": len(df.columns)})

    validation = validate_campaign_dataframe(df)
    if validation["missing_required"]:
        validation["status"] = "error"
    elif validation["alerts"] or validation["missing_recommended"]:
        validation["status"] = "warn"
    else:
        validation["status"] = "ok"

    logger.info(
        "Data ingestion completed",
        **metadata,
        validation_status=validation["status"],
        missing_required=len(validation["missing_required"]),
        missing_recommended=len(validation["missing_recommended"]),
        alerts=len(validation["alerts"]),
    )

    return df, metadata, validation


def ingest_campaign_data(uploaded_file, source: str = "auto_analysis") -> Tuple[Optional[pd.DataFrame], Dict, Dict]:
    """Centralized ingestion pipeline with logging and validation."""
    metadata = {
        "source": source,
        "file_name": getattr(uploaded_file, "name", "unknown"),
        "file_type": getattr(uploaded_file, "type", "unknown"),
        "file_size": getattr(uploaded_file, "size", 0),
    }

    df, error = DataLoader.load_from_streamlit_upload(uploaded_file, validate=True, fix_column_names=False)
    if error:
        logger.error("Data ingestion failed", **metadata, error=error)
        return None, metadata, {"error": error}

    return _process_campaign_dataframe(df, metadata)


def load_sample_campaign_data() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Load bundled sample dataset for demos."""
    if not SAMPLE_DATA_PATH.exists():
        return None, "Sample dataset not found"

    df, error = DataLoader.load_csv(SAMPLE_DATA_PATH, validate=False, fix_column_names=False)
    if error:
        return None, error

    df, _, _ = _process_campaign_dataframe(df, {"source": "sample", "file_name": SAMPLE_DATA_PATH.name})
    return df, None


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image(
        "https://via.placeholder.com/220x80/667eea/ffffff?text=PCA+Agent",
        width="stretch",
    )
    st.markdown("---")

    st.markdown("### 🎯 Capabilities")
    st.markdown(
        """
        - 📊 Auto-insights dashboard
        - 💡 Executive summaries & metrics
        - 📈 Performance analytics & visualizations
        - 💬 Q&A
        - 📜 Query history & tracking
        """
    )

    st.markdown("---")
    if st.button("🔄 Reset Workspace", width="stretch"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        if os.path.exists(LAST_CSV_PATH):
            try:
                os.remove(LAST_CSV_PATH)
            except Exception:
                pass
        st.experimental_set_query_params()
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Q&A Metrics")
    metrics = st.session_state.query_tracker.get_metrics_summary()
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Total Queries", metrics["total_queries"])
        st.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
    with col_b:
        st.metric("Avg Feedback", f"{metrics['avg_feedback']:.2f}")
        st.metric("Interp. Accuracy", f"{metrics['interpretation_accuracy']:.1f}%")
    st.metric("Avg Response Time", f"{metrics['avg_execution_time_ms']:.0f} ms")

    if st.button("📥 Export Query Logs", width="stretch"):
        export_path = st.session_state.query_tracker.export_to_csv()
        st.success(f"Exported to {export_path}")


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<h1 class="main-header">PCA Agent Intelligence Hub</h1>', unsafe_allow_html=True)
st.markdown(
    "**Automated campaign analysis with AI-powered insights and natural language Q&A.**"
)
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_auto, tab_deepdive, tab_qa, tab_history, tab_metrics = st.tabs(
    [
        "📊 Auto Analysis",
        "🔬 Deep Dive",
        "💬 Q&A",
        "📜 Query History",
        "📈 System Analytics",
    ]
)


# ---------------------------------------------------------------------------
# Auto Analysis Tab (restored UI)
# ---------------------------------------------------------------------------
with tab_auto:
    # Always show upload section (even after analysis is complete)
    st.markdown("## 📤 Upload Your Campaign Data")
    col_upload, col_tip = st.columns([2, 1])
    with col_upload:
        input_method = st.radio(
            "Choose Input Method",
            options=["📊 CSV Data", "🗄️ Database", "📸 Dashboard Screenshots"],
            horizontal=True,
        )
    with col_tip:
        pass  # Removed tip

    st.markdown("---")

    # Show upload interface regardless of analysis state
    if True:  # Always show upload section
        if input_method == "📊 CSV Data":
            uploaded_file = st.file_uploader(
                "Upload your campaign data (CSV or Excel)",
                type=["csv", "xlsx", "xls"],
                help="Include Campaign_Name, Platform, Spend, ROAS, etc.",
            )

            if uploaded_file:
                try:
                    # Read file based on extension
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    if file_extension in ['xlsx', 'xls']:
                        # Check for multiple sheets
                        excel_file = pd.ExcelFile(uploaded_file)
                        sheet_names = excel_file.sheet_names
                        
                        if len(sheet_names) > 1:
                            st.info(f"📑 Found {len(sheet_names)} sheets in Excel file")
                            selected_sheet = st.selectbox(
                                "Select sheet to analyze:",
                                options=sheet_names,
                                index=0
                            )
                            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
                        else:
                            df = pd.read_excel(uploaded_file)
                            if len(sheet_names) == 1:
                                st.info(f"📄 Reading sheet: {sheet_names[0]}")
                    else:
                        df = pd.read_csv(uploaded_file)
                    
                    # Show original columns for debugging
                    original_cols = df.columns.tolist()
                    
                    # Normalize column names
                    df = normalize_campaign_dataframe(df)
                    
                    # Clean data: Remove extremely long concatenated strings
                    cleaned_columns = []
                    for col in df.columns:
                        if df[col].dtype == 'object':  # String column
                            max_length = df[col].astype(str).str.len().max()
                            if max_length > 1000:
                                logger.warning(f"Column '{col}' has extremely long values (max: {max_length} chars). Cleaning...")
                                df[col] = df[col].apply(
                                    lambda x: 'Mixed' if isinstance(x, str) and len(x) > 1000 else x
                                )
                                cleaned_columns.append(col)
                    
                    if cleaned_columns:
                        st.warning(f"⚠️ Data quality issue detected and fixed: Columns {', '.join(cleaned_columns)} had concatenated values and were cleaned automatically.")
                    
                    st.session_state.df = df
                    try:
                        df.to_csv(LAST_CSV_PATH, index=False)
                    except Exception:
                        pass
                    
                    # Save to database
                    with st.spinner("💾 Saving to database..."):
                        if save_to_database(df):
                            st.success(f"✅ Loaded {len(df)} rows • {len(df.columns)} columns • Saved to database")
                        else:
                            st.success(f"✅ Loaded {len(df)} rows • {len(df.columns)} columns")
                            st.warning("⚠️ Database save failed (data still available in session)")
                    
                    # Show what was mapped
                    normalized_cols = df.columns.tolist()
                    
                    # Show column mapping info
                    if original_cols != normalized_cols:
                        with st.expander("🔄 Column Mapping Applied", expanded=False):
                            mapping_info = []
                            for orig, norm in zip(original_cols, normalized_cols):
                                if orig != norm:
                                    mapping_info.append(f"✓ `{orig}` → `{norm}`")
                                else:
                                    mapping_info.append(f"  `{orig}` (unchanged)")
                            st.markdown("\n".join(mapping_info))

                    with st.expander("📋 Data Preview", expanded=True):
                        st.dataframe(df.head(10), width="stretch")
                        col_a, col_b, col_c, col_d = st.columns(4)

                        # Basic row count
                        col_a.metric("Rows", len(df))

                        # Campaign count using flexible column mapping
                        campaign_col = _get_column(df, "campaign")
                        campaigns = (
                            df[campaign_col].nunique() if campaign_col else 0
                        )
                        col_b.metric("Campaigns", campaigns)

                        # Platform count (fallback to 0 if missing)
                        platforms = (
                            df["Platform"].nunique()
                            if "Platform" in df.columns
                            else 0
                        )
                        col_c.metric("Platforms", platforms)

                        # Total spend using flexible column mapping
                        spend_col = _get_column(df, "spend")
                        total_spend = (
                            float(df[spend_col].sum()) if spend_col else 0.0
                        )
                        col_d.metric("Total Spend", f"${total_spend:,.0f}")

                    st.markdown("---")
                    
                    # B2B/B2C Context Collection
                    with st.expander("🎯 Business Context (Optional - Enhances Analysis)", expanded=False):
                        st.markdown("**Provide business context for more relevant insights and benchmarks**")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            business_model = st.selectbox(
                                "Business Model",
                                options=["Auto-detect", "B2B", "B2C", "B2B2C"],
                                help="Select your business model for context-aware analysis"
                            )
                            
                            industry_vertical = st.selectbox(
                                "Industry",
                                options=["Select Industry", "SaaS", "Financial Services", "E-commerce", "Healthcare", "Auto", "Retail"],
                                help="Your industry for relevant benchmarks"
                            )
                        
                        with col2:
                            if business_model in ["B2B", "B2B2C"]:
                                sales_cycle = st.number_input(
                                    "Sales Cycle (days)",
                                    min_value=1,
                                    max_value=365,
                                    value=60,
                                    help="Average sales cycle length"
                                )
                                
                                avg_deal_size = st.number_input(
                                    "Average Deal Size ($)",
                                    min_value=0,
                                    value=10000,
                                    step=1000,
                                    help="Average contract value"
                                )
                                
                                target_audience = st.selectbox(
                                    "Target Audience Level",
                                    options=["C-suite", "VP/Director", "Manager", "Individual Contributor", "Mixed"],
                                    help="Primary decision-maker level"
                                )
                            
                            if business_model in ["B2C", "B2B2C"]:
                                avg_order_value = st.number_input(
                                    "Average Order Value ($)",
                                    min_value=0.0,
                                    value=50.0,
                                    step=5.0,
                                    help="Average transaction value"
                                )
                                
                                purchase_freq = st.selectbox(
                                    "Purchase Frequency",
                                    options=["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"],
                                    help="How often customers purchase"
                                )
                        
                        # Common fields
                        col3, col4 = st.columns(2)
                        with col3:
                            ltv = st.number_input(
                                "Customer Lifetime Value ($)",
                                min_value=0,
                                value=0,
                                step=100,
                                help="Total value of a customer over their lifetime"
                            )
                        
                        with col4:
                            target_cac = st.number_input(
                                "Target CAC ($)",
                                min_value=0,
                                value=0,
                                step=10,
                                help="Target customer acquisition cost"
                            )
                        
                        # Store context in session state
                        if business_model != "Auto-detect" and industry_vertical != "Select Industry":
                            campaign_context = CampaignContext(
                                business_model=BusinessModel[business_model.replace("-", "_")],
                                industry_vertical=industry_vertical,
                                sales_cycle_length=sales_cycle if business_model in ["B2B", "B2B2C"] else None,
                                average_deal_size=float(avg_deal_size) if business_model in ["B2B", "B2B2C"] else None,
                                target_audience_level=TargetAudienceLevel[target_audience.upper().replace("/", "_").replace("-", "_")] if business_model in ["B2B", "B2B2C"] else None,
                                average_order_value=float(avg_order_value) if business_model in ["B2C", "B2B2C"] else None,
                                purchase_frequency=purchase_freq.lower() if business_model in ["B2C", "B2B2C"] else None,
                                customer_lifetime_value=float(ltv) if ltv > 0 else None,
                                target_cac=float(target_cac) if target_cac > 0 else None
                            )
                            st.session_state.campaign_context = campaign_context
                            st.success(f"✅ Context saved: {campaign_context.get_context_summary()}")
                        else:
                            st.session_state.campaign_context = None
                    
                    st.markdown("---")
                    if st.button("🚀 Analyze Data & Generate Insights", type="primary"):
                        # Create timing container
                        timing_placeholder = st.empty()
                        
                        with st.spinner("🤖 AI Expert analyzing your data..."):
                            auto_start = time.time()
                            expert = MediaAnalyticsExpert()
                            analysis = expert.analyze_all(df)
                            auto_elapsed = time.time() - auto_start
                            
                            # Store timing
                            analysis['timing'] = {'auto_analysis_seconds': round(auto_elapsed, 2)}
                            
                            # Enhance with B2B/B2C context if provided
                            if hasattr(st.session_state, 'campaign_context') and st.session_state.campaign_context:
                                with st.spinner("🎯 Applying business context..."):
                                    b2b_start = time.time()
                                    b2b_specialist = B2BSpecialistAgent()
                                    analysis = b2b_specialist.enhance_analysis(
                                        base_insights=analysis,
                                        campaign_context=st.session_state.campaign_context,
                                        campaign_data=df
                                    )
                                    analysis['timing']['b2b_enhancement_seconds'] = round(time.time() - b2b_start, 2)
                            
                            # Show timing
                            timing_placeholder.success(f"⏱️ Auto Analysis completed in **{auto_elapsed:.1f}s**")
                            
                            st.session_state.analysis_data = analysis
                            st.session_state.analysis_complete = True
                            st.rerun()
                except Exception as exc:
                    st.error(f"❌ Error loading CSV: {exc}")
            elif st.session_state.df is not None:
                df = st.session_state.df
                st.success(
                    f"✅ Using previously loaded data • {len(df)} rows • {len(df.columns)} columns"
                )

                with st.expander("📋 Data Preview", expanded=True):
                    st.dataframe(df.head(10), width="stretch")
                    col_a, col_b, col_c, col_d = st.columns(4)

                    col_a.metric("Rows", len(df))

                    campaign_col = _get_column(df, "campaign")
                    campaigns = (
                        df[campaign_col].nunique() if campaign_col else 0
                    )
                    col_b.metric("Campaigns", campaigns)

                    platforms = (
                        df["Platform"].nunique()
                        if "Platform" in df.columns
                        else 0
                    )
                    col_c.metric("Platforms", platforms)

                    spend_col = _get_column(df, "spend")
                    total_spend = (
                        float(df[spend_col].sum()) if spend_col else 0.0
                    )
                    col_d.metric("Total Spend", f"${total_spend:,.0f}")

                st.markdown("---")
                if st.button("🚀 Analyze Data & Generate Insights", type="primary"):
                    timing_placeholder = st.empty()
                    with st.spinner("🤖 AI Expert analyzing your data..."):
                        auto_start = time.time()
                        expert = MediaAnalyticsExpert()
                        analysis = expert.analyze_all(df)
                        auto_elapsed = time.time() - auto_start
                        analysis['timing'] = {'auto_analysis_seconds': round(auto_elapsed, 2)}
                        timing_placeholder.success(f"⏱️ Auto Analysis completed in **{auto_elapsed:.1f}s**")
                        st.session_state.analysis_data = analysis
                        st.session_state.analysis_complete = True
                        st.rerun()

        elif input_method == "🗄️ Database":
            from src.data.database_connector import DatabaseConnector
            
            st.markdown("### 🗄️ Connect to Database")
            
            # Database type selection with categories
            db_category = st.radio(
                "Database Category",
                options=["Traditional Databases", "Cloud Data Warehouses", "Cloud Storage"],
                horizontal=True
            )
            
            if db_category == "Traditional Databases":
                db_options = {
                    "postgresql": "PostgreSQL",
                    "mysql": "MySQL",
                    "sqlite": "SQLite",
                    "mssql": "SQL Server"
                }
            elif db_category == "Cloud Data Warehouses":
                db_options = {
                    "duckdb": "DuckDB",
                    "snowflake": "Snowflake",
                    "bigquery": "Google BigQuery",
                    "redshift": "AWS Redshift",
                    "databricks": "Databricks"
                }
            else:  # Cloud Storage
                db_options = {
                    "s3": "AWS S3",
                    "azure_blob": "Azure Blob Storage",
                    "gcs": "Google Cloud Storage"
                }
            
            db_type = st.selectbox(
                "Select Database/Storage",
                options=list(db_options.keys()),
                format_func=lambda x: db_options.get(x, x)
            )
            
            # Connection parameters based on database type
            if db_type in ["sqlite", "duckdb"]:
                file_path = st.text_input("Database File Path", placeholder="path/to/database.db" if db_type == "sqlite" else ":memory: or path/to/database.duckdb")
                
                if st.button(f"🔌 Connect to {db_type.upper()}"):
                    if file_path or db_type == "duckdb":
                        try:
                            with st.spinner("Connecting to database..."):
                                connector = DatabaseConnector()
                                connector.connect(db_type=db_type, file_path=file_path or ":memory:")
                                st.session_state.db_connector = connector
                                st.session_state.db_connected = True
                                st.success(f"✅ Connected to {db_type.upper()} database!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")
                    else:
                        st.warning("Please provide database file path")
            
            elif db_type == "snowflake":
                col1, col2 = st.columns(2)
                with col1:
                    account = st.text_input("Account", placeholder="xy12345.us-east-1")
                    database = st.text_input("Database", placeholder="CAMPAIGN_DB")
                    warehouse = st.text_input("Warehouse", placeholder="COMPUTE_WH")
                with col2:
                    username = st.text_input("Username", placeholder="user")
                    password = st.text_input("Password", type="password")
                    schema = st.text_input("Schema", value="PUBLIC")
                
                if st.button("🔌 Connect to Snowflake"):
                    if all([account, database, username, password, warehouse]):
                        try:
                            with st.spinner("Connecting to Snowflake..."):
                                connector = DatabaseConnector()
                                connector.connect(
                                    db_type="snowflake",
                                    host=None,
                                    database=database,
                                    username=username,
                                    password=password,
                                    account=account,
                                    warehouse=warehouse,
                                    schema=schema
                                )
                                st.session_state.db_connector = connector
                                st.session_state.db_connected = True
                                st.success("✅ Connected to Snowflake!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")
                    else:
                        st.warning("Please fill in all required fields")
            
            elif db_type == "bigquery":
                project_id = st.text_input("Project ID", placeholder="my-project-123")
                credentials_path = st.text_input("Credentials JSON Path (optional)", placeholder="path/to/credentials.json")
                
                if st.button("🔌 Connect to BigQuery"):
                    if project_id:
                        try:
                            with st.spinner("Connecting to BigQuery..."):
                                connector = DatabaseConnector()
                                connector.connect(
                                    db_type="bigquery",
                                    database=project_id,
                                    project_id=project_id,
                                    credentials_path=credentials_path if credentials_path else None
                                )
                                st.session_state.db_connector = connector
                                st.session_state.db_connected = True
                                st.success("✅ Connected to BigQuery!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")
                    else:
                        st.warning("Please provide Project ID")
            
            elif db_type == "databricks":
                col1, col2 = st.columns(2)
                with col1:
                    host = st.text_input("Host", placeholder="dbc-xyz.cloud.databricks.com")
                    http_path = st.text_input("HTTP Path", placeholder="/sql/1.0/warehouses/abc123")
                with col2:
                    token = st.text_input("Access Token", type="password")
                    catalog = st.text_input("Catalog", value="main")
                
                if st.button("🔌 Connect to Databricks"):
                    if all([host, http_path, token, catalog]):
                        try:
                            with st.spinner("Connecting to Databricks..."):
                                connector = DatabaseConnector()
                                connector.connect(
                                    db_type="databricks",
                                    host=host,
                                    database=catalog,
                                    password=token,
                                    http_path=http_path,
                                    token=token
                                )
                                st.session_state.db_connector = connector
                                st.session_state.db_connected = True
                                st.success("✅ Connected to Databricks!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")
                    else:
                        st.warning("Please fill in all required fields")
            
            elif db_type in ["s3", "azure_blob", "gcs"]:
                # Cloud storage - handle differently (no connection, direct file load)
                st.info("Cloud storage requires direct file path. Enter details below to load data.")
                st.session_state.db_type = db_type
                st.session_state.db_connected = True  # Mark as "connected" to show file selection
            
            elif db_type == "redshift":
                col1, col2 = st.columns(2)
                with col1:
                    host = st.text_input("Host", placeholder="cluster.region.redshift.amazonaws.com")
                    database = st.text_input("Database", placeholder="dev")
                with col2:
                    port = st.number_input("Port", value=5439, min_value=1, max_value=65535)
                    username = st.text_input("Username", placeholder="admin")
                
                password = st.text_input("Password", type="password")
                
                if st.button("🔌 Connect to Redshift"):
                    if all([host, database, username, password]):
                        try:
                            with st.spinner("Connecting to Redshift..."):
                                connector = DatabaseConnector()
                                connector.connect(
                                    db_type="redshift",
                                    host=host,
                                    port=port,
                                    database=database,
                                    username=username,
                                    password=password
                                )
                                st.session_state.db_connector = connector
                                st.session_state.db_connected = True
                                st.success("✅ Connected to Redshift!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")
                    else:
                        st.warning("Please fill in all connection fields")
            
            else:
                # Server-based databases
                col1, col2 = st.columns(2)
                with col1:
                    host = st.text_input("Host", placeholder="localhost")
                    database = st.text_input("Database Name", placeholder="campaign_data")
                with col2:
                    port = st.number_input("Port", value={
                        "postgresql": 5432,
                        "mysql": 3306,
                        "mssql": 1433
                    }.get(db_type, 5432), min_value=1, max_value=65535)
                    
                col3, col4 = st.columns(2)
                with col3:
                    username = st.text_input("Username", placeholder="user")
                with col4:
                    password = st.text_input("Password", type="password", placeholder="password")
                
                if st.button(f"🔌 Connect to {db_type.upper()}"):
                    if all([host, database, username, password]):
                        try:
                            with st.spinner("Connecting to database..."):
                                connector = DatabaseConnector()
                                connector.connect(
                                    db_type=db_type,
                                    host=host,
                                    port=port,
                                    database=database,
                                    username=username,
                                    password=password
                                )
                                st.session_state.db_connector = connector
                                st.session_state.db_connected = True
                                st.success(f"✅ Connected to {db_type.upper()} database!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")
                    else:
                        st.warning("Please fill in all connection fields")
            
            # Show table selection if connected
            if st.session_state.get('db_connected', False):
                st.markdown("---")
                st.markdown("### 📊 Select Data")
                
                # Handle cloud storage differently
                if st.session_state.get('db_type') in ["s3", "azure_blob", "gcs"]:
                    storage_type = st.session_state.get('db_type')
                    connector = DatabaseConnector()
                    
                    if storage_type == "s3":
                        s3_path = st.text_input("S3 Path", placeholder="s3://bucket-name/path/to/file.csv")
                        aws_access_key = st.text_input("AWS Access Key (optional)")
                        aws_secret_key = st.text_input("AWS Secret Key (optional)", type="password")
                        region = st.text_input("Region", value="us-east-1")
                        
                        if st.button("📥 Load from S3"):
                            if s3_path:
                                try:
                                    with st.spinner("Loading from S3..."):
                                        df = connector.load_from_s3(
                                            s3_path=s3_path,
                                            aws_access_key_id=aws_access_key if aws_access_key else None,
                                            aws_secret_access_key=aws_secret_key if aws_secret_key else None,
                                            region_name=region
                                        )
                                        df = normalize_campaign_dataframe(df)
                                        st.session_state.df = df
                                        st.success(f"✅ Loaded {len(df)} rows from S3")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Failed to load from S3: {str(e)}")
                            else:
                                st.warning("Please provide S3 path")
                    
                    elif storage_type == "azure_blob":
                        container = st.text_input("Container Name", placeholder="my-container")
                        blob_name = st.text_input("Blob Name", placeholder="path/to/file.csv")
                        
                        auth_method = st.radio("Authentication", ["Connection String", "Account Key"])
                        
                        if auth_method == "Connection String":
                            conn_str = st.text_input("Connection String", type="password")
                            account_name = None
                            account_key = None
                        else:
                            conn_str = None
                            account_name = st.text_input("Account Name")
                            account_key = st.text_input("Account Key", type="password")
                        
                        if st.button("📥 Load from Azure"):
                            if container and blob_name:
                                try:
                                    with st.spinner("Loading from Azure..."):
                                        df = connector.load_from_azure_blob(
                                            container_name=container,
                                            blob_name=blob_name,
                                            connection_string=conn_str,
                                            account_name=account_name,
                                            account_key=account_key
                                        )
                                        df = normalize_campaign_dataframe(df)
                                        st.session_state.df = df
                                        st.success(f"✅ Loaded {len(df)} rows from Azure")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Failed to load from Azure: {str(e)}")
                            else:
                                st.warning("Please provide container and blob name")
                    
                    elif storage_type == "gcs":
                        bucket_name = st.text_input("Bucket Name", placeholder="my-bucket")
                        blob_name = st.text_input("Blob Name", placeholder="path/to/file.csv")
                        credentials_path = st.text_input("Credentials JSON Path (optional)", placeholder="path/to/credentials.json")
                        
                        if st.button("📥 Load from GCS"):
                            if bucket_name and blob_name:
                                try:
                                    with st.spinner("Loading from GCS..."):
                                        df = connector.load_from_gcs(
                                            bucket_name=bucket_name,
                                            blob_name=blob_name,
                                            credentials_path=credentials_path if credentials_path else None
                                        )
                                        df = normalize_campaign_dataframe(df)
                                        st.session_state.df = df
                                        st.success(f"✅ Loaded {len(df)} rows from GCS")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Failed to load from GCS: {str(e)}")
                            else:
                                st.warning("Please provide bucket and blob name")
                    
                    # Show loaded data preview
                    if 'df' in st.session_state and st.session_state.df is not None:
                        df = st.session_state.df
                        st.markdown("---")
                        st.markdown("### 📊 Data Preview")
                        st.dataframe(df.head(10), width="stretch")
                        
                        # Show metrics
                        col_a, col_b, col_c, col_d = st.columns(4)
                        col_a.metric("Rows", f"{len(df):,}")
                        col_b.metric("Columns", len(df.columns))
                        
                        if "Spend" in df.columns:
                            total_spend = df["Spend"].sum()
                            col_d.metric("Total Spend", f"${total_spend:,.0f}")
                        
                        st.markdown("---")
                        if st.button("🚀 Analyze Data & Generate Insights", type="primary", key="analyze_cloud"):
                            timing_placeholder = st.empty()
                            with st.spinner("🤖 AI Expert analyzing your data..."):
                                auto_start = time.time()
                                expert = MediaAnalyticsExpert()
                                analysis = expert.analyze_all(df)
                                auto_elapsed = time.time() - auto_start
                                analysis['timing'] = {'auto_analysis_seconds': round(auto_elapsed, 2)}
                                timing_placeholder.success(f"⏱️ Auto Analysis completed in **{auto_elapsed:.1f}s**")
                                st.session_state.analysis_data = analysis
                                st.session_state.analysis_complete = True
                                st.rerun()
                
                else:
                    # Database connection (not cloud storage)
                    connector = st.session_state.db_connector
                    
                    # Get tables
                    try:
                        tables = connector.get_tables()
                        
                        data_source = st.radio(
                            "Data Source",
                            options=["📋 Select Table", "✍️ Custom Query"],
                            horizontal=True
                        )
                        
                        if data_source == "📋 Select Table":
                            selected_table = st.selectbox("Select Table", options=tables)
                            
                            # Show schema
                            if st.checkbox("Show Table Schema"):
                                schema = connector.get_table_schema(selected_table)
                                st.dataframe(schema, width="stretch")
                            
                            # Row limit
                            limit = st.number_input("Row Limit (0 = all rows)", min_value=0, value=10000, step=1000)
                            
                            if st.button("📥 Load Data from Table"):
                                try:
                                    with st.spinner(f"Loading data from {selected_table}..."):
                                        if limit > 0:
                                            df = connector.load_table(selected_table, limit=limit)
                                        else:
                                            df = connector.load_table(selected_table)
                                        
                                        # Normalize column names
                                        df = normalize_campaign_dataframe(df)
                                        st.session_state.df = df
                                        
                                        st.success(f"✅ Loaded {len(df)} rows • {len(df.columns)} columns")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Failed to load data: {str(e)}")
                        
                        else:  # Custom Query
                            query = st.text_area(
                                "SQL Query",
                                placeholder="SELECT * FROM campaigns WHERE date >= '2024-01-01'",
                                height=150
                            )
                            
                            if st.button("▶️ Execute Query"):
                                if query.strip():
                                    try:
                                        with st.spinner("Executing query..."):
                                            df = connector.execute_query(query)
                                            
                                            # Normalize column names
                                            df = normalize_campaign_dataframe(df)
                                            st.session_state.df = df
                                            
                                            st.success(f"✅ Loaded {len(df)} rows • {len(df.columns)} columns")
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Query failed: {str(e)}")
                                else:
                                    st.warning("Please enter a SQL query")
                        
                        # Show loaded data preview
                        if 'df' in st.session_state and st.session_state.df is not None:
                            df = st.session_state.df
                            st.markdown("---")
                            st.markdown("### 📊 Data Preview")
                            st.dataframe(df.head(10), width="stretch")
                            
                            # Show metrics
                            col_a, col_b, col_c, col_d = st.columns(4)
                            col_a.metric("Rows", f"{len(df):,}")
                            col_b.metric("Columns", len(df.columns))
                            
                            if "Spend" in df.columns:
                                total_spend = df["Spend"].sum()
                                col_d.metric("Total Spend", f"${total_spend:,.0f}")
                            
                            st.markdown("---")
                            if st.button("🚀 Analyze Data & Generate Insights", type="primary"):
                                timing_placeholder = st.empty()
                                with st.spinner("🤖 AI Expert analyzing your data..."):
                                    auto_start = time.time()
                                    expert = MediaAnalyticsExpert()
                                    analysis = expert.analyze_all(df)
                                    auto_elapsed = time.time() - auto_start
                                    analysis['timing'] = {'auto_analysis_seconds': round(auto_elapsed, 2)}
                                    timing_placeholder.success(f"⏱️ Auto Analysis completed in **{auto_elapsed:.1f}s**")
                                    st.session_state.analysis_data = analysis
                                    st.session_state.analysis_complete = True
                                    st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        if st.button("🔌 Reconnect"):
                            st.session_state.db_connected = False
                            st.session_state.db_connector = None
                            st.rerun()

        else:
            st.warning(
                "Screenshot ingestion requires the backend vision pipeline. "
                "Switch to CSV mode for self-contained analysis."
            )
            uploaded_images = st.file_uploader(
                "Upload dashboard screenshots",
                type=["png", "jpg", "jpeg", "pdf"],
                accept_multiple_files=True,
            )
            if uploaded_images:
                st.success(f"📸 {len(uploaded_images)} files uploaded")
                with st.expander("Preview Files"):
                    cols = st.columns(3)
                    for i, img in enumerate(uploaded_images):
                        cols[i % 3].image(img, caption=img.name, use_column_width=True)

    # Show analysis results if available (below upload section)
    if st.session_state.analysis_complete:
        analysis = st.session_state.analysis_data
        df = st.session_state.df

        st.markdown("---")
        st.markdown("## 📊 Analysis Results")
        
        # Show data preview at the top after analysis
        with st.expander("📋 Loaded Data Preview", expanded=False):
            st.dataframe(df.head(20), width="stretch")
            col_a, col_b, col_c, col_d = st.columns(4)
            
            col_a.metric("Rows", len(df))
            
            campaign_col = _get_column(df, "campaign")
            campaigns = df[campaign_col].nunique() if campaign_col else 0
            col_b.metric("Campaigns", campaigns)
            
            platforms = df["Platform"].nunique() if "Platform" in df.columns else 0
            col_c.metric("Platforms", platforms)
            
            spend_col = _get_column(df, "spend")
            total_spend = float(df[spend_col].sum()) if spend_col else 0.0
            col_d.metric("Total Spend", f"${total_spend:,.0f}")
        
        st.markdown("---")
        
        # NOTE: Channel-Specific Intelligence moved to Deep Dive tab
        # Store channel analysis for Deep Dive tab
        if 'channel_analysis_data' not in st.session_state:
            st.session_state.channel_analysis_data = None
        
        # Run channel analysis in background for Deep Dive tab
        try:
            channel_router = ChannelRouter()
            st.session_state.channel_analysis_data = channel_router.route_and_analyze(df)
        except Exception as e:
            logger.warning(f"Channel analysis prep failed: {e}")
        
        # Channel-Specific Intelligence MOVED to Deep Dive tab
        
        # B2B/B2C Business Model Analysis
        if 'business_model_analysis' in analysis:
            st.markdown("## 💼 Business Model Analysis")
            
            bm_analysis = analysis['business_model_analysis']
            business_model = bm_analysis.get('business_model', 'Unknown')
            industry = bm_analysis.get('industry_vertical', 'Unknown')
            context_summary = bm_analysis.get('context_summary', '')
            
            # Display header
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Business Model", business_model)
            with col2:
                st.metric("Industry", industry)
            
            if context_summary:
                st.info(f"📊 {context_summary}")
            
            # B2B-Specific Analysis
            if business_model in ['B2B', 'B2B2C']:
                st.markdown("### 🎯 B2B Analysis")
                
                b2b_tabs = []
                b2b_data = []
                
                # Lead Quality
                if 'lead_quality_analysis' in bm_analysis:
                    b2b_tabs.append("Lead Quality")
                    b2b_data.append(('lead_quality', bm_analysis['lead_quality_analysis']))
                
                # Pipeline Impact
                if 'pipeline_contribution' in bm_analysis:
                    b2b_tabs.append("Pipeline Impact")
                    b2b_data.append(('pipeline', bm_analysis['pipeline_contribution']))
                
                # Sales Cycle
                if 'sales_cycle_alignment' in bm_analysis:
                    b2b_tabs.append("Sales Cycle")
                    b2b_data.append(('sales_cycle', bm_analysis['sales_cycle_alignment']))
                
                # Audience Seniority
                if 'audience_seniority_analysis' in bm_analysis:
                    b2b_tabs.append("Audience Level")
                    b2b_data.append(('audience', bm_analysis['audience_seniority_analysis']))
                
                if b2b_tabs:
                    tabs = st.tabs(b2b_tabs)
                    for tab, (key, data) in zip(tabs, b2b_data):
                        with tab:
                            # Display findings
                            findings = data.get('findings', [])
                            if findings:
                                for finding in findings:
                                    st.markdown(f"{finding}")
                            
                            # Display metrics
                            metric_cols = st.columns(3)
                            col_idx = 0
                            for k, v in data.items():
                                if k not in ['metric', 'findings', 'recommendation', 'status'] and col_idx < 3:
                                    if isinstance(v, (int, float, str)):
                                        metric_cols[col_idx].metric(
                                            k.replace('_', ' ').title(),
                                            str(v)
                                        )
                                        col_idx += 1
                            
                            # Display recommendation
                            if 'recommendation' in data:
                                st.info(f"💡 **Recommendation:** {data['recommendation']}")
            
            # B2C-Specific Analysis
            if business_model in ['B2C', 'B2B2C']:
                st.markdown("### 🛍️ B2C Analysis")
                
                b2c_tabs = []
                b2c_data = []
                
                # Purchase Behavior
                if 'purchase_behavior_analysis' in bm_analysis:
                    b2c_tabs.append("Purchase Behavior")
                    b2c_data.append(('purchase', bm_analysis['purchase_behavior_analysis']))
                
                # CAC Efficiency
                if 'customer_acquisition_efficiency' in bm_analysis:
                    b2c_tabs.append("CAC Efficiency")
                    b2c_data.append(('cac', bm_analysis['customer_acquisition_efficiency']))
                
                # LTV Analysis
                if 'lifetime_value_analysis' in bm_analysis:
                    b2c_tabs.append("Lifetime Value")
                    b2c_data.append(('ltv', bm_analysis['lifetime_value_analysis']))
                
                # Conversion Funnel
                if 'conversion_funnel_analysis' in bm_analysis:
                    b2c_tabs.append("Conversion Funnel")
                    b2c_data.append(('funnel', bm_analysis['conversion_funnel_analysis']))
                
                if b2c_tabs:
                    tabs = st.tabs(b2c_tabs)
                    for tab, (key, data) in zip(tabs, b2c_data):
                        with tab:
                            # Display findings
                            findings = data.get('findings', [])
                            if findings:
                                for finding in findings:
                                    st.markdown(f"{finding}")
                            
                            # Display metrics
                            metric_cols = st.columns(3)
                            col_idx = 0
                            for k, v in data.items():
                                if k not in ['metric', 'findings', 'recommendation', 'status', 'bottleneck'] and col_idx < 3:
                                    if isinstance(v, (int, float, str)):
                                        metric_cols[col_idx].metric(
                                            k.replace('_', ' ').title(),
                                            str(v)
                                        )
                                        col_idx += 1
                            
                            # Display recommendation
                            if 'recommendation' in data:
                                st.info(f"💡 **Recommendation:** {data['recommendation']}")
            
            # Display B2B/B2C specific recommendations
            if 'recommendations' in analysis:
                bm_recs = [r for r in analysis['recommendations'] 
                          if isinstance(r, dict) and r.get('category') in ['Lead Quality', 'Sales Cycle', 'Audience Targeting', 'CAC Efficiency', 'LTV:CAC Ratio', 'Conversion Funnel']]
                
                if bm_recs:
                    st.markdown("### 💡 Business Model Recommendations")
                    for rec in bm_recs[:5]:
                        priority = rec.get('priority', 'medium')
                        category = rec.get('category', 'General')
                        recommendation = rec.get('recommendation', '')
                        
                        if priority == 'high':
                            st.error(f"**🔴 {category}:** {recommendation}")
                        elif priority == 'medium':
                            st.warning(f"**🟡 {category}:** {recommendation}")
                        else:
                            st.info(f"**🟢 {category}:** {recommendation}")
        
        st.markdown("---")
        
        # Dynamic Contextual Benchmarks
        if hasattr(st.session_state, 'campaign_context') and st.session_state.campaign_context:
            st.markdown("## 📊 Contextual Benchmarks")
            
            try:
                benchmark_engine = DynamicBenchmarkEngine()
                
                # Detect channel from data
                detected_channel = 'google_search'  # Default
                if 'Platform' in df.columns:
                    platform_lower = df['Platform'].iloc[0].lower() if len(df) > 0 else ''
                    if 'linkedin' in platform_lower:
                        detected_channel = 'linkedin'
                    elif 'meta' in platform_lower or 'facebook' in platform_lower or 'instagram' in platform_lower:
                        detected_channel = 'meta'
                    elif 'dv360' in platform_lower or 'display' in platform_lower:
                        detected_channel = 'dv360'
                
                # Get campaign objective (if available)
                campaign_objective = None
                if 'Objective' in df.columns:
                    campaign_objective = df['Objective'].iloc[0] if len(df) > 0 else None
                
                # Get contextual benchmarks
                context = st.session_state.campaign_context
                benchmarks = benchmark_engine.get_contextual_benchmarks(
                    channel=detected_channel,
                    business_model=context.business_model.value,
                    industry=context.industry_vertical,
                    objective=campaign_objective,
                    region=context.geographic_focus[0] if context.geographic_focus else None
                )
                
                # Display context
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Channel", detected_channel.replace('_', ' ').title())
                with col2:
                    st.metric("Region", benchmarks['region'])
                with col3:
                    st.metric("Objective", benchmarks['objective'])
                
                # Display interpretation
                st.info(f"💡 **Context:** {benchmarks['interpretation_guidance']}")
                
                # Display benchmarks in expandable sections
                st.markdown("### 📈 Performance Benchmarks")
                
                # Create columns for benchmark display
                benchmark_metrics = list(benchmarks['benchmarks'].keys())
                
                if benchmark_metrics:
                    # Display benchmarks in tabs
                    benchmark_tabs = st.tabs([metric.upper().replace('_', ' ') for metric in benchmark_metrics])
                    
                    for tab, metric in zip(benchmark_tabs, benchmark_metrics):
                        with tab:
                            ranges = benchmarks['benchmarks'][metric]
                            
                            # Display as colored metrics
                            cols = st.columns(len(ranges))
                            for idx, (level, value) in enumerate(ranges.items()):
                                # Format value based on metric type
                                if metric in ['ctr', 'conv_rate', 'conversion_rate', 'quality_score', 
                                             'impression_share', 'viewability', 'brand_safety', 'ivt_rate',
                                             'lead_quality_rate', 'roas', 'frequency']:
                                    if metric in ['quality_score']:
                                        formatted_value = f"{value:.1f}"
                                    elif metric in ['roas', 'frequency']:
                                        formatted_value = f"{value:.2f}"
                                    else:
                                        formatted_value = f"{value:.1%}"
                                else:
                                    formatted_value = f"${value:.2f}"
                                
                                # Color code by level
                                if level in ['excellent', 'good']:
                                    cols[idx].success(f"**{level.title()}**\n\n{formatted_value}")
                                elif level in ['average', 'acceptable']:
                                    cols[idx].warning(f"**{level.title()}**\n\n{formatted_value}")
                                else:
                                    cols[idx].error(f"**{level.title()}**\n\n{formatted_value}")
                
                # Compare actual performance to benchmarks
                st.markdown("### 🎯 Your Performance vs Benchmarks")
                
                # Calculate actual metrics from data
                actual_metrics = {}
                
                if 'CTR' in df.columns:
                    actual_metrics['ctr'] = df['CTR'].mean()
                if 'CPC' in df.columns:
                    actual_metrics['cpc'] = df['CPC'].mean()
                if 'Conversions' in df.columns and 'Clicks' in df.columns:
                    total_conv = df['Conversions'].sum()
                    total_clicks = df['Clicks'].sum()
                    if total_clicks > 0:
                        actual_metrics['conv_rate'] = total_conv / total_clicks
                if 'ROAS' in df.columns:
                    actual_metrics['roas'] = df['ROAS'].mean()
                
                if actual_metrics:
                    comparison = benchmark_engine.compare_to_benchmarks(actual_metrics, benchmarks)
                    
                    # Display overall score
                    score = comparison['overall_score']
                    assessment = comparison['overall_assessment']
                    
                    # Color code the score
                    if score >= 90:
                        st.success(f"### 🟢 Overall Score: {score:.0f}/100")
                    elif score >= 75:
                        st.success(f"### 🟡 Overall Score: {score:.0f}/100")
                    elif score >= 50:
                        st.warning(f"### 🟠 Overall Score: {score:.0f}/100")
                    else:
                        st.error(f"### 🔴 Overall Score: {score:.0f}/100")
                    
                    st.write(f"**{assessment}**")
                    
                    # Display metric-by-metric comparison
                    st.markdown("#### Metric Breakdown")
                    
                    for metric, comp in comparison['comparisons'].items():
                        with st.expander(f"{metric.upper().replace('_', ' ')} - {comp['assessment'].upper()}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Format actual value
                                if metric in ['ctr', 'conv_rate', 'conversion_rate']:
                                    actual_display = f"{comp['actual']:.2%}"
                                elif metric in ['roas']:
                                    actual_display = f"{comp['actual']:.2f}x"
                                else:
                                    actual_display = f"${comp['actual']:.2f}"
                                
                                st.metric("Your Performance", actual_display)
                            
                            with col2:
                                # Show benchmark range
                                benchmark_range = comp['benchmarks']
                                if 'good' in benchmark_range:
                                    if metric in ['ctr', 'conv_rate', 'conversion_rate']:
                                        benchmark_display = f"{benchmark_range['good']:.2%}"
                                    elif metric in ['roas']:
                                        benchmark_display = f"{benchmark_range['good']:.2f}x"
                                    else:
                                        benchmark_display = f"${benchmark_range['good']:.2f}"
                                    st.metric("Good Benchmark", benchmark_display)
                            
                            # Display message
                            if comp['assessment'] == 'excellent':
                                st.success(comp['message'])
                            elif comp['assessment'] == 'good':
                                st.info(comp['message'])
                            elif comp['assessment'] == 'average':
                                st.warning(comp['message'])
                            else:
                                st.error(comp['message'])
                else:
                    st.info("ℹ️ Upload data with CTR, CPC, and Conversion metrics to see performance comparison")
            
            except Exception as e:
                logger.error(f"Error displaying contextual benchmarks: {e}")
                st.warning(f"⚠️ Could not load contextual benchmarks: {str(e)}")
        
        st.markdown("---")
        
        # Pattern Analysis MOVED to Deep Dive tab
        # Store pattern analysis for Deep Dive tab
        pattern_analysis = None
        if 'pattern_analysis_data' not in st.session_state:
            st.session_state.pattern_analysis_data = None
        
        try:
            benchmark_engine = DynamicBenchmarkEngine() if hasattr(st.session_state, 'campaign_context') and st.session_state.campaign_context else None
            reasoning_agent = EnhancedReasoningAgent(
                rag_retriever=None,
                benchmark_engine=benchmark_engine
            )
            pattern_analysis = reasoning_agent.analyze(
                campaign_data=df,
                channel_insights=None,
                campaign_context=st.session_state.campaign_context if hasattr(st.session_state, 'campaign_context') else None
            )
            st.session_state.pattern_analysis_data = pattern_analysis
        except Exception as e:
            logger.warning(f"Pattern analysis prep failed: {e}")
        
        # REMOVED: Pattern Analysis, Dashboard View, Quick Navigation - now in Deep Dive tab

        # Removed action buttons as per user request
        
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        
        st.markdown("<div id='executive-summary'></div>", unsafe_allow_html=True)
        
        # RAG Comparison Toggle
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("## 📊 Executive Summary")
        with col2:
            enable_rag_comparison = st.toggle("🔬 Compare with RAG", value=False, help="Generate RAG-enhanced summary for comparison")
        with col3:
            if enable_rag_comparison:
                st.caption("🧪 Experimental")
        
        exec_summary_raw = analysis.get("executive_summary")
        
        # Handle both dict (new format) and string (old format) for backward compatibility
        if isinstance(exec_summary_raw, dict):
            brief_summary = _strip_light_markup(exec_summary_raw.get("brief", "")) if exec_summary_raw.get("brief") else None
            detailed_summary = _strip_light_markup(exec_summary_raw.get("detailed", "")) if exec_summary_raw.get("detailed") else None
        else:
            # Old format - treat as detailed summary
            brief_summary = None
            detailed_summary = _strip_light_markup(exec_summary_raw) if exec_summary_raw else None
        
        # Debug logging
        if brief_summary or detailed_summary:
            logger.info(f"📊 Displaying executive summary (brief: {len(brief_summary) if brief_summary else 0} chars, detailed: {len(detailed_summary) if detailed_summary else 0} chars)")
        else:
            logger.warning("⚠️ No executive summary found in analysis results")
        
        # Generate RAG summary if comparison enabled
        rag_brief_summary = None
        rag_detailed_summary = None
        rag_metadata = None
        campaign_id = st.session_state.get('selected_campaign', 'all_campaigns')
        
        if enable_rag_comparison and brief_summary:
            try:
                rag_timing_placeholder = st.empty()
                with st.spinner("🔬 Generating RAG-enhanced summary..."):
                    from src.utils.comparison_logger import ComparisonLogger
                    import uuid
                    import time
                    
                    # Create analyzer instance for RAG
                    analyzer = MediaAnalyticsExpert()
                    
                    # Generate RAG summary
                    metrics = analysis.get("metrics", {})
                    insights = analysis.get("insights", [])
                    recommendations = analysis.get("recommendations", [])
                    
                    start_time = time.time()
                    rag_result = analyzer._generate_executive_summary_with_rag(metrics, insights, recommendations)
                    rag_latency = time.time() - start_time
                    
                    # Show RAG timing prominently
                    rag_timing_placeholder.info(f"⏱️ RAG Analysis completed in **{rag_latency:.1f}s**")
                    
                    if isinstance(rag_result, dict):
                        rag_brief_summary = _strip_light_markup(rag_result.get("brief", ""))
                        rag_detailed_summary = _strip_light_markup(rag_result.get("detailed", ""))
                        rag_metadata = rag_result.get("rag_metadata", {})
                        
                        # Log comparison
                        session_id = st.session_state.get('session_id', str(uuid.uuid4())[:8])
                        
                        comparison_logger = ComparisonLogger()
                        comparison_logger.log_comparison(
                            session_id=session_id,
                            campaign_id=campaign_id,
                            standard_result={
                                'summary_brief': brief_summary,
                                'summary_detailed': detailed_summary,
                                'tokens_input': 2500,  # Estimated
                                'tokens_output': len(brief_summary.split()) * 1.3,
                                'cost': 0.015,
                                'latency': 2.5,
                                'model': 'standard'
                            },
                            rag_result={
                                'summary_brief': rag_brief_summary,
                                'summary_detailed': rag_detailed_summary,
                                'tokens_input': rag_metadata.get('tokens_input', 0),
                                'tokens_output': rag_metadata.get('tokens_output', 0),
                                'cost': 0.022,
                                'latency': rag_latency,
                                'model': rag_metadata.get('model', 'unknown'),
                                'knowledge_sources': rag_metadata.get('knowledge_sources', [])
                            }
                        )
                        
                        logger.info(f"✅ RAG comparison generated and logged (session: {session_id})")
            except Exception as e:
                logger.error(f"❌ RAG comparison failed: {e}")
                st.error(f"RAG comparison failed: {str(e)}")
        
        # Display summaries
        if enable_rag_comparison and rag_brief_summary:
            # Timing Summary Box
            timing_data = analysis.get('timing', {})
            auto_time = timing_data.get('auto_analysis_seconds', 0)
            rag_time = rag_metadata.get('latency', 0) if rag_metadata else 0
            total_time = auto_time + rag_time
            
            st.markdown("### ⏱️ Performance Timing")
            timing_col1, timing_col2, timing_col3, timing_col4 = st.columns(4)
            with timing_col1:
                st.metric("Auto Analysis", f"{auto_time:.1f}s")
            with timing_col2:
                st.metric("RAG Analysis", f"{rag_time:.1f}s")
            with timing_col3:
                st.metric("Total Time", f"{total_time:.1f}s")
            with timing_col4:
                perf_stats = analysis.get('performance_stats', {})
                if perf_stats.get('parallel_enabled'):
                    st.metric("Mode", "⚡ Parallel")
                else:
                    st.metric("Mode", "Sequential")
            
            # Side-by-side comparison
            st.markdown("### 📊 Comparison View")
            
            col_standard, col_rag = st.columns(2)
            
            with col_standard:
                st.markdown("#### 📄 Standard Summary")
                st.info(brief_summary)
                
                if detailed_summary:
                    with st.expander("📄 View Detailed", expanded=False):
                        st.markdown(detailed_summary)
            
            with col_rag:
                st.markdown("#### 🔬 RAG-Enhanced Summary")
                st.success(rag_brief_summary)
                
                if rag_metadata:
                    st.caption(f"🧠 Knowledge sources: {rag_metadata.get('retrieval_count', 0)} | "
                             f"⏱️ {rag_metadata.get('latency', 0):.1f}s | "
                             f"💰 +{((rag_metadata.get('tokens_input', 0) / 2500 - 1) * 100):.0f}% tokens")
                
                if rag_detailed_summary:
                    with st.expander("📄 View Detailed", expanded=False):
                        st.markdown(rag_detailed_summary)
            
            # Feedback section
            st.markdown("---")
            st.markdown("#### 💬 Which summary do you prefer?")
            
            feedback_col1, feedback_col2, feedback_col3, feedback_col4 = st.columns([1, 1, 1, 2])
            
            with feedback_col1:
                if st.button("👍 Standard", key="prefer_standard"):
                    try:
                        comparison_logger = ComparisonLogger()
                        comparison_logger.log_feedback(
                            session_id=st.session_state.get('session_id', 'unknown'),
                            campaign_id=campaign_id,
                            user_preference='standard',
                            quality_rating=None,
                            usefulness_rating=None,
                            comments="User preferred standard summary"
                        )
                        st.success("✅ Feedback recorded!")
                    except Exception as e:
                        logger.error(f"Failed to log feedback: {e}")
            
            with feedback_col2:
                if st.button("👍 RAG-Enhanced", key="prefer_rag"):
                    try:
                        comparison_logger = ComparisonLogger()
                        comparison_logger.log_feedback(
                            session_id=st.session_state.get('session_id', 'unknown'),
                            campaign_id=campaign_id,
                            user_preference='rag',
                            quality_rating=None,
                            usefulness_rating=None,
                            comments="User preferred RAG-enhanced summary"
                        )
                        st.success("✅ Feedback recorded!")
                    except Exception as e:
                        logger.error(f"Failed to log feedback: {e}")
            
            with feedback_col3:
                if st.button("🤷 Same Quality", key="prefer_same"):
                    try:
                        comparison_logger = ComparisonLogger()
                        comparison_logger.log_feedback(
                            session_id=st.session_state.get('session_id', 'unknown'),
                            campaign_id=campaign_id,
                            user_preference='same',
                            quality_rating=None,
                            usefulness_rating=None,
                            comments="User found both summaries equally good"
                        )
                        st.success("✅ Feedback recorded!")
                    except Exception as e:
                        logger.error(f"Failed to log feedback: {e}")
        
        else:
            # Standard display (no comparison)
            if brief_summary:
                st.markdown(brief_summary)
            else:
                # Fallback to highlights if LLM failed
                st.warning("⚠️ Executive summary generation failed. Showing key highlights instead:")
                highlights = _build_key_highlights(analysis)
                if highlights:
                    for point in highlights:
                        st.markdown(f"• {point}")
                else:
                    st.error("Unable to generate executive summary or highlights. Check API keys and try again.")
            
            # Show detailed summary in an expander
            if detailed_summary:
                with st.expander("📄 View Detailed Executive Summary", expanded=False):
                    st.markdown(detailed_summary)
        
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        
        # Display data quality warnings for ROAS/Revenue
        roas_analysis = analysis.get("roas_revenue_analysis", {})
        data_quality = roas_analysis.get("data_quality", {})
        missing_warning = data_quality.get("missing_data_warning")
        zero_roas_count = data_quality.get("zero_roas_count", 0)
        
        if missing_warning or zero_roas_count > 0:
            st.markdown("### ⚠️ Data Quality Notices")
            if missing_warning:
                st.warning(f"**Revenue Data:** {missing_warning}")
            if zero_roas_count > 0:
                st.info(f"📊 **Note:** {zero_roas_count} records with zero ROAS were excluded from revenue analysis to ensure accurate metrics.")

        st.markdown("<div id='overview'></div>", unsafe_allow_html=True)
        st.markdown("## 🧭 Overview")
        
        # Dynamic dimension detection
        dimension_columns = []
        possible_dimensions = [
            ('Campaign_Name', 'Campaign'),
            ('Platform', 'Platform'),
            ('Placement', 'Placement'),
            ('Funnel_Stage', 'Funnel'),
            ('Audience', 'Audience'),
            ('Ad_Type', 'Ad Type'),
            ('Region', 'Region'),
            ('Age_Group', 'Age'),
            ('Device', 'Device'),
            ('Gender', 'Gender')
        ]
        
        for col_name, display_name in possible_dimensions:
            if col_name in df.columns:
                dimension_columns.append((col_name, display_name))
        
        # Create filter columns dynamically
        num_filters = min(len(dimension_columns) + 1, 6)  # +1 for date, max 6
        filter_cols = st.columns(num_filters)
        
        # Campaign filter
        campaign_options = ["All Campaigns"] + (
            sorted(df["Campaign_Name"].dropna().unique().tolist())
            if "Campaign_Name" in df.columns
            else []
        )
        selected_campaign = filter_cols[0].selectbox(
            "Campaign",
            options=campaign_options,
        )
        
        # Dynamic dimension filters
        selected_filters = {}
        filter_idx = 1
        for col_name, display_name in dimension_columns[1:num_filters-1]:  # Skip Campaign (already added)
            options = sorted(df[col_name].dropna().unique().tolist())
            selected = filter_cols[filter_idx].multiselect(
                display_name,
                options=options,
                default=options,
            )
            selected_filters[col_name] = selected
            filter_idx += 1
        # Date filter (last column)
        date_range = None
        if "Date" in df.columns and filter_idx < num_filters:
            try:
                df_dates = pd.to_datetime(df["Date"], errors="coerce")
                min_date, max_date = df_dates.min(), df_dates.max()
                if pd.notna(min_date) and pd.notna(max_date):
                    date_range = filter_cols[filter_idx].date_input(
                        "Date Range",
                        value=(min_date.date(), max_date.date()),
                    )
            except Exception:
                date_range = None

        # Apply filters
        df_mgmt = df.copy()
        if selected_campaign != "All Campaigns" and "Campaign_Name" in df_mgmt.columns:
            df_mgmt = df_mgmt[df_mgmt["Campaign_Name"] == selected_campaign]
        
        # Apply dynamic dimension filters
        for col_name, selected_values in selected_filters.items():
            if selected_values and col_name in df_mgmt.columns:
                df_mgmt = df_mgmt[df_mgmt[col_name].isin(selected_values)]
        if date_range and "Date" in df_mgmt.columns:
            df_mgmt = df_mgmt.copy()
            df_mgmt["Date"] = pd.to_datetime(df_mgmt["Date"], errors="coerce")
            start_date, end_date = date_range
            df_mgmt = df_mgmt[
                (df_mgmt["Date"] >= pd.to_datetime(start_date))
                & (df_mgmt["Date"] <= pd.to_datetime(end_date))
            ]

        # Use flexible column mapping for spend/conversions
        spend_col_mgmt = _get_column(df_mgmt, "spend")
        conv_col_mgmt = _get_column(df_mgmt, "conversions")
        roas_col_mgmt = _get_column(df_mgmt, "roas")
        cpa_col_mgmt = _get_column(df_mgmt, "cpa")

        # Build dynamic metrics based on available columns
        available_metrics = []
        if spend_col_mgmt:
            available_metrics.append(("Total Spend", f"${float(df_mgmt[spend_col_mgmt].sum()):,.0f}"))
        if conv_col_mgmt:
            available_metrics.append(("Total Conversions", f"{float(df_mgmt[conv_col_mgmt].sum()):,.0f}"))
        if roas_col_mgmt:
            available_metrics.append(("Avg ROAS", f"{df_mgmt[roas_col_mgmt].mean():.2f}x"))
        if cpa_col_mgmt:
            available_metrics.append(("Avg CPA", f"${df_mgmt[cpa_col_mgmt].mean():.2f}"))
        
        # Show only available metrics
        if available_metrics:
            cols = st.columns(len(available_metrics))
            for idx, (label, value) in enumerate(available_metrics):
                cols[idx].metric(label, value)

        # Weekly Performance Chart (Dual-Axis)
        if not df_mgmt.empty and "Date" in df_mgmt.columns:
            df_line = df_mgmt.copy()
            df_line["Date"] = pd.to_datetime(df_line["Date"], errors="coerce")
            df_line = df_line.dropna(subset=["Date"])
            # Use week start date only (Monday)
            df_line["Week"] = df_line["Date"].dt.to_period('W').dt.start_time.dt.strftime('%Y-%m-%d')
            
            # Build aggregation for weekly data
            weekly_agg = {}
            if spend_col_mgmt:
                weekly_agg[spend_col_mgmt] = "sum"
            if conv_col_mgmt:
                weekly_agg[conv_col_mgmt] = "sum"
            
            if weekly_agg:
                weekly = df_line.groupby("Week").agg(weekly_agg).reset_index()
                
                # Create dual-axis chart
                from plotly.subplots import make_subplots
                import plotly.graph_objects as go
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                if spend_col_mgmt:
                    fig.add_trace(
                        go.Bar(x=weekly["Week"], y=weekly[spend_col_mgmt], name=spend_col_mgmt, marker_color='#3b82f6'),
                        secondary_y=False,
                    )
                
                if conv_col_mgmt:
                    fig.add_trace(
                        go.Scatter(x=weekly["Week"], y=weekly[conv_col_mgmt], name=conv_col_mgmt, mode='lines+markers', marker_color='#10b981', line=dict(width=3)),
                        secondary_y=True,
                    )
                
                fig.update_xaxes(title_text="Week")
                if spend_col_mgmt:
                    fig.update_yaxes(title_text=f"<b>{spend_col_mgmt}</b>", secondary_y=False)
                if conv_col_mgmt:
                    fig.update_yaxes(title_text=f"<b>{conv_col_mgmt}</b>", secondary_y=True)
                fig.update_layout(title_text="Weekly Performance", height=400)
                
                st.plotly_chart(fig, width="stretch")

        st.markdown("<div id='key-performance-metrics'></div>", unsafe_allow_html=True)
        st.markdown("## 📈 Key Performance Metrics")
        overview = analysis["metrics"]["overview"]
        
        # Build dynamic overview metrics based on what's available (6 KPIs)
        overview_metrics = []
        if overview.get('total_spend', 0) > 0:
            overview_metrics.append(("Total Spend", f"${overview['total_spend']:,.0f}"))
        if overview.get('total_conversions', 0) > 0:
            overview_metrics.append(("Total Conversions", f"{overview['total_conversions']:,.0f}"))
        if overview.get('avg_roas') and overview['avg_roas'] > 0:
            overview_metrics.append(("Average ROAS", f"{overview['avg_roas']:.2f}x"))
        if overview.get('avg_cpa') and overview['avg_cpa'] > 0:
            overview_metrics.append(("Average CPA", f"${overview['avg_cpa']:.2f}"))
        if overview.get('avg_ctr') and overview['avg_ctr'] > 0:
            overview_metrics.append(("Average CTR", f"{overview['avg_ctr']:.2f}%"))
        if overview.get('avg_cpc') and overview['avg_cpc'] > 0:
            overview_metrics.append(("Average CPC", f"${overview['avg_cpc']:.2f}"))
        
        if overview_metrics:
            cols = st.columns(min(len(overview_metrics), 6))
            for idx, (label, value) in enumerate(overview_metrics):
                cols[idx].metric(label, value)

        # ===== NEW CHARTS SECTION =====
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div id='performance-analytics'></div>", unsafe_allow_html=True)
        st.markdown("## 📊 Performance Analytics")
        
        # Get available columns for charts
        has_platform = 'Platform' in df.columns
        has_date = 'Date' in df.columns
        has_ctr = 'CTR' in df.columns
        has_roas = 'ROAS' in df.columns
        has_cpa = 'CPA' in df.columns
        has_cpc = 'CPC' in df.columns
        has_conv_rate = 'Conversion_Rate' in df.columns
        spend_col = _get_column(df, 'spend')
        conv_col = _get_column(df, 'conversions')
        clicks_col = _get_column(df, 'clicks')
        impr_col = _get_column(df, 'impressions')
        roas_col = _get_column(df, 'roas') or ('ROAS' if 'ROAS' in df.columns else None)
        cpa_col = _get_column(df, 'cpa') or ('CPA' if 'CPA' in df.columns else None)
        ctr_col = _get_column(df, 'ctr') or ('CTR' if 'CTR' in df.columns else None)
        cpm_col = _get_column(df, 'cpm') or ('CPM' if 'CPM' in df.columns else None)
        revenue_col = _get_column(df, 'revenue') or ('Revenue' if 'Revenue' in df.columns else None)
        
        # 1. Channel Performance Comparison
        if has_platform and (has_ctr or has_roas or has_cpa):
            st.markdown("### 📈 Channel Performance Comparison")
            
            # Let user select two metrics to compare
            available_kpis = []
            if has_ctr:
                available_kpis.append('CTR')
            if has_roas:
                available_kpis.append('ROAS')
            if has_cpa:
                available_kpis.append('CPA')
            if has_cpc:
                available_kpis.append('CPC')
            if has_conv_rate:
                available_kpis.append('Conversion_Rate')
            
            if len(available_kpis) >= 2:
                col1, col2 = st.columns(2)
                metric1 = col1.selectbox('Select First Metric', available_kpis, index=0, key='channel_metric1')
                metric2 = col2.selectbox('Select Second Metric', available_kpis, index=min(1, len(available_kpis)-1), key='channel_metric2')
                
                # Create platform aggregation
                platform_agg = df.groupby('Platform').agg({
                    metric1: 'mean',
                    metric2: 'mean'
                }).reset_index()
                
                # Create dual-axis chart
                from plotly.subplots import make_subplots
                import plotly.graph_objects as go
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig.add_trace(
                    go.Bar(x=platform_agg['Platform'], y=platform_agg[metric1], name=metric1, marker_color='#3498db'),
                    secondary_y=False,
                )
                
                fig.add_trace(
                    go.Scatter(x=platform_agg['Platform'], y=platform_agg[metric2], name=metric2, mode='lines+markers', marker_color='#e74c3c', line=dict(width=3)),
                    secondary_y=True,
                )
                
                fig.update_xaxes(title_text="Platform")
                fig.update_yaxes(title_text=f"<b>{metric1}</b>", secondary_y=False)
                fig.update_yaxes(title_text=f"<b>{metric2}</b>", secondary_y=True)
                fig.update_layout(title_text=f"Channel Performance: {metric1} vs {metric2}", height=400)
                
                st.plotly_chart(fig, width="stretch")
        
        # 2. Adaptive Time Trend Analysis (Monthly/Weekly/Daily based on data)
        if has_date and spend_col:
            df_trend = df.copy()
            df_trend['Date'] = pd.to_datetime(df_trend['Date'], errors='coerce')
            df_trend = df_trend.dropna(subset=['Date'])
            
            # Determine optimal time granularity based on data span
            date_range = (df_trend['Date'].max() - df_trend['Date'].min()).days
            unique_dates = df_trend['Date'].nunique()
            
            if date_range <= 60 and unique_dates >= 7:
                # Less than 2 months with daily data -> use Daily
                time_granularity = 'Daily'
                df_trend['Time_Period'] = df_trend['Date'].dt.strftime('%Y-%m-%d')
                period_label = 'Day'
            elif date_range <= 180 and unique_dates >= 12:
                # Less than 6 months with weekly data -> use Weekly
                time_granularity = 'Weekly'
                df_trend['Time_Period'] = df_trend['Date'].dt.to_period('W').apply(lambda r: r.start_time.strftime('%Y-%m-%d'))
                period_label = 'Week'
            else:
                # Default to Monthly for longer periods
                time_granularity = 'Monthly'
                df_trend['Time_Period'] = df_trend['Date'].dt.to_period('M').astype(str)
                period_label = 'Month'
            
            # Keep Month_Year for backward compatibility
            df_trend['Month_Year'] = df_trend['Time_Period']
            
            st.markdown(f"### 📅 {time_granularity} Trend Analysis")
            st.caption(f"📊 Auto-detected granularity: **{time_granularity}** (Date range: {date_range} days, {unique_dates} unique dates)")

            # Optional dimension filtering (Campaign, Placement, Funnel, Creative, Audience, etc.)
            dimension_map = [
                ("Campaign", _resolve_dimension_column(df_trend, ["Campaign_Name", "Campaign", "Campaign ID"])),
                ("Placement", _resolve_dimension_column(df_trend, ["Placement", "Placement_Name", "Placement Type"])),
                ("Funnel Stage", _get_funnel_column(df_trend)),
                ("Creative", _resolve_dimension_column(df_trend, ["Creative", "Creative_Name", "Ad_Creative", "Ad Name"])),
                ("Audience", _resolve_dimension_column(df_trend, ["Audience", "Audience_Name", "Segment", "Cohort"])),
                ("Platform", _resolve_dimension_column(df_trend, ["Platform", "Channel", "Source"])),
                ("Region", _resolve_dimension_column(df_trend, ["Region", "Country", "Geo", "Market"])),
            ]

            available_dimensions = {"All Data": None}
            for label, column in dimension_map:
                if column:
                    available_dimensions[label] = column
            dimension_options = sorted(available_dimensions.keys(), key=lambda x: (x != "All Data", x))

            dim_col_label, dim_col_values = st.columns([1, 1])
            metric_col1, metric_col2 = st.columns(2)

            selected_dimension_label = dim_col_label.selectbox(
                "Filter by Dimension (optional)",
                options=dimension_options,
                key="trend_dimension_label"
            )
            selected_dimension_col = available_dimensions[selected_dimension_label]

            if selected_dimension_col:
                unique_values = sorted(df_trend[selected_dimension_col].dropna().unique().tolist())
                chosen_values = dim_col_values.multiselect(
                    f"{selected_dimension_label} values",
                    options=unique_values,
                    default=unique_values if len(unique_values) <= 8 else unique_values[:8],
                    key=f"trend_dimension_values_{selected_dimension_label}"
                )
                if chosen_values:
                    df_trend = df_trend[df_trend[selected_dimension_col].isin(chosen_values)]

            # Aggregate metrics by month
            monthly_metrics = {spend_col: 'sum'}
            if clicks_col:
                monthly_metrics[clicks_col] = 'sum'
            if conv_col:
                monthly_metrics[conv_col] = 'sum'
            if impr_col:
                monthly_metrics[impr_col] = 'sum'
            if roas_col:
                monthly_metrics[roas_col] = 'mean'
            if cpa_col:
                monthly_metrics[cpa_col] = 'mean'
            if ctr_col:
                monthly_metrics[ctr_col] = 'mean'
            if cpm_col:
                monthly_metrics[cpm_col] = 'mean'
            if revenue_col:
                monthly_metrics[revenue_col] = 'sum'
            
            if df_trend.empty:
                st.info("No data available for the selected filter. Showing empty chart.")
                monthly_data = pd.DataFrame(columns=['Month_Year'] + list(monthly_metrics.keys()))
            else:
                monthly_data = df_trend.groupby('Month_Year').agg(monthly_metrics).reset_index()
            
            # Add derived metrics
            if clicks_col and impr_col and clicks_col in monthly_data.columns and impr_col in monthly_data.columns:
                monthly_data['CTR (calc %)'] = (monthly_data[clicks_col] / monthly_data[impr_col] * 100).round(2)
            if conv_col and clicks_col and conv_col in monthly_data.columns and clicks_col in monthly_data.columns:
                monthly_data['Conversion Rate (calc %)'] = (monthly_data[conv_col] / monthly_data[clicks_col] * 100).round(2)
            if revenue_col and spend_col and revenue_col in monthly_data.columns and spend_col in monthly_data.columns:
                monthly_data['ROAS (calc)'] = (monthly_data[revenue_col] / monthly_data[spend_col]).replace([np.inf, -np.inf], np.nan).round(2)
            
            numeric_columns = [col for col in monthly_data.columns if col != 'Month_Year']
            all_metrics = numeric_columns
            
            if not all_metrics:
                st.warning("No numeric metrics available for trend chart.")
            else:
                metric1 = metric_col1.selectbox(
                    'Primary Metric (Left Axis)',
                    options=all_metrics,
                    index=0,
                    key='monthly_metric1'
                )
                metric2 = metric_col2.selectbox(
                    'Secondary Metric (Right Axis)',
                    options=all_metrics,
                    index=min(1, len(all_metrics)-1),
                    key='monthly_metric2'
                )

                # Create dual-axis chart
                from plotly.subplots import make_subplots
                import plotly.graph_objects as go
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig.add_trace(
                    go.Bar(x=monthly_data['Month_Year'], y=monthly_data[metric1], name=metric1, marker_color='#3b82f6'),
                    secondary_y=False,
                )
                
                fig.add_trace(
                    go.Scatter(x=monthly_data['Month_Year'], y=monthly_data[metric2], name=metric2, mode='lines+markers', marker_color='#ec4899', line=dict(width=3)),
                    secondary_y=True,
                )
                
                fig.update_xaxes(title_text="Month")
                fig.update_yaxes(title_text=f"<b>{metric1}</b>", secondary_y=False)
                fig.update_yaxes(title_text=f"<b>{metric2}</b>", secondary_y=True)
                fig.update_layout(title_text="Monthly Performance Trends", height=400)
                
                st.plotly_chart(fig, width="stretch")
        
        # 3. Funnel Analysis - CLEARLY DENOTE AWARENESS, CONSIDERATION & CONVERSION
        if has_date and clicks_col and conv_col:
            st.markdown("### 🔄 Funnel Performance Trend Analysis")
            st.markdown("**Performance across three funnel stages: Awareness → Consideration → Conversion**")
            
            df_funnel = df.copy()
            df_funnel['Date'] = pd.to_datetime(df_funnel['Date'], errors='coerce')
            df_funnel = df_funnel.dropna(subset=['Date'])
            df_funnel['Month_Year'] = df_funnel['Date'].dt.to_period('M').astype(str)
            funnel_stage_col = _get_funnel_column(df_funnel)

            if funnel_stage_col:
                st.info(f"✅ Funnel column detected: `{funnel_stage_col}`")
                stage_df = df_funnel.dropna(subset=[funnel_stage_col])
                
                # Debug: Show unique funnel values
                unique_funnels = sorted(stage_df[funnel_stage_col].unique().tolist())
                st.caption(f"Funnel stages found in data: {', '.join(map(str, unique_funnels))}")
                
                agg_dict = {clicks_col: 'sum', conv_col: 'sum'}
                if impr_col:
                    agg_dict[impr_col] = 'sum'
                if spend_col:
                    agg_dict[spend_col] = 'sum'
                    
                stage_monthly = (
                    stage_df
                    .groupby(['Month_Year', funnel_stage_col])
                    .agg(agg_dict)
                    .reset_index()
                )

                # Calculate key metrics for each funnel stage
                if impr_col and impr_col in stage_monthly.columns:
                    stage_monthly['CTR'] = (stage_monthly[clicks_col] / stage_monthly[impr_col] * 100).replace([np.inf, -np.inf], np.nan).round(2)
                else:
                    stage_monthly['CTR'] = np.nan
                stage_monthly['Conversions'] = stage_monthly[conv_col]
                
                if spend_col and spend_col in stage_monthly.columns:
                    stage_monthly['CPA'] = (stage_monthly[spend_col] / stage_monthly[conv_col]).replace([np.inf, -np.inf], np.nan).round(2)

                from plotly.subplots import make_subplots
                import plotly.graph_objects as go

                # Create dual-axis chart
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # Define the three funnel stages with distinct colors and emojis
                stage_order = ["Awareness", "Consideration", "Conversion"]
                stage_emojis = {
                    "Awareness": "👁️",
                    "Consideration": "🤔", 
                    "Conversion": "✅"
                }
                color_map = {
                    "Awareness": "#3b82f6",      # Blue - Top of funnel
                    "Consideration": "#f59e0b",  # Orange - Middle of funnel
                    "Conversion": "#10b981"      # Green - Bottom of funnel
                }

                # Store original column name before normalization
                funnel_stage_col_original = funnel_stage_col
                
                # Map funnel stage values to standard names (case-insensitive)
                def normalize_funnel_stage(stage):
                    stage_str = str(stage).strip().lower()
                    # Awareness keywords - expanded (including "upper")
                    if any(x in stage_str for x in ['aware', 'awareness', 'top', 'upper', 'impression', 'reach', 'brand', 'discovery', 'tofu']):
                        return 'Awareness'
                    # Conversion keywords - check BEFORE consideration to avoid false matches (including "lower")
                    elif any(x in stage_str for x in ['convert', 'conversion', 'bottom', 'lower', 'action', 'purchase', 'lead', 'bofu', 'sale', 'acquisition']):
                        return 'Conversion'
                    # Consideration keywords
                    elif any(x in stage_str for x in ['consider', 'consideration', 'middle', 'mid', 'interest', 'engagement', 'mofu', 'evaluation']):
                        return 'Consideration'
                    return stage  # Keep original if no match
                
                stage_monthly['Normalized_Stage'] = stage_monthly[funnel_stage_col].apply(normalize_funnel_stage)
                
                # Debug: Show original vs normalized stages with detailed mapping
                original_stages = stage_monthly[funnel_stage_col_original].unique()
                normalized_stages_before = stage_monthly['Normalized_Stage'].unique()
                
                # Create detailed mapping report
                mapping_details = []
                for orig in original_stages:
                    norm = normalize_funnel_stage(orig)
                    count = len(stage_monthly[stage_monthly[funnel_stage_col_original] == orig])
                    mapping_details.append(f"  • '{orig}' → '{norm}' ({count} records)")
                
                st.info(f"🔍 **Funnel Stage Mapping:**\n\n"
                       f"Original stages found: {', '.join(map(str, original_stages))}\n\n"
                       f"Detailed mapping:\n" + "\n".join(mapping_details) + "\n\n"
                       f"Normalized stages before filter: {', '.join(map(str, normalized_stages_before))}")
                
                # Filter data to only include the three main funnel stages
                records_before = len(stage_monthly)
                stage_monthly = stage_monthly[stage_monthly['Normalized_Stage'].isin(stage_order)]
                records_after = len(stage_monthly)
                normalized_stages_after = stage_monthly['Normalized_Stage'].unique()
                
                st.caption(f"📊 Filter results: {records_before} records → {records_after} records | "
                          f"Stages after filter: {', '.join(map(str, normalized_stages_after))}")
                
                # Use normalized stage for grouping
                funnel_stage_col = 'Normalized_Stage'

                # Check if we have any data after normalization
                if stage_monthly.empty:
                    st.warning(f"⚠️ No data matched the standard funnel stages after normalization. Original stages found: {', '.join(map(str, unique_funnels))}")
                else:
                    # Debug: Show data availability per stage
                    st.caption("📈 **Data availability per stage:**")
                    for stage in stage_order:
                        stage_subset = stage_monthly[stage_monthly[funnel_stage_col] == stage]
                        if not stage_subset.empty:
                            ctr_valid = stage_subset['CTR'].notna().sum()
                            conv_valid = stage_subset['Conversions'].notna().sum()
                            st.caption(f"  • {stage}: {len(stage_subset)} records | CTR: {ctr_valid} valid | Conversions: {conv_valid} valid")
                    
                    # Add traces for each funnel stage
                    for stage in stage_order:
                        stage_subset = stage_monthly[stage_monthly[funnel_stage_col] == stage]
                        if stage_subset.empty:
                            st.caption(f"⚠️ No data for {stage}")
                            continue
                        
                        color = color_map[stage]
                        emoji = stage_emojis[stage]
                        
                        # Primary metric: CTR (solid line with markers)
                        # Only add trace if we have valid CTR data
                        if stage_subset['CTR'].notna().any():
                            fig.add_trace(
                                go.Scatter(
                                    x=stage_subset['Month_Year'],
                                    y=stage_subset['CTR'],
                                    name=f"{emoji} {stage} - CTR",
                                    mode='lines+markers',
                                    line=dict(color=color, width=3.5),
                                    marker=dict(size=10, symbol='circle'),
                                    legendgroup=stage,
                                    connectgaps=True,  # Connect lines even with missing data
                                    hovertemplate=f'<b>{stage}</b><br>CTR: %{{y:.2f}}%<extra></extra>'
                                ),
                                secondary_y=False
                            )
                        
                        # Secondary metric: Conversions (dashed line)
                        # Only add trace if we have valid Conversions data
                        if stage_subset['Conversions'].notna().any():
                            fig.add_trace(
                                go.Scatter(
                                    x=stage_subset['Month_Year'],
                                    y=stage_subset['Conversions'],
                                    name=f"{emoji} {stage} - Conversions",
                                    mode='lines+markers',
                                    line=dict(color=color, width=2.5, dash='dot'),
                                    marker=dict(size=8, symbol='diamond'),
                                    legendgroup=stage,
                                    connectgaps=True,  # Connect lines even with missing data
                                    hovertemplate=f'<b>{stage}</b><br>Conversions: %{{y:,.0f}}<extra></extra>'
                                ),
                                secondary_y=True
                            )

                    # Update layout with clear funnel stage indicators
                    fig.update_layout(
                        title={
                            'text': '🔄 Funnel Performance: Awareness → Consideration → Conversion',
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {'size': 16, 'color': '#e2e8f0'}
                        },
                        xaxis_title='Month',
                        hovermode='x unified',
                        height=450,
                        legend=dict(
                            orientation="v",
                            yanchor="top",
                            y=1,
                            xanchor="left",
                            x=1.02,
                            bgcolor='rgba(30, 41, 59, 0.8)',
                            bordercolor='rgba(148, 163, 184, 0.3)',
                            borderwidth=1
                        ),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                    )
                    
                    # Update axes with clear labels
                    fig.update_yaxes(
                        title_text='<b>CTR (%)</b>', 
                        secondary_y=False,
                        showgrid=True,
                        gridcolor='rgba(128,128,128,0.2)'
                    )
                    fig.update_yaxes(
                        title_text='<b>Conversions</b>', 
                        secondary_y=True,
                        showgrid=False
                    )
                    fig.update_xaxes(
                        showgrid=True,
                        gridcolor='rgba(128,128,128,0.2)'
                    )

                    # Add summary metrics for each funnel stage BEFORE chart
                    st.markdown("#### 📊 Funnel Stage Summary")
                    funnel_cols = st.columns(3)
                    
                    # Display all three stages
                    for idx, stage in enumerate(stage_order):
                        stage_data = stage_monthly[stage_monthly[funnel_stage_col] == stage]
                        with funnel_cols[idx]:
                            emoji = stage_emojis[stage]
                            if not stage_data.empty:
                                avg_ctr = stage_data['CTR'].mean()
                                total_conv = stage_data['Conversions'].sum()
                                
                                st.markdown(f"**{emoji} {stage}**")
                                st.metric("Avg CTR", f"{avg_ctr:.2f}%" if not pd.isna(avg_ctr) else "N/A")
                                st.metric("Total Conversions", f"{total_conv:,.0f}" if not pd.isna(total_conv) else "N/A")
                                
                                if 'CPA' in stage_data.columns:
                                    avg_cpa = stage_data['CPA'].mean()
                                    if not pd.isna(avg_cpa):
                                        st.metric("Avg CPA", f"${avg_cpa:.2f}")
                            else:
                                # Show placeholder for missing stage
                                st.markdown(f"**{emoji} {stage}**")
                                st.caption("No data available")
                    
                    # Show the chart only if we have traces
                    if len(fig.data) > 0:
                        st.plotly_chart(fig, width="stretch")
                    else:
                        st.warning("⚠️ No funnel data to display after filtering.")
            else:
                # No funnel column detected - show warning
                st.warning("⚠️ **No Funnel Stage column detected in your data.**\n\n"
                          "To see performance by funnel stage (Awareness, Consideration, Conversion), "
                          "please ensure your data has a column named one of: `Funnel_Stage`, `Funnel`, `Stage`, or `Campaign_Type` "
                          "with values: 'Awareness', 'Consideration', 'Conversion'.\n\n"
                          "**Showing aggregate funnel metrics instead:**")
                
                # Fall back to aggregate view if no funnel dimension detected
                funnel_agg = {clicks_col: 'sum'}
                if conv_col:
                    funnel_agg[conv_col] = 'sum'
                if impr_col:
                    funnel_agg[impr_col] = 'sum'
                funnel_monthly = df_funnel.groupby('Month_Year').agg(funnel_agg).reset_index()
                if impr_col and clicks_col in funnel_monthly.columns:
                    funnel_monthly['CTR'] = (funnel_monthly[clicks_col] / funnel_monthly[impr_col] * 100).round(2)
                if clicks_col and conv_col and clicks_col in funnel_monthly.columns and conv_col in funnel_monthly.columns:
                    funnel_monthly['Conversion_Rate'] = (funnel_monthly[conv_col] / funnel_monthly[clicks_col] * 100).round(2)

                import plotly.graph_objects as go
                fig = go.Figure()
                if clicks_col in funnel_monthly.columns:
                    fig.add_trace(go.Scatter(
                        x=funnel_monthly['Month_Year'],
                        y=funnel_monthly[clicks_col],
                        name='Clicks',
                        mode='lines+markers',
                        line=dict(color='#3b82f6', width=3)
                    ))
                if 'CTR' in funnel_monthly.columns:
                    fig.add_trace(go.Scatter(
                        x=funnel_monthly['Month_Year'],
                        y=funnel_monthly['CTR'],
                        name='CTR (%)',
                        mode='lines+markers',
                        line=dict(color='#10b981', width=3),
                        yaxis='y2'
                    ))
                if 'Conversion_Rate' in funnel_monthly.columns:
                    fig.add_trace(go.Scatter(
                        x=funnel_monthly['Month_Year'],
                        y=funnel_monthly['Conversion_Rate'],
                        name='Conversion Rate (%)',
                        mode='lines+markers',
                        line=dict(color='#8b5cf6', width=3),
                        yaxis='y2'
                    ))
                fig.update_layout(
                    title='Funnel Performance: Clicks, CTR & Conversion Rate',
                    xaxis_title='Month',
                    yaxis_title='Clicks',
                    yaxis2=dict(title='Rate (%)', overlaying='y', side='right'),
                    height=400,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, width="stretch")
        
        # Move Opportunities & Risks here (after Funnel chart)
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div id='opportunities-risks'></div>", unsafe_allow_html=True)
        st.markdown("## 💡 Opportunities & Risks")

        # Nicely formatted opportunity cards
        for opp in analysis["opportunities"]:
            opp_type = opp.get("type", "Opportunity")
            period = opp.get("period")
            avg_roas = opp.get("avg_roas")
            desc = opp.get("opportunity") or opp.get("description")
            impact = opp.get("potential_impact") or opp.get("impact")

            details = []
            if period:
                details.append(f"<strong>Period:</strong> {period}")
            if avg_roas is not None:
                try:
                    details.append(f"<strong>Avg ROAS:</strong> {float(avg_roas):.2f}x")
                except Exception:
                    details.append(f"<strong>Avg ROAS:</strong> {avg_roas}")
            if desc:
                details.append(f"<strong>Why it matters:</strong> {desc}")
            if impact:
                details.append(f"<strong>Recommended action:</strong> {impact}")

            body_html = "<br>".join(details)
            card_html = (
                "<div class='insight-card'>"
                f"✅ <strong>{opp_type}</strong><br>"
                f"{body_html}"
                "</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)

        # Nicely formatted risk cards
        for risk in analysis["risks"]:
            severity = risk.get("severity", "Risk")
            title = risk.get("risk", "Performance Risk")
            details = risk.get("details")
            impact = risk.get("impact")
            action = risk.get("action")

            lines = []
            lines.append(f"<strong>Severity:</strong> {severity}")
            lines.append(f"<strong>Risk:</strong> {title}")
            if details:
                lines.append(f"<strong>Details:</strong> {details}")
            if impact:
                lines.append(f"<strong>Impact:</strong> {impact}")
            if action:
                lines.append(f"<strong>Recommended action:</strong> {action}")

            body_html = "<br>".join(lines)
            card_html = (
                "<div class='insight-card' style='border-left-color:#e74c3c'>"
                f"⚠️ <strong>{title}</strong><br>"
                f"{body_html}"
                "</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)
        
        # 4. Correlation Analysis
        if spend_col and conv_col and (has_ctr or has_roas):
            st.markdown("### 🔗 Correlation Analysis")
            
            col1, col2 = st.columns(2)
            
            # Correlation 1: Spend vs Conversions
            with col1:
                fig = px.scatter(
                    df,
                    x=spend_col,
                    y=conv_col,
                    color='Platform' if has_platform else None,
                    title=f'{spend_col} vs {conv_col}',
                    trendline='ols',
                    hover_data=['Campaign_Name'] if 'Campaign_Name' in df.columns else None
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, width="stretch")
            
            # Correlation 2: CTR vs ROAS or CTR vs Conv Rate
            with col2:
                if has_ctr and has_roas:
                    fig = px.scatter(
                        df,
                        x='CTR',
                        y='ROAS',
                        color='Platform' if has_platform else None,
                        title='CTR vs ROAS',
                        trendline='ols',
                        hover_data=['Campaign_Name'] if 'Campaign_Name' in df.columns else None
                    )
                elif has_ctr and has_conv_rate:
                    fig = px.scatter(
                        df,
                        x='CTR',
                        y='Conversion_Rate',
                        color='Platform' if has_platform else None,
                        title='CTR vs Conversion Rate',
                        trendline='ols',
                        hover_data=['Campaign_Name'] if 'Campaign_Name' in df.columns else None
                    )
                else:
                    # Fallback: CPA vs Conversions if available
                    if has_cpa:
                        fig = px.scatter(
                            df,
                            x='CPA',
                            y=conv_col,
                            color='Platform' if has_platform else None,
                            title=f'CPA vs {conv_col}',
                            trendline='ols',
                            hover_data=['Campaign_Name'] if 'Campaign_Name' in df.columns else None
                        )
                    else:
                        fig = None
                
                if fig:
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, width="stretch")
        
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Deep Dive Tab - Channel Intelligence, Pattern Analysis, Dashboard View
# ---------------------------------------------------------------------------
with tab_deepdive:
    st.markdown("## 🔬 Deep Dive Analysis")
    
    if st.session_state.df is None or not st.session_state.analysis_complete:
        st.info("📊 Complete Auto Analysis first to access Deep Dive features.")
    else:
        df = st.session_state.df
        analysis = st.session_state.analysis_data
        
        # Create sub-tabs for Deep Dive sections
        dd_channel, dd_patterns, dd_dashboard = st.tabs([
            "🎯 Channel Intelligence",
            "🔍 Pattern Analysis",
            "📊 Dashboard View"
        ])
        
        # Channel Intelligence Tab
        with dd_channel:
            st.markdown("### 🎯 Channel-Specific Intelligence")
            
            # Get channel/platform column
            channel_col = None
            for col in ['Platform', 'Channel', 'Source', 'Medium']:
                if col in df.columns:
                    channel_col = col
                    break
            
            if channel_col:
                st.success(f"📊 Analyzing by: **{channel_col}**")
                
                # Channel performance summary
                channels = df[channel_col].unique()
                st.markdown(f"#### 📈 Performance by {channel_col} ({len(channels)} found)")
                
                # Build channel metrics
                channel_metrics = []
                for channel in channels:
                    ch_df = df[df[channel_col] == channel]
                    metrics = {'Channel': channel, 'Records': len(ch_df)}
                    
                    # Add available metrics
                    for metric_col in ['Spend', 'Impressions', 'Clicks', 'Conversions', 'CTR', 'CPC', 'CPA']:
                        if metric_col in ch_df.columns:
                            if metric_col in ['CTR', 'CPC', 'CPA']:
                                metrics[metric_col] = ch_df[metric_col].mean()
                            else:
                                metrics[metric_col] = ch_df[metric_col].sum()
                    channel_metrics.append(metrics)
                
                # Display as table
                channel_df = pd.DataFrame(channel_metrics)
                st.dataframe(channel_df, use_container_width=True)
                
                # Top/Bottom performers
                if 'Spend' in channel_df.columns and 'Conversions' in channel_df.columns:
                    channel_df['Efficiency'] = channel_df['Conversions'] / channel_df['Spend'].replace(0, 1)
                    top_channel = channel_df.loc[channel_df['Efficiency'].idxmax(), 'Channel']
                    bottom_channel = channel_df.loc[channel_df['Efficiency'].idxmin(), 'Channel']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.success(f"🏆 **Top Performer**: {top_channel}")
                    with col2:
                        st.warning(f"⚠️ **Needs Attention**: {bottom_channel}")
                
                # Channel recommendations from analysis
                if analysis and 'recommendations' in analysis:
                    channel_recs = [r for r in analysis['recommendations'] 
                                   if isinstance(r, dict) and 'channel' in str(r).lower()]
                    if channel_recs:
                        st.markdown("#### 💡 Channel Recommendations")
                        for rec in channel_recs[:3]:
                            st.info(f"• {rec.get('recommendation', rec.get('text', str(rec)))}")
            else:
                st.info("ℹ️ No channel/platform column found in data. Upload data with Platform or Channel column.")
        
        # Pattern Analysis Tab
        with dd_patterns:
            st.markdown("### 🔍 Pattern Analysis & Insights")
            
            # Use insights from main analysis
            insights = analysis.get('insights', []) if analysis else []
            
            if insights:
                st.markdown("#### 💡 Key Insights from Analysis")
                for idx, insight in enumerate(insights[:10], 1):
                    if isinstance(insight, dict):
                        title = insight.get('title', insight.get('insight', f'Insight {idx}'))
                        impact = insight.get('impact', 'medium')
                        emoji = '🔴' if impact == 'high' else '🟡' if impact == 'medium' else '🟢'
                        st.markdown(f"{emoji} **{title}**")
                        if 'description' in insight:
                            st.caption(insight['description'])
                    else:
                        st.info(f"• {insight}")
            else:
                st.info("ℹ️ No pattern insights available yet.")
            
            # Show data trends if date column exists
            date_col = None
            for col in ['Date', 'date', 'DATE', 'Day', 'Week', 'Month']:
                if col in df.columns:
                    date_col = col
                    break
            
            if date_col:
                st.markdown("#### 📈 Time-Based Trends")
                
                # Aggregate by date
                df_trend = df.copy()
                df_trend[date_col] = pd.to_datetime(df_trend[date_col], errors='coerce')
                df_trend = df_trend.dropna(subset=[date_col])
                
                if len(df_trend) > 0:
                    # Find numeric columns to plot
                    numeric_cols = [c for c in ['Spend', 'Impressions', 'Clicks', 'Conversions', 'CTR'] 
                                   if c in df_trend.columns]
                    
                    if numeric_cols:
                        metric_to_plot = st.selectbox("Select metric to view trend:", numeric_cols, key="dd_trend_metric")
                        
                        daily_data = df_trend.groupby(date_col)[metric_to_plot].sum().reset_index()
                        
                        import plotly.express as px
                        fig = px.line(daily_data, x=date_col, y=metric_to_plot, 
                                     title=f"{metric_to_plot} Over Time")
                        fig.update_layout(height=350)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Calculate trend
                        if len(daily_data) >= 2:
                            first_half = daily_data[metric_to_plot].iloc[:len(daily_data)//2].mean()
                            second_half = daily_data[metric_to_plot].iloc[len(daily_data)//2:].mean()
                            change = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0
                            
                            if change > 5:
                                st.success(f"📈 **Upward Trend**: {metric_to_plot} increased by {change:.1f}%")
                            elif change < -5:
                                st.warning(f"📉 **Downward Trend**: {metric_to_plot} decreased by {abs(change):.1f}%")
                            else:
                                st.info(f"➡️ **Stable**: {metric_to_plot} relatively flat ({change:+.1f}%)")
            
            # Show recommendations
            recommendations = analysis.get('recommendations', []) if analysis else []
            if recommendations:
                st.markdown("#### 💡 Recommendations")
                for rec in recommendations[:5]:
                    if isinstance(rec, dict):
                        priority = rec.get('priority', 'medium')
                        emoji = '🔴' if priority == 'high' else '🟡' if priority == 'medium' else '🟢'
                        text = rec.get('recommendation', rec.get('text', str(rec)))
                        st.markdown(f"{emoji} {text}")
                    else:
                        st.markdown(f"• {rec}")
        
        # Dashboard View Tab
        with dd_dashboard:
            st.markdown("### 📊 Dashboard View")
            
            # Build simple charts based on available data
            import plotly.express as px
            import plotly.graph_objects as go
            
            charts_created = 0
            
            # 1. Spend Distribution (if Platform/Channel exists)
            channel_col = None
            for col in ['Platform', 'Channel', 'Source']:
                if col in df.columns:
                    channel_col = col
                    break
            
            if channel_col and 'Spend' in df.columns:
                st.markdown("#### 💰 Spend Distribution")
                spend_by_channel = df.groupby(channel_col)['Spend'].sum().reset_index()
                fig = px.pie(spend_by_channel, values='Spend', names=channel_col, 
                            title=f"Spend by {channel_col}")
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
                charts_created += 1
            
            # 2. Performance Metrics Overview
            st.markdown("#### 📈 Key Metrics Summary")
            metric_cols = []
            for col in ['Spend', 'Impressions', 'Clicks', 'Conversions']:
                if col in df.columns:
                    metric_cols.append(col)
            
            if metric_cols:
                cols = st.columns(len(metric_cols))
                for i, col in enumerate(metric_cols):
                    with cols[i]:
                        total = df[col].sum()
                        if col == 'Spend':
                            st.metric(col, f"${total:,.0f}")
                        else:
                            st.metric(col, f"{total:,.0f}")
                charts_created += 1
            
            # 3. CTR/CPC Analysis (if available)
            if 'CTR' in df.columns and channel_col:
                st.markdown("#### 📊 CTR by Channel")
                ctr_by_channel = df.groupby(channel_col)['CTR'].mean().reset_index()
                fig = px.bar(ctr_by_channel, x=channel_col, y='CTR', 
                            title=f"Average CTR by {channel_col}")
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
                charts_created += 1
            
            # 4. Conversions trend (if date exists)
            date_col = None
            for col in ['Date', 'date', 'Day']:
                if col in df.columns:
                    date_col = col
                    break
            
            if date_col and 'Conversions' in df.columns:
                st.markdown("#### 📈 Conversions Over Time")
                df_time = df.copy()
                df_time[date_col] = pd.to_datetime(df_time[date_col], errors='coerce')
                df_time = df_time.dropna(subset=[date_col])
                
                if len(df_time) > 0:
                    daily_conv = df_time.groupby(date_col)['Conversions'].sum().reset_index()
                    fig = px.area(daily_conv, x=date_col, y='Conversions', 
                                 title="Daily Conversions")
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
                    charts_created += 1
            
            # 5. Funnel metrics if available
            funnel_col = None
            for col in ['Funnel_Stage', 'Funnel', 'Stage']:
                if col in df.columns:
                    funnel_col = col
                    break
            
            if funnel_col and 'Spend' in df.columns:
                st.markdown("#### 🔄 Funnel Performance")
                funnel_data = df.groupby(funnel_col).agg({
                    'Spend': 'sum',
                    'Clicks': 'sum' if 'Clicks' in df.columns else lambda x: 0,
                    'Conversions': 'sum' if 'Conversions' in df.columns else lambda x: 0
                }).reset_index()
                
                fig = px.bar(funnel_data, x=funnel_col, y='Spend', 
                            title=f"Spend by {funnel_col}")
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
                charts_created += 1
            
            if charts_created > 0:
                st.success(f"✅ Dashboard complete: {charts_created} charts generated")
            else:
                st.warning("⚠️ Not enough data columns to generate charts. Need: Spend, Platform/Channel, Date, etc.")


# ---------------------------------------------------------------------------
# Natural Language Q&A Tab
# ---------------------------------------------------------------------------
with tab_qa:
    st.markdown("## 💬 Ask Questions")
    if st.session_state.df is None:
        st.info("Upload data in the Auto Analysis tab before running queries.")
    else:
        # Lazily initialize the NL → SQL engine and orchestrator
        if st.session_state.query_engine is None:
            api_key = get_api_key("OPENAI_API_KEY", "OPENAI_API_KEY")
            if not api_key:
                st.error("❌ OPENAI_API_KEY not found. Set it in your .env to use Q&A.")
            else:
                with st.spinner("🤖 Initializing Q&A engine..."):
                    engine = NaturalLanguageQueryEngine(api_key)
                    engine.load_data(st.session_state.df)
                    st.session_state.query_engine = engine
                    
                    # Initialize orchestrator
               #     st.session_state.orchestrator = QueryOrchestrator(
               #         query_engine=engine,
                #        interpreter=st.session_state.interpreter
                 #   )

        user_query = st.text_input(
            "🔍 Ask a question about your campaigns",
            placeholder="e.g., sort by funnel performance, show top campaigns, what are the KPIs",
            key="user_query_input"
        )

        data_loaded = st.session_state.df is not None
        engine_ready = st.session_state.query_engine is not None

        status_col, button_col = st.columns([3, 1])
        with status_col:
            if data_loaded:
                st.success(f"✅ Data loaded ({len(st.session_state.df):,} rows · {len(st.session_state.df.columns)} columns)")
            else:
                st.warning("⚠️ No dataset loaded yet. Upload data on the Auto Analysis tab.")

            if data_loaded and not engine_ready:
                st.info("Initializing Q&A engine...")

        with button_col:
            ask_disabled = not (data_loaded and engine_ready and user_query.strip())
            ask_clicked = st.button(
                "🚀 Ask Question",
                type="primary",
                width="stretch",
                disabled=ask_disabled,
            )

        # Direct execution only - no interpretation layer
        if ask_clicked:
            if st.session_state.query_engine:
                with st.spinner("🔄 Generating SQL & running query..."):
                    try:
                        start = time.time()
                        result = st.session_state.query_engine.ask(user_query)
                        exec_time = int((time.time() - start) * 1000)
                        
                        # Extract results
                        sql_text = result.get("sql_query") or result.get("sql") or ""
                        results_df = result.get("results")
                        answer = result.get("answer")
                        
                        # Store results
                        st.session_state.last_result = {
                            "sql": sql_text,
                            "df": results_df,
                            "answer": answer,
                            "model_used": result.get("model_used", "unknown")
                        }
                        
                        # Log to tracker
                        st.session_state.current_query_id = st.session_state.query_tracker.start_query(
                            original_query=user_query,
                            interpretations=[],
                            user_id="analyst",
                            session_id=st.session_state["session_id"],
                        )
                        st.session_state.query_tracker.update_query(
                            query_id=st.session_state.current_query_id,
                            generated_sql=sql_text,
                            execution_time_ms=exec_time,
                            result_count=len(results_df) if isinstance(results_df, pd.DataFrame) else 0,
                        )
                        
                        st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if "insufficient_quota" in error_msg or "429" in error_msg:
                            st.error("❌ **OpenAI API Quota Exceeded**")
                            st.warning("⚠️ Your OpenAI API key has no credits left.")
                            st.info("**Solutions:**\n1. Add credits at https://platform.openai.com/account/billing\n2. Or use a different API key")
                        elif "authentication_error" in error_msg or "401" in error_msg:
                            st.error("❌ **API Authentication Failed**")
                            st.warning("⚠️ Your API key is invalid or expired.")
                            st.info("**Solutions:**\n1. Check your .env file\n2. Get a new API key from OpenAI or Anthropic")
                        else:
                            st.error(f"❌ Query failed: {error_msg}")
                        
                        import traceback
                        with st.expander("🔍 Error Details"):
                            st.code(traceback.format_exc())
        
        # Display results if available
        if st.session_state.get("last_result"):
            result_data = st.session_state.last_result
            
            st.markdown("### 📊 Results")
            
            # Show which model was used
            if result_data.get("model_used"):
                model_name = result_data["model_used"]
                if "gemini" in model_name.lower():
                    st.success(f"🤖 **Model Used:** {model_name} (FREE)")
                else:
                    st.info(f"🤖 **Model Used:** {model_name}")
            
            with st.expander("🔍 Generated SQL", expanded=False):
                sql_text = result_data.get("sql")
                if sql_text:
                    st.code(sql_text, language="sql")
                else:
                    # No SQL captured (likely due to an error before generation/execution)
                    st.code("-- No SQL was generated or the query failed before SQL could be produced.\n-- Check the error details shown above.", language="sql")

            results_df = result_data.get("df")
            if results_df is not None and isinstance(results_df, pd.DataFrame) and not results_df.empty:
                st.dataframe(result_data["df"], width="stretch")
                csv = result_data["df"].to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    "query_results.csv",
                    "text/csv",
                )
                
                # ===== AUTO-GENERATE CHART FOR Q&A RESULTS =====
                st.markdown("### 📊 Visualization")
                
                # Detect numeric and categorical columns
                numeric_cols = results_df.select_dtypes(include=['number']).columns.tolist()
                categorical_cols = results_df.select_dtypes(include=['object', 'category']).columns.tolist()
                
                # Smart chart generation based on data structure with priority metrics
                if len(results_df) > 0:
                    # Define priority metrics (most important first)
                    priority_metrics = [
                        'CTR', 'Conversions', 'Conversion_Rate', 'ROAS', 'CPA', 'CPC',
                        'Revenue', 'Spend', 'Clicks', 'Impressions'
                    ]
                    
                    # Helper function to prioritize metrics
                    def prioritize_metrics(cols, priority_list, max_count=3):
                        """Select most important metrics based on priority list."""
                        prioritized = []
                        # First add priority metrics that exist
                        for metric in priority_list:
                            matching = [col for col in cols if metric.lower() in col.lower()]
                            prioritized.extend(matching)
                            if len(prioritized) >= max_count:
                                break
                        # Then add remaining metrics if needed
                        for col in cols:
                            if col not in prioritized:
                                prioritized.append(col)
                            if len(prioritized) >= max_count:
                                break
                        return prioritized[:max_count]
                    
                    # Case 1: Single row with multiple metrics (show as bar chart)
                    if len(results_df) == 1 and len(numeric_cols) > 1:
                        # Prioritize metrics
                        selected_metrics = prioritize_metrics(numeric_cols, priority_metrics, max_count=5)
                        chart_data = pd.DataFrame({
                            'Metric': selected_metrics,
                            'Value': [results_df[col].iloc[0] for col in selected_metrics]
                        })
                        fig = px.bar(chart_data, x='Metric', y='Value', title='Key Metrics Overview')
                        st.plotly_chart(fig, width="stretch")
                    
                    # Case 2: Multiple rows with 1 categorical + numeric (ALWAYS use dual-axis for 2+ metrics)
                    elif len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                        x_col = categorical_cols[0]
                        
                        # Prioritize numeric columns - always get top 2 for dual-axis
                        selected_metrics = prioritize_metrics(numeric_cols, priority_metrics, max_count=2)
                        
                        if len(selected_metrics) == 1:
                            # Single metric - simple bar chart
                            y_col = selected_metrics[0]
                            fig = px.bar(results_df, x=x_col, y=y_col, title=f'{y_col} by {x_col}',
                                       color_discrete_sequence=['#3498db'])
                        else:
                            # 2+ metrics - DUAL-AXIS chart with priority metrics
                            from plotly.subplots import make_subplots
                            import plotly.graph_objects as go
                            
                            fig = make_subplots(specs=[[{"secondary_y": True}]])
                            
                            # Primary metric (bar chart) - typically the more important one
                            fig.add_trace(
                                go.Bar(
                                    x=results_df[x_col], 
                                    y=results_df[selected_metrics[0]], 
                                    name=selected_metrics[0], 
                                    marker_color='#3498db',
                                    marker_line_color='#2980b9',
                                    marker_line_width=1.5
                                ),
                                secondary_y=False,
                            )
                            
                            # Secondary metric (line chart) - complementary metric
                            fig.add_trace(
                                go.Scatter(
                                    x=results_df[x_col], 
                                    y=results_df[selected_metrics[1]], 
                                    name=selected_metrics[1], 
                                    mode='lines+markers', 
                                    marker=dict(size=8, color='#e74c3c', line=dict(width=2, color='#c0392b')),
                                    line=dict(width=3, color='#e74c3c')
                                ),
                                secondary_y=True,
                            )
                            
                            # Update axes
                            fig.update_xaxes(title_text=x_col, showgrid=True, gridcolor='rgba(128,128,128,0.2)')
                            fig.update_yaxes(title_text=selected_metrics[0], secondary_y=False, 
                                           showgrid=True, gridcolor='rgba(128,128,128,0.2)')
                            fig.update_yaxes(title_text=selected_metrics[1], secondary_y=True,
                                           showgrid=False)
                            
                            # Update layout
                            fig.update_layout(
                                title_text=f'{selected_metrics[0]} & {selected_metrics[1]} by {x_col}',
                                hovermode='x unified',
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(size=12),
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1
                                )
                            )
                        
                        st.plotly_chart(fig, width="stretch")
                    
                    # Case 3: Time series data (Date column + numeric) - DUAL-AXIS for trends
                    elif any('date' in col.lower() or 'month' in col.lower() or 'year' in col.lower() for col in categorical_cols) and len(numeric_cols) >= 1:
                        date_col = next((col for col in categorical_cols if 'date' in col.lower() or 'month' in col.lower() or 'year' in col.lower()), categorical_cols[0])
                        
                        # Prioritize metrics for time series
                        selected_metrics = prioritize_metrics(numeric_cols, priority_metrics, max_count=2)
                        
                        if len(selected_metrics) == 1:
                            # Single metric trend
                            fig = px.line(results_df, x=date_col, y=selected_metrics[0], 
                                        title=f'{selected_metrics[0]} Trend', markers=True,
                                        color_discrete_sequence=['#3498db'])
                        else:
                            # Dual-axis time series
                            from plotly.subplots import make_subplots
                            import plotly.graph_objects as go
                            
                            fig = make_subplots(specs=[[{"secondary_y": True}]])
                            
                            # Primary metric (line)
                            fig.add_trace(
                                go.Scatter(
                                    x=results_df[date_col], 
                                    y=results_df[selected_metrics[0]], 
                                    name=selected_metrics[0],
                                    mode='lines+markers',
                                    marker=dict(size=6, color='#3498db'),
                                    line=dict(width=2.5, color='#3498db')
                                ),
                                secondary_y=False,
                            )
                            
                            # Secondary metric (line)
                            fig.add_trace(
                                go.Scatter(
                                    x=results_df[date_col], 
                                    y=results_df[selected_metrics[1]], 
                                    name=selected_metrics[1],
                                    mode='lines+markers',
                                    marker=dict(size=6, color='#e74c3c'),
                                    line=dict(width=2.5, color='#e74c3c')
                                ),
                                secondary_y=True,
                            )
                            
                            # Update axes
                            fig.update_xaxes(title_text=date_col, showgrid=True, gridcolor='rgba(128,128,128,0.2)')
                            fig.update_yaxes(title_text=selected_metrics[0], secondary_y=False,
                                           showgrid=True, gridcolor='rgba(128,128,128,0.2)')
                            fig.update_yaxes(title_text=selected_metrics[1], secondary_y=True,
                                           showgrid=False)
                            
                            # Update layout
                            fig.update_layout(
                                title_text=f'{selected_metrics[0]} & {selected_metrics[1]} Trend',
                                hovermode='x unified',
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(size=12),
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1
                                )
                            )
                        
                        st.plotly_chart(fig, width="stretch")
                    
                    # Case 4: Just numeric columns (correlation heatmap or scatter)
                    elif len(numeric_cols) >= 2 and len(results_df) > 3:
                        if len(numeric_cols) == 2:
                            fig = px.scatter(results_df, x=numeric_cols[0], y=numeric_cols[1], 
                                           title=f'{numeric_cols[0]} vs {numeric_cols[1]}', trendline='ols')
                            st.plotly_chart(fig, width="stretch")
                        else:
                            # Show correlation heatmap
                            import plotly.figure_factory as ff
                            corr_matrix = results_df[numeric_cols].corr()
                            fig = ff.create_annotated_heatmap(
                                z=corr_matrix.values,
                                x=corr_matrix.columns.tolist(),
                                y=corr_matrix.columns.tolist(),
                                colorscale='RdBu',
                                showscale=True
                            )
                            fig.update_layout(title='Correlation Matrix')
                            st.plotly_chart(fig, width="stretch")
                    
                    # Case 5: Pie chart for percentage/share data
                    elif len(categorical_cols) == 1 and len(numeric_cols) == 1 and len(results_df) <= 10:
                        fig = px.pie(results_df, names=categorical_cols[0], values=numeric_cols[0], 
                                    title=f'{numeric_cols[0]} Distribution')
                        st.plotly_chart(fig, width="stretch")
                    
                    else:
                        st.info("💡 Data structure doesn't match common chart patterns. Showing table view above.")
                
            else:
                st.info("No data returned.")

            if result_data.get("answer"):
                st.markdown("### 💡 Insight Analysis")
                
                # Format the insight professionally
                insight_text = result_data["answer"]
                
                # Clean up formatting issues
                import html
                import re
                
                # Escape HTML to prevent rendering issues
                insight_text = html.escape(insight_text)
                
                # Convert markdown-style formatting to HTML
                # Bold: **text** or __text__ -> <strong>text</strong>
                insight_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', insight_text)
                insight_text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', insight_text)
                
                # Italic: *text* or _text_ -> <em>text</em> (but avoid breaking numbers)
                insight_text = re.sub(r'(?<!\w)\*([^*]+?)\*(?!\w)', r'<em>\1</em>', insight_text)
                insight_text = re.sub(r'(?<!\w)_([^_]+?)_(?!\w)', r'<em>\1</em>', insight_text)
                
                # Numbers and percentages: make them stand out
                insight_text = re.sub(r'(\d+\.?\d*%)', r'<span style="color: #60a5fa; font-weight: 600;">\1</span>', insight_text)
                insight_text = re.sub(r'(\$[\d,]+\.?\d*)', r'<span style="color: #34d399; font-weight: 600;">\1</span>', insight_text)
                
                # Numbered lists: format properly
                insight_text = re.sub(r'^(\d+)\.\s+', r'<br><strong>\1.</strong> ', insight_text, flags=re.MULTILINE)
                
                # Bullet points
                insight_text = re.sub(r'^[•\-]\s+', r'<br>• ', insight_text, flags=re.MULTILINE)
                
                # Preserve line breaks
                insight_text = insight_text.replace('\n', '<br>')
                
                # Create a professional card with scrollable content
                insight_html = f"""
                <div style='
                    background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
                    backdrop-filter: blur(16px);
                    padding: 1.75rem;
                    border-left: 4px solid #3b82f6;
                    border-radius: 12px;
                    margin: 1rem 0;
                    color: #e2e8f0;
                    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
                    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    font-size: 0.95rem;
                    line-height: 1.8;
                    letter-spacing: 0.01em;
                    max-height: 400px;
                    overflow-y: auto;
                '>
                    {insight_text}
                </div>
                """
                st.markdown(insight_html, unsafe_allow_html=True)
                
                # Add "Show More" expander for very long insights
                if len(insight_text) > 1500:
                    with st.expander("📖 View Full Analysis"):
                        st.markdown(result_data["answer"])

            col_fb1, col_fb2, col_fb3 = st.columns(3)
            if col_fb1.button("👍 Helpful"):
                st.session_state.query_tracker.add_feedback(
                    st.session_state.current_query_id,
                    feedback=1,
                )
                st.success("Thanks for your feedback!")
            if col_fb2.button("😐 Neutral"):
                st.session_state.query_tracker.add_feedback(
                    st.session_state.current_query_id,
                    feedback=0,
                )
                st.info("Feedback recorded.")
            if col_fb3.button("👎 Needs work"):
                st.session_state.query_tracker.add_feedback(
                    st.session_state.current_query_id,
                    feedback=-1,
                )
                st.warning("We'll work on improving this.")


# ---------------------------------------------------------------------------
# Query history tab
# ---------------------------------------------------------------------------
with tab_history:
    st.markdown("## 📜 Recent Queries")
    if not hasattr(st.session_state, 'query_tracker') or st.session_state.query_tracker is None:
        st.info("Query tracker not initialized. Please upload data first.")
    else:
        query_df = st.session_state.query_tracker.get_all_queries(limit=100)
        if query_df.empty:
            st.info("No queries yet. Run Q&A to populate history.")
        else:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total", len(query_df))
            col2.metric("Successful", len(query_df[query_df["error_message"].isna()]))
            col3.metric("With Feedback", len(query_df[query_df["user_feedback"].notna()]))
            col4.metric(
                "Avg Time",
                f"{query_df['execution_time_ms'].mean():.0f} ms"
                if query_df["execution_time_ms"].notna().any()
                else "N/A",
            )
            query_df["timestamp"] = pd.to_datetime(query_df["timestamp"]).dt.strftime(
                "%Y-%m-%d %H:%M"
            )
            st.dataframe(
                query_df[
                    [
                        "timestamp",
                        "original_query",
                        "selected_interpretation",
                        "execution_time_ms",
                        "result_count",
                        "user_feedback",
                    ]
                ],
                width="stretch",
            )

            st.markdown("### 🔎 Query details")
            query_ids = query_df["query_id"].tolist()
            if query_ids:
                labels = {
                    row["query_id"]: f"{row['timestamp']} • {row['original_query'][:80]}"
                    for _, row in query_df.iterrows()
                }
                selected_qid = st.selectbox(
                    "Select a query to inspect",
                    options=query_ids,
                    format_func=lambda qid: labels.get(qid, qid),
                )
                if selected_qid:
                    log = st.session_state.query_tracker.get_query_log(selected_qid)
                    if log:
                        st.markdown(f"**Original query:** {log['original_query']}")
                        st.caption(
                            f"Timestamp: {log['timestamp']} • Query ID: {log['query_id']}"
                        )
                        col_a, col_b, col_c, col_d = st.columns(4)
                        exec_ms = log.get("execution_time_ms") or 0
                        col_a.metric("Exec time", f"{exec_ms} ms")
                        col_b.metric("Rows", str(log.get("result_count") or 0))
                        sel_idx = log.get("selected_interpretation_index")
                        if sel_idx is not None:
                            col_c.metric("Selected interpretation", str(sel_idx + 1))
                        else:
                            col_c.metric("Selected interpretation", "None")
                        fb_map = {1: "👍", 0: "😐", -1: "👎"}
                        col_d.metric("Feedback", fb_map.get(log.get("user_feedback"), "—"))

                        # Parse interpretations from JSON string
                        try:
                            import json
                            interpretations = json.loads(log.get("interpretations", "[]"))
                        except:
                            interpretations = []

                        left, right = st.columns(2)
                        with left:
                            st.markdown("#### 🧠 Interpretations")
                            if interpretations:
                                for i, interp in enumerate(interpretations):
                                    label = interp.get("interpretation", "")
                                    prefix = f"{i+1}. {label}"
                                    if sel_idx is not None and i == sel_idx:
                                        prefix += " (selected)"
                                    st.markdown(f"- {prefix}")
                            else:
                                st.caption("No interpretations stored.")
                        with right:
                            st.markdown("#### 🔍 Generated SQL")
                            st.code(
                                log.get("generated_sql") or "No SQL generated",
                                language="sql",
                            )

                        if log.get("feedback_comment"):
                            st.markdown("#### 💬 User comment")
                            st.write(log["feedback_comment"])


# ---------------------------------------------------------------------------
# Metrics tab
# ---------------------------------------------------------------------------
with tab_metrics:
    st.markdown("## 📈 Q&A Performance Analytics")
    query_df = st.session_state.query_tracker.get_all_queries(limit=1000)
    if query_df.empty:
        st.info("Run a few queries to unlock analytics.")
    else:
        interp_accuracy = (
            query_df["selected_interpretation_index"].fillna(-1) == 0
        ).mean() * 100
        st.metric("First Interpretation Selected", f"{interp_accuracy:.1f}%")
        feedback_counts = query_df["user_feedback"].value_counts()
        feedback_df = pd.DataFrame(
            {
                "Feedback": ["👍", "😐", "👎"],
                "Count": [
                    feedback_counts.get(1.0, 0),
                    feedback_counts.get(0.0, 0),
                    feedback_counts.get(-1.0, 0),
                ],
            }
        ).set_index("Feedback")
        st.bar_chart(feedback_df)
        st.markdown("### 🔥 Most common queries")
        st.write(query_df["original_query"].value_counts().head(10))
        
        # Get metrics summary
        st.markdown("### 📊 Performance Summary")
        metrics = st.session_state.query_tracker.get_metrics_summary()
        col1, col2, col3 = st.columns(3)
        col1.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
        col2.metric("Avg Execution Time", f"{metrics['avg_execution_time_ms']:.0f} ms")
        col3.metric("Avg Feedback", f"{metrics['avg_feedback']:.2f}")


st.markdown("---")
st.caption("PCA Agent • Unified intelligence workspace • Built with ❤️")

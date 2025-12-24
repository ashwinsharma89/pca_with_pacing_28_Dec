"""
Configuration for PCA Agent Streamlit Applications
"""
import os
from pathlib import Path

# ============================================================================
# Paths
# ============================================================================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
TEMP_DIR = BASE_DIR / "temp"

# Create directories if they don't exist
for dir_path in [DATA_DIR, MODELS_DIR, REPORTS_DIR, TEMP_DIR]:
    dir_path.mkdir(exist_ok=True)

# ============================================================================
# API Configuration
# ============================================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ============================================================================
# Model Configuration
# ============================================================================
PREDICTOR_MODEL_PATH = MODELS_DIR / "campaign_success_predictor.pkl"
DEFAULT_MODEL_ACCURACY_THRESHOLD = 0.80

# ============================================================================
# UI Configuration
# ============================================================================
APP_TITLE = "🔮 PCA Agent - Post-Campaign Analysis & Predictive Analytics"
APP_ICON = "🔮"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# Color scheme
PRIMARY_COLOR = "#1f77b4"
SECONDARY_COLOR = "#ff7f0e"
SUCCESS_COLOR = "#2ecc71"
WARNING_COLOR = "#f39c12"
DANGER_COLOR = "#e74c3c"

# ============================================================================
# Feature Flags
# ============================================================================
ENABLE_CAMPAIGN_ANALYSIS = True
ENABLE_PREDICTIVE_ANALYTICS = True
ENABLE_NATURAL_LANGUAGE_QA = True
ENABLE_REPORTS = True
ENABLE_SETTINGS = True

# ============================================================================
# Data Configuration
# ============================================================================
SUPPORTED_PLATFORMS = [
    "Google Ads",
    "Meta Ads",
    "LinkedIn Ads",
    "Snapchat Ads",
    "DV360",
    "CM360"
]

SUPPORTED_FILE_TYPES = {
    'images': ['png', 'jpg', 'jpeg'],
    'data': ['csv', 'xlsx', 'json'],
    'reports': ['pptx', 'pdf']
}

MAX_FILE_SIZE_MB = 10

# ============================================================================
# Predictive Analytics Configuration
# ============================================================================
DEFAULT_SUCCESS_CRITERIA = {
    'roas': 3.0,
    'cpa': 75
}

OPTIMIZATION_GOALS = ['roas', 'conversions', 'awareness', 'engagement']

# ============================================================================
# Session State Keys
# ============================================================================
SESSION_KEYS = {
    'historical_data': 'historical_data',
    'predictor': 'predictor',
    'epi': 'epi',
    'optimizer': 'optimizer',
    'current_campaign': 'current_campaign',
    'analysis_results': 'analysis_results',
    'uploaded_files': 'uploaded_files'
}

# ============================================================================
# Logging Configuration
# ============================================================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# Cache Configuration
# ============================================================================
CACHE_TTL = 3600  # 1 hour in seconds
ENABLE_CACHING = True

# ============================================================================
# Help & Documentation
# ============================================================================
DOCUMENTATION_URL = "https://github.com/yourusername/pca-agent"
SUPPORT_EMAIL = "support@example.com"
VERSION = "1.0.0"

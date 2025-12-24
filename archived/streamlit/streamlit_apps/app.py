"""
PCA Agent - Unified Streamlit Dashboard
Main entry point for all PCA Agent features
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from streamlit_apps.config import APP_TITLE, APP_ICON, LAYOUT, INITIAL_SIDEBAR_STATE
from streamlit_apps.utils import apply_custom_css, init_session_state
from streamlit_apps.components import render_sidebar, render_header, render_footer

# ============================================================================
# Page Configuration
# ============================================================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)

# ============================================================================
# Initialize
# ============================================================================
apply_custom_css()
init_session_state()

# ============================================================================
# Sidebar
# ============================================================================
render_sidebar()

# ============================================================================
# Main Content
# ============================================================================
render_header(
    title="🔮 PCA Agent",
    subtitle="Post-Campaign Analysis & Predictive Analytics Platform"
)

# Welcome section
st.markdown("""
## Welcome to PCA Agent! 👋

Your comprehensive platform for **campaign analysis** and **predictive analytics**.

### 🎯 What You Can Do:

""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 📊 Campaign Analysis
    - Upload campaign screenshots
    - AI-powered data extraction
    - Automated insights
    - PowerPoint reports
    """)

with col2:
    st.markdown("""
    #### 🔮 Predictive Analytics
    - Predict campaign success
    - Early performance monitoring
    - Budget optimization
    - ML model training
    """)

with col3:
    st.markdown("""
    #### 💬 Natural Language Q&A
    - Ask questions about data
    - SQL-free analysis
    - Interactive exploration
    - Custom insights
    """)

st.markdown("---")

# Quick start guide
st.markdown("## 🚀 Quick Start")

tab1, tab2, tab3 = st.tabs(["📊 Campaign Analysis", "🔮 Predictive Analytics", "💬 Natural Language Q&A"])

with tab1:
    st.markdown("""
    ### Campaign Analysis Workflow
    
    1. **Upload Screenshots** 📸
       - Navigate to **Campaign Analysis** page
       - Upload 6 campaign dashboard screenshots
       - Supported platforms: Google Ads, Meta, LinkedIn, etc.
    
    2. **AI Analysis** 🤖
       - Vision AI extracts data from screenshots
       - Reasoning AI generates insights
       - Visualization AI creates charts
    
    3. **Get Report** 📄
       - Download PowerPoint report
       - Review insights and recommendations
       - Share with stakeholders
    
    **👉 Go to: Campaign Analysis page** (in sidebar)
    """)

with tab2:
    st.markdown("""
    ### Predictive Analytics Workflow
    
    1. **Load Data** 📁
       - Upload historical campaign data (CSV)
       - Or use sample data for testing
    
    2. **Train Model** 🎓
       - Navigate to **Predictive Analytics** page
       - Go to "Model Training" tab
       - Click "Train Model"
       - Save trained model
    
    3. **Make Predictions** 🎯
       - Go to "Campaign Success Predictor" tab
       - Enter campaign details
       - Get success probability
       - Review recommendations
    
    **👉 Go to: Predictive Analytics page** (in sidebar)
    """)

with tab3:
    st.markdown("""
    ### Natural Language Q&A Workflow
    
    1. **Load Campaign Data** 📊
       - Upload campaign performance CSV
       - Or use sample data
    
    2. **Ask Questions** 💬
       - Navigate to **Natural Language Q&A** page
       - Type your question in plain English
       - Example: "What was the average ROAS?"
    
    3. **Get Insights** 💡
       - View SQL query generated
       - See results in table format
       - Export data if needed
    
    **👉 Go to: Natural Language Q&A page** (in sidebar)
    """)

st.markdown("---")

# System status
st.markdown("## 📊 System Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.session_state.get('historical_data') is not None:
        data_count = len(st.session_state['historical_data'])
        st.metric("📁 Data Loaded", f"{data_count} campaigns", delta="Ready")
    else:
        st.metric("📁 Data Loaded", "No data", delta="Upload needed")

with col2:
    if st.session_state.get('predictor') is not None:
        predictor = st.session_state['predictor']
        if hasattr(predictor, 'model_metrics'):
            accuracy = predictor.model_metrics.get('test_accuracy', 0)
            st.metric("🤖 Model Status", f"{accuracy:.1%}", delta="Trained")
        else:
            st.metric("🤖 Model Status", "Loaded", delta="Ready")
    else:
        st.metric("🤖 Model Status", "Not loaded", delta="Train needed")

with col3:
    st.metric("🎯 Features", "3 Active", delta="All systems go")

with col4:
    st.metric("📈 Version", "1.0.0", delta="Latest")

st.markdown("---")

# Feature cards
st.markdown("## 🎨 Features Overview")

feature_col1, feature_col2 = st.columns(2)

with feature_col1:
    with st.expander("📊 Campaign Analysis - Vision AI", expanded=False):
        st.markdown("""
        **Automated Post-Campaign Analysis**
        
        - 🤖 AI-powered screenshot analysis
        - 📊 Multi-platform support (6 platforms)
        - 📈 Automated insights generation
        - 📄 PowerPoint report generation
        - 🎯 Achievement detection
        - 💡 Strategic recommendations
        
        **Platforms Supported:**
        - Google Ads
        - Meta Ads (Facebook/Instagram)
        - LinkedIn Ads
        - Snapchat Ads
        - DV360
        - CM360
        """)
    
    with st.expander("💬 Natural Language Q&A", expanded=False):
        st.markdown("""
        **Ask Questions About Your Data**
        
        - 💬 Natural language interface
        - 🔍 SQL-free data exploration
        - 📊 Interactive results
        - 📈 Custom metrics calculation
        - 🎯 Training question system
        - 💾 Export capabilities
        
        **Example Questions:**
        - "What was the average ROAS?"
        - "Which campaign had the highest conversions?"
        - "Show me campaigns with ROAS > 3"
        """)

with feature_col2:
    with st.expander("🔮 Predictive Analytics - ML Models", expanded=False):
        st.markdown("""
        **Forward-Looking Strategic Planning**
        
        - 🎯 Campaign success prediction (85% accuracy)
        - ⚡ Early performance monitoring (24h)
        - 💰 Budget allocation optimization
        - 📊 Model training & management
        - 🚨 Automated alerts
        - 📈 ROI forecasting
        
        **Key Capabilities:**
        - Pre-campaign success probability
        - In-campaign early warnings
        - Post-campaign learning
        - Budget optimization
        """)
    
    with st.expander("📈 Reports & Exports", expanded=False):
        st.markdown("""
        **Professional Reporting**
        
        - 📄 PowerPoint generation
        - 📊 Data exports (CSV, Excel)
        - 📈 Custom visualizations
        - 🎨 Branded templates
        - 📧 Email delivery (coming soon)
        - 🗓️ Scheduled reports (coming soon)
        
        **Report Types:**
        - Campaign performance
        - Predictive insights
        - Budget recommendations
        - Executive summaries
        """)

st.markdown("---")

# Next steps
st.markdown("## 🎯 Next Steps")

next_col1, next_col2, next_col3 = st.columns(3)

with next_col1:
    st.markdown("""
    ### 1️⃣ First Time Users
    
    1. Load sample data
    2. Explore features
    3. Train a model
    4. Make predictions
    5. Review documentation
    """)

with next_col2:
    st.markdown("""
    ### 2️⃣ Regular Users
    
    1. Upload your data
    2. Run analysis
    3. Get predictions
    4. Optimize budgets
    5. Generate reports
    """)

with next_col3:
    st.markdown("""
    ### 3️⃣ Advanced Users
    
    1. Retrain models
    2. Custom queries
    3. API integration
    4. Batch processing
    5. Automation setup
    """)

st.markdown("---")

# Help section
st.markdown("## 💡 Need Help?")

help_col1, help_col2 = st.columns(2)

with help_col1:
    st.markdown("""
    ### 📚 Documentation
    - [User Guide](https://github.com)
    - [API Reference](https://github.com)
    - [Video Tutorials](https://github.com)
    - [FAQ](https://github.com)
    """)

with help_col2:
    st.markdown("""
    ### 💬 Support
    - [Email Support](mailto:support@example.com)
    - [Report Bug](https://github.com)
    - [Feature Request](https://github.com)
    - [Community Forum](https://github.com)
    """)

# Footer
render_footer()

# ============================================================================
# Instructions
# ============================================================================
st.sidebar.markdown("---")
st.sidebar.info("""
**👈 Navigate using the pages in the sidebar**

- 📊 Campaign Analysis
- 🔮 Predictive Analytics  
- 💬 Natural Language Q&A
- 📈 Reports
- ⚙️ Settings
""")

"""
Campaign Analysis Page
AI-Powered Multi-Platform Campaign Analysis with Auto-Insights & Visualizations
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv
from src.utils.data_loader import normalize_campaign_dataframe

# Import shared components and utilities
from streamlit_apps.components import render_header, render_footer
from streamlit_apps.utils import apply_custom_css, init_session_state
from streamlit_apps.config import APP_TITLE

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title=f"{APP_TITLE} - Campaign Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()

# Initialize session state
init_session_state()

# Additional session state for this page
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'df' not in st.session_state:
    st.session_state.df = None

# Page header
render_header(
    title="📊 Campaign Analysis",
    subtitle="AI-Powered Multi-Platform Campaign Analysis with Auto-Insights & Visualizations"
)

# Sidebar info
with st.sidebar:
    st.markdown("### 🎯 Capabilities")
    st.markdown("""
    - 📊 **Auto-Insights**: AI-powered analysis
    - 📈 **Visualizations**: Interactive charts
    - 💬 **Q&A**: Ask anything about your data
    - 💰 **ROAS Analysis**: Revenue optimization
    - 🎯 **Funnel Analysis**: Conversion optimization
    - 👥 **Audience Insights**: Targeting recommendations
    - 🚀 **Tactical Recommendations**: Actionable steps
    """)
    
    st.markdown("---")
    st.markdown("### 🔗 Quick Navigation")
    
    # Styled navigation buttons
    st.markdown("""
    <style>
    .nav-button {
        display: block;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-decoration: underline;
        border-radius: 5px;
        text-align: center;
        font-weight: 600;
    }
    .nav-button:hover {
        opacity: 0.8;
    }
    </style>
    
    <a href="#upload-your-data" class="nav-button">📤 Upload Data</a>
    <a href="#executive-summary" class="nav-button">📊 Executive Summary</a>
    <a href="#key-performance-metrics" class="nav-button">📈 Key Metrics</a>
    <a href="#performance-visualizations" class="nav-button">📊 Visualizations</a>
    <a href="#ai-generated-insights" class="nav-button">💡 AI Insights</a>
    <a href="#strategic-recommendations" class="nav-button">🎯 Recommendations</a>
    """, unsafe_allow_html=True)
    
    
    st.markdown("---")
    st.markdown("### 📱 Supported Platforms")
    platforms = ["Google Ads", "Meta Ads", "LinkedIn Ads", "DV360", "CM360", "Snapchat Ads"]
    for platform in platforms:
        st.markdown(f"✓ {platform}")
    
    st.markdown("---")
    if st.button("🔄 Reset Analysis", use_container_width=True):
        st.session_state.analysis_complete = False
        st.session_state.analysis_data = None
        # Don't reset df to preserve data preview
        st.rerun()

# Main tabs
tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "💬 Ask Questions", "📖 Documentation"])

# ============================================================================
# TAB 1: Analytics Dashboard
# ============================================================================
with tab1:
    # Upload Section
    if not st.session_state.analysis_complete:
        st.markdown("## 📤 Upload Your Data")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            input_method = st.radio(
                "Choose Input Method",
                options=["📊 CSV Data Files", "📸 Dashboard Screenshots"],
                horizontal=True,
                help="Upload CSV for instant analysis or screenshots for vision-based extraction"
            )
        
        with col2:
            st.info("💡 **Tip**: CSV files provide instant analysis!")
        
        st.markdown("---")
        
        if input_method == "📊 CSV Data Files":
            st.markdown("### Upload Campaign Data CSV")
            
            # Download sample
            sample_csv = """Campaign_Name,Platform,Date,Impressions,Clicks,CTR,Conversions,Spend,CPC,CPA,ROAS,Reach,Frequency
Q4_Holiday_2024,google_ads,2024-10-01,1250000,25000,2.0,850,45000,1.80,52.94,4.2,980000,1.28
Q4_Holiday_2024,meta_ads,2024-10-01,980000,18500,1.89,620,32000,1.73,51.61,3.8,750000,1.31
Black_Friday_2024,google_ads,2024-11-24,2500000,50000,2.0,1800,85000,1.70,47.22,5.1,2000000,1.25"""
            
            st.download_button(
                label="📥 Download Sample CSV Template",
                data=sample_csv,
                file_name="sample_campaign_data.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            uploaded_file = st.file_uploader(
                "Upload your campaign CSV file",
                type=["csv"],
                help="Upload CSV with campaign metrics (Campaign_Name, Platform, Spend, ROAS, etc.)"
            )
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    df = normalize_campaign_dataframe(df)
                    st.session_state.df = df
                    
                    st.success(f"✅ Loaded {len(df)} rows with {len(df.columns)} columns")
                    
                    # Quick preview
                    with st.expander("📋 Data Preview", expanded=True):
                        st.dataframe(df.head(10), use_container_width=True)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Rows", len(df))
                        with col2:
                            campaigns = df['Campaign_Name'].nunique() if 'Campaign_Name' in df.columns else 0
                            st.metric("Campaigns", campaigns)
                        with col3:
                            platforms = df['Platform'].nunique() if 'Platform' in df.columns else 0
                            st.metric("Platforms", platforms)
                        with col4:
                            spend = df['Spend'].sum() if 'Spend' in df.columns else 0
                            st.metric("Total Spend", f"${spend:,.0f}")
                    
                    # Analyze button
                    st.markdown("---")
                    if st.button("🚀 **Analyze Data & Generate Insights**", type="primary", use_container_width=True):
                        with st.spinner("🤖 AI Expert analyzing your data... This may take 30-60 seconds..."):
                            try:
                                from src.analytics import MediaAnalyticsExpert
                                
                                # Check which LLM to use
                                use_anthropic = os.getenv('USE_ANTHROPIC', 'false').lower() == 'true'
                                
                                if use_anthropic:
                                    api_key = os.getenv('ANTHROPIC_API_KEY')
                                    if not api_key or api_key == 'your_anthropic_api_key_here':
                                        st.error("❌ Anthropic API key not found. Set ANTHROPIC_API_KEY in .env file.")
                                        st.info("💡 Get your key at: https://console.anthropic.com/")
                                    else:
                                        # Run analysis with Claude
                                        expert = MediaAnalyticsExpert()
                                        analysis = expert.analyze_all(df)
                                        
                                        st.session_state.analysis_data = analysis
                                        st.session_state.analysis_complete = True
                                        st.rerun()
                                else:
                                    api_key = os.getenv('OPENAI_API_KEY')
                                    if not api_key or api_key == 'your_openai_api_key_here':
                                        st.error("❌ OpenAI API key not found. Set OPENAI_API_KEY in .env file.")
                                        st.info("💡 Get your key at: https://platform.openai.com/api-keys")
                                    else:
                                        # Run analysis with OpenAI
                                        expert = MediaAnalyticsExpert()
                                        analysis = expert.analyze_all(df)
                                        
                                        st.session_state.analysis_data = analysis
                                        st.session_state.analysis_complete = True
                                        st.rerun()
                            
                            except Exception as e:
                                st.error(f"❌ Error during analysis: {str(e)}")
                                import traceback
                                with st.expander("Error Details"):
                                    st.code(traceback.format_exc())
                
                except Exception as e:
                    st.error(f"❌ Error loading CSV: {str(e)}")
        
        else:  # Screenshots
            st.markdown("### Upload Dashboard Screenshots")
            st.info("📸 **Screenshot Mode**: Upload PNG, JPG, or PDF files of your campaign dashboards")
            
            uploaded_files = st.file_uploader(
                "Choose screenshot files",
                type=["png", "jpg", "jpeg", "pdf"],
                accept_multiple_files=True,
                help="Upload dashboard screenshots from Google Ads, Meta, LinkedIn, etc."
            )
            
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} files uploaded")
                
                with st.expander("Preview Uploaded Files"):
                    cols = st.columns(3)
                    for i, file in enumerate(uploaded_files):
                        with cols[i % 3]:
                            st.image(file, caption=file.name, use_container_width=True)
                
                st.warning("⚠️ Screenshot analysis requires API backend. Use CSV mode for instant analysis.")
    
    # Analysis Results
    else:
        analysis = st.session_state.analysis_data
        df = st.session_state.df
        
        # Executive Summary
        st.markdown("## 📊 Executive Summary")
        st.info(analysis['executive_summary'])
        
        st.markdown("---")
        
        # Key Metrics
        st.markdown("## 📈 Key Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Spend",
                f"${analysis['metrics']['overview']['total_spend']:,.0f}",
                help="Total advertising spend across all campaigns"
            )
        with col2:
            st.metric(
                "Total Conversions",
                f"{analysis['metrics']['overview']['total_conversions']:,.0f}",
                help="Total conversions generated"
            )
        with col3:
            st.metric(
                "Average ROAS",
                f"{analysis['metrics']['overview']['avg_roas']:.2f}x",
                delta=f"{(analysis['metrics']['overview']['avg_roas'] - 3.0):.1f}x vs 3.0x target",
                help="Return on ad spend"
            )
        with col4:
            st.metric(
                "Average CPA",
                f"${analysis['metrics']['overview']['avg_cpa']:.2f}",
                help="Cost per acquisition"
            )
        
        st.markdown("---")
        
        # Visualizations
        st.markdown("## 📊 Performance Visualizations")
        
        viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs([
            "📈 Platform Performance",
            "🎯 Campaign Comparison",
            "💰 ROAS Analysis",
            "📉 Funnel Analysis"
        ])
        
        with viz_tab1:
            # Platform performance charts
            if 'Platform' in df.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Spend by platform
                    platform_spend = df.groupby('Platform')['Spend'].sum().reset_index()
                    fig = px.bar(
                        platform_spend,
                        x='Platform',
                        y='Spend',
                        title='Total Spend by Platform',
                        color='Spend',
                        color_continuous_scale='Blues'
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # ROAS by platform
                    platform_roas = df.groupby('Platform')['ROAS'].mean().reset_index()
                    fig = px.bar(
                        platform_roas,
                        x='Platform',
                        y='ROAS',
                        title='Average ROAS by Platform',
                        color='ROAS',
                        color_continuous_scale='Greens'
                    )
                    fig.add_hline(y=3.0, line_dash="dash", line_color="red", annotation_text="Target: 3.0x")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Platform metrics table
                st.markdown("### Platform Performance Summary")
                platform_metrics = df.groupby('Platform').agg({
                    'Spend': 'sum',
                    'Conversions': 'sum',
                    'ROAS': 'mean',
                    'CPA': 'mean',
                    'CTR': 'mean'
                }).round(2)
                st.dataframe(platform_metrics, use_container_width=True)
        
        with viz_tab2:
            # Campaign comparison
            if 'Campaign_Name' in df.columns:
                campaign_metrics = df.groupby('Campaign_Name').agg({
                    'Spend': 'sum',
                    'Conversions': 'sum',
                    'ROAS': 'mean'
                }).reset_index()
                
                # Bubble chart
                fig = px.scatter(
                    campaign_metrics,
                    x='Spend',
                    y='ROAS',
                    size='Conversions',
                    color='ROAS',
                    hover_name='Campaign_Name',
                    title='Campaign Performance: Spend vs ROAS (size = Conversions)',
                    color_continuous_scale='RdYlGn'
                )
                fig.add_hline(y=3.0, line_dash="dash", line_color="gray", annotation_text="Target ROAS")
                st.plotly_chart(fig, use_container_width=True)
                
                # Top campaigns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🏆 Top 5 Campaigns by ROAS")
                    top_roas = campaign_metrics.nlargest(5, 'ROAS')[['Campaign_Name', 'ROAS', 'Spend']]
                    st.dataframe(top_roas, use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("### 💰 Top 5 Campaigns by Spend")
                    top_spend = campaign_metrics.nlargest(5, 'Spend')[['Campaign_Name', 'Spend', 'ROAS']]
                    st.dataframe(top_spend, use_container_width=True, hide_index=True)
        
        with viz_tab3:
            # ROAS analysis
            if analysis.get('roas_analysis'):
                roas_data = analysis['roas_analysis']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 💰 Revenue & Profit")
                    st.metric("Total Revenue", f"${roas_data['overall']['implied_revenue']:,.0f}")
                    st.metric("Total Profit", f"${roas_data['overall']['profit']:,.0f}")
                    st.metric("Profit Margin", f"{roas_data['overall']['profit_margin']:.1f}%")
                
                with col2:
                    # ROAS distribution
                    if 'ROAS' in df.columns:
                        fig = px.histogram(
                            df,
                            x='ROAS',
                            nbins=20,
                            title='ROAS Distribution',
                            color_discrete_sequence=['#667eea']
                        )
                        fig.add_vline(x=3.0, line_dash="dash", line_color="red", annotation_text="Target")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Efficiency tiers
                if roas_data.get('efficiency_tiers'):
                    st.markdown("### 🎯 Performance Tiers")
                    tiers = roas_data['efficiency_tiers']
                    
                    tier_df = pd.DataFrame({
                        'Tier': ['Excellent (4.5x+)', 'Good (3.5-4.5x)', 'Needs Improvement (<3.5x)'],
                        'Count': [tiers['excellent']['count'], tiers['good']['count'], tiers['needs_improvement']['count']],
                        'Spend': [tiers['excellent']['spend'], tiers['good']['spend'], tiers['needs_improvement']['spend']]
                    })
                    
                    fig = px.bar(
                        tier_df,
                        x='Tier',
                        y='Spend',
                        color='Tier',
                        title='Spend Distribution by Performance Tier',
                        color_discrete_map={
                            'Excellent (4.5x+)': '#10b981',
                            'Good (3.5-4.5x)': '#f59e0b',
                            'Needs Improvement (<3.5x)': '#ef4444'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with viz_tab4:
            # Funnel analysis
            if analysis.get('funnel_analysis') and analysis['funnel_analysis'].get('stages'):
                funnel_data = analysis['funnel_analysis']
                
                # Show funnel stage performance if detected
                if funnel_data.get('by_funnel_stage'):
                    st.markdown("### 🎯 Funnel Stage Performance")
                    st.info("💡 Funnel stages detected from campaign/placement names")
                    
                    funnel_stages_data = funnel_data['by_funnel_stage']
                    
                    # Create metrics for each stage
                    stage_cols = st.columns(len(funnel_stages_data))
                    for idx, (stage, data) in enumerate(funnel_stages_data.items()):
                        with stage_cols[idx]:
                            st.markdown(f"**{stage}**")
                            st.metric("Spend", f"${data['spend']:,.0f}")
                            st.metric("ROAS", f"{data['roas']:.2f}x")
                            st.metric("CTR", f"{data['ctr']:.2f}%")
                            st.metric("Conv Rate", f"{data['conversion_rate']:.2f}%")
                    
                    # Funnel stage comparison chart
                    st.markdown("---")
                    funnel_stage_df = pd.DataFrame([
                        {"Stage": stage, "Spend": data['spend'], "ROAS": data['roas'], 
                         "Conversions": data['conversions'], "CTR": data['ctr']}
                        for stage, data in funnel_stages_data.items()
                    ])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig = px.bar(
                            funnel_stage_df,
                            x='Stage',
                            y='Spend',
                            title='Spend by Funnel Stage',
                            color='ROAS',
                            color_continuous_scale='RdYlGn'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = px.bar(
                            funnel_stage_df,
                            x='Stage',
                            y='Conversions',
                            title='Conversions by Funnel Stage',
                            color='Stage',
                            color_discrete_map={
                                'Awareness': '#667eea',
                                'Consideration': '#764ba2',
                                'Conversion': '#f093fb'
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("---")
                
                # Overall funnel visualization
                st.markdown("### 📊 Overall Marketing Funnel")
                stages = funnel_data['stages']
                funnel_df = pd.DataFrame({
                    'Stage': ['Awareness', 'Consideration', 'Conversion'],
                    'Value': [
                        stages['awareness']['value'],
                        stages['consideration']['value'],
                        stages['conversion']['value']
                    ],
                    'Percentage': [
                        stages['awareness']['percentage'],
                        stages['consideration']['percentage'],
                        stages['conversion']['percentage']
                    ]
                })
                
                fig = go.Figure(go.Funnel(
                    y=funnel_df['Stage'],
                    x=funnel_df['Value'],
                    textinfo="value+percent initial",
                    marker=dict(color=['#667eea', '#764ba2', '#f093fb'])
                ))
                fig.update_layout(title='Marketing Funnel Performance')
                st.plotly_chart(fig, use_container_width=True)
                
                # Conversion rates
                st.markdown("### 📊 Conversion Rates")
                col1, col2, col3 = st.columns(3)
                
                conv_rates = funnel_data['conversion_rates']
                with col1:
                    st.metric("Awareness → Consideration", f"{conv_rates['awareness_to_consideration']:.2f}%")
                with col2:
                    st.metric("Consideration → Conversion", f"{conv_rates['consideration_to_conversion']:.2f}%")
                with col3:
                    st.metric("Overall Conversion", f"{conv_rates['awareness_to_conversion']:.2f}%")
                
                # Drop-off points
                if funnel_data.get('drop_off_points'):
                    st.markdown("### ⚠️ Drop-off Points")
                    for drop_off in funnel_data['drop_off_points']:
                        st.warning(f"**{drop_off['stage']}**: {drop_off['issue']}")
                        st.info(f"💡 {drop_off['recommendation']}")
        
        st.markdown("---")
        
        # AI Insights
        st.markdown("## 💡 AI-Generated Insights")
        
        insight_cols = st.columns(2)
        for i, insight in enumerate(analysis['insights']):
            with insight_cols[i % 2]:
                impact_emoji = "🔴" if insight['impact'] == "High" else "🟡" if insight['impact'] == "Medium" else "🟢"
                with st.expander(f"{impact_emoji} {insight['category']}: {insight['insight'][:50]}..."):
                    st.markdown(f"**{insight['insight']}**")
                    st.write(insight['explanation'])
                    st.caption(f"Impact: {insight['impact']}")
        
        st.markdown("---")
        
        # Opportunities
        if analysis.get('opportunities'):
            st.markdown("## 🚀 Opportunities")
            
            for i, opp in enumerate(analysis['opportunities'], 1):
                with st.expander(f"💰 #{i}: {opp.get('type', 'Opportunity')}", expanded=i<=3):
                    if 'details' in opp:
                        st.markdown(f"**Details:** {opp['details']}")
                    if 'why_it_matters' in opp:
                        st.markdown(f"**Why it matters:** {opp['why_it_matters']}")
                    if 'recommended_action' in opp:
                        st.markdown(f"**Recommended action:** {opp['recommended_action']}")
                    if 'expected_impact' in opp:
                        st.markdown(f"**Expected impact:** {opp['expected_impact']}")
                    if 'current_metrics' in opp:
                        st.caption(f"Current metrics: {opp['current_metrics']}")
                    if 'campaigns' in opp:
                        st.markdown(f"**Campaigns to scale:** {', '.join(opp['campaigns'])}")
                    
                    # Display other fields if available
                    for key, value in opp.items():
                        if key not in ['type', 'details', 'why_it_matters', 'recommended_action', 'expected_impact', 'current_metrics', 'campaigns']:
                            if isinstance(value, (int, float)):
                                st.metric(key.replace('_', ' ').title(), f"{value:,.2f}" if isinstance(value, float) else f"{value:,}")
                            elif isinstance(value, str) and len(value) < 200:
                                st.caption(f"{key.replace('_', ' ').title()}: {value}")
        
        st.markdown("---")
        
        # Risks
        if analysis.get('risks'):
            st.markdown("## ⚠️ Risks & Red Flags")
            
            for i, risk in enumerate(analysis['risks'], 1):
                severity_emoji = "🔴" if risk.get('severity') == "High" else "🟠" if risk.get('severity') == "Medium" else "🟡"
                with st.expander(f"{severity_emoji} #{i}: {risk.get('risk', 'Risk')}", expanded=i<=3):
                    st.markdown(f"**Severity:** {risk.get('severity', 'Unknown')}")
                    if 'details' in risk:
                        st.markdown(f"**Details:** {risk['details']}")
                    if 'impact' in risk:
                        st.markdown(f"**Impact:** {risk['impact']}")
                    if 'worst_performers' in risk:
                        st.markdown(f"**Worst performers:** {risk['worst_performers']}")
                    if 'action' in risk:
                        st.markdown(f"**Action required:** {risk['action']}")
        
        st.markdown("---")
        
        # Recommendations
        st.markdown("## 🎯 Strategic Recommendations")
        
        for i, rec in enumerate(analysis['recommendations'], 1):
            priority_color = "🔴" if rec['priority'] == "Critical" else "🟠" if rec['priority'] == "High" else "🟡"
            
            with st.expander(f"{priority_color} #{i}: {rec['recommendation'][:60]}...", expanded=i<=3):
                st.markdown(f"### {rec['recommendation']}")
                st.markdown(f"**Expected Impact:** {rec['expected_impact']}")
                st.markdown(f"**Implementation:** {rec['implementation']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Priority", rec['priority'])
                with col2:
                    st.metric("Timeline", rec['timeline'])
                with col3:
                    st.metric("Estimated ROI", rec['estimated_roi'])
        
        st.markdown("---")
        
        # Download report
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            # Convert Period objects in dictionary keys to strings
            def convert_periods(obj):
                """Recursively convert Period objects to strings in nested structures"""
                if isinstance(obj, dict):
                    return {str(k): convert_periods(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_periods(item) for item in obj]
                elif hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                elif hasattr(obj, '__str__') and type(obj).__name__ == 'Period':
                    return str(obj)
                else:
                    return obj
            
            # Convert the analysis data
            analysis_clean = convert_periods(analysis)
            
            # Custom JSON serializer for remaining objects
            def json_serializer(obj):
                """Custom JSON serializer for objects not serializable by default"""
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                elif hasattr(obj, '__str__'):
                    return str(obj)
                return obj
            
            report_json = json.dumps(analysis_clean, indent=2, default=json_serializer)
            st.download_button(
                label="📥 Download Full Analysis Report (JSON)",
                data=report_json,
                file_name=f"campaign_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

# ============================================================================
# TAB 2: Ask Questions
# ============================================================================
with tab2:
    st.markdown("## 💬 Ask Questions About Your Data")
    
    if st.session_state.df is not None:
        df = st.session_state.df
        
        # Query mode
        query_mode = st.radio(
            "Choose query mode:",
            options=["🤖 Natural Language (AI-powered)", "📝 Direct SQL Query"],
            horizontal=True
        )
        
        if query_mode == "🤖 Natural Language (AI-powered)":
            st.markdown("**Ask any question about your data in plain English:**")
            
            # Suggested questions
            with st.expander("💡 Suggested Questions"):
                suggested = [
                    "Which campaign had the highest ROAS?",
                    "What is the total spend across all campaigns?",
                    "Show me the top 5 campaigns by conversions",
                    "Which platform performs best on average?",
                    "Compare spend between google_ads and meta_ads"
                ]
                
                for q in suggested:
                    if st.button(q, key=f"suggested_{q}", use_container_width=True):
                        st.session_state.current_question = q
            
            question = st.text_input(
                "Your question:",
                value=st.session_state.get('current_question', ''),
                placeholder="e.g., Which campaign had the best ROAS?"
            )
            
            if st.button("🔍 Get Answer", type="primary"):
                if question:
                    with st.spinner("🤔 Thinking..."):
                        try:
                            from src.query_engine import NaturalLanguageQueryEngine
                            
                            api_key = os.getenv('OPENAI_API_KEY')
                            if api_key:
                                engine = NaturalLanguageQueryEngine(api_key)
                                engine.load_data(df)
                                result = engine.ask(question)
                                
                                if result['success']:
                                    st.success("✅ Answer:")
                                    st.markdown(f"### {result['answer']}")
                                    
                                    with st.expander("🔧 Generated SQL Query"):
                                        st.code(result['sql_query'], language="sql")
                                    
                                    with st.expander("📊 Detailed Results"):
                                        st.dataframe(result['results'], use_container_width=True)
                                else:
                                    st.error(f"❌ Error: {result['error']}")
                            else:
                                st.warning("⚠️ OpenAI API key not found.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        
        else:
            st.markdown("**Write your SQL query:**")
            st.info("💡 Table name: `campaigns`")
            
            sql_query = st.text_area(
                "SQL Query:",
                height=150,
                placeholder="SELECT * FROM campaigns WHERE ROAS > 4.0 ORDER BY ROAS DESC LIMIT 10"
            )
            
            if st.button("▶️ Execute Query", type="primary"):
                if sql_query:
                    try:
                        import duckdb
                        conn = duckdb.connect(':memory:')
                        conn.register('campaigns', df)
                        result_df = conn.execute(sql_query).fetchdf()
                        conn.close()
                        
                        st.success(f"✅ Query executed! Returned {len(result_df)} rows.")
                        st.dataframe(result_df, use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ SQL Error: {e}")
    else:
        st.info("👆 Upload data in the Analytics Dashboard tab first!")

# ============================================================================
# TAB 3: Documentation
# ============================================================================
with tab3:
    st.markdown("## 📖 Documentation")
    
    st.markdown("""
    ### How to Use Campaign Analysis
    
    #### 1. Upload Your Data
    - **CSV Mode** (Recommended): Upload campaign data CSV for instant analysis
    - **Screenshot Mode**: Upload dashboard screenshots for vision-based extraction
    
    #### 2. Automatic Analysis
    - Click "Analyze Data & Generate Insights"
    - AI expert analyzes all campaigns
    - Generates insights, recommendations, and visualizations
    
    #### 3. Explore Results
    - **Executive Summary**: High-level overview
    - **Key Metrics**: Performance dashboard
    - **Visualizations**: Interactive charts
    - **AI Insights**: Data-driven insights
    - **Recommendations**: Actionable steps
    
    #### 4. Ask Questions
    - Use natural language or SQL
    - Get instant answers
    - Download results
    
    ### CSV Format
    
    Required columns:
    - `Campaign_Name`: Campaign identifier
    - `Platform`: google_ads, meta_ads, linkedin_ads, etc.
    - `Spend`: Total spend
    - `Conversions`: Total conversions
    - `ROAS`: Return on ad spend
    
    Optional columns:
    - `Date`, `Impressions`, `Clicks`, `CTR`, `CPA`, `CPC`, `CPM`, `Reach`, `Frequency`
    
    ### Supported Platforms
    - Google Ads
    - Meta Ads (Facebook/Instagram)
    - LinkedIn Ads
    - Display & Video 360 (DV360)
    - Campaign Manager 360 (CM360)
    - Snapchat Ads
    
    ### AI Capabilities
    - **Funnel Analysis**: Awareness → Consideration → Conversion
    - **ROAS Optimization**: Revenue and profit analysis
    - **Audience Insights**: Targeting recommendations
    - **Tactical Recommendations**: Bidding, creative, placement strategies
    - **Budget Optimization**: Reallocation recommendations
    - **Risk Assessment**: Identify underperformers
    
    ### Support
    For questions or issues, refer to the documentation in `docs/` folder.
    """)

# Footer
render_footer()

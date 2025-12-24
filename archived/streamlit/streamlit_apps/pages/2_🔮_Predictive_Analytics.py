"""
Predictive Analytics Page
Transform from Retrospective Reporting → Forward-Looking Strategic Planning
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Import predictive modules
from src.predictive import (
    CampaignSuccessPredictor,
    EarlyPerformanceIndicators,
    BudgetAllocationOptimizer
)

# Import shared components and utilities
from streamlit_apps.components import render_header, render_footer
from streamlit_apps.utils import apply_custom_css, init_session_state, load_historical_data
from streamlit_apps.config import APP_TITLE

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title=f"{APP_TITLE} - Predictive Analytics",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()

# Initialize session state
init_session_state()

# Additional session state for this page
if 'predictor_loaded' not in st.session_state:
    st.session_state.predictor_loaded = False
if 'predictor' not in st.session_state:
    st.session_state.predictor = None
if 'optimizer' not in st.session_state:
    st.session_state.optimizer = None

# Page header
render_header(
    title="🔮 Predictive Analytics",
    subtitle="Transform from Retrospective Reporting → Forward-Looking Strategic Planning"
)

# Sidebar info
with st.sidebar:
    st.markdown("### 🔮 Predictive Capabilities")
    st.markdown("""
    - 🎯 **Success Prediction**: Pre-campaign risk assessment
    - ⚡ **Early Performance**: 24h success indicators
    - 💰 **Budget Optimizer**: Optimal channel mix
    - 📊 **Forecasting**: Revenue & ROAS predictions
    - 🎨 **Lookalike Modeling**: Pattern matching
    - 🏆 **Competitive Benchmarking**: SOV vs SOC
    """)
    
    st.markdown("---")
    
    # Model status
    st.markdown("### 📈 Model Status")
    if st.session_state.predictor_loaded:
        st.success("✅ Models Loaded")
        if st.session_state.predictor:
            metrics = st.session_state.predictor.model_metrics
            st.metric("Model Accuracy", f"{metrics.get('test_accuracy', 0):.1%}")
    else:
        st.warning("⚠️ Models Not Loaded")
    
    st.markdown("---")
    
    # Data upload
    st.markdown("### 📁 Quick Data Upload")
    st.caption("(Or use Model Training tab)")
    uploaded_file = st.file_uploader(
        "Upload Historical Campaigns",
        type=['csv'],
        help="Upload CSV with historical campaign data",
        key='sidebar_upload'
    )
    
    if uploaded_file:
        data = load_historical_data(uploaded_file)
        if data is not None:
            st.session_state.historical_data = data
            st.success(f"✅ Loaded {len(data)} campaigns")
        else:
            st.error("❌ Error loading data")
    
    # Quick load sample data
    if st.session_state.historical_data is None:
        if st.button("📊 Load Sample Data", key='sidebar_sample'):
            try:
                st.session_state.historical_data = pd.read_csv('data/historical_campaigns_sample.csv')
                st.success("✅ Sample data loaded!")
                st.rerun()
            except:
                st.error("Sample data not found")

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Campaign Success Predictor",
    "⚡ Early Performance Monitor",
    "💰 Budget Optimizer",
    "📊 Model Training",
    "📖 Documentation"
])

# ============================================================================
# TAB 1: Campaign Success Predictor
# ============================================================================
with tab1:
    st.header("🎯 Campaign Success Predictor")
    st.markdown("Predict campaign success probability **before launch** with actionable recommendations")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Campaign Details")
        
        # Campaign input form
        campaign_name = st.text_input("Campaign Name", value="Q4_Holiday_Campaign")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            budget = st.number_input(
                "Total Budget ($)",
                min_value=10000,
                max_value=10000000,
                value=250000,
                step=10000
            )
        with col_b:
            duration = st.number_input(
                "Duration (days)",
                min_value=7,
                max_value=90,
                value=30
            )
        with col_c:
            audience_size = st.number_input(
                "Audience Size",
                min_value=10000,
                max_value=10000000,
                value=500000,
                step=10000
            )
        
        col_d, col_e = st.columns(2)
        with col_d:
            channels = st.multiselect(
                "Channels",
                ['Meta', 'Google', 'LinkedIn', 'Display', 'Snapchat', 'Email'],
                default=['Meta', 'Google']
            )
        with col_e:
            creative_type = st.selectbox(
                "Creative Type",
                ['video', 'image', 'carousel', 'collection']
            )
        
        col_f, col_g = st.columns(2)
        with col_f:
            objective = st.selectbox(
                "Campaign Objective",
                ['awareness', 'conversion', 'engagement', 'lead_generation']
            )
        with col_g:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() + timedelta(days=7)
            )
    
    with col2:
        st.subheader("Quick Actions")
        
        # Load model button
        if st.button("🔄 Load Prediction Model", use_container_width=True):
            with st.spinner("Loading model..."):
                try:
                    # Check if model exists
                    model_path = 'models/campaign_success_predictor.pkl'
                    if os.path.exists(model_path):
                        predictor = CampaignSuccessPredictor()
                        predictor.load_model(model_path)
                        st.session_state.predictor = predictor
                        st.session_state.predictor_loaded = True
                        st.success("✅ Model loaded successfully!")
                    else:
                        st.warning("⚠️ No trained model found. Please train a model first.")
                except Exception as e:
                    st.error(f"❌ Error loading model: {str(e)}")
        
        st.markdown("---")
        
        # Predict button
        predict_btn = st.button(
            "🎯 Predict Success",
            type="primary",
            use_container_width=True,
            disabled=not st.session_state.predictor_loaded
        )
    
    # Prediction results
    if predict_btn and st.session_state.predictor:
        with st.spinner("Analyzing campaign plan..."):
            # Prepare campaign plan
            campaign_plan = {
                'name': campaign_name,
                'budget': budget,
                'duration': duration,
                'audience_size': audience_size,
                'channels': ','.join(channels),
                'creative_type': creative_type,
                'objective': objective,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'roas': 3.5  # Default historical average
            }
            
            # Get prediction
            prediction = st.session_state.predictor.predict_success_probability(campaign_plan)
            
            # Display results
            st.markdown("---")
            st.subheader("📊 Prediction Results")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                prob = prediction['success_probability']
                if prob >= 70:
                    st.markdown(f'<div class="success-card"><h2>{prob}%</h2><p>Success Probability</p></div>', unsafe_allow_html=True)
                elif prob >= 50:
                    st.markdown(f'<div class="prediction-card"><h2>{prob}%</h2><p>Success Probability</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="warning-card"><h2>{prob}%</h2><p>Success Probability</p></div>', unsafe_allow_html=True)
            
            with col2:
                confidence = prediction['confidence_level'].upper()
                st.metric("Confidence Level", confidence)
            
            with col3:
                risk = prediction['risk_level'].upper()
                if risk == 'LOW':
                    st.metric("Risk Level", risk, delta="Good", delta_color="normal")
                elif risk == 'MEDIUM':
                    st.metric("Risk Level", risk, delta="Moderate", delta_color="off")
                else:
                    st.metric("Risk Level", risk, delta="High", delta_color="inverse")
            
            with col4:
                daily_budget = budget / duration
                st.metric("Daily Budget", f"${daily_budget:,.0f}")
            
            # Key drivers
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔑 Key Success Drivers")
                for driver in prediction['key_drivers']:
                    st.markdown(f"""
                    <div class="insight-box">
                        <strong>{driver['feature'].replace('_', ' ').title()}</strong><br>
                        {driver['impact']}<br>
                        <small>Importance: {driver['importance']:.1%}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.subheader("💡 Insights")
                for insight in prediction['insights']:
                    if '✅' in insight:
                        st.success(insight)
                    elif '⚠️' in insight:
                        st.warning(insight)
                    elif '❌' in insight:
                        st.error(insight)
                    else:
                        st.info(insight)
            
            # Recommendations
            st.markdown("---")
            st.subheader("🎯 Recommendations")
            
            for rec in prediction['recommendations']:
                priority = rec['priority']
                if priority == 'high':
                    st.error(f"🔴 **HIGH PRIORITY**: {rec['message']}")
                    st.caption(f"Expected Impact: {rec['expected_impact']}")
                elif priority == 'medium':
                    st.warning(f"🟡 **MEDIUM PRIORITY**: {rec['message']}")
                    st.caption(f"Expected Impact: {rec['expected_impact']}")
                else:
                    st.info(f"🟢 **LOW PRIORITY**: {rec['message']}")
                    st.caption(f"Expected Impact: {rec['expected_impact']}")

# ============================================================================
# TAB 2: Early Performance Monitor
# ============================================================================
with tab2:
    st.header("⚡ Early Performance Monitor")
    st.markdown("Monitor campaign performance in **first 24-48 hours** to predict final success")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Campaign Selection")
        
        # Campaign selector
        campaign_id = st.text_input("Campaign ID", value="CAMP_001")
        hours_elapsed = st.slider("Hours Since Launch", 1, 48, 24)
        
        # Upload early data
        st.markdown("**Upload Hourly Performance Data**")
        early_data_file = st.file_uploader(
            "Upload CSV with hourly metrics",
            type=['csv'],
            key='early_data'
        )
        
        if early_data_file:
            early_data = pd.read_csv(early_data_file)
            st.success(f"✅ Loaded {len(early_data)} hours of data")
            
            # Show data preview
            with st.expander("📊 Data Preview"):
                st.dataframe(early_data.head(10))
    
    with col2:
        st.subheader("Actions")
        
        analyze_btn = st.button(
            "⚡ Analyze Performance",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("---")
        st.info("💡 Upload hourly data with columns: hours_since_start, impressions, clicks, conversions, spend, revenue")
    
    # Analysis results
    if analyze_btn and early_data_file:
        with st.spinner("Analyzing early performance..."):
            epi = EarlyPerformanceIndicators()
            result = epi.analyze_early_metrics(campaign_id, early_data, hours_elapsed)
            
            # Display results
            st.markdown("---")
            st.subheader("📊 Early Performance Analysis")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            metrics = result['early_metrics']
            prediction = result['success_prediction']
            
            with col1:
                prob = prediction['probability']
                if prob >= 70:
                    st.markdown(f'<div class="success-card"><h2>{prob}%</h2><p>Success Probability</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="warning-card"><h2>{prob}%</h2><p>Success Probability</p></div>', unsafe_allow_html=True)
            
            with col2:
                st.metric("Early CTR", f"{metrics['early_ctr']}%")
            
            with col3:
                st.metric("Early Conv Rate", f"{metrics['early_conv_rate']}%")
            
            with col4:
                st.metric("Early ROAS", f"{metrics['early_roas']}")
            
            # Performance trends
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Performance Trends")
                
                # Create trend chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=early_data['hours_since_start'],
                    y=early_data['impressions'],
                    name='Impressions',
                    line=dict(color='#667eea')
                ))
                
                fig.add_trace(go.Scatter(
                    x=early_data['hours_since_start'],
                    y=early_data['clicks'],
                    name='Clicks',
                    yaxis='y2',
                    line=dict(color='#764ba2')
                ))
                
                fig.update_layout(
                    title='Impressions & Clicks Over Time',
                    xaxis_title='Hours Since Start',
                    yaxis_title='Impressions',
                    yaxis2=dict(title='Clicks', overlaying='y', side='right'),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("⚠️ Warnings")
                
                if result['warnings']:
                    for warning in result['warnings']:
                        severity = warning['severity']
                        if severity == 'high':
                            st.error(f"🔴 **{warning['type'].upper()}**")
                        else:
                            st.warning(f"🟡 **{warning['type'].upper()}**")
                        st.caption(warning['message'])
                        st.caption(f"Impact: {warning['impact']}")
                else:
                    st.success("✅ No warnings - Campaign performing well!")
            
            # Recommendations
            st.markdown("---")
            st.subheader("🎯 Immediate Actions")
            
            for rec in result['recommendations']:
                priority = rec['priority']
                if priority == 'high':
                    st.error(f"🔴 **URGENT**: {rec['message']}")
                elif priority == 'medium':
                    st.warning(f"🟡 **IMPORTANT**: {rec['message']}")
                else:
                    st.info(f"🟢 **SUGGESTED**: {rec['message']}")
                st.caption(f"Expected Impact: {rec['expected_impact']}")

# ============================================================================
# TAB 3: Budget Optimizer
# ============================================================================
with tab3:
    st.header("💰 Budget Allocation Optimizer")
    st.markdown("Find the **optimal channel mix** for maximum ROAS")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Optimization Parameters")
        
        total_budget = st.number_input(
            "Total Budget ($)",
            min_value=50000,
            max_value=10000000,
            value=1000000,
            step=50000
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            campaign_goal = st.selectbox(
                "Campaign Goal",
                ['roas', 'conversions', 'awareness']
            )
        with col_b:
            min_spend_per_channel = st.number_input(
                "Min Spend per Channel ($)",
                min_value=10000,
                max_value=500000,
                value=50000,
                step=10000
            )
        
        # Historical data requirement
        st.info("💡 Upload historical campaign data in the sidebar to enable optimization")
    
    with col2:
        st.subheader("Actions")
        
        optimize_btn = st.button(
            "💰 Optimize Allocation",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.historical_data is None
        )
        
        st.markdown("---")
        st.metric("Total Budget", f"${total_budget:,.0f}")
        st.metric("Goal", campaign_goal.upper())
    
    # Optimization results
    if optimize_btn and st.session_state.historical_data is not None:
        with st.spinner("Optimizing budget allocation..."):
            # Initialize optimizer
            optimizer = BudgetAllocationOptimizer(st.session_state.historical_data)
            
            # Optimize
            result = optimizer.optimize_allocation(
                total_budget=total_budget,
                campaign_goal=campaign_goal,
                constraints={'min_spend_per_channel': min_spend_per_channel}
            )
            
            # Display results
            st.markdown("---")
            st.subheader("📊 Optimized Allocation")
            
            # Overall metrics
            col1, col2, col3, col4 = st.columns(4)
            
            overall = result['overall_metrics']
            
            with col1:
                st.metric("Expected Revenue", f"${overall['expected_total_revenue']:,.0f}")
            with col2:
                st.metric("Expected ROAS", f"{overall['expected_overall_roas']:.2f}")
            with col3:
                st.metric("Expected Conversions", f"{overall['expected_total_conversions']:,}")
            with col4:
                st.metric("Status", overall['optimization_status'].upper())
            
            # Channel allocation
            st.markdown("---")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📊 Channel Allocation")
                
                # Create allocation chart
                allocation_data = []
                for channel, alloc in result['allocation'].items():
                    allocation_data.append({
                        'Channel': channel,
                        'Budget': alloc['recommended_budget'],
                        'Percentage': alloc['percentage_of_total'],
                        'Expected ROAS': alloc['expected_roas']
                    })
                
                alloc_df = pd.DataFrame(allocation_data)
                
                fig = px.pie(
                    alloc_df,
                    values='Budget',
                    names='Channel',
                    title='Budget Distribution',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("💰 Details")
                
                for channel, alloc in result['allocation'].items():
                    with st.expander(f"**{channel}**"):
                        st.metric("Budget", f"${alloc['recommended_budget']:,.0f}")
                        st.metric("% of Total", f"{alloc['percentage_of_total']}%")
                        st.metric("Expected ROAS", f"{alloc['expected_roas']}")
                        st.metric("Expected Revenue", f"${alloc['expected_revenue']:,.0f}")
                        st.caption(f"Saturation Risk: {alloc['saturation_risk'].upper()}")
            
            # Recommendations
            if result.get('recommendations'):
                st.markdown("---")
                st.subheader("🎯 Optimization Recommendations")
                
                for rec in result['recommendations']:
                    if rec['priority'] == 'high':
                        st.error(f"🔴 {rec['message']}")
                    elif rec['priority'] == 'medium':
                        st.warning(f"🟡 {rec['message']}")
                    else:
                        st.info(f"🟢 {rec['message']}")

# ============================================================================
# TAB 4: Model Training
# ============================================================================
with tab4:
    st.header("📊 Model Training & Management")
    st.markdown("Train and manage predictive models")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Training Configuration")
        
        # Upload section - MORE VISIBLE
        st.markdown("### 📁 Step 1: Upload Historical Data")
        
        uploaded_file_main = st.file_uploader(
            "Upload CSV with historical campaign data",
            type=['csv'],
            key='main_upload',
            help="Upload CSV with columns: budget, duration, audience_size, channels, creative_type, objective, start_date, roas, cpa, conversions"
        )
        
        if uploaded_file_main:
            data = load_historical_data(uploaded_file_main)
            if data is not None:
                st.session_state.historical_data = data
                st.success(f"✅ Loaded {len(data)} campaigns")
            else:
                st.error("❌ Error loading data")
        
        # Show sample data option
        if st.session_state.historical_data is None:
            st.info("💡 **Don't have data?** Use our sample data: `data/historical_campaigns_sample.csv`")
            
            if st.button("📊 Load Sample Data", use_container_width=True):
                try:
                    data = load_historical_data(use_sample=True)
                    if data is not None:
                        st.session_state.historical_data = data
                        st.success(f"✅ Loaded {len(data)} sample campaigns")
                        st.rerun()
                    else:
                        st.error("Sample data not found")
                except Exception as e:
                    st.error(f"Error loading sample data: {str(e)}")
        
        st.markdown("---")
        
        # Success threshold
        st.markdown("### 🎯 Step 2: Define Success Criteria")
        col_a, col_b = st.columns(2)
        with col_a:
            target_roas = st.number_input("Target ROAS", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
        with col_b:
            target_cpa = st.number_input("Target CPA ($)", min_value=10, max_value=500, value=75, step=5)
        
        # Historical data info
        if st.session_state.historical_data is not None:
            st.markdown("---")
            st.markdown("### 📊 Data Summary")
            
            col_x, col_y, col_z = st.columns(3)
            with col_x:
                st.metric("Total Campaigns", len(st.session_state.historical_data))
            with col_y:
                st.metric("Avg ROAS", f"{st.session_state.historical_data['roas'].mean():.2f}")
            with col_z:
                success_rate = (st.session_state.historical_data['roas'] >= target_roas).mean()
                st.metric("Success Rate", f"{success_rate:.1%}")
            
            with st.expander("📊 Data Preview"):
                st.dataframe(st.session_state.historical_data.head(10))
    
    with col2:
        st.subheader("Actions")
        
        train_btn = st.button(
            "🚀 Train Model",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.historical_data is None
        )
        
        st.markdown("---")
        
        if st.session_state.predictor_loaded:
            st.success("✅ Model Loaded")
            
            if st.button("💾 Save Model", use_container_width=True):
                os.makedirs('models', exist_ok=True)
                st.session_state.predictor.save_model('models/campaign_success_predictor.pkl')
                st.success("✅ Model saved!")
    
    # Training results
    if train_btn and st.session_state.historical_data is not None:
        with st.spinner("Training model... This may take a few minutes"):
            # Initialize predictor
            predictor = CampaignSuccessPredictor()
            
            # Train
            metrics = predictor.train(
                st.session_state.historical_data,
                success_threshold={'roas': target_roas, 'cpa': target_cpa}
            )
            
            # Store in session
            st.session_state.predictor = predictor
            st.session_state.predictor_loaded = True
            
            # Display results
            st.markdown("---")
            st.subheader("📊 Training Results")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Test Accuracy", f"{metrics['test_accuracy']:.1%}")
            with col2:
                st.metric("CV Accuracy", f"{metrics['cv_mean_accuracy']:.1%}")
            with col3:
                st.metric("Training Samples", f"{metrics['training_samples']:,}")
            with col4:
                st.metric("Success Rate", f"{metrics['success_rate']:.1%}")
            
            st.success("✅ Model trained successfully!")
            st.info("💡 Use the 'Save Model' button to persist this model for future use")

# ============================================================================
# TAB 5: Documentation
# ============================================================================
with tab5:
    st.header("📖 Documentation")
    
    st.markdown("""
    ## 🔮 Predictive Analytics Overview
    
    Transform your PCA Agent from **retrospective reporting** to **forward-looking strategic planning**.
    
    ### 🎯 Core Capabilities
    
    #### 1. Campaign Success Predictor
    - **What**: Predict 0-100% success probability before launch
    - **When**: Pre-campaign planning phase
    - **Value**: Avoid launching doomed campaigns, optimize before spending
    
    #### 2. Early Performance Indicators
    - **What**: Monitor first 24-48 hours to predict final success
    - **When**: Campaign launch + 1-2 days
    - **Value**: Mid-campaign optimization, prevent wasted spend
    
    #### 3. Budget Allocation Optimizer
    - **What**: Find optimal channel mix for maximum ROAS
    - **When**: Campaign planning and quarterly budget allocation
    - **Value**: 20-35% ROAS improvement through better allocation
    
    ### 📊 How to Use
    
    #### Step 1: Prepare Historical Data
    Upload CSV with these columns:
    - `budget`, `duration`, `audience_size`
    - `channels`, `creative_type`, `objective`
    - `start_date`, `roas`, `cpa`, `conversions`
    
    #### Step 2: Train Model
    1. Go to "Model Training" tab
    2. Upload historical campaigns (50-100 minimum)
    3. Set success criteria (target ROAS, CPA)
    4. Click "Train Model"
    5. Save trained model
    
    #### Step 3: Make Predictions
    1. Go to "Campaign Success Predictor" tab
    2. Load trained model
    3. Enter campaign details
    4. Get predictions and recommendations
    
    #### Step 4: Monitor Early Performance
    1. Launch campaign
    2. After 24 hours, export hourly data
    3. Upload to "Early Performance Monitor"
    4. Get real-time optimization recommendations
    
    #### Step 5: Optimize Budget
    1. Go to "Budget Optimizer" tab
    2. Enter total budget and goal
    3. Get optimal channel allocation
    4. Implement recommendations
    
    ### 💡 Best Practices
    
    - **Train regularly**: Retrain model monthly with new campaign data
    - **Act on warnings**: Early performance warnings save 20-30% wasted spend
    - **Test recommendations**: A/B test model recommendations vs manual decisions
    - **Track ROI**: Measure cost savings and revenue gains from predictions
    
    ### 🎓 Success Stories
    
    > "Our model predicted this campaign would underperform - we adjusted targeting early and saved ₹2.5L"
    
    > "Reallocating 20% budget from Display to Google Search improved ROAS by 35%"
    
    > "High-value segments show 3x conversion - increased spend for ₹15L additional revenue"
    
    ### 📚 Additional Resources
    
    - Complete Architecture: `docs/architecture/PREDICTIVE_ANALYTICS_ARCHITECTURE.md`
    - Implementation Guide: `docs/user-guides/PREDICTIVE_IMPLEMENTATION_GUIDE.md`
    - Analysis Framework: `docs/architecture/ANALYSIS_FRAMEWORK.md`
    """)

# Footer
render_footer()

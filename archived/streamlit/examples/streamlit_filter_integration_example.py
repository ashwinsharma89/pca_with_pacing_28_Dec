"""
Streamlit Filter Integration Example
Demonstrates how to integrate interactive filters into Streamlit app
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# This would be imported in actual streamlit_app.py
from src.agents.visualization_filters import SmartFilterEngine
from streamlit_components.smart_filters import (
    InteractiveFilterPanel,
    QuickFilterBar,
    FilterPresets
)


def create_sample_data():
    """Create sample campaign data"""
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
    
    data = []
    for date in dates:
        for channel in ['Google Ads', 'Meta', 'LinkedIn']:
            for campaign in ['Brand', 'Performance']:
                data.append({
                    'date': date,
                    'channel': channel,
                    'campaign': campaign,
                    'device': np.random.choice(['Desktop', 'Mobile', 'Tablet'], p=[0.35, 0.55, 0.1]),
                    'spend': np.random.uniform(500, 3000),
                    'impressions': np.random.randint(5000, 50000),
                    'clicks': np.random.randint(200, 2000),
                    'conversions': np.random.randint(20, 200),
                    'ctr': np.random.uniform(0.02, 0.06),
                    'cpc': np.random.uniform(2, 8),
                    'cpa': np.random.uniform(20, 100),
                    'roas': np.random.uniform(1.5, 5.0)
                })
    
    return pd.DataFrame(data)


def main():
    """Main Streamlit app with filter integration"""
    
    st.set_page_config(
        page_title="Filter Integration Example",
        page_icon="🎛️",
        layout="wide"
    )
    
    st.title("🎛️ Interactive Filter System Example")
    st.markdown("Demonstration of smart filters in Streamlit")
    
    # Load data
    if 'campaign_data' not in st.session_state:
        st.session_state.campaign_data = create_sample_data()
    
    data = st.session_state.campaign_data
    
    # Initialize filter engine
    filter_engine = SmartFilterEngine()
    
    # ========================================
    # METHOD 1: Filter Presets (Quick Start)
    # ========================================
    st.markdown("---")
    st.header("Method 1: Filter Presets")
    
    preset_filters = FilterPresets.render_preset_selector()
    
    if preset_filters:
        filtered_data_preset = filter_engine.apply_filters(data, preset_filters)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Original Rows", f"{len(data):,}")
        col2.metric("Filtered Rows", f"{len(filtered_data_preset):,}")
        col3.metric("Reduction", f"{(1 - len(filtered_data_preset)/len(data))*100:.1f}%")
        
        with st.expander("View Filtered Data"):
            st.dataframe(filtered_data_preset.head(10))
    
    # ========================================
    # METHOD 2: Quick Filter Bar (Main Area)
    # ========================================
    st.markdown("---")
    st.header("Method 2: Quick Filter Bar")
    
    quick_filter_bar = QuickFilterBar(data)
    quick_filters = quick_filter_bar.render()
    
    if quick_filters:
        filtered_data_quick = filter_engine.apply_filters(data, quick_filters)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Original Rows", f"{len(data):,}")
        col2.metric("Filtered Rows", f"{len(filtered_data_quick):,}")
        col3.metric("Reduction", f"{(1 - len(filtered_data_quick)/len(data))*100:.1f}%")
        
        # Show summary statistics
        st.markdown("### 📊 Filtered Data Summary")
        summary_cols = st.columns(4)
        
        if 'spend' in filtered_data_quick.columns:
            summary_cols[0].metric("Total Spend", f"${filtered_data_quick['spend'].sum():,.0f}")
        if 'conversions' in filtered_data_quick.columns:
            summary_cols[1].metric("Total Conversions", f"{filtered_data_quick['conversions'].sum():,.0f}")
        if 'roas' in filtered_data_quick.columns:
            summary_cols[2].metric("Avg ROAS", f"{filtered_data_quick['roas'].mean():.2f}")
        if 'ctr' in filtered_data_quick.columns:
            summary_cols[3].metric("Avg CTR", f"{filtered_data_quick['ctr'].mean():.2%}")
    
    # ========================================
    # METHOD 3: Full Filter Panel (Sidebar)
    # ========================================
    st.markdown("---")
    st.header("Method 3: Full Interactive Filter Panel")
    st.markdown("Use the sidebar to access all filter options →")
    
    # Context for filter suggestions
    context = {
        'business_model': 'B2B',
        'benchmarks': {
            'ctr': 0.035,
            'roas': 2.5,
            'cpc': 4.5
        }
    }
    
    # Render interactive filter panel in sidebar
    filter_panel = InteractiveFilterPanel(filter_engine, data)
    filtered_data_full = filter_panel.render(context)
    
    # Display results
    if len(filtered_data_full) < len(data):
        st.success(f"✅ Filters applied! {len(data)} → {len(filtered_data_full)} rows")
        
        # Show detailed metrics
        st.markdown("### 📊 Detailed Metrics")
        
        metric_cols = st.columns(5)
        
        metrics = [
            ('Spend', 'spend', '${:,.0f}'),
            ('Conversions', 'conversions', '{:,.0f}'),
            ('ROAS', 'roas', '{:.2f}'),
            ('CTR', 'ctr', '{:.2%}'),
            ('CPA', 'cpa', '${:.2f}')
        ]
        
        for idx, (label, col, fmt) in enumerate(metrics):
            if col in filtered_data_full.columns:
                if col == 'spend' or col == 'conversions':
                    value = filtered_data_full[col].sum()
                else:
                    value = filtered_data_full[col].mean()
                
                metric_cols[idx].metric(label, fmt.format(value))
        
        # Show data breakdown
        st.markdown("### 📈 Data Breakdown")
        
        tab1, tab2, tab3 = st.tabs(["By Channel", "By Device", "By Campaign"])
        
        with tab1:
            if 'channel' in filtered_data_full.columns:
                channel_summary = filtered_data_full.groupby('channel').agg({
                    'spend': 'sum',
                    'conversions': 'sum',
                    'roas': 'mean'
                }).round(2)
                st.dataframe(channel_summary, use_container_width=True)
        
        with tab2:
            if 'device' in filtered_data_full.columns:
                device_summary = filtered_data_full.groupby('device').agg({
                    'spend': 'sum',
                    'conversions': 'sum',
                    'roas': 'mean'
                }).round(2)
                st.dataframe(device_summary, use_container_width=True)
        
        with tab3:
            if 'campaign' in filtered_data_full.columns:
                campaign_summary = filtered_data_full.groupby('campaign').agg({
                    'spend': 'sum',
                    'conversions': 'sum',
                    'roas': 'mean'
                }).round(2)
                st.dataframe(campaign_summary, use_container_width=True)
        
        # Show raw data
        with st.expander("📋 View Filtered Data"):
            st.dataframe(filtered_data_full, use_container_width=True)
    
    else:
        st.info("ℹ️ No filters applied. Use the sidebar to add filters.")
    
    # ========================================
    # Filter Impact Analysis
    # ========================================
    st.markdown("---")
    st.header("📊 Filter Impact Analysis")
    
    if filter_panel.active_filters:
        impact = filter_engine.get_filter_impact_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Original Rows", f"{impact['rows_original']:,}")
        col2.metric("Filtered Rows", f"{impact['rows_filtered']:,}")
        col3.metric("Rows Removed", f"{impact['rows_removed']:,}")
        col4.metric("Reduction %", f"{impact['reduction_percentage']:.1f}%")
        
        # Show warnings
        if impact.get('warnings'):
            st.markdown("### ⚠️ Warnings")
            for warning in impact['warnings']:
                if warning['severity'] == 'high':
                    st.error(f"**{warning['message']}**\n\n💡 {warning['suggestion']}")
                elif warning['severity'] == 'medium':
                    st.warning(f"**{warning['message']}**\n\n💡 {warning['suggestion']}")
                else:
                    st.info(f"**{warning['message']}**\n\n💡 {warning['suggestion']}")
    
    # ========================================
    # Integration Tips
    # ========================================
    st.markdown("---")
    st.header("💡 Integration Tips")
    
    with st.expander("How to integrate into your Streamlit app"):
        st.markdown("""
        ### Step 1: Import Components
        ```python
        from src.agents.visualization_filters import SmartFilterEngine
        from streamlit_components.smart_filters import InteractiveFilterPanel
        ```
        
        ### Step 2: Initialize
        ```python
        filter_engine = SmartFilterEngine()
        filter_panel = InteractiveFilterPanel(filter_engine, campaign_data)
        ```
        
        ### Step 3: Render in Sidebar
        ```python
        filtered_data = filter_panel.render(context={'benchmarks': {...}})
        ```
        
        ### Step 4: Use Filtered Data
        ```python
        # Create visualizations with filtered data
        viz_agent.create_executive_dashboard(
            insights=insights,
            campaign_data=filtered_data,  # Use filtered data!
            context=context
        )
        ```
        
        ### Benefits
        - ✅ Automatic filter suggestions based on data
        - ✅ Interactive UI components
        - ✅ Filter impact analysis
        - ✅ Warning system
        - ✅ Easy integration
        """)


if __name__ == "__main__":
    main()

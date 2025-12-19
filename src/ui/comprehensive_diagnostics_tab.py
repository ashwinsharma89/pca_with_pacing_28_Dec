"""
Comprehensive Diagnostics Tab - Combines Causal and Driver Analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def render_comprehensive_diagnostics(df: pd.DataFrame, diagnostics):
    """Render comprehensive diagnostics combining causal and driver analysis."""
    
    st.markdown("### 🔬 Comprehensive Performance Diagnostics")
    st.markdown("*Unified analysis combining causal decomposition and ML-driven insights*")
    
    st.info("""
    **What is Comprehensive Diagnostics?**
    
    This analysis combines:
    - 🎯 **Causal Analysis:** Mathematical decomposition of metric changes
    - 🔍 **Driver Analysis:** ML-based identification of key performance drivers
    - ✅ **Cross-Validation:** Findings validated across both methods
    - 💡 **Unified Recommendations:** Actionable insights from combined analysis
    """)
    
    # Configuration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        available_metrics = ['ROAS', 'CPA', 'CTR', 'CVR', 'CPC', 'CPM', 'Revenue', 'Spend']
        metric = st.selectbox(
            "Select Metric",
            available_metrics,
            key="comp_metric"
        )
    
    with col2:
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        date_col = st.selectbox(
            "Date Column",
            date_cols if date_cols else ['Date'],
            key="comp_date_col"
        )
    
    with col3:
        lookback_days = st.slider(
            "Lookback Period (days)",
            min_value=7,
            max_value=90,
            value=30,
            key="comp_lookback"
        )
    
    # Split date selection
    col1, col2 = st.columns(2)
    with col1:
        use_auto_split = st.checkbox("Auto-detect split point", value=True, key="comp_auto_split")
    
    with col2:
        if not use_auto_split and date_col in df.columns:
            df_dates = pd.to_datetime(df[date_col], errors='coerce')
            min_date = df_dates.min()
            max_date = df_dates.max()
            split_date = st.date_input(
                "Split Date",
                value=min_date + (max_date - min_date) / 2,
                min_value=min_date,
                max_value=max_date,
                key="comp_split_date"
            )
        else:
            split_date = None
    
    # Run comprehensive analysis
    if st.button("🚀 Run Comprehensive Diagnostics", type="primary", key="run_comprehensive"):
        with st.spinner(f"Running comprehensive analysis on {metric}..."):
            try:
                results = diagnostics.comprehensive_diagnostics(
                    df=df,
                    metric=metric,
                    date_col=date_col,
                    split_date=str(split_date) if split_date and not use_auto_split else None,
                    lookback_days=lookback_days
                )
                
                st.session_state.comprehensive_results = results
                st.success("✅ Comprehensive analysis complete!")
                
            except Exception as e:
                st.error(f"Error in comprehensive analysis: {str(e)}")
                logger.error(f"Comprehensive analysis error: {e}", exc_info=True)
    
    # Display results
    if 'comprehensive_results' in st.session_state:
        display_comprehensive_results(st.session_state.comprehensive_results, metric)


def display_comprehensive_results(results: Dict[str, Any], metric: str):
    """Display comprehensive diagnostics results."""
    
    st.divider()
    st.markdown("## 📊 Comprehensive Diagnostics Results")
    
    # Combined Insights Section
    if results.get('combined_insights'):
        st.markdown("### 🎯 Key Findings (Cross-Validated)")
        
        for insight in results['combined_insights']:
            st.markdown(f"- {insight}")
        
        st.divider()
    
    # Create two columns for side-by-side comparison
    col1, col2 = st.columns(2)
    
    # Left Column: Causal Analysis
    with col1:
        st.markdown("### 🎯 Causal Analysis")
        
        causal_result = results.get('causal_analysis')
        if causal_result:
            # Summary metrics
            st.metric(
                "Total Change",
                f"{causal_result.total_change:+.2f}",
                delta=f"{causal_result.total_change_pct:+.1f}%"
            )
            
            if causal_result.primary_driver:
                st.metric(
                    "Primary Cause",
                    causal_result.primary_driver.component[:25],
                    delta=f"{causal_result.primary_driver.percentage_contribution:.0f}%"
                )
            
            # Top 3 components
            if causal_result.contributions:
                st.markdown("**Top Components:**")
                for i, contrib in enumerate(sorted(
                    causal_result.contributions,
                    key=lambda x: abs(x.absolute_change),
                    reverse=True
                )[:3], 1):
                    direction_emoji = "📈" if contrib.impact_direction == "positive" else "📉"
                    st.markdown(
                        f"{i}. {direction_emoji} **{contrib.component}**: "
                        f"{contrib.absolute_change:+.4f} ({contrib.percentage_contribution:.1f}%)"
                    )
            
            # Platform attribution
            if causal_result.platform_attribution:
                st.markdown("**Platform Impact:**")
                platform_data = pd.DataFrame([
                    {'Platform': k, 'Impact': v}
                    for k, v in sorted(
                        causal_result.platform_attribution.items(),
                        key=lambda x: abs(x[1]),
                        reverse=True
                    )[:3]
                ])
                st.dataframe(platform_data, use_container_width=True, hide_index=True)
        else:
            st.warning("Causal analysis not available")
    
    # Right Column: Driver Analysis
    with col2:
        st.markdown("### 🔍 Driver Analysis")
        
        driver_result = results.get('driver_analysis')
        if driver_result:
            # Model quality
            score_pct = driver_result.model_score * 100
            score_emoji = "🟢" if driver_result.model_score > 0.7 else "🟡" if driver_result.model_score > 0.4 else "🔴"
            st.metric(
                "Model Quality (R²)",
                f"{score_emoji} {score_pct:.1f}%"
            )
            
            if driver_result.top_drivers:
                st.metric(
                    "Top Driver",
                    driver_result.top_drivers[0][0][:25],
                    delta=f"{driver_result.top_drivers[0][1]:.3f}"
                )
            
            # Top 3 drivers
            if driver_result.top_drivers:
                st.markdown("**Top ML Drivers:**")
                for i, (feature, importance, direction) in enumerate(driver_result.top_drivers[:3], 1):
                    st.markdown(
                        f"{i}. **{feature}**: {importance:.4f} ({direction})"
                    )
            
            # Insights
            if driver_result.insights:
                st.markdown("**ML Insights:**")
                for insight in driver_result.insights[:3]:
                    st.caption(insight)
        else:
            st.warning("Driver analysis not available")
    
    # Full Details in Expandable Sections
    st.divider()
    
    # Detailed Causal Analysis
    causal_result = results.get('causal_analysis')
    if causal_result:
        with st.expander("📊 Detailed Causal Analysis", expanded=False):
            # Component breakdown table
            if causal_result.contributions:
                breakdown_data = []
                for contrib in causal_result.contributions:
                    breakdown_data.append({
                        'Component': contrib.component,
                        'Impact': f"{contrib.absolute_change:+.4f}",
                        '% Contribution': f"{contrib.percentage_contribution:.1f}%",
                        'Direction': contrib.impact_direction.capitalize(),
                        'Actionability': contrib.actionability.capitalize()
                    })
                
                breakdown_df = pd.DataFrame(breakdown_data)
                st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
            
            # Recommendations
            if causal_result.recommendations:
                st.markdown("**Recommendations:**")
                for i, rec in enumerate(causal_result.recommendations, 1):
                    st.markdown(f"{i}. {rec}")
    
    # Detailed Driver Analysis
    driver_result = results.get('driver_analysis')
    if driver_result:
        with st.expander("🔍 Detailed Driver Analysis", expanded=False):
            # Feature importance table
            if driver_result.feature_importance:
                importance_data = pd.DataFrame([
                    {'Feature': k, 'Importance': v}
                    for k, v in sorted(
                        driver_result.feature_importance.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:10]
                ])
                st.dataframe(importance_data, use_container_width=True, hide_index=True)
            
            # All insights
            if driver_result.insights:
                st.markdown("**All Insights:**")
                for insight in driver_result.insights:
                    st.markdown(f"- {insight}")
    
    # Comparison Chart
    st.divider()
    st.markdown("### 📊 Comparative Analysis")
    
    if causal_result and driver_result:
        # Create comparison visualization
        fig = create_comparison_chart(causal_result, driver_result, metric)
        st.plotly_chart(fig, use_container_width=True)
    
    # Export Results
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export Summary Report", key="export_summary"):
            summary_text = generate_summary_report(results, metric)
            st.download_button(
                label="Download Report (TXT)",
                data=summary_text,
                file_name=f"diagnostics_report_{metric}.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("📊 Export Detailed Data", key="export_detailed"):
            st.info("Detailed export functionality coming soon!")


def create_comparison_chart(causal_result, driver_result, metric: str) -> go.Figure:
    """Create comparison chart between causal and driver analysis."""
    
    # Extract top factors from both analyses
    causal_factors = {}
    if causal_result.contributions:
        for contrib in sorted(causal_result.contributions, key=lambda x: abs(x.absolute_change), reverse=True)[:5]:
            causal_factors[contrib.component] = abs(contrib.absolute_change)
    
    driver_factors = {}
    if driver_result.top_drivers:
        for feature, importance, _ in driver_result.top_drivers[:5]:
            driver_factors[feature] = importance
    
    # Normalize for comparison
    if causal_factors:
        max_causal = max(causal_factors.values())
        causal_factors = {k: v/max_causal for k, v in causal_factors.items()}
    
    if driver_factors:
        max_driver = max(driver_factors.values())
        driver_factors = {k: v/max_driver for k, v in driver_factors.items()}
    
    # Create grouped bar chart
    all_factors = set(causal_factors.keys()) | set(driver_factors.keys())
    
    causal_values = [causal_factors.get(f, 0) for f in all_factors]
    driver_values = [driver_factors.get(f, 0) for f in all_factors]
    
    fig = go.Figure(data=[
        go.Bar(name='Causal Analysis', x=list(all_factors), y=causal_values, marker_color='#1f77b4'),
        go.Bar(name='Driver Analysis (ML)', x=list(all_factors), y=driver_values, marker_color='#ff7f0e')
    ])
    
    fig.update_layout(
        title=f"Causal vs Driver Analysis: Top Factors for {metric}",
        xaxis_title="Factors",
        yaxis_title="Normalized Importance",
        barmode='group',
        template='plotly_dark',
        height=400
    )
    
    return fig


def generate_summary_report(results: Dict[str, Any], metric: str) -> str:
    """Generate text summary report."""
    
    report = []
    report.append("=" * 80)
    report.append(f"COMPREHENSIVE DIAGNOSTICS REPORT: {metric}")
    report.append("=" * 80)
    report.append("")
    
    # Combined Insights
    if results.get('combined_insights'):
        report.append("KEY FINDINGS (Cross-Validated)")
        report.append("-" * 80)
        for insight in results['combined_insights']:
            # Remove markdown formatting
            clean_insight = insight.replace('**', '').replace('*', '')
            report.append(f"  • {clean_insight}")
        report.append("")
    
    # Causal Analysis
    causal_result = results.get('causal_analysis')
    if causal_result:
        report.append("CAUSAL ANALYSIS")
        report.append("-" * 80)
        report.append(f"Total Change: {causal_result.total_change:+.2f} ({causal_result.total_change_pct:+.1f}%)")
        report.append(f"Before: {causal_result.before_value:.2f}")
        report.append(f"After: {causal_result.after_value:.2f}")
        report.append(f"Confidence: {causal_result.confidence * 100:.0f}%")
        report.append("")
        
        if causal_result.primary_driver:
            report.append(f"Primary Cause: {causal_result.primary_driver.component}")
            report.append(f"  Contribution: {causal_result.primary_driver.percentage_contribution:.1f}%")
        report.append("")
        
        if causal_result.contributions:
            report.append("Component Breakdown:")
            for contrib in sorted(causal_result.contributions, key=lambda x: abs(x.absolute_change), reverse=True):
                report.append(f"  • {contrib.component}: {contrib.absolute_change:+.4f} ({contrib.percentage_contribution:.1f}%)")
        report.append("")
    
    # Driver Analysis
    driver_result = results.get('driver_analysis')
    if driver_result:
        report.append("DRIVER ANALYSIS (ML)")
        report.append("-" * 80)
        report.append(f"Model Quality (R²): {driver_result.model_score * 100:.1f}%")
        report.append("")
        
        if driver_result.top_drivers:
            report.append("Top Drivers:")
            for i, (feature, importance, direction) in enumerate(driver_result.top_drivers, 1):
                report.append(f"  {i}. {feature}: {importance:.4f} ({direction})")
        report.append("")
        
        if driver_result.insights:
            report.append("Insights:")
            for insight in driver_result.insights:
                report.append(f"  • {insight}")
        report.append("")
    
    report.append("=" * 80)
    report.append("End of Report")
    report.append("=" * 80)
    
    return "\n".join(report)

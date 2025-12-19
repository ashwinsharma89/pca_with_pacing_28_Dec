"""
Streamlit UI Component for Smart Performance Diagnostics
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional
import logging

from src.analytics.performance_diagnostics import (
    PerformanceDiagnostics,
    CausalBreakdown,
    DriverAnalysis
)
from src.analytics.causal_analysis import (
    CausalAnalysisEngine,
    CausalAnalysisResult,
    DecompositionMethod
)
from src.ui.comprehensive_diagnostics_tab import render_comprehensive_diagnostics

logger = logging.getLogger(__name__)


class DiagnosticsComponent:
    """UI component for performance diagnostics."""
    
    @staticmethod
    def render(df: pd.DataFrame):
        """Render the diagnostics interface."""
        
        st.markdown("## 🔬 Smart Performance Diagnostics")
        st.markdown("*Understand what's driving your performance changes*")
        
        # Initialize diagnostics engines
        if 'diagnostics_engine' not in st.session_state:
            st.session_state.diagnostics_engine = PerformanceDiagnostics()
        if 'causal_engine' not in st.session_state:
            st.session_state.causal_engine = CausalAnalysisEngine()
        
        diagnostics = st.session_state.diagnostics_engine
        causal_engine = st.session_state.causal_engine
        
        # Create tabs for different analysis types
        tab1, tab2, tab3 = st.tabs([
            "🎯 Causal Analysis",
            "🔍 Driver Analysis",
            "🔬 Comprehensive Diagnostics"
        ])
        
        with tab1:
            DiagnosticsComponent._render_causal_analysis(df, causal_engine)
        
        with tab2:
            DiagnosticsComponent._render_driver_analysis(df, diagnostics)
        
        with tab3:
            render_comprehensive_diagnostics(df, diagnostics)
    
    @staticmethod
    def _render_causal_analysis(df: pd.DataFrame, causal_engine: CausalAnalysisEngine):
        """Render causal analysis section."""
        
        st.markdown("### 🎯 Advanced Causal Analysis")
        st.markdown("*Quantified cause-and-effect breakdown with mathematical decomposition*")
        
        # Configuration
        col1, col2, col3 = st.columns(3)
        
        with col1:
            available_metrics = ['ROAS', 'CPA', 'CTR', 'CVR', 'CPC', 'CPM']
            metric = st.selectbox(
                "Select Metric to Analyze",
                available_metrics,
                key="causal_metric"
            )
        
        with col2:
            # Date column selection
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            date_col = st.selectbox(
                "Date Column",
                date_cols if date_cols else ['Date'],
                key="causal_date_col"
            )
        
        with col3:
            lookback_days = st.slider(
                "Lookback Period (days)",
                min_value=7,
                max_value=90,
                value=30,
                key="causal_lookback"
            )
        
        # Split date selection
        col1, col2 = st.columns(2)
        with col1:
            use_auto_split = st.checkbox("Auto-detect split point", value=True, key="auto_split")
        
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
                    key="split_date"
                )
            else:
                split_date = None
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                decomp_method = st.selectbox(
                    "Decomposition Method",
                    ["Hybrid", "Additive", "Multiplicative"],
                    key="decomp_method"
                )
                include_ml = st.checkbox("Include ML Analysis", value=True, key="include_ml")
            with col2:
                include_attribution = st.checkbox("Include Channel Attribution", value=True, key="include_attr")
        
        # Map method name to enum
        method_map = {
            "Hybrid": DecompositionMethod.HYBRID,
            "Additive": DecompositionMethod.ADDITIVE,
            "Multiplicative": DecompositionMethod.MULTIPLICATIVE
        }
        
        # Run analysis button
        if st.button("🔍 Analyze Root Cause", type="primary", key="run_causal"):
            with st.spinner(f"Analyzing {metric} changes with advanced decomposition..."):
                try:
                    result = causal_engine.analyze(
                        df=df,
                        metric=metric,
                        date_col=date_col,
                        split_date=str(split_date) if split_date and not use_auto_split else None,
                        lookback_days=lookback_days,
                        method=method_map[decomp_method],
                        include_ml=include_ml,
                        include_attribution=include_attribution
                    )
                    
                    st.session_state.causal_result = result
                    st.success("✅ Analysis complete!")
                    
                except Exception as e:
                    st.error(f"Error in causal analysis: {str(e)}")
                    logger.error(f"Causal analysis error: {e}", exc_info=True)
        
        # Display results
        if 'causal_result' in st.session_state:
            DiagnosticsComponent._display_advanced_causal_results(st.session_state.causal_result)
    
    @staticmethod
    def _display_causal_results(breakdown: CausalBreakdown):
        """Display causal analysis results."""
        
        st.divider()
        st.markdown("### 📊 Analysis Results")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            change_color = "normal" if breakdown.total_change >= 0 else "inverse"
            st.metric(
                "Total Change",
                f"{breakdown.total_change:+.2f}",
                delta=f"{breakdown.total_change_pct:+.1f}%",
                delta_color=change_color
            )
        
        with col2:
            st.metric(
                "Root Cause",
                breakdown.root_cause,
                help="Primary driver of the change"
            )
        
        with col3:
            confidence_pct = breakdown.confidence * 100
            confidence_emoji = "🟢" if breakdown.confidence > 0.7 else "🟡" if breakdown.confidence > 0.4 else "🔴"
            st.metric(
                "Confidence",
                f"{confidence_emoji} {confidence_pct:.0f}%"
            )
        
        with col4:
            before_val = breakdown.period_comparison.get('before', 0)
            after_val = breakdown.period_comparison.get('after', 0)
            st.metric(
                "Before → After",
                f"{after_val:.2f}",
                delta=f"from {before_val:.2f}"
            )
        
        # Component breakdown
        if breakdown.components:
            st.markdown("#### 🔍 Component Breakdown")
            
            # Create waterfall chart
            fig = DiagnosticsComponent._create_waterfall_chart(breakdown)
            st.plotly_chart(fig, use_container_width=True)
            
            # Component table
            st.markdown("#### 📋 Detailed Breakdown")
            
            component_data = []
            for component, value in breakdown.components.items():
                pct = breakdown.component_pcts.get(component, 0)
                component_data.append({
                    'Component': component,
                    'Contribution': value,
                    '% of Total Change': f"{pct:.1f}%",
                    'Impact': '↑ Positive' if value > 0 else '↓ Negative'
                })
            
            component_df = pd.DataFrame(component_data)
            component_df = component_df.sort_values('Contribution', key=abs, ascending=False)
            
            st.dataframe(
                component_df.style.format({
                    'Contribution': '{:+.4f}'
                }),
                use_container_width=True
            )
            
            # Insights
            st.markdown("#### 💡 Key Insights")
            
            # Generate insights
            insights = DiagnosticsComponent._generate_causal_insights(breakdown)
            for insight in insights:
                st.markdown(f"- {insight}")
    
    @staticmethod
    def _create_waterfall_chart(breakdown: CausalBreakdown) -> go.Figure:
        """Create waterfall chart for component breakdown."""
        
        # Prepare data for waterfall
        components = list(breakdown.components.keys())
        values = list(breakdown.components.values())
        
        # Sort by absolute value
        sorted_items = sorted(zip(components, values), key=lambda x: abs(x[1]), reverse=True)
        components, values = zip(*sorted_items) if sorted_items else ([], [])
        
        # Create waterfall chart
        fig = go.Figure(go.Waterfall(
            name="Component Contribution",
            orientation="v",
            measure=["relative"] * len(components) + ["total"],
            x=list(components) + ["Total Change"],
            y=list(values) + [breakdown.total_change],
            text=[f"{v:+.4f}" for v in values] + [f"{breakdown.total_change:+.4f}"],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "green"}},
            decreasing={"marker": {"color": "red"}},
            totals={"marker": {"color": "blue"}}
        ))
        
        fig.update_layout(
            title=f"{breakdown.metric} Change Breakdown",
            showlegend=False,
            height=500,
            template='plotly_dark',
            xaxis=dict(title="Components"),
            yaxis=dict(title="Contribution to Change")
        )
        
        return fig
    
    @staticmethod
    def _display_advanced_causal_results(result: CausalAnalysisResult):
        """Display advanced causal analysis results."""
        
        st.divider()
        st.markdown("### 📊 Causal Analysis Results")
        
        # Summary metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            change_color = "normal" if result.total_change >= 0 else "inverse"
            st.metric(
                "Total Change",
                f"{result.total_change:+.2f}",
                delta=f"{result.total_change_pct:+.1f}%",
                delta_color=change_color
            )
        
        with col2:
            st.metric(
                "Before → After",
                f"{result.after_value:.2f}",
                delta=f"from {result.before_value:.2f}"
            )
        
        with col3:
            if result.primary_driver:
                st.metric(
                    "Primary Driver",
                    result.primary_driver.component[:20],
                    delta=f"{result.primary_driver.percentage_contribution:.0f}%"
                )
        
        with col4:
            confidence_pct = result.confidence * 100
            confidence_emoji = "🟢" if result.confidence > 0.7 else "🟡" if result.confidence > 0.4 else "🔴"
            st.metric(
                "Confidence",
                f"{confidence_emoji} {confidence_pct:.0f}%"
            )
        
        # Period information
        st.caption(f"**Period Before:** {result.period_before} | **Period After:** {result.period_after}")
        
        # Key Insights
        if result.insights:
            st.markdown("#### 💡 Key Insights")
            for insight in result.insights:
                st.markdown(f"- {insight}")
        
        # Component Breakdown
        if result.contributions:
            st.markdown("#### 🔍 Component Breakdown")
            
            # Create detailed breakdown table
            breakdown_data = []
            for contrib in result.contributions:
                breakdown_data.append({
                    'Component': contrib.component,
                    'Before': f"{contrib.before_value:.2f}",
                    'After': f"{contrib.after_value:.2f}",
                    'Δ Change': f"{contrib.delta:+.2f}",
                    'Δ %': f"{contrib.delta_pct:+.1f}%",
                    'Impact on Metric': f"{contrib.absolute_change:+.4f}",
                    '% Contribution': f"{contrib.percentage_contribution:.1f}%",
                    'Direction': contrib.impact_direction.capitalize(),
                    'Actionability': contrib.actionability.capitalize()
                })
            
            breakdown_df = pd.DataFrame(breakdown_data)
            
            # Color code by impact direction
            def highlight_impact(row):
                if row['Direction'] == 'Positive':
                    return ['background-color: rgba(0, 255, 0, 0.1)'] * len(row)
                elif row['Direction'] == 'Negative':
                    return ['background-color: rgba(255, 0, 0, 0.1)'] * len(row)
                else:
                    return [''] * len(row)
            
            st.dataframe(
                breakdown_df.style.apply(highlight_impact, axis=1),
                use_container_width=True
            )
            
            # Waterfall chart
            st.markdown("#### 📊 Waterfall Chart")
            fig = DiagnosticsComponent._create_advanced_waterfall_chart(result)
            st.plotly_chart(fig, use_container_width=True)
        
        # Attribution Analysis
        if result.platform_attribution or result.channel_attribution:
            st.markdown("#### 🏆 Attribution Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if result.platform_attribution:
                    st.markdown("**Platform Attribution**")
                    platform_data = pd.DataFrame([
                        {'Platform': k, 'Contribution': v}
                        for k, v in sorted(result.platform_attribution.items(), key=lambda x: abs(x[1]), reverse=True)
                    ])
                    
                    fig = px.bar(
                        platform_data,
                        x='Contribution',
                        y='Platform',
                        orientation='h',
                        title='Platform Contribution to Change',
                        color='Contribution',
                        color_continuous_scale='RdYlGn'
                    )
                    fig.update_layout(template='plotly_dark', height=300)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if result.channel_attribution:
                    st.markdown("**Channel Attribution**")
                    channel_data = pd.DataFrame([
                        {'Channel': k, 'Contribution': v}
                        for k, v in sorted(result.channel_attribution.items(), key=lambda x: abs(x[1]), reverse=True)
                    ])
                    
                    fig = px.bar(
                        channel_data,
                        x='Contribution',
                        y='Channel',
                        orientation='h',
                        title='Channel Contribution to Change',
                        color='Contribution',
                        color_continuous_scale='RdYlGn'
                    )
                    fig.update_layout(template='plotly_dark', height=300)
                    st.plotly_chart(fig, use_container_width=True)
        
        # ML Insights
        if result.ml_drivers:
            with st.expander("🤖 ML-Based Driver Analysis"):
                st.markdown("**Feature Importance from XGBoost**")
                ml_data = pd.DataFrame([
                    {'Feature': k, 'Importance': v}
                    for k, v in sorted(result.ml_drivers.items(), key=lambda x: x[1], reverse=True)[:10]
                ])
                st.dataframe(ml_data, use_container_width=True)
        
        # Recommendations
        if result.recommendations:
            st.markdown("#### 🎯 Actionable Recommendations")
            for i, rec in enumerate(result.recommendations, 1):
                st.markdown(f"{i}. {rec}")
    
    @staticmethod
    def _create_advanced_waterfall_chart(result: CausalAnalysisResult) -> go.Figure:
        """Create waterfall chart for advanced causal analysis."""
        
        # Sort contributions by absolute value
        sorted_contribs = sorted(result.contributions, key=lambda x: abs(x.absolute_change), reverse=True)
        
        components = [c.component for c in sorted_contribs]
        values = [c.absolute_change for c in sorted_contribs]
        
        fig = go.Figure(go.Waterfall(
            name="Component Contribution",
            orientation="v",
            measure=["relative"] * len(components) + ["total"],
            x=components + ["Total Change"],
            y=values + [result.total_change],
            text=[f"{v:+.4f}" for v in values] + [f"{result.total_change:+.4f}"],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "green"}},
            decreasing={"marker": {"color": "red"}},
            totals={"marker": {"color": "blue"}}
        ))
        
        fig.update_layout(
            title=f"{result.metric} Change Decomposition",
            showlegend=False,
            height=500,
            template='plotly_dark',
            xaxis=dict(title="Components", tickangle=-45),
            yaxis=dict(title="Contribution to Change")
        )
        
        return fig
    
    @staticmethod
    def _generate_causal_insights(breakdown: CausalBreakdown) -> list:
        """Generate insights from causal breakdown."""
        
        insights = []
        
        # Root cause insight
        root_pct = breakdown.component_pcts.get(breakdown.root_cause, 0)
        insights.append(
            f"**{breakdown.root_cause}** is the primary driver, contributing {root_pct:.0f}% of the total change"
        )
        
        # Direction insight
        if breakdown.total_change > 0:
            insights.append(f"📈 {breakdown.metric} **improved** by {abs(breakdown.total_change_pct):.1f}%")
        else:
            insights.append(f"📉 {breakdown.metric} **declined** by {abs(breakdown.total_change_pct):.1f}%")
        
        # Component insights
        positive_components = [k for k, v in breakdown.components.items() if v > 0]
        negative_components = [k for k, v in breakdown.components.items() if v < 0]
        
        if positive_components:
            insights.append(f"✅ Positive contributors: {', '.join(positive_components[:2])}")
        
        if negative_components:
            insights.append(f"⚠️ Negative contributors: {', '.join(negative_components[:2])}")
        
        # Confidence insight
        if breakdown.confidence < 0.5:
            insights.append("⚠️ Low confidence - consider collecting more data or checking data quality")
        
        return insights
    
    @staticmethod
    def _render_driver_analysis(df: pd.DataFrame, diagnostics: PerformanceDiagnostics):
        """Render driver analysis section."""
        
        st.markdown("### 🔍 Driver Analysis")
        st.markdown("*ML-powered identification of performance drivers*")
        
        # Configuration
        col1, col2 = st.columns(2)
        
        with col1:
            # Target metric selection
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            common_metrics = ['ROAS', 'CPA', 'CTR', 'CVR', 'CPC', 'Spend', 'Conversions', 'Revenue']
            available_targets = [m for m in common_metrics if m in numeric_cols] + numeric_cols
            
            target_metric = st.selectbox(
                "Target Metric",
                list(dict.fromkeys(available_targets)),  # Remove duplicates
                key="driver_target"
            )
        
        with col2:
            # Feature selection
            use_auto_features = st.checkbox(
                "Auto-select features",
                value=True,
                key="auto_features"
            )
        
        if not use_auto_features:
            feature_cols = st.multiselect(
                "Select Features",
                [col for col in numeric_cols if col != target_metric],
                default=[col for col in numeric_cols if col != target_metric][:5],
                key="manual_features"
            )
        else:
            feature_cols = None
        
        # Categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            selected_categoricals = st.multiselect(
                "Include Categorical Features (will be encoded)",
                categorical_cols,
                default=[],
                key="categorical_features"
            )
        else:
            selected_categoricals = None
        
        # Run analysis button
        if st.button("🚀 Analyze Drivers", type="primary", key="run_driver"):
            with st.spinner(f"Analyzing drivers of {target_metric}..."):
                try:
                    driver_analysis = diagnostics.analyze_drivers(
                        df=df,
                        target_metric=target_metric,
                        feature_cols=feature_cols,
                        categorical_cols=selected_categoricals if selected_categoricals else None
                    )
                    
                    st.session_state.driver_analysis = driver_analysis
                    
                except Exception as e:
                    st.error(f"Error in driver analysis: {str(e)}")
                    logger.error(f"Driver analysis error: {e}", exc_info=True)
        
        # Display results
        if 'driver_analysis' in st.session_state:
            DiagnosticsComponent._display_driver_results(st.session_state.driver_analysis)
    
    @staticmethod
    def _display_driver_results(analysis: DriverAnalysis):
        """Display driver analysis results."""
        
        st.divider()
        st.markdown("### 📊 Driver Analysis Results")
        
        # Model quality
        col1, col2 = st.columns(2)
        
        with col1:
            score_pct = analysis.model_score * 100
            score_emoji = "🟢" if analysis.model_score > 0.7 else "🟡" if analysis.model_score > 0.4 else "🔴"
            st.metric(
                "Model Quality (R²)",
                f"{score_emoji} {score_pct:.1f}%",
                help="How well the model explains the variance"
            )
        
        with col2:
            st.metric(
                "Top Driver",
                analysis.top_drivers[0][0] if analysis.top_drivers else "N/A",
                help="Most important feature"
            )
        
        # Insights
        st.markdown("#### 💡 Key Insights")
        for insight in analysis.insights:
            st.markdown(f"- {insight}")
        
        # Feature importance chart
        if analysis.feature_importance:
            st.markdown("#### 📊 Feature Importance")
            
            # Create bar chart
            fig = DiagnosticsComponent._create_importance_chart(analysis)
            st.plotly_chart(fig, use_container_width=True)
        
        # Top drivers table
        if analysis.top_drivers:
            st.markdown("#### 🎯 Top Drivers")
            
            driver_data = []
            for i, (feature, importance, direction) in enumerate(analysis.top_drivers, 1):
                driver_data.append({
                    'Rank': i,
                    'Feature': feature,
                    'Importance Score': importance,
                    'Direction': direction
                })
            
            driver_df = pd.DataFrame(driver_data)
            st.dataframe(
                driver_df.style.format({
                    'Importance Score': '{:.4f}'
                }),
                use_container_width=True
            )
        
        # SHAP values if available
        if analysis.shap_values:
            with st.expander("🔬 Advanced: SHAP Values"):
                st.markdown("*SHAP values show the impact of each feature on predictions*")
                
                shap_df = pd.DataFrame([
                    {'Feature': k, 'SHAP Value': v}
                    for k, v in sorted(analysis.shap_values.items(), key=lambda x: x[1], reverse=True)[:10]
                ])
                
                st.dataframe(shap_df, use_container_width=True)
    
    @staticmethod
    def _create_importance_chart(analysis: DriverAnalysis) -> go.Figure:
        """Create feature importance chart."""
        
        # Sort by importance
        sorted_features = sorted(
            analysis.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Top 10
        
        features, importances = zip(*sorted_features) if sorted_features else ([], [])
        
        fig = go.Figure(go.Bar(
            x=list(importances),
            y=list(features),
            orientation='h',
            marker=dict(
                color=list(importances),
                colorscale='Viridis',
                showscale=True
            ),
            text=[f"{imp:.3f}" for imp in importances],
            textposition='auto'
        ))
        
        fig.update_layout(
            title=f"Top 10 Drivers of {analysis.target_metric}",
            xaxis_title="Importance Score",
            yaxis_title="Feature",
            height=500,
            template='plotly_dark',
            showlegend=False
        )
        
        return fig

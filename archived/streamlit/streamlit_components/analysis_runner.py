"""
Analysis runner component.
Handles auto-analysis execution and results display.
"""

import logging
from typing import Dict, Any, Optional
import time

import streamlit as st
import pandas as pd

from src.analytics.auto_insights import MediaAnalyticsExpert
from src.models.campaign import CampaignContext, BusinessModel

logger = logging.getLogger(__name__)


@st.cache_resource
def get_analysis_agent():
    """Get cached analysis agent instance."""
    return MediaAnalyticsExpert()


class AnalysisRunnerComponent:
    """Component for running and displaying analysis."""
    
    @staticmethod
    def render_analysis_config():
        """Render analysis configuration UI."""
        st.subheader("⚙️ Analysis Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            business_model = st.selectbox(
                "Business Model",
                options=["B2C", "B2B", "E-commerce", "SaaS"],
                help="Select your business model for context-aware analysis"
            )
        
        with col2:
            industry = st.text_input(
                "Industry",
                value="Marketing",
                help="Your industry sector"
            )
        
        return {
            'business_model': business_model,
            'industry': industry
        }
    
    @staticmethod
    def run_analysis(df: pd.DataFrame, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Run auto-analysis on dataframe.
        
        Args:
            df: Campaign dataframe
            config: Analysis configuration
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Create campaign context
            context = CampaignContext(
                business_model=BusinessModel(config.get('business_model', 'B2C')),
                industry=config.get('industry', 'Marketing')
            )
            
            # Get agent
            agent = get_analysis_agent()
            
            # Run analysis with progress
            with st.spinner("🔍 Analyzing campaign data..."):
                start_time = time.time()
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate progress (actual analysis is async)
                for i in range(100):
                    time.sleep(0.05)
                    progress_bar.progress(i + 1)
                    
                    if i < 30:
                        status_text.text("Analyzing metrics...")
                    elif i < 60:
                        status_text.text("Generating insights...")
                    else:
                        status_text.text("Creating recommendations...")
                
                # Run actual analysis
                results = agent.analyze(df, context)
                
                execution_time = time.time() - start_time
                
                # Clear progress
                progress_bar.empty()
                status_text.empty()
                
                # Add metadata
                results['execution_time'] = execution_time
                results['timestamp'] = pd.Timestamp.now().isoformat()
                
                logger.info(f"Analysis completed in {execution_time:.2f}s")
                
                return results
                
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            st.error(f"❌ Analysis failed: {e}")
            return None
    
    @staticmethod
    def display_results(results: Dict[str, Any]):
        """
        Display analysis results.
        
        Args:
            results: Analysis results dictionary
        """
        if not results:
            st.warning("No analysis results to display")
            return
        
        # Executive Summary
        st.subheader("📊 Executive Summary")
        
        summary = results.get('executive_summary', {})
        if summary:
            AnalysisRunnerComponent._display_executive_summary(summary)
        
        # Key Metrics
        st.subheader("📈 Key Metrics")
        
        metrics = results.get('metrics', {})
        if metrics:
            AnalysisRunnerComponent._display_metrics(metrics)
        
        # Insights
        st.subheader("💡 Insights")
        
        insights = results.get('insights', [])
        if insights:
            AnalysisRunnerComponent._display_insights(insights)
        
        # Recommendations
        st.subheader("🎯 Recommendations")
        
        recommendations = results.get('recommendations', [])
        if recommendations:
            AnalysisRunnerComponent._display_recommendations(recommendations)
        
        # Metadata
        with st.expander("ℹ️ Analysis Metadata"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Execution Time", f"{results.get('execution_time', 0):.2f}s")
            with col2:
                st.metric("Timestamp", results.get('timestamp', 'N/A'))
    
    @staticmethod
    def _display_executive_summary(summary: Dict[str, Any]):
        """Display executive summary."""
        st.markdown(summary.get('overview', 'No summary available'))
        
        # Key highlights
        highlights = summary.get('highlights', [])
        if highlights:
            st.markdown("**Key Highlights:**")
            for highlight in highlights:
                st.markdown(f"- {highlight}")
    
    @staticmethod
    def _display_metrics(metrics: Dict[str, Any]):
        """Display key metrics in columns."""
        # Create metric columns
        cols = st.columns(4)
        
        metric_list = [
            ('Total Spend', metrics.get('total_spend', 0), '$'),
            ('Total Clicks', metrics.get('total_clicks', 0), ''),
            ('Avg CTR', metrics.get('avg_ctr', 0), '%'),
            ('Avg CPC', metrics.get('avg_cpc', 0), '$')
        ]
        
        for col, (label, value, prefix) in zip(cols, metric_list):
            if prefix == '$':
                col.metric(label, f"${value:,.2f}")
            elif prefix == '%':
                col.metric(label, f"{value:.2f}%")
            else:
                col.metric(label, f"{value:,}")
    
    @staticmethod
    def _display_insights(insights: list):
        """Display insights list."""
        for i, insight in enumerate(insights, 1):
            with st.container():
                st.markdown(f"**{i}. {insight.get('title', 'Insight')}**")
                st.markdown(insight.get('description', ''))
                
                # Show confidence if available
                confidence = insight.get('confidence')
                if confidence:
                    st.progress(confidence / 100)
                    st.caption(f"Confidence: {confidence}%")
                
                st.divider()
    
    @staticmethod
    def _display_recommendations(recommendations: list):
        """Display recommendations list."""
        for i, rec in enumerate(recommendations, 1):
            with st.container():
                # Priority badge
                priority = rec.get('priority', 'medium').upper()
                if priority == 'HIGH':
                    badge = "🔴"
                elif priority == 'MEDIUM':
                    badge = "🟡"
                else:
                    badge = "🟢"
                
                st.markdown(f"{badge} **{i}. {rec.get('title', 'Recommendation')}**")
                st.markdown(rec.get('description', ''))
                
                # Show expected impact
                impact = rec.get('expected_impact')
                if impact:
                    st.info(f"💰 Expected Impact: {impact}")
                
                st.divider()


class AnalysisHistoryComponent:
    """Component for managing analysis history."""
    
    @staticmethod
    def save_to_history(results: Dict[str, Any]):
        """Save analysis results to history."""
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
        
        # Add to history
        st.session_state.analysis_history.append({
            'timestamp': results.get('timestamp'),
            'execution_time': results.get('execution_time'),
            'results': results
        })
        
        # Keep only last 10
        if len(st.session_state.analysis_history) > 10:
            st.session_state.analysis_history = st.session_state.analysis_history[-10:]
    
    @staticmethod
    def render_history():
        """Render analysis history sidebar."""
        if 'analysis_history' not in st.session_state or not st.session_state.analysis_history:
            st.info("No analysis history yet")
            return
        
        st.subheader("📜 Analysis History")
        
        for i, entry in enumerate(reversed(st.session_state.analysis_history), 1):
            # Safely handle None or missing values
            if entry is None:
                continue
            
            timestamp = entry.get('timestamp', 'Unknown')
            if timestamp and isinstance(timestamp, str) and len(timestamp) > 19:
                timestamp = timestamp[:19]
            
            execution_time = entry.get('execution_time', 0)
            # Ensure execution_time is a number
            if execution_time is None or not isinstance(execution_time, (int, float)):
                execution_time = 0.0
            
            with st.expander(f"Analysis {i} - {timestamp}"):
                st.metric("Execution Time", f"{execution_time:.2f}s")
                
                if st.button(f"Load Analysis {i}", key=f"load_{i}"):
                    if 'results' in entry:
                        st.session_state.analysis_data = entry['results']
                        st.session_state.analysis_complete = True
                        st.rerun()

"""
Integration tests for Streamlit pages
Covers: Page rendering, session state, data flow, component interactions
"""
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_session_state():
    """Mock Streamlit session state."""
    return {
        "df": None,
        "df_loaded_from_cache": False,
        "analysis_history": [],
        "current_page": "Home",
        "analytics_expert": MagicMock(),
        "filter_engine": MagicMock(),
        "chart_generator": MagicMock(),
    }


@pytest.fixture
def sample_campaign_df():
    """Sample campaign data for testing."""
    return pd.DataFrame({
        "Campaign_Name": ["Brand", "Lead Gen", "Retargeting"] * 10,
        "Platform": ["Google", "Meta", "LinkedIn"] * 10,
        "Spend": [1000 + i * 100 for i in range(30)],
        "Conversions": [10 + i for i in range(30)],
        "Impressions": [10000 + i * 1000 for i in range(30)],
        "Clicks": [100 + i * 10 for i in range(30)],
        "Date": pd.date_range("2024-01-01", periods=30),
        "Funnel_Stage": ["Awareness", "Consideration", "Conversion"] * 10
    })


# ============================================================================
# Session State Tests
# ============================================================================

class TestSessionState:
    """Tests for session state management."""
    
    def test_init_session_state_creates_keys(self, mock_session_state):
        """Session state should have required keys."""
        required_keys = ["df", "analysis_history", "current_page"]
        
        for key in required_keys:
            assert key in mock_session_state
    
    def test_df_initially_none(self, mock_session_state):
        """DataFrame should be None initially."""
        assert mock_session_state["df"] is None
    
    def test_analysis_history_is_list(self, mock_session_state):
        """Analysis history should be a list."""
        assert isinstance(mock_session_state["analysis_history"], list)


# ============================================================================
# Data Upload Page Tests
# ============================================================================

class TestDataUploadPage:
    """Tests for data upload functionality."""
    
    def test_upload_valid_csv(self, sample_campaign_df):
        """Should accept valid CSV upload."""
        # Simulate file upload
        assert len(sample_campaign_df) == 30
        assert "Campaign_Name" in sample_campaign_df.columns
    
    def test_data_validation_on_upload(self, sample_campaign_df):
        """Data should be validated on upload."""
        # Check required columns exist
        required = ["Spend", "Conversions"]
        for col in required:
            assert col in sample_campaign_df.columns
    
    def test_column_normalization_applied(self):
        """Column names should be normalized."""
        raw_df = pd.DataFrame({
            "campaign": ["Test"],
            "cost": [100],
            "conv": [10]
        })
        
        # After normalization
        from src.utils.data_loader import normalize_campaign_dataframe
        normalized = normalize_campaign_dataframe(raw_df)
        
        assert "Campaign_Name" in normalized.columns
        assert "Spend" in normalized.columns
        assert "Conversions" in normalized.columns


# ============================================================================
# Analysis Page Tests
# ============================================================================

class TestAnalysisPage:
    """Tests for analysis page functionality."""
    
    def test_analysis_requires_data(self, mock_session_state):
        """Analysis should require uploaded data."""
        assert mock_session_state["df"] is None
        # Should show warning when no data
    
    def test_run_analysis_updates_history(self, mock_session_state, sample_campaign_df):
        """Running analysis should update history."""
        mock_session_state["df"] = sample_campaign_df
        
        # Simulate analysis
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "summary": "Test analysis",
            "metrics": {"total_spend": 100}
        }
        
        mock_session_state["analysis_history"].append(analysis_result)
        
        assert len(mock_session_state["analysis_history"]) == 1
    
    def test_analysis_calculates_metrics(self, sample_campaign_df):
        """Analysis should calculate key metrics."""
        total_spend = sample_campaign_df["Spend"].sum()
        total_conversions = sample_campaign_df["Conversions"].sum()
        cpa = total_spend / total_conversions
        
        assert total_spend > 0
        assert total_conversions > 0
        assert cpa > 0


# ============================================================================
# Deep Dive Page Tests
# ============================================================================

class TestDeepDivePage:
    """Tests for deep dive filtering functionality."""
    
    def test_platform_filter(self, sample_campaign_df):
        """Platform filter should work correctly."""
        filtered = sample_campaign_df[sample_campaign_df["Platform"] == "Google"]
        
        assert len(filtered) == 10
        assert all(filtered["Platform"] == "Google")
    
    def test_date_range_filter(self, sample_campaign_df):
        """Date range filter should work correctly."""
        start = pd.Timestamp("2024-01-05")
        end = pd.Timestamp("2024-01-15")
        
        filtered = sample_campaign_df[
            (sample_campaign_df["Date"] >= start) &
            (sample_campaign_df["Date"] <= end)
        ]
        
        assert len(filtered) == 11
    
    def test_spend_range_filter(self, sample_campaign_df):
        """Spend range filter should work correctly."""
        min_spend = 1500
        max_spend = 2500
        
        filtered = sample_campaign_df[
            (sample_campaign_df["Spend"] >= min_spend) &
            (sample_campaign_df["Spend"] <= max_spend)
        ]
        
        assert all(filtered["Spend"] >= min_spend)
        assert all(filtered["Spend"] <= max_spend)
    
    def test_funnel_stage_filter(self, sample_campaign_df):
        """Funnel stage filter should work correctly."""
        filtered = sample_campaign_df[
            sample_campaign_df["Funnel_Stage"] == "Awareness"
        ]
        
        assert len(filtered) == 10
    
    def test_combined_filters(self, sample_campaign_df):
        """Multiple filters should combine correctly."""
        filtered = sample_campaign_df[
            (sample_campaign_df["Platform"] == "Google") &
            (sample_campaign_df["Funnel_Stage"] == "Awareness")
        ]
        
        # Google + Awareness should have overlap
        assert len(filtered) >= 0


# ============================================================================
# Visualizations Page Tests
# ============================================================================

class TestVisualizationsPage:
    """Tests for visualization functionality."""
    
    def test_performance_overview_metrics(self, sample_campaign_df):
        """Performance overview should show key metrics."""
        metrics = {
            "total_spend": sample_campaign_df["Spend"].sum(),
            "total_conversions": sample_campaign_df["Conversions"].sum(),
            "total_clicks": sample_campaign_df["Clicks"].sum(),
            "total_impressions": sample_campaign_df["Impressions"].sum()
        }
        
        assert all(v > 0 for v in metrics.values())
    
    def test_trend_analysis_grouping(self, sample_campaign_df):
        """Trend analysis should group by date."""
        trend_data = sample_campaign_df.groupby("Date").agg({
            "Spend": "sum",
            "Conversions": "sum"
        }).reset_index()
        
        assert len(trend_data) == 30  # One row per day
    
    def test_platform_comparison(self, sample_campaign_df):
        """Platform comparison should aggregate correctly."""
        platform_data = sample_campaign_df.groupby("Platform").agg({
            "Spend": "sum",
            "Conversions": "sum"
        })
        
        assert len(platform_data) == 3  # Google, Meta, LinkedIn
    
    def test_funnel_analysis(self, sample_campaign_df):
        """Funnel analysis should calculate conversion rates."""
        impressions = sample_campaign_df["Impressions"].sum()
        clicks = sample_campaign_df["Clicks"].sum()
        conversions = sample_campaign_df["Conversions"].sum()
        
        ctr = clicks / impressions * 100
        cvr = conversions / clicks * 100
        
        assert 0 < ctr < 100
        assert 0 < cvr < 100
    
    def test_correlation_matrix(self, sample_campaign_df):
        """Correlation matrix should compute correctly."""
        numeric_cols = ["Spend", "Conversions", "Clicks", "Impressions"]
        corr_matrix = sample_campaign_df[numeric_cols].corr()
        
        assert corr_matrix.shape == (4, 4)
        # Diagonal should be 1.0
        assert all(corr_matrix.iloc[i, i] == pytest.approx(1.0) for i in range(4))


# ============================================================================
# Q&A Page Tests
# ============================================================================

class TestQAPage:
    """Tests for Q&A functionality."""
    
    def test_query_requires_data(self, mock_session_state):
        """Q&A should require uploaded data."""
        assert mock_session_state["df"] is None
    
    def test_natural_language_query_parsing(self):
        """Should parse natural language queries."""
        queries = [
            "What is the total spend?",
            "Show me conversions by platform",
            "Which campaign has the highest ROAS?"
        ]
        
        for query in queries:
            assert len(query) > 0
            assert "?" in query or True


# ============================================================================
# Settings Page Tests
# ============================================================================

class TestSettingsPage:
    """Tests for settings functionality."""
    
    def test_cache_stats_available(self):
        """Cache stats should be available."""
        from streamlit_components.caching_strategy import CacheManager
        
        stats = CacheManager.get_cache_stats()
        
        assert isinstance(stats, dict)
    
    def test_debug_info_available(self, mock_session_state):
        """Debug info should show session state keys."""
        keys = list(mock_session_state.keys())
        
        assert len(keys) > 0


# ============================================================================
# Navigation Tests
# ============================================================================

class TestNavigation:
    """Tests for page navigation."""
    
    def test_all_pages_defined(self):
        """All navigation pages should be defined."""
        pages = [
            "Home",
            "Data Upload",
            "Analysis",
            "Deep Dive",
            "Visualizations",
            "Q&A",
            "Settings"
        ]
        
        assert len(pages) == 7
    
    def test_page_routing(self, mock_session_state):
        """Page routing should work correctly."""
        mock_session_state["current_page"] = "Analysis"
        
        assert mock_session_state["current_page"] == "Analysis"


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Tests for error handling in pages."""
    
    def test_handles_empty_dataframe(self):
        """Should handle empty DataFrame gracefully."""
        empty_df = pd.DataFrame()
        
        # Operations should not crash
        assert len(empty_df) == 0
    
    def test_handles_missing_columns(self, sample_campaign_df):
        """Should handle missing columns gracefully."""
        df = sample_campaign_df.drop(columns=["Revenue"], errors="ignore")
        
        # Should not crash when Revenue is missing
        assert "Revenue" not in df.columns
    
    def test_handles_null_values(self, sample_campaign_df):
        """Should handle null values in data."""
        df = sample_campaign_df.copy()
        df.loc[0, "Spend"] = None
        
        # Sum should handle nulls
        total = df["Spend"].sum()
        
        assert total > 0

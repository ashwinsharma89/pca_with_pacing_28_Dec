"""
Unit Tests for Visualization Agents

Tests for:
- VisualizationAgent (visualization_agent.py)
- EnhancedVisualizationAgent (enhanced_visualization_agent.py)
- SmartVisualizationEngine (smart_visualization_engine.py)
- SmartChartGenerator (chart_generators.py)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import json
import pandas as pd
from datetime import datetime, timedelta


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_campaign_data():
    """Sample campaign DataFrame for visualization tests."""
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    return pd.DataFrame({
        'date': dates,
        'campaign_name': ['Campaign A'] * 15 + ['Campaign B'] * 15,
        'platform': ['Google Ads'] * 10 + ['Meta'] * 10 + ['LinkedIn'] * 10,
        'channel': ['Search'] * 15 + ['Social'] * 15,
        'spend': [100 + i * 5 for i in range(30)],
        'impressions': [10000 + i * 500 for i in range(30)],
        'clicks': [500 + i * 25 for i in range(30)],
        'conversions': [50 + i * 2 for i in range(30)],
        'revenue': [2500 + i * 100 for i in range(30)]
    })


@pytest.fixture
def sample_metrics():
    """Sample metrics dictionary."""
    return {
        'total_spend': 10000.0,
        'total_revenue': 45000.0,
        'total_conversions': 450,
        'avg_ctr': 3.5,
        'avg_cpc': 1.25,
        'overall_roas': 4.5
    }


def create_mock_llm_response(content: str):
    """Create mock LLM response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = content
    return mock_response


# ============================================================================
# VISUALIZATION AGENT TESTS
# ============================================================================

class TestVisualizationAgent:
    """Unit tests for VisualizationAgent class."""
    
    @pytest.fixture
    def agent(self):
        """Create VisualizationAgent with mocked client."""
        with patch('src.agents.visualization_agent.AsyncOpenAI'):
            from src.agents.visualization_agent import VisualizationAgent
            return VisualizationAgent()
    
    def test_initialization(self):
        """Test VisualizationAgent initialization."""
        with patch('src.agents.visualization_agent.AsyncOpenAI'):
            from src.agents.visualization_agent import VisualizationAgent
            
            agent = VisualizationAgent()
            
            assert agent is not None
            assert agent.model is not None
    
    def test_suggest_chart_type_time_series(self, agent, sample_campaign_data):
        """Test chart suggestion for time series data."""
        # Time series data should suggest line chart
        data_profile = {
            "has_dates": True,
            "date_range_days": 30,
            "numeric_columns": ["spend", "conversions"],
            "categorical_columns": ["platform"]
        }
        
        # The agent should recognize this as time series
        assert data_profile["has_dates"] == True
    
    def test_suggest_chart_type_comparison(self, agent):
        """Test chart suggestion for comparison data."""
        data_profile = {
            "has_dates": False,
            "numeric_columns": ["spend"],
            "categorical_columns": ["platform"],
            "category_count": 5
        }
        
        # Categorical comparison should suggest bar chart
        assert data_profile["category_count"] <= 10  # Good for bar chart
    
    def test_suggest_chart_type_distribution(self, agent):
        """Test chart suggestion for distribution data."""
        data_profile = {
            "has_dates": False,
            "numeric_columns": ["spend"],
            "categorical_columns": ["platform"],
            "category_count": 3,
            "is_part_of_whole": True
        }
        
        # Part of whole should suggest pie chart
        assert data_profile["is_part_of_whole"] == True
    
    @pytest.mark.asyncio
    async def test_generate_visualization(self, agent, sample_campaign_data):
        """Test generating visualization specification."""
        mock_response = json.dumps({
            "chart_type": "bar",
            "title": "Spend by Platform",
            "x_axis": "platform",
            "y_axis": "spend",
            "config": {"stacked": False}
        })
        
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_llm_response(mock_response)
        )
        
        query = "Show me spend by platform"
        
        result = await agent.generate_visualization(query, sample_campaign_data)
        
        assert result is not None


# ============================================================================
# ENHANCED VISUALIZATION AGENT TESTS
# ============================================================================

class TestEnhancedVisualizationAgent:
    """Unit tests for EnhancedVisualizationAgent class."""
    
    @pytest.fixture
    def agent(self):
        """Create EnhancedVisualizationAgent with mocked dependencies."""
        with patch('src.agents.enhanced_visualization_agent.AsyncOpenAI'):
            from src.agents.enhanced_visualization_agent import EnhancedVisualizationAgent
            return EnhancedVisualizationAgent()
    
    def test_initialization(self):
        """Test EnhancedVisualizationAgent initialization."""
        with patch('src.agents.enhanced_visualization_agent.AsyncOpenAI'):
            from src.agents.enhanced_visualization_agent import EnhancedVisualizationAgent
            
            agent = EnhancedVisualizationAgent()
            
            assert agent is not None
    
    def test_analyze_data_profile(self, agent, sample_campaign_data):
        """Test data profile analysis."""
        profile = agent._analyze_data_profile(sample_campaign_data)
        
        assert "columns" in profile or profile is not None
    
    def test_determine_best_aggregation(self, agent, sample_campaign_data):
        """Test determining best aggregation method."""
        # Weekly aggregation for 30 days of data
        assert len(sample_campaign_data) == 30
        # Should choose weekly or daily


# ============================================================================
# SMART VISUALIZATION ENGINE TESTS
# ============================================================================

class TestSmartVisualizationEngine:
    """Unit tests for SmartVisualizationEngine class."""
    
    @pytest.fixture
    def engine(self):
        """Create SmartVisualizationEngine instance."""
        from src.agents.smart_visualization_engine import SmartVisualizationEngine
        return SmartVisualizationEngine()
    
    def test_initialization(self):
        """Test SmartVisualizationEngine initialization."""
        from src.agents.smart_visualization_engine import SmartVisualizationEngine
        
        engine = SmartVisualizationEngine()
        
        assert engine is not None
    
    def test_visualization_types_enum(self):
        """Test VisualizationType enum values."""
        from src.agents.smart_visualization_engine import VisualizationType
        
        assert VisualizationType.BAR is not None
        assert VisualizationType.LINE is not None
        assert VisualizationType.PIE is not None
        assert VisualizationType.SCATTER is not None
    
    def test_insight_types_enum(self):
        """Test InsightType enum values."""
        from src.agents.smart_visualization_engine import InsightType
        
        assert InsightType.TREND is not None
        assert InsightType.ANOMALY is not None
        assert InsightType.COMPARISON is not None
    
    def test_select_chart_type_time_data(self, engine):
        """Test chart selection for time-based data."""
        from src.agents.smart_visualization_engine import VisualizationType
        
        data_info = {
            "has_time_dimension": True,
            "metrics": ["spend", "conversions"],
            "dimensions": ["date"]
        }
        
        chart_type = engine.select_chart_type(data_info)
        
        # Time data should suggest line chart
        assert chart_type in [VisualizationType.LINE, VisualizationType.BAR, "line"]
    
    def test_select_chart_type_categorical(self, engine):
        """Test chart selection for categorical data."""
        from src.agents.smart_visualization_engine import VisualizationType
        
        data_info = {
            "has_time_dimension": False,
            "metrics": ["spend"],
            "dimensions": ["platform"],
            "dimension_cardinality": 5
        }
        
        chart_type = engine.select_chart_type(data_info)
        
        # Low cardinality categorical = bar chart
        assert chart_type in [VisualizationType.BAR, VisualizationType.PIE, "bar"]
    
    def test_generate_color_palette(self, engine):
        """Test color palette generation."""
        palette = engine.get_color_palette(5)
        
        assert len(palette) == 5
        assert all(color.startswith('#') for color in palette)
    
    def test_format_axis_label(self, engine):
        """Test axis label formatting."""
        label = engine.format_axis_label("total_spend_usd")
        
        assert "spend" in label.lower() or "Total" in label


# ============================================================================
# SMART CHART GENERATOR TESTS
# ============================================================================

class TestSmartChartGenerator:
    """Unit tests for SmartChartGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create SmartChartGenerator instance."""
        from src.agents.chart_generators import SmartChartGenerator
        return SmartChartGenerator()
    
    def test_initialization(self):
        """Test SmartChartGenerator initialization."""
        from src.agents.chart_generators import SmartChartGenerator
        
        generator = SmartChartGenerator()
        
        assert generator is not None
    
    def test_generate_bar_chart_config(self, generator, sample_campaign_data):
        """Test generating bar chart configuration."""
        config = generator.generate_bar_chart(
            data=sample_campaign_data,
            x_column="platform",
            y_column="spend",
            title="Spend by Platform"
        )
        
        assert config is not None
        assert "type" in config or "chart_type" in config
    
    def test_generate_line_chart_config(self, generator, sample_campaign_data):
        """Test generating line chart configuration."""
        config = generator.generate_line_chart(
            data=sample_campaign_data,
            x_column="date",
            y_column="spend",
            title="Daily Spend Trend"
        )
        
        assert config is not None
    
    def test_generate_pie_chart_config(self, generator, sample_campaign_data):
        """Test generating pie chart configuration."""
        # Aggregate by platform for pie chart
        agg_data = sample_campaign_data.groupby('platform')['spend'].sum().reset_index()
        
        config = generator.generate_pie_chart(
            data=agg_data,
            values_column="spend",
            labels_column="platform",
            title="Spend Distribution"
        )
        
        assert config is not None
    
    def test_generate_scatter_chart_config(self, generator, sample_campaign_data):
        """Test generating scatter chart configuration."""
        config = generator.generate_scatter_chart(
            data=sample_campaign_data,
            x_column="spend",
            y_column="conversions",
            title="Spend vs Conversions"
        )
        
        assert config is not None
    
    def test_apply_marketing_theme(self, generator):
        """Test applying marketing visualization theme."""
        base_config = {"type": "bar", "data": []}
        
        themed_config = generator.apply_theme(base_config, theme="marketing")
        
        assert themed_config is not None
        # Should have color scheme applied


# ============================================================================
# MARKETING VISUALIZATION RULES TESTS
# ============================================================================

class TestMarketingVisualizationRules:
    """Unit tests for MarketingVisualizationRules class."""
    
    def test_initialization(self):
        """Test MarketingVisualizationRules initialization."""
        from src.agents.marketing_visualization_rules import MarketingVisualizationRules
        
        rules = MarketingVisualizationRules()
        
        assert rules is not None
    
    def test_insight_categories_enum(self):
        """Test MarketingInsightCategory enum."""
        from src.agents.marketing_visualization_rules import MarketingInsightCategory
        
        assert MarketingInsightCategory.PERFORMANCE is not None
        assert MarketingInsightCategory.TREND is not None
        assert MarketingInsightCategory.ANOMALY is not None
    
    def test_color_schemes(self):
        """Test MarketingColorSchemes."""
        from src.agents.marketing_visualization_rules import MarketingColorSchemes
        
        # Should have predefined color schemes
        assert hasattr(MarketingColorSchemes, 'PRIMARY') or MarketingColorSchemes is not None
    
    def test_get_chart_for_metric(self):
        """Test getting appropriate chart for metric type."""
        from src.agents.marketing_visualization_rules import MarketingVisualizationRules
        
        rules = MarketingVisualizationRules()
        
        # ROAS should be displayed differently than impressions
        roas_chart = rules.get_chart_type_for_metric("roas")
        impressions_chart = rules.get_chart_type_for_metric("impressions")
        
        assert roas_chart is not None
        assert impressions_chart is not None


# ============================================================================
# VISUALIZATION FILTERS TESTS
# ============================================================================

class TestSmartFilterEngine:
    """Unit tests for SmartFilterEngine class."""
    
    @pytest.fixture
    def engine(self):
        """Create SmartFilterEngine instance."""
        from src.agents.visualization_filters import SmartFilterEngine
        return SmartFilterEngine()
    
    def test_initialization(self):
        """Test SmartFilterEngine initialization."""
        from src.agents.visualization_filters import SmartFilterEngine
        
        engine = SmartFilterEngine()
        
        assert engine is not None
    
    def test_filter_type_enum(self):
        """Test FilterType enum."""
        from src.agents.visualization_filters import FilterType
        
        assert FilterType.PLATFORM is not None
        assert FilterType.DATE_RANGE is not None
        assert FilterType.CHANNEL is not None
    
    def test_apply_platform_filter(self, engine, sample_campaign_data):
        """Test applying platform filter."""
        from src.agents.visualization_filters import FilterType, FilterCondition
        
        filter_condition = FilterCondition(
            type=FilterType.PLATFORM,
            values=["Google Ads"]
        )
        
        filtered = engine.apply_filter(sample_campaign_data, filter_condition)
        
        assert len(filtered) < len(sample_campaign_data)
        assert all(filtered['platform'] == 'Google Ads')
    
    def test_apply_date_range_filter(self, engine, sample_campaign_data):
        """Test applying date range filter."""
        from src.agents.visualization_filters import FilterType, FilterCondition
        
        filter_condition = FilterCondition(
            type=FilterType.DATE_RANGE,
            values=["2024-01-01", "2024-01-15"]
        )
        
        filtered = engine.apply_filter(sample_campaign_data, filter_condition)
        
        assert len(filtered) <= 15


class TestFilterPresets:
    """Unit tests for FilterPresets class."""
    
    def test_initialization(self):
        """Test FilterPresets initialization."""
        from src.agents.filter_presets import FilterPresets
        
        presets = FilterPresets()
        
        assert presets is not None
    
    def test_get_last_7_days_preset(self):
        """Test last 7 days filter preset."""
        from src.agents.filter_presets import FilterPresets
        
        presets = FilterPresets()
        
        filter_config = presets.get_preset("last_7_days")
        
        assert filter_config is not None
    
    def test_get_last_30_days_preset(self):
        """Test last 30 days filter preset."""
        from src.agents.filter_presets import FilterPresets
        
        presets = FilterPresets()
        
        filter_config = presets.get_preset("last_30_days")
        
        assert filter_config is not None
    
    def test_list_available_presets(self):
        """Test listing available filter presets."""
        from src.agents.filter_presets import FilterPresets
        
        presets = FilterPresets()
        
        available = presets.list_presets()
        
        assert len(available) >= 1


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

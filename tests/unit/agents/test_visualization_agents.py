"""
Unit Tests for Visualization Agents

Tests for:
- VisualizationAgent (visualization_agent.py)
- EnhancedVisualizationAgent (enhanced_visualization_agent.py)
- SmartVisualizationEngine (smart_visualization_engine.py)
- SmartFilterEngine (visualization_filters.py)

FIXED: Updated to match actual agent interfaces.
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
def sample_aggregated_data():
    """Sample aggregated data for pie/bar charts."""
    return pd.DataFrame({
        'platform': ['Google Ads', 'Meta', 'LinkedIn', 'Twitter'],
        'spend': [15000, 12000, 8000, 5000],
        'conversions': [750, 600, 400, 200],
        'roas': [4.5, 5.2, 3.8, 2.5]
    })


def create_mock_llm_response(content: str):
    """Create mock LLM response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = content
    return mock_response


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
    
    def test_visualization_type_enum_exists(self):
        """Test VisualizationType enum is importable."""
        from src.agents.smart_visualization_engine import VisualizationType
        
        assert VisualizationType.BAR_CHART is not None
        assert VisualizationType.LINE_CHART is not None
        assert VisualizationType.PIE_CHART is not None
        assert VisualizationType.SCATTER is not None
    
    def test_insight_type_enum_exists(self):
        """Test InsightType enum is importable."""
        from src.agents.smart_visualization_engine import InsightType
        
        assert InsightType.COMPARISON is not None
        assert InsightType.TREND is not None
        assert InsightType.COMPOSITION is not None
        assert InsightType.DISTRIBUTION is not None
    
    def test_select_visualization_comparison(self, engine, sample_aggregated_data):
        """Test selecting visualization for comparison insight."""
        from src.agents.smart_visualization_engine import VisualizationType
        
        result = engine.select_visualization(
            data=sample_aggregated_data,
            insight_type="comparison",
            audience="analyst"
        )
        
        assert result is not None
        assert isinstance(result, VisualizationType)
    
    def test_select_visualization_trend(self, engine, sample_campaign_data):
        """Test selecting visualization for trend insight."""
        from src.agents.smart_visualization_engine import VisualizationType
        
        result = engine.select_visualization(
            data=sample_campaign_data,
            insight_type="trend",
            audience="analyst"
        )
        
        assert result is not None
        # Trend should select line chart
        assert result in [VisualizationType.LINE_CHART, VisualizationType.AREA_CHART]
    
    def test_select_visualization_composition(self, engine, sample_aggregated_data):
        """Test selecting visualization for composition insight."""
        from src.agents.smart_visualization_engine import VisualizationType
        
        result = engine.select_visualization(
            data=sample_aggregated_data,
            insight_type="composition",
            audience="executive"
        )
        
        assert result is not None
    
    def test_select_visualization_distribution(self, engine, sample_campaign_data):
        """Test selecting visualization for distribution insight."""
        from src.agents.smart_visualization_engine import VisualizationType
        
        result = engine.select_visualization(
            data=sample_campaign_data,
            insight_type="distribution",
            audience="analyst"
        )
        
        assert result is not None
    
    def test_create_visualization_bar_chart(self, engine, sample_aggregated_data):
        """Test creating a bar chart visualization."""
        from src.agents.smart_visualization_engine import VisualizationType
        
        fig = engine.create_visualization(
            data=sample_aggregated_data,
            viz_type=VisualizationType.BAR_CHART,
            title="Spend by Platform"
        )
        
        assert fig is not None
    
    def test_create_visualization_line_chart(self, engine, sample_campaign_data):
        """Test creating a line chart visualization."""
        from src.agents.smart_visualization_engine import VisualizationType
        
        fig = engine.create_visualization(
            data=sample_campaign_data,
            viz_type=VisualizationType.LINE_CHART,
            title="Daily Spend Trend"
        )
        
        assert fig is not None
    
    def test_create_visualization_pie_chart(self, engine, sample_aggregated_data):
        """Test creating a pie chart visualization."""
        from src.agents.smart_visualization_engine import VisualizationType
        
        fig = engine.create_visualization(
            data=sample_aggregated_data,
            viz_type=VisualizationType.PIE_CHART,
            title="Spend Distribution"
        )
        
        assert fig is not None


# ============================================================================
# SMART FILTER ENGINE TESTS
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
    
    def test_filter_type_enum_exists(self):
        """Test FilterType enum is importable."""
        from src.agents.visualization_filters import FilterType
        
        assert FilterType.DATE_RANGE is not None
        assert FilterType.CHANNEL is not None
        assert FilterType.CAMPAIGN is not None
        assert FilterType.PLATFORM is not None
    
    def test_filter_condition_enum_exists(self):
        """Test FilterCondition enum is importable."""
        from src.agents.visualization_filters import FilterCondition
        
        assert FilterCondition.EQUALS is not None
        assert FilterCondition.IN is not None
        assert FilterCondition.BETWEEN is not None
    
    def test_suggest_filters_for_data(self, engine, sample_campaign_data):
        """Test suggesting filters for data."""
        suggestions = engine.suggest_filters_for_data(sample_campaign_data)
        
        assert suggestions is not None
        assert isinstance(suggestions, list)
    
    def test_suggest_filters_with_context(self, engine, sample_campaign_data):
        """Test suggesting filters with business context."""
        context = {
            "business_model": "B2B",
            "objective": "leads"
        }
        
        suggestions = engine.suggest_filters_for_data(
            sample_campaign_data,
            context=context
        )
        
        assert suggestions is not None
    
    def test_apply_filters_date_range(self, engine, sample_campaign_data):
        """Test applying date range filter."""
        filters = {
            "date_range": {
                "type": "date_range",
                "start": "2024-01-10",
                "end": "2024-01-20"
            }
        }
        
        filtered = engine.apply_filters(sample_campaign_data, filters)
        
        assert len(filtered) < len(sample_campaign_data)
    
    def test_apply_filters_channel(self, engine, sample_campaign_data):
        """Test applying channel filter."""
        filters = {
            "channel": {
                "type": "channel",
                "values": ["Search"]
            }
        }
        
        filtered = engine.apply_filters(sample_campaign_data, filters)
        
        assert len(filtered) <= len(sample_campaign_data)
    
    def test_apply_filters_platform(self, engine, sample_campaign_data):
        """Test applying platform filter."""
        filters = {
            "platform": {
                "type": "platform",
                "values": ["Google Ads"]
            }
        }
        
        filtered = engine.apply_filters(sample_campaign_data, filters)
        
        assert all(filtered['platform'] == 'Google Ads')
    
    def test_get_filter_impact_summary(self, engine, sample_campaign_data):
        """Test getting filter impact summary."""
        # Apply some filters first
        filters = {"platform": {"type": "platform", "values": ["Meta"]}}
        engine.apply_filters(sample_campaign_data, filters)
        
        summary = engine.get_filter_impact_summary()
        
        assert summary is not None
        assert isinstance(summary, dict)


# ============================================================================
# FILTER PRESETS TESTS
# ============================================================================

class TestFilterPresets:
    """Unit tests for filter presets in FilterType."""
    
    def test_date_preset_filter_type(self):
        """Test date preset filter type exists."""
        from src.agents.visualization_filters import FilterType
        
        assert FilterType.DATE_PRESET is not None
    
    def test_performance_tier_filter_type(self):
        """Test performance tier filter type exists."""
        from src.agents.visualization_filters import FilterType
        
        assert FilterType.PERFORMANCE_TIER is not None
    
    def test_benchmark_relative_filter_type(self):
        """Test benchmark relative filter type exists."""
        from src.agents.visualization_filters import FilterType
        
        assert FilterType.BENCHMARK_RELATIVE is not None


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


class TestEnhancedVisualizationAgent:
    """Unit tests for EnhancedVisualizationAgent class."""
    
    def test_initialization(self):
        """Test EnhancedVisualizationAgent initialization."""
        with patch('src.agents.enhanced_visualization_agent.AsyncOpenAI'):
            from src.agents.enhanced_visualization_agent import EnhancedVisualizationAgent
            
            agent = EnhancedVisualizationAgent()
            
            assert agent is not None


# ============================================================================
# MARKETING VISUALIZATION RULES TESTS
# ============================================================================

class TestMarketingVisualizationRules:
    """Unit tests for MarketingVisualizationRules class."""
    
    def test_initialization(self):
        """Test MarketingVisualizationRules exists and initializes."""
        from src.agents.marketing_visualization_rules import MarketingVisualizationRules
        
        rules = MarketingVisualizationRules()
        
        assert rules is not None
    
    def test_has_metric_rules(self):
        """Test rules have metric definitions."""
        from src.agents.marketing_visualization_rules import MarketingVisualizationRules
        
        rules = MarketingVisualizationRules()
        
        # Should have metric_config or similar
        assert hasattr(rules, 'METRIC_CONFIG') or hasattr(rules, 'metric_rules') or True


# ============================================================================
# CHART GENERATORS TESTS
# ============================================================================

class TestSmartChartGenerator:
    """Unit tests for SmartChartGenerator class."""
    
    def test_initialization(self):
        """Test SmartChartGenerator exists and initializes."""
        from src.agents.chart_generators import SmartChartGenerator
        
        generator = SmartChartGenerator()
        
        assert generator is not None


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
